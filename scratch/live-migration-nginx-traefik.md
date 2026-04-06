# Introduction

Historically the JupyterHub on Kubernetes workflow tutorial for Jetstream2 has used `ingress-nginx` as its ingress-controller. In Kubernetes-land, an Ingress is a Kubernetes (K8s) resource that defines routes for incoming network traffic to take to get to the cluster's services, such as JupyterHub. An ingress-controller, such as `ingress-nginx`, will monitor Ingress resources and update a proxy server's configuration to route traffic appropriately. However, `ingress-nginx` is being [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) and will no longer receive any updates. As such, it is necessary to migrate to a different method of allowing network traffic into Kubernetes clusters.

Kubernetes suggests using its modern [GatewayAPI ](https://gateway-api.sigs.k8s.io/guides/getting-started/), however, in order to minimize any migration friction, we will instead use the [Traefik proxy](https://doc.traefik.io/traefik/getting-started/kubernetes/), as it supports usage as an Ingress controller, but also has support for Kubernetes' GatewayAPI. By migrating to Traefik, we can be minimally disruptive to existing workflows now by simply switching Ingress controllers while being minimally disruptive in the future if we decide to migrate to GatewayAPI.

This tutorial will focus on migrating an existing cluster from `ingress-nginx` to `traefik`. For new clusters, see the [updated tutorial](https://www.zonca.dev/posts/2024-12-11-jetstream_kubernetes_magnum) on deploying JupyterHub on Kubernetes on Jetstream2.

This tutorial is based on Traefik's [documentation](https://doc.traefik.io/traefik/migrate/nginx-to-traefik/) for migrating from `ingress-nginx`, adapted for Jetstream2 deployments.
# Prerequisites and assumptions

This tutorial assumes that you've created a Kubernetes cluster using Jetstream2's Magnum/ClusterAPI as described in the tutorial linked above. As such, it assumes satisfaction of any prerequisites described therein such as installation of `kubectl`, `helm`, the `openstack` CLI tool, etc.

# How to migrate

## Installing traefik

Ensure you've cloned the [jupyterhub-deploy-kubernetes-jetstream](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) and have pulled in the most recent changes. In your terminal, navigate the `kubernetes-magnum` directory.

Edit the `install-traefik.sh` script to include the `--set 'providers.kubernetesIngressNGINX.enabled=true'` flag as below. Optionally, remove the last two `--set` arguments if desired. These enable access logs and tell Kubernetes to schedule the new `traefik` pod on a `default-worker` node.

```bash
helm repo add traefik https://traefik.github.io/charts
helm repo update

helm upgrade --install traefik traefik/traefik \
        --namespace ingress-traefik --create-namespace \
        --set 'api.dashboard=false' \
        --set 'providers.kubernetesCRD.enabled=false' \
		--set 'providers.kubernetesIngressNginx.enabled=true'
        --set 'logs.access.enabled=true' \
        --set 'nodeSelector.capi\.stackhpc\.com/node-group=default-worker'
```

Run the script with `bash install-traefik.sh`. This will create the `traefik` Pod in the `ingress-traefik` namespace as well as create a new LoadBalancer to accept network traffic through the newly deployed `traefik` Ingress. Because we've enabled the `kubernetesIngressNGINX` provider, `traefik` will serve Ingress resources whose IngressClass is `nginx`.

You can monitor the LoadBalancer creation with:

```bash
watch kubectl get svc -n ingress-traefik
```

Initially, the `EXTERNAL_IP` column with show `pending` but will eventually show an IP.

## Optional/Advanced: Update ingress resources

An ingress-controller such as `traefik` and `ingress-nginx` will monitor Kubernetes for Ingress resources and update the proxy configuration to serve ingress. You can list all Ingress resources in your cluster by running:

```bash
kubectl get ingress -A
```

The proxy can be configured per Ingress with "annotations" on the ingress resource. Traefik has [support](https://doc.traefik.io/traefik/reference/routing-configuration/kubernetes/ingress-nginx/) for some common `ingress-nginx` annotations. However, not all annotations are supported. For example, under `ingress-nginx` some JupyterHub administrators may elect to set the following annotation to allow large data uploads:

```yaml
# In JupyterHub's secrets.yaml
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt"
  	# nginx annotation unsupported by traefik:
  	"nginx.ingress.kubernetes.io/proxy-body-size": "500m"
  	# The corresponding traefik annotation:
  	"traefik.ingress.kubernetes.io/middlewares.limit.buffering.maxRequestBodyBytes": "500000000"
```

Reinstall JupyterHub to apply this change.

## Add traefik to your subdomain

Now we will add the new LoadBalancer to our existing DNS entry. If you followed the standard tutorial to create this cluster, you should be able to see it with:

```bash
openstack recordset show $PROJ.projects.jetstream-cloud.org. $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org.
```

Take a note of the existing IP in the `records` field. This is the IP of the existing `nginx` LoadBalancer. Alternatively, run the following command to save this information in a variable:

```bash
export NGINX_IP=$(openstack recordset show $PROJ.projects.jetstream-cloud.org. $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. -c records -f value)
```

Now, get the `traefik` LoadBalancer IP:

```bash
export TRAEFIK_IP=$(kubectl get svc -n ingress-traefik traefik -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

Update the DNS entry to include both IPs:

```bash
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $NGINX_IP \
  --record $TRAEFIK_IP
```

After some time, you should be able to run the following command and see the domain name resolve to both IPs:

```bash
nslookup $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org
# => ...
# => Non-authoritative answer:
# => Name:	$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org
# => Address: $NGINX_IP 
# => Name:	$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org
# => Address: $TRAEFIK_IP
```

You should now be able to test connectivity via either Ingress on both HTTP and HTTPS. The following commands will ensure that you can connect to one LoadBalancer or the other, shows verbose output to see SSL/TLS handshakes, and dump headers to the standard output:

```bash
export FQDN=$K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org

# Observe HTTPS redirections:
curl --connect-to "${FQDN}:80:${NGINX_IP}:80" "http://${FQDN}" -v -D -
curl --connect-to "${FQDN}:80:${TRAEFIK_IP}:80" "http://${FQDN}" -v -D - # note X-Forwarded-Server which should be traefik

# Test HTTPS
curl --connect-to "${FQDN}:443:${NGINX_IP}:443" "https://${FQDN}" -v -D -
curl --connect-to "${FQDN}:443:${TRAEFIK_IP}:443" "https://${FQDN}" -v -D -
```

For the `HTTPS` connections, you should see a line in the output saying:

```
...
*  SSL certificate verify ok.
...
```

## Removing ingress-nginx

Now that both ingress-controllers are running simultaneously, we can remove `ingress-nginx` from the cluster. First we update the DNS entry to only have the `$TRAEFIK_IP`:

```bash
openstack recordset set \
  $PROJ.projects.jetstream-cloud.org. \
  $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org. \
  --record $TRAEFIK_IP
```

Now we wait for DNS servers and caches to "catch up" with the change. You can check on this by `watch`-ing the previous `nslookup` command:

```bash
watch nslookup $K8S_CLUSTER_NAME.$PROJ.projects.jetstream-cloud.org
```

Finally, we can remove `ingress-nginx` and its namespace from the cluster. Assuming you installed `ingress-nginx` via `helm` as in the original tutorial, you can delete it with `helm`:

```bash
helm list -n ingress-nginx # Verify it was installed via helm
helm uninstall -n ingress-nginx ingress-nginx
kubectl delete ns ingress-nginx
```
