---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-05-18'
layout: post
slug: kubernetes-jetstream2-traefik-jupyterhub-2026
title: Install Traefik, HTTPS, and JupyterHub on Jetstream2 Kubernetes
---

This guide covers how to set up [Traefik](https://doc.traefik.io/traefik/) as an ingress controller on a Jetstream2 Kubernetes cluster, configure HTTPS with Let's Encrypt, and deploy JupyterHub. It assumes you already have a running cluster — see [Deploy Kubernetes on Jetstream2 with Magnum and Cluster API](/posts/kubernetes-jetstream2-magnum-2026) if you need to create one first.

Traefik replaces `ingress-nginx`, which has been [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/). Traefik supports both the standard Kubernetes Ingress API and the newer Gateway API, making it a forward-compatible choice.

## Install Traefik

Install the Traefik Helm chart:

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update
helm upgrade --install traefik traefik/traefik \
    --namespace traefik --create-namespace
```

This creates a Traefik deployment and a Kubernetes Service of type `LoadBalancer`. On Jetstream2, this automatically provisions an OpenStack Octavia load balancer with a floating IP.

Wait for the external IP to be assigned:

```bash
kubectl get svc -n traefik traefik -w
```

Once the `EXTERNAL-IP` column shows an address, note it:

```bash
export IP=$(kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo $IP
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

## Configure DNS

### Using the Jetstream Subdomain

Jetstream2 provides a subdomain for each project:

```bash
xxxxxx.$PROJ.projects.jetstream-cloud.org
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

Deploy a simple echo server to verify that Traefik and DNS are working:

```bash
kubectl create -f echo-test.yaml
```

The `echo-test.yaml` manifest creates a Deployment, a Service, and an Ingress. Make sure the Ingress uses `ingressClassName: traefik` and the `host` field matches your domain. Then visit:

```bash
http://testpage.$PROJ.projects.jetstream-cloud.org
```

You should see a response like "Testing Traefik Ingress on Jetstream!".

Once verified, clean up the test deployment:

```bash
kubectl delete -f echo-test.yaml
```

## Deploy JupyterHub

First, create the secrets file from the root of the repository:

```bash
cd jupyterhub-deploy-kubernetes-jetstream
bash create_secrets.sh
```

The default `secrets.yaml` assumes you are deploying on a `projects.jetstream-cloud.org` subdomain. If using a custom domain, edit the file accordingly.

Then configure and install JupyterHub:

```bash
bash configure_helm_jupyterhub.sh
bash install_jhub.sh
```

JupyterHub should now be accessible at `http://jhub.$PROJ.projects.jetstream-cloud.org` (without HTTPS for now).

## Setup HTTPS with cert-manager

### Install cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.1/cert-manager.yaml
```

Wait for all cert-manager pods to be ready:

```bash
kubectl -n cert-manager get pods -w
```

### Patch cert-manager to Run on the Control Plane

On small Jetstream2 clusters, the worker node may be autoscaled away, which would disrupt cert-manager. Patch the deployments to run on the control-plane node:

```bash
cd setup_https
bash deploymentPatch.sh
```

### Create a ClusterIssuer

Create a Let's Encrypt ClusterIssuer. Replace `YOUREMAIL` with your email address:

```bash
sed 's/YOUREMAIL/your@email.edu/' https_cluster_issuer.yml | kubectl apply -f -
```

The ClusterIssuer uses `http01` challenges with `ingress.class: traefik` to verify domain ownership.

Once the ClusterIssuer is created, JupyterHub's Ingress will automatically request a certificate from Let's Encrypt. After a minute or two, your deployment should have a valid HTTPS certificate.

Verify the certificate status:

```bash
kubectl get certificate -n jhub
```

You should see the certificate transition to `Ready=True`.

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/) to report any issue or give feedback.
