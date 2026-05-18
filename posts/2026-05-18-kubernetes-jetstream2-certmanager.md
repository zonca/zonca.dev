---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-05-18 11:00:00'
layout: post
slug: kubernetes-jetstream2-certmanager
title: Setup HTTPS with cert-manager on Jetstream2 Kubernetes (4 of 4)
---

This post is part of a series on deploying JupyterHub on Jetstream2:

1. [Deploy Kubernetes on Jetstream2](/posts/2026-05-18-kubernetes-jetstream2-magnum)
2. [Install Traefik Ingress Controller](/posts/2026-05-18-kubernetes-jetstream2-traefik)
3. [Deploy JupyterHub](/posts/2026-05-18-kubernetes-jetstream2-jupyterhub)
4. **Setup HTTPS with cert-manager**

This guide covers how to set up HTTPS with Let's Encrypt on a Jetstream2 Kubernetes cluster using [cert-manager](https://cert-manager.io/). It assumes you already have a running cluster with Traefik as the ingress controller and JupyterHub deployed — see the earlier posts in this series if you need to set those up.

## Install cert-manager

Install cert-manager from the official manifest:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.1/cert-manager.yaml
```

Wait for all three pods to be ready:

```bash
kubectl -n cert-manager get pods -w
```

```
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-5d8b6764c6-xxxxx              1/1     Running   0          2m
cert-manager-cainjector-7db8f9d4d-xxxxx    1/1     Running   0          2m
cert-manager-webhook-6c6f4dc87d-xxxxx      1/1     Running   0          2m
```

## Patch cert-manager to Run on the Control Plane

On small Jetstream2 clusters, the worker node may be autoscaled away, which would disrupt cert-manager. Patch the deployments to run on the control-plane node instead:

```bash
cd jupyterhub-deploy-kubernetes-jetstream/setup_https
export KUBECONFIG=../kubernetes_magnum/config
bash deploymentPatch.sh
```

This patches `cert-manager`, `cert-manager-cainjector`, and `cert-manager-webhook` to use a `nodeSelector` for the control-plane node and tolerate its taints.

## Create a ClusterIssuer

Create a Let's Encrypt ClusterIssuer that uses HTTP01 challenges via Traefik. Replace `YOUREMAIL` with your email address:

```bash
cd jupyterhub-deploy-kubernetes-jetstream/setup_https
sed 's/YOUREMAIL/your@email.edu/' https_cluster_issuer.yml | kubectl apply -f -
```

Verify the ClusterIssuer was created:

```bash
kubectl get clusterissuer letsencrypt
```

## Verify the Certificate

Once the ClusterIssuer is ready, JupyterHub's Ingress (which was configured with the `cert-manager.io/cluster-issuer: letsencrypt` annotation) will automatically request a certificate from Let's Encrypt. This takes about a minute.

Check the certificate status:

```bash
kubectl get certificate -n jhub
```

```
NAME                         READY   SECRET                       AGE
certmanager-tls-jupyterhub   True    certmanager-tls-jupyterhub   2m
```

When `READY` is `True`, the certificate has been issued. Your JupyterHub deployment is now accessible over HTTPS:

```
https://k8s.$PROJ.projects.jetstream-cloud.org
```

## Troubleshooting

If the certificate is not being issued, check the cert-manager logs and the order/challenge status:

```bash
kubectl -n cert-manager logs deploy/cert-manager
kubectl get order -n jhub
kubectl get challenge -n jhub
```

Common issues:
- The DNS record is not pointing to the correct IP (Traefik load balancer)
- The ClusterIssuer references the wrong ingress class (should be `traefik`)
- cert-manager pods are running on a worker node that was scaled away

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.
