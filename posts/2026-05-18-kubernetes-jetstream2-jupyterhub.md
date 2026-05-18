---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-05-18'
layout: post
slug: kubernetes-jetstream2-jupyterhub
title: Deploy JupyterHub on Jetstream2 Kubernetes (3 of 4)
---

This post is part of a series on deploying JupyterHub on Jetstream2:

1. [Deploy Kubernetes on Jetstream2](/posts/kubernetes-jetstream2-magnum)
2. [Install Traefik Ingress Controller](/posts/kubernetes-jetstream2-traefik)
3. **Deploy JupyterHub**
4. [Setup HTTPS with cert-manager](/posts/kubernetes-jetstream2-certmanager)

This guide covers how to deploy JupyterHub on a Jetstream2 Kubernetes cluster using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/). It assumes you already have a running cluster with Traefik as the ingress controller and DNS configured — see the earlier posts in this series if you need to set those up.

## Create Secrets

JupyterHub requires two secrets: a cookie secret for the hub and a proxy secret token. Generate them and create a `secrets.yaml` file:

```bash
cd jupyterhub-deploy-kubernetes-jetstream
bash create_secrets.sh
```

The `create_secrets.sh` script generates random secrets and writes them to `secrets.yaml`. It also configures the JupyterHub Ingress with `ingressClassName: traefik` and enables TLS via cert-manager.

The default `secrets.yaml` assumes you are deploying on a `projects.jetstream-cloud.org` subdomain. If using a custom domain, edit `secrets.yaml` and change the `hosts` and `tls.hosts` entries accordingly.

## Configure the Helm Chart

Add the JupyterHub Helm repository:

```bash
bash configure_helm_jupyterhub.sh
```

## Install JupyterHub

```bash
bash install_jhub.sh
```

This installs JupyterHub into the `jhub` namespace using the Helm chart version 4.3.3. The installation takes a few minutes as it pulls the JupyterHub images.

Monitor the rollout:

```bash
kubectl -n jhub get pods -w
```

Once all pods are running, JupyterHub is accessible at your domain over HTTP:

```bash
http://jhub.$PROJ.projects.jetstream-cloud.org
```

> **Security warning**: At this point JupyterHub is running over plain HTTP. Continue to [Setup HTTPS with cert-manager](/posts/kubernetes-jetstream2-certmanager) to enable HTTPS with Let's Encrypt.

## Troubleshooting

Check the hub and proxy logs if JupyterHub is not responding:

```bash
kubectl -n jhub logs deploy/hub
kubectl -n jhub logs deploy/proxy
```

If the Ingress is not getting an address, verify that Traefik is running:

```bash
kubectl get svc -n traefik traefik
kubectl get ingress -n jhub
```
