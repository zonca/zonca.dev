---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-05-18 12:00:00'
layout: post
slug: migrate-nginx-traefik-jetstream2-kubernetes
title: Migrate from NGINX to Traefik Ingress on Jetstream2 Kubernetes
---

`ingress-nginx` has been [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) and will no longer receive updates. This guide walks through migrating an existing Jetstream2 Kubernetes cluster from `ingress-nginx` to [Traefik](https://doc.traefik.io/traefik/), with minimal downtime.

This guide is for **existing clusters** already running JupyterHub with `ingress-nginx`. For new clusters, see the [4-post tutorial series](/posts/2026-05-18-kubernetes-jetstream2-magnum).

This guide is based on [Ana V. Espinoza's migration instructions](https://github.com/zonca/zonca.dev/pull/73) and [Traefik's official migration documentation](https://doc.traefik.io/traefik/migrate/nginx-to-traefik/), adapted and live-tested on Jetstream2.

## Prerequisites

- An existing Jetstream2 Kubernetes cluster running `ingress-nginx` as the ingress controller
- JupyterHub deployed with HTTPS via cert-manager
- `kubectl`, `helm`, and the `openstack` CLI installed and configured
- The `KUBECONFIG` environment variable set for your cluster

## Overview

The migration follows a side-by-side strategy: install Traefik alongside nginx, switch the Ingress class, update DNS, and then remove nginx. This approach minimizes downtime because both ingress controllers run simultaneously during the transition.

1. Install Traefik alongside `ingress-nginx`
2. Update the JupyterHub Ingress to use `ingressClassName: traefik`
3. Update the cert-manager ClusterIssuer to use Traefik
4. Update DNS to point to the Traefik load balancer IP
5. Remove `ingress-nginx`

## Step 1: Install Traefik

Install the Traefik Helm chart. This creates a second load balancer alongside the existing nginx one:

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm upgrade --install traefik traefik/traefik \
    --namespace traefik --create-namespace
```

Wait for the external IP to be assigned (takes about 2 minutes):

```bash
kubectl get svc -n traefik traefik -w
```

Note the Traefik IP:

```bash
export TRAEFIK_IP=$(kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $TRAEFIK_IP
```

Also note the existing nginx IP:

```bash
export NGINX_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $NGINX_IP
```

At this point, both ingress controllers are running. Nginx continues to serve traffic, while Traefik is idle.

## Step 2: Update the JupyterHub Ingress

Update `secrets.yaml` to use `ingressClassName: traefik` instead of the deprecated `kubernetes.io/ingress.class: "nginx"` annotation. If your `secrets.yaml` still uses the annotation format, change it:

**Before:**
```yaml
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt"
```

**After:**
```yaml
ingress:
  enabled: true
  ingressClassName: traefik
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt"
```

Then upgrade JupyterHub:

```bash
helm upgrade jhub jupyterhub/jupyterhub \
    --namespace jhub --version 4.3.3 \
    --values config_standard_storage.yaml --values secrets.yaml
```

This immediately changes the Ingress class from `nginx` to `traefik`. From this point:

- **Traffic through the Traefik load balancer** reaches JupyterHub ✅
- **Traffic through the nginx load balancer** gets a 404, because nginx no longer watches this Ingress ⚠️

This is why the DNS switch in Step 4 is important.

> **Note on nginx-specific annotations**: If you use nginx-specific annotations like `nginx.ingress.kubernetes.io/proxy-body-size`, replace them with the Traefik equivalent. For example, to allow large file uploads:
>
> ```yaml
> # nginx annotation (unsupported by Traefik):
> # nginx.ingress.kubernetes.io/proxy-body-size: "500m"
>
> # Traefik equivalent:
> traefik.ingress.kubernetes.io/middlewares.limit.buffering.maxRequestBodyBytes: "500000000"
> ```

## Step 3: Update the cert-manager ClusterIssuer

Update the ClusterIssuer to use Traefik for HTTP01 challenges. Edit `https_cluster_issuer.yml` and change the `class` from `nginx` to `traefik`, then apply:

```bash
cd jupyterhub-deploy-kubernetes-jetstream/setup_https
sed 's/YOUREMAIL/your@email.edu/' https_cluster_issuer.yml | kubectl apply -f -
```

This ensures that future certificate renewals use Traefik for the HTTP01 challenge.

## Step 4: Update DNS

### Option A: Direct cutover (brief downtime)

Update the DNS record to point to the Traefik IP:

```bash
export PROJ="xxx000000"
export K8S_CLUSTER_NAME=k8s
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $TRAEFIK_IP
```

There will be a brief downtime while DNS caches update. You can verify when the change has propagated:

```bash
watch nslookup $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org
```

### Option B: Dual-A-record (zero downtime)

Add both IPs to the DNS record so that traffic can reach either ingress controller:

```bash
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $NGINX_IP --record $TRAEFIK_IP
```

Clients that resolve to the Traefik IP get JupyterHub directly. Clients that still resolve to the nginx IP get a 404, but DNS round-robin means roughly half of requests succeed. After DNS fully propagates (wait a few minutes), switch to the Traefik-only record:

```bash
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $TRAEFIK_IP
```

### Verify connectivity

Test both load balancers directly to confirm Traefik is serving JupyterHub and nginx is no longer needed:

```bash
export FQDN=$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org

# Test HTTPS via Traefik
curl --connect-to "${FQDN}:443:${TRAEFIK_IP}:443" "https://${FQDN}" -v -D - 2>&1 | grep "HTTP/"

# Test HTTPS via nginx (should return 404)
curl --connect-to "${FQDN}:443:${NGINX_IP}:443" "https://${FQDN}" -v -D - 2>&1 | grep "HTTP/"
```

## Step 5: Remove ingress-nginx

Once DNS points to the Traefik IP and JupyterHub is accessible, uninstall `ingress-nginx`:

```bash
helm uninstall -n ingress-nginx ingress-nginx
kubectl delete ns ingress-nginx
```

This removes the nginx pods, the nginx load balancer, and its namespace. The associated OpenStack load balancer is also cleaned up automatically.

## Verify the Migration

Confirm that everything works:

```bash
# Check that only Traefik is running as an ingress controller
kubectl get ns | grep -E "traefik|ingress"

# Check the Ingress class
kubectl get ingress -n jhub

# Check the certificate
kubectl get certificate -n jhub

# Test HTTPS access
curl -s -o /dev/null -w "%{http_code}" https://k8s.$PROJ.projects.jetstream-cloud.org/
```

You should see:
- Only the `traefik` namespace (no `ingress-nginx`)
- Ingress with `CLASS: traefik`
- Certificate `READY: True`
- HTTPS returns `302`

## Summary of Changes

| Component | Before | After |
|-----------|--------|-------|
| Ingress controller | `ingress-nginx` | `traefik` |
| Ingress class | `nginx` | `traefik` |
| Secret annotation | `kubernetes.io/ingress.class: "nginx"` | `ingressClassName: traefik` |
| cert-manager solver | `class: nginx` | `class: traefik` |
| Load balancer IP | `$NGINX_IP` | `$TRAEFIK_IP` |

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.
