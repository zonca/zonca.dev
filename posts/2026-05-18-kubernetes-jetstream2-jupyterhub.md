     1|---
     2|categories:
     3|- kubernetes
     4|- jetstream
     5|- jupyterhub
     6|date: '2026-05-18 10:00:00'
     7|layout: post
     8|slug: kubernetes-jetstream2-jupyterhub
     9|title: Deploy JupyterHub on Jetstream2 Kubernetes (3 of 4)
    10|---
    11|
    12|This post is part of a series on deploying JupyterHub on Jetstream2:
    13|
    14|1. [Deploy Kubernetes on Jetstream2](/posts/2026-05-18-kubernetes-jetstream2-magnum)
    15|2. [Install Traefik Ingress Controller](/posts/2026-05-18-kubernetes-jetstream2-traefik)
    16|3. **Deploy JupyterHub**
    17|4. [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager)
    18|
    19|This guide covers how to deploy JupyterHub on a Jetstream2 Kubernetes cluster using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/). It assumes you already have a running cluster with Traefik as the ingress controller and DNS configured — see the earlier posts in this series if you need to set those up.
    20|
    21|## Create Secrets
    22|
    23|JupyterHub requires two secrets: a cookie secret for the hub and a proxy secret token. Generate them and create a `secrets.yaml` file:
    24|
    25|```bash
    26|cd jupyterhub-deploy-kubernetes-jetstream
    27|export PROJ="xxx000000"
    28|bash create_secrets.sh
    29|```
    30|
    31|The `create_secrets.sh` script generates random secrets and writes them to `secrets.yaml`. It also configures the JupyterHub Ingress with `ingressClassName: traefik` and enables TLS via cert-manager.
    32|
    33|The default `secrets.yaml` uses `k8s` as the subdomain (i.e., `k8s.$PROJ.projects.jetstream-cloud.org`). If you prefer a different subdomain, edit `secrets.yaml` and change the `hosts` and `tls.hosts` entries. If using a custom domain, update those entries accordingly.
    34|
    35|## Configure the Helm Chart
    36|
    37|Add the JupyterHub Helm repository:
    38|
    39|```bash
    40|bash configure_helm_jupyterhub.sh
    41|```
    42|
    43|## Install JupyterHub
    44|
    45|```bash
    46|bash install_jhub.sh
    47|```
    48|
    49|This installs JupyterHub into the `jhub` namespace using the Helm chart version 4.3.3. The installation takes a few minutes as it pulls the JupyterHub images.
    50|
    51|Monitor the rollout:
    52|
    53|```bash
    54|kubectl -n jhub get pods -w
    55|```
    56|
    57|Once all pods are running, JupyterHub is accessible at your subdomain over HTTP:
    58|
    59|```
    60|http://k8s.$PROJ.projects.jetstream-cloud.org
    61|```
    62|
    63|> **Security warning**: At this point JupyterHub is running over plain HTTP. Continue to [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager) to enable HTTPS with Let's Encrypt.
    64|
    65|## Troubleshooting
    66|
    67|Check the hub and proxy logs if JupyterHub is not responding:
    68|
    69|```bash
    70|kubectl -n jhub logs deploy/hub
    71|kubectl -n jhub logs deploy/proxy
    72|```
    73|
    74|If the Ingress is not getting an address, verify that Traefik is running:
    75|
```bash
kubectl get svc -n traefik traefik
kubectl get ingress -n jhub
```

**Next**: [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager)
    80|