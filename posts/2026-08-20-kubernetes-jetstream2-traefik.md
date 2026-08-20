---
categories:
- kubernetes
- jetstream
date: '2026-08-20 09:00:00'
layout: post
slug: kubernetes-jetstream2-traefik
title: Install Traefik Ingress Controller on Jetstream2 Kubernetes (2 of 4)
---

This post is part of a series on deploying JupyterHub on Jetstream2:

1. [Deploy Kubernetes on Jetstream2](/posts/2026-08-20-kubernetes-jetstream2-magnum)
2. **Install Traefik Ingress Controller**
3. [Deploy JupyterHub](/posts/2026-08-20-kubernetes-jetstream2-jupyterhub)
4. [Setup HTTPS with cert-manager](/posts/2026-08-20-kubernetes-jetstream2-certmanager)

This guide covers how to install [Traefik](https://doc.traefik.io/traefik/) as an ingress controller on a Jetstream2 Kubernetes cluster and configure DNS. Traefik replaces `ingress-nginx`, which has been [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/). Traefik supports both the standard Kubernetes Ingress API and the newer Gateway API, making it a forward-compatible choice.

This guide assumes you already have a running cluster — see [Deploy Kubernetes on Jetstream2](/posts/2026-08-20-kubernetes-jetstream2-magnum) if you need to create one first. Make sure `KUBECONFIG` is set and `kubectl get nodes` works.

## Install Traefik

Install the Traefik Helm chart:

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm upgrade --install traefik traefik/traefik \
    --namespace traefik --create-namespace
```

This deploys Traefik (this tutorial tested with v3.7) and creates a Kubernetes Service of type `LoadBalancer`. On Jetstream2, this automatically provisions an OpenStack Octavia load balancer with a floating IP.

Wait for the external IP to be assigned (takes about 2 minutes):

```bash
kubectl get svc -n traefik traefik -w
```

Once the `EXTERNAL-IP` column shows an address, note it:

```bash
export IP=$(kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $IP
```

```
149.165.173.224
```

Verify the Traefik pod is running:

```bash
kubectl get pods -n traefik
```

```
NAME                       READY   STATUS    RESTARTS   AGE
traefik-798b4cb98f-8bwfd   1/1     Running   0          2m46s
```

### Use a Fixed Floating IP

By default, Traefik creates a new OpenStack load balancer with a random floating IP. If you delete and recreate the cluster, this IP changes. To use a fixed IP instead:

1. Create a floating IP in OpenStack:

```bash
openstack floating ip create public
export FIXED_IP=<FLOATING_IP>
```

2. Find the Traefik load balancer:

```bash
export LB=$(openstack loadbalancer list --name traefik -f value -c id)
```

> **Note**: The `openstack loadbalancer` command requires `python-octaviaclient`. Install it with `pip install python-octaviaclient` if the command is not found.

3. Associate the fixed IP with the load balancer's VIP port:

```bash
LB_VIP_PORT_ID=$(openstack loadbalancer show $LB -c vip_port_id -f value)
EXISTING_FIP=$(openstack floating ip list --port $LB_VIP_PORT_ID -f value -c ID)
if [ -n "$EXISTING_FIP" ]; then
    openstack floating ip unset --port $EXISTING_FIP
fi
openstack floating ip set --port $LB_VIP_PORT_ID $FIXED_IP
export IP=$FIXED_IP
```

> **Alternative — request the IP at install time:** You can instead ask Traefik to request a specific floating IP by passing `--set service.spec.loadBalancerIP=$FIXED_IP` to the `helm upgrade --install` command in the [Install Traefik](#install-traefik) section. This flag only takes effect on a **fresh** install; if Traefik is already running, `helm uninstall traefik` first, then reinstall with the flag. (Discovered by Ana V. Espinoza during live testing — see the [migration guide](/posts/2026-08-20-migrate-nginx-traefik-jetstream2-kubernetes#retain-the-existing-ip-optional).)

## Configure DNS

### Using the Jetstream Subdomain

Jetstream2 provides a subdomain for each project:

```
subdomain.$PROJ.projects.jetstream-cloud.org
```

where `PROJ` is the ID of your Jetstream2 allocation (all lowercase). Create a DNS record pointing to the Traefik IP:

```bash
export PROJ="xxx000000"
export SUBDOMAIN="jhub"
openstack recordset create $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN --type A --record $IP --ttl 3600
```

If you get a "Duplicate recordset" error, update the existing record:

```bash
openstack recordset set $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN.$PROJ.projects.jetstream-cloud.org. --record $IP
```

### Using a Custom Domain

If you have a custom domain, create an A record pointing to `$IP` with your DNS provider.

## Test the Traefik Ingress

Deploy a simple echo server to verify that Traefik and DNS are working. The repository includes an `echo-test.yaml` manifest that creates a Deployment, a Service, and an Ingress with `ingressClassName: traefik`.

Edit the `host` field in `echo-test.yaml` to match your subdomain, then deploy:

```bash
kubectl create -f echo-test.yaml
```

Wait for the pod to be ready:

```bash
kubectl get pods -w
```

Check that the Ingress got the Traefik IP:

```bash
kubectl get ingress
```

```
NAME           CLASS     HOSTS                                             ADDRESS           PORTS   AGE
echo-ingress   traefik   testpage.cis230085.projects.jetstream-cloud.org   149.165.173.224   80      4s
```

Then test with curl:

```bash
curl http://testpage.$PROJ.projects.jetstream-cloud.org
```

```
Testing Traefik Ingress on Jetstream!
```

Once verified, clean up the test deployment:

```bash
kubectl delete -f echo-test.yaml
```

With Traefik installed and DNS configured, continue to [Deploy JupyterHub](/posts/2026-08-20-kubernetes-jetstream2-jupyterhub). You can also skip ahead to [Setup HTTPS with cert-manager](/posts/2026-08-20-kubernetes-jetstream2-certmanager) if you already have JupyterHub running.
