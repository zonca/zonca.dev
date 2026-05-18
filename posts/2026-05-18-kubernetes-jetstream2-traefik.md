     1|---
     2|categories:
     3|- kubernetes
     4|- jetstream
     5|date: '2026-05-18 09:00:00'
     6|layout: post
     7|slug: kubernetes-jetstream2-traefik
     8|title: Install Traefik Ingress Controller on Jetstream2 Kubernetes (2 of 4)
     9|---
    10|
    11|This post is part of a series on deploying JupyterHub on Jetstream2:
    12|
    13|1. [Deploy Kubernetes on Jetstream2](/posts/2026-05-18-kubernetes-jetstream2-magnum)
    14|2. **Install Traefik Ingress Controller**
    15|3. [Deploy JupyterHub](/posts/2026-05-18-kubernetes-jetstream2-jupyterhub)
    16|4. [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager)
    17|
    18|This guide covers how to install [Traefik](https://doc.traefik.io/traefik/) as an ingress controller on a Jetstream2 Kubernetes cluster and configure DNS. Traefik replaces `ingress-nginx`, which has been [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/). Traefik supports both the standard Kubernetes Ingress API and the newer Gateway API, making it a forward-compatible choice.
    19|
    20|This guide assumes you already have a running cluster — see [Deploy Kubernetes on Jetstream2](/posts/2026-05-18-kubernetes-jetstream2-magnum) if you need to create one first. Make sure `KUBECONFIG` is set and `kubectl get nodes` works.
    21|
    22|## Install Traefik
    23|
    24|Install the Traefik Helm chart:
    25|
    26|```bash
    27|helm repo add traefik https://traefik.github.io/charts
    28|helm repo update
    29|helm upgrade --install traefik traefik/traefik \
    30|    --namespace traefik --create-namespace
    31|```
    32|
    33|This deploys Traefik (this tutorial tested with v3.7) and creates a Kubernetes Service of type `LoadBalancer`. On Jetstream2, this automatically provisions an OpenStack Octavia load balancer with a floating IP.
    34|
    35|Wait for the external IP to be assigned (takes about 2 minutes):
    36|
    37|```bash
    38|kubectl get svc -n traefik traefik -w
    39|```
    40|
    41|Once the `EXTERNAL-IP` column shows an address, note it:
    42|
    43|```bash
    44|export IP=$(kubectl get svc -n traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    45|echo $IP
    46|```
    47|
    48|```
    49|149.165.173.224
    50|```
    51|
    52|Verify the Traefik pod is running:
    53|
    54|```bash
    55|kubectl get pods -n traefik
    56|```
    57|
    58|```
    59|NAME                       READY   STATUS    RESTARTS   AGE
    60|traefik-798b4cb98f-8bwfd   1/1     Running   0          2m46s
    61|```
    62|
    63|### Use a Fixed Floating IP
    64|
    65|By default, Traefik creates a new OpenStack load balancer with a random floating IP. If you delete and recreate the cluster, this IP changes. To use a fixed IP instead:
    66|
    67|1. Create a floating IP in OpenStack:
    68|
    69|```bash
    70|openstack floating ip create public
    71|export FIXED_IP=<FLOATING_IP>
    72|```
    73|
    74|2. Find the Traefik load balancer:
    75|
    76|```bash
    77|export LB=$(openstack loadbalancer list --name traefik -f value -c id)
    78|```
    79|
    80|> **Note**: The `openstack loadbalancer` command requires `python-octaviaclient`. Install it with `pip install python-octaviaclient` if the command is not found.
    81|
    82|3. Associate the fixed IP with the load balancer's VIP port:
    83|
    84|```bash
    85|LB_VIP_PORT_ID=$(openstack loadbalancer show $LB -c vip_port_id -f value)
    86|EXISTING_FIP=$(openstack floating ip list --port $LB_VIP_PORT_ID -f value -c ID)
    87|if [ -n "$EXISTING_FIP" ]; then
    88|    openstack floating ip unset --port $EXISTING_FIP
    89|fi
    90|openstack floating ip set --port $LB_VIP_PORT_ID $FIXED_IP
    91|export IP=$FIXED_IP
    92|```
    93|
    94|## Configure DNS
    95|
    96|### Using the Jetstream Subdomain
    97|
    98|Jetstream2 provides a subdomain for each project:
    99|
   100|```
   101|subdomain.$PROJ.projects.jetstream-cloud.org
   102|```
   103|
   104|where `PROJ` is the ID of your Jetstream2 allocation (all lowercase). Create a DNS record pointing to the Traefik IP:
   105|
   106|```bash
   107|export PROJ="xxx000000"
   108|export SUBDOMAIN="jhub"
   109|openstack recordset create $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN --type A --record $IP --ttl 3600
   110|```
   111|
   112|If you get a "Duplicate recordset" error, update the existing record:
   113|
   114|```bash
   115|openstack recordset set $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN.$PROJ.projects.jetstream-cloud.org. --record $IP
   116|```
   117|
   118|### Using a Custom Domain
   119|
   120|If you have a custom domain, create an A record pointing to `$IP` with your DNS provider.
   121|
   122|## Test the Traefik Ingress
   123|
   124|Deploy a simple echo server to verify that Traefik and DNS are working. The repository includes an `echo-test.yaml` manifest that creates a Deployment, a Service, and an Ingress with `ingressClassName: traefik`.
   125|
   126|Edit the `host` field in `echo-test.yaml` to match your subdomain, then deploy:
   127|
   128|```bash
   129|kubectl create -f echo-test.yaml
   130|```
   131|
   132|Wait for the pod to be ready:
   133|
   134|```bash
   135|kubectl get pods -w
   136|```
   137|
   138|Check that the Ingress got the Traefik IP:
   139|
   140|```bash
   141|kubectl get ingress
   142|```
   143|
   144|```
   145|NAME           CLASS     HOSTS                                             ADDRESS           PORTS   AGE
   146|echo-ingress   traefik   testpage.cis230085.projects.jetstream-cloud.org   149.165.173.224   80      4s
   147|```
   148|
   149|Then test with curl:
   150|
   151|```bash
   152|curl http://testpage.$PROJ.projects.jetstream-cloud.org
   153|```
   154|
   155|```
   156|Testing Traefik Ingress on Jetstream!
   157|```
   158|
   159|Once verified, clean up the test deployment:
   160|
   161|```bash
   162|kubectl delete -f echo-test.yaml
   163|```
   164|
   165|With Traefik installed and DNS configured, continue to [Deploy JupyterHub](/posts/2026-05-18-kubernetes-jetstream2-jupyterhub). You can also skip ahead to [Setup HTTPS with cert-manager](/posts/2026-05-18-kubernetes-jetstream2-certmanager) if you already have JupyterHub running.
   166|