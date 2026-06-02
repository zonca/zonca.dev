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

The migration follows a side-by-side strategy: install Traefik alongside nginx, switch the Ingress class, update DNS, and then remove nginx.

### Simple approach (brief downtime)

This is the simplest method. After switching the JupyterHub Ingress to `ingressClassName: traefik`, nginx can no longer serve it, so there is a brief downtime window while DNS propagates.

1. Install Traefik alongside `ingress-nginx`
2. Update the JupyterHub Ingress to use `ingressClassName: traefik`
3. Update the cert-manager ClusterIssuer to use Traefik
4. Update DNS to point to the Traefik load balancer IP
5. Remove `ingress-nginx`

### Minimal-downtime approach

If uptime is critical, use Traefik's [`kubernetesIngressNGINX`](https://doc.traefik.io/traefik/migrate/nginx-to-traefik/) provider, which makes Traefik serve existing `nginx`-class Ingresses without any changes. This allows you to switch DNS to Traefik first, verify everything works, and only then update the Ingress class and remove nginx. See the [Minimal-Downtime Migration](#minimal-downtime-migration) section below.

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
curl -s -o /dev/null -w "%{http_code}\n" https://$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org/
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

## Minimal-Downtime Migration

If uptime is critical, use Traefik's `kubernetesIngressNGINX` provider to serve existing `nginx`-class Ingresses through Traefik without any changes. This eliminates the downtime window between switching the Ingress class and updating DNS. The approach was [suggested by Ana V. Espinoza](https://github.com/zonca/zonca.dev/pull/94#issuecomment-4568109164) and follows [Traefik's official migration guide](https://doc.traefik.io/traefik/migrate/nginx-to-traefik/).

The step order changes from the simple approach:

1. Install Traefik **with** `kubernetesIngressNGINX.enabled=true` and `publishService.enabled=false`
2. Switch DNS to the Traefik IP (nginx-class Ingresses still work via Traefik)
3. Preserve the `nginx` IngressClass, then uninstall `ingress-nginx`
4. Update the JupyterHub Ingress to `ingressClassName: traefik`
5. Update the cert-manager ClusterIssuer
6. (Optional) Re-install Traefik without `kubernetesIngressNGINX` and delete the `nginx` IngressClass

### Step 1: Install Traefik with NGINX compatibility

Install Traefik with the `kubernetesIngressNGINX` provider enabled. This provider makes Traefik watch for `nginx`-class Ingresses and serve them natively, translating NGINX annotations into Traefik configuration automatically.

Disable `publishService` to prevent Traefik from overwriting the Ingress status with its own IP, which would cause a race condition with nginx:

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm upgrade --install traefik traefik/traefik \
    --namespace traefik --create-namespace \
    --set providers.kubernetesIngressNGINX.enabled=true \
    --set providers.kubernetesIngressNGINX.publishService.enabled=false
```

Wait for the external IP:

```bash
export TRAEFIK_IP=$(kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $TRAEFIK_IP
```

At this point, **both nginx and Traefik serve your existing Ingresses**. Traffic is still flowing through nginx since DNS points to the nginx IP.

### Step 2: Switch DNS to Traefik

Before changing DNS, verify that Traefik correctly serves your Ingresses by testing directly against the Traefik IP:

```bash
export FQDN=$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org

# Test HTTPS via Traefik (should return 302)
curl -s -o /dev/null -w "%{http_code}\n" \
    --connect-to "${FQDN}:443:${TRAEFIK_IP}:443" "https://${FQDN}"
```

If that returns `302`, switch DNS to point to the Traefik IP:

```bash
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $TRAEFIK_IP
```

Wait for DNS propagation, then verify JupyterHub is accessible via the domain name. There is **zero downtime** because Traefik serves the `nginx`-class Ingresses identically.

### Step 3: Remove ingress-nginx

Before uninstalling nginx, preserve the `nginx` IngressClass with a `helm.sh/resource-policy: keep` annotation. Traefik's `kubernetesIngressNGINX` provider needs this IngressClass to discover the Ingresses:

```bash
helm upgrade ingress-nginx ingress-nginx \
    --repo https://kubernetes.github.io/ingress-nginx \
    --namespace ingress-nginx \
    --reuse-values \
    --set-json 'controller.ingressClassResource.annotations={"helm.sh/resource-policy":"keep"}'
```

> **Important:** The `--reuse-values` flag preserves your existing nginx configuration. Without it, Helm resets everything to defaults.

Then uninstall nginx:

```bash
helm uninstall -n ingress-nginx ingress-nginx
kubectl delete ns ingress-nginx
```

The `nginx` IngressClass is preserved by the annotation. Verify that JupyterHub still works — Traefik continues serving the `nginx`-class Ingresses through the `kubernetesIngressNGINX` provider.

### Step 4: Update the JupyterHub Ingress

Now update `secrets.yaml` to use `ingressClassName: traefik` and upgrade JupyterHub (same as Step 2 in the simple approach above).

### Step 5: Update the cert-manager ClusterIssuer

Update the ClusterIssuer to use `class: traefik` (same as Step 3 in the simple approach above).

### Step 6: Clean up (optional)

Once all Ingresses have been updated to `ingressClassName: traefik`, the `kubernetesIngressNGINX` provider is no longer needed. Re-install Traefik without it and delete the preserved `nginx` IngressClass:

```bash
helm upgrade --install traefik traefik/traefik \
    --namespace traefik \
    --reuse-values \
    --set providers.kubernetesIngressNGINX.enabled=false

kubectl delete ingressclass nginx
```

> **Note:** After disabling `kubernetesIngressNGINX`, any remaining `nginx`-class Ingresses will return 404. Make sure all Ingresses have been updated to `ingressClassName: traefik` before running this step.

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.
