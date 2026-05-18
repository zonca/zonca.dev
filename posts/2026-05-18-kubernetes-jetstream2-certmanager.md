     1|---
     2|categories:
     3|- kubernetes
     4|- jetstream
     5|- jupyterhub
     6|date: '2026-05-18 11:00:00'
     7|layout: post
     8|slug: kubernetes-jetstream2-certmanager
     9|title: Setup HTTPS with cert-manager on Jetstream2 Kubernetes (4 of 4)
    10|---
    11|
    12|This post is part of a series on deploying JupyterHub on Jetstream2:
    13|
    14|1. [Deploy Kubernetes on Jetstream2](/posts/2026-05-18-kubernetes-jetstream2-magnum)
    15|2. [Install Traefik Ingress Controller](/posts/2026-05-18-kubernetes-jetstream2-traefik)
    16|3. [Deploy JupyterHub](/posts/2026-05-18-kubernetes-jetstream2-jupyterhub)
    17|4. **Setup HTTPS with cert-manager**
    18|
    19|This guide covers how to set up HTTPS with Let's Encrypt on a Jetstream2 Kubernetes cluster using [cert-manager](https://cert-manager.io/). It assumes you already have a running cluster with Traefik as the ingress controller and JupyterHub deployed — see the earlier posts in this series if you need to set those up.
    20|
    21|## Install cert-manager
    22|
    23|Install cert-manager from the official manifest:
    24|
    25|```bash
    26|kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.1/cert-manager.yaml
    27|```
    28|
    29|Wait for all three pods to be ready:
    30|
    31|```bash
    32|kubectl -n cert-manager get pods -w
    33|```
    34|
    35|```
    36|NAME                                       READY   STATUS    RESTARTS   AGE
    37|cert-manager-5d8b6764c6-xxxxx              1/1     Running   0          2m
    38|cert-manager-cainjector-7db8f9d4d-xxxxx    1/1     Running   0          2m
    39|cert-manager-webhook-6c6f4dc87d-xxxxx      1/1     Running   0          2m
    40|```
    41|
    42|## Patch cert-manager to Run on the Control Plane
    43|
    44|On small Jetstream2 clusters, the worker node may be autoscaled away, which would disrupt cert-manager. Patch the deployments to run on the control-plane node instead:
    45|
    46|```bash
    47|cd jupyterhub-deploy-kubernetes-jetstream/setup_https
    48|export KUBECONFIG=../kubernetes_magnum/config
    49|bash deploymentPatch.sh
    50|```
    51|
    52|This patches `cert-manager`, `cert-manager-cainjector`, and `cert-manager-webhook` to use a `nodeSelector` for the control-plane node and tolerate its taints.
    53|
    54|## Create a ClusterIssuer
    55|
    56|Create a Let's Encrypt ClusterIssuer that uses HTTP01 challenges via Traefik. Replace `YOUREMAIL` with your email address:
    57|
    58|```bash
    59|cd jupyterhub-deploy-kubernetes-jetstream/setup_https
    60|sed 's/YOUREMAIL/your@email.edu/' https_cluster_issuer.yml | kubectl apply -f -
    61|```
    62|
    63|Verify the ClusterIssuer was created:
    64|
    65|```bash
    66|kubectl get clusterissuer letsencrypt
    67|```
    68|
    69|## Verify the Certificate
    70|
    71|Once the ClusterIssuer is ready, JupyterHub's Ingress (which was configured with the `cert-manager.io/cluster-issuer: letsencrypt` annotation) will automatically request a certificate from Let's Encrypt. This takes about a minute.
    72|
    73|Check the certificate status:
    74|
    75|```bash
    76|kubectl get certificate -n jhub
    77|```
    78|
    79|```
    80|NAME                     READY   SECRET                   AGE
    81|certmanager-tls-jupyterhub   True    certmanager-tls-jupyterhub   2m
    82|```
    83|
    84|When `READY` is `True`, the certificate has been issued. Your JupyterHub deployment is now accessible over HTTPS:
    85|
    86|```
    87|https://k8s.$PROJ.projects.jetstream-cloud.org
    88|```
    89|
    90|## Troubleshooting
    91|
    92|If the certificate is not being issued, check the cert-manager logs and the order/challenge status:
    93|
    94|```bash
    95|kubectl -n cert-manager logs deploy/cert-manager
    96|kubectl get order -n jhub
    97|kubectl get challenge -n jhub
    98|```
    99|
   100|Common issues:
   101|- The DNS record is not pointing to the correct IP (Traefik load balancer)
   102|- The ClusterIssuer references the wrong ingress class (should be `traefik`)
   103|- cert-manager pods are running on a worker node that was scaled away
   104|
   105|## Issues and Feedback
   106|
   107|Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.
   108|