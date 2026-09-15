---
categories:
- kubernetes
- jetstream
- jupyterhub
- openstack
date: '2026-09-14'
layout: post
title: "Deploy JupyterHub on Jetstream2 with OpenTofu, Magnum and Traefik"
---

This tutorial deploys a JupyterHub on Jetstream2 with a single `tofu apply`.
It combines the steps of the [four-post Jetstream2 Kubernetes
series](./2026-08-20-kubernetes-jetstream2-magnum.md) (Magnum cluster,
Traefik ingress, JupyterHub, cert-manager) into one reproducible OpenTofu
configuration.

This post replaces the older [Deploying JupyterHub on OpenStack Magnum
with OpenTofu](./2026-04-22-deploy-jupyterhub-openstack-magnum-tofu.md)
tutorial, which used `ingress-nginx`. Since `ingress-nginx` has been
[retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/),
the new recipe installs [Traefik](https://doc.traefik.io/traefik/), which
supports both the Ingress and Gateway APIs.

## What you get at the end

- A functional Kubernetes cluster on Jetstream2 via Magnum, with the
  Cluster API backend.
- A Traefik ingress controller with a public floating IP attached to its
  load balancer.
- A DNS record on your project subdomain
  (`<project>.projects.jetstream-cloud.org`).
- Automatic HTTPS certificates via cert-manager and Let's Encrypt (HTTP01
  challenge through Traefik).
- A JupyterHub accessible at
  `https://<subdomain>.<project>.projects.jetstream-cloud.org`.
- A modular, reproducible OpenTofu configuration in
  [jupyterhub-deploy-kubernetes-jetstream](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream).

## 1. Prerequisites

### Install OpenTofu and the Kubernetes tooling

Install OpenTofu with the official script:

```bash
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh | sh
```

You also need `kubectl` (official instructions at
<https://kubernetes.io/docs/tasks/tools/>), `helm`
(<https://helm.sh/docs/intro/install/>), and `jq`. This tutorial was
tested with OpenTofu 1.12.6, kubectl 1.36.1, and helm 3.21.4.

### Clone the repository

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd jupyterhub-deploy-kubernetes-jetstream
```

### Create an application credential

Create an application credential in the Jetstream2 dashboard (Identity ->
Application credentials): choose **Unrestricted** and include all
permissions, notably **load balancer**. Download the `openrc` file and
place it at the repository root (it is gitignored), then source it:

```bash
source app-cred-XXXX-openrc.sh
```

### Python environment for the OpenStack clients

OpenTofu and the support scripts need the OpenStack clients. Create a
virtual environment and install them:

```bash
python3 -m venv .venv
.venv/bin/pip install python-openstackclient python-magnumclient \
  python-octaviaclient python-designateclient
source .venv/bin/activate
```

This tutorial was tested with python-openstackclient 10.2.1,
python-magnumclient 4.11.0, python-octaviaclient 3.14.0, and
python-designateclient 7.0.0.

Make sure `tofu`, `openstack`, `kubectl`, `helm`, and `jq` are available
in `PATH` of the shell you run `tofu` from.

## 2. Configuration

Copy the example variables file:

```bash
cd tofu_magnum/full_stack_https
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` for your project. The important settings:

| Variable | Description |
| --- | --- |
| `cluster_name` | Name of the Magnum cluster |
| `cluster_template_id` | UUID of the Magnum cluster template (see below) |
| `ssh_public_key` | Name of your OpenStack keypair |
| `project_id` | Lowercase Jetstream allocation ID (e.g. `cisXXXXXX`) |
| `subdomain` | Hostname prefix of the hub URL |
| `letsencrypt_email` | Email for Let's Encrypt notifications |

The hub will be available at
`https://<subdomain>.<project>.projects.jetstream-cloud.org`.

Optional tuning: `master_count`, `master_flavor`, `node_count`,
`worker_flavor`, `docker_volume_size`, `enable_autoscaling`,
`autoscaling_min_node_count`, `autoscaling_max_node_count`,
`dns_zone_name`.

### Choosing the cluster template

Find the available templates:

```bash
openstack coe cluster template list
```

The example uses the `kubernetes-1-33-jammy-fixed-labels` template.
Prefer the **fixed-labels** variant over `kubernetes-1-33-jammy`: the
default template deploys a Kubernetes dashboard app that is now defunct,
which can leave Magnum stuck at `CREATE_IN_PROGRESS` even though the
cluster is functional. Also reference the template by its **UUID** (as in
the example file), not by name: Magnum reads community-shared images
referenced by name as `Unset` and rejects the request (HTTP 400).

## 3. Deploy

Initialize the workspace and deploy:

```bash
tofu init
tofu apply
```

OpenTofu performs these steps in order:

1. Creates the Magnum Kubernetes cluster (autoscaling labels enabled on
   the worker node group).
2. Installs Traefik via Helm into the `traefik` namespace.
3. Attaches a fixed floating IP to the Traefik load balancer.
4. Creates the DNS A record for your subdomain.
5. Installs cert-manager (pinned to the control-plane node) and the
   Let's Encrypt ClusterIssuer.
6. Installs JupyterHub via Helm and requests the TLS certificate.

The cluster takes about 10 minutes to create on warm OpenStack images;
the first deployment in a project can take longer (up to a couple of
hours) while images are being cached. The recipe waits up to 4 hours for
the cluster to be ready, so a slow first deploy is not an error.

When finished, OpenTofu prints:

```text
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.

Outputs:

cluster_id = "68f23a9c-528f-4041-a64c-c6564aa46c14"
ingress_fixed_ip = "149.165.169.231"
jupyterhub_url = "https://tofu-traefik.cisXXXXXX.projects.jetstream-cloud.org"
kubeconfig_path = "./config"
```

(Your IDs and IPs will differ.)

## 4. Verification

Export the kubeconfig and check the cluster:

```bash
export KUBECONFIG=$(pwd)/config
kubectl get nodes
```

```text
NAME                                                       STATUS   ROLES           AGE   VERSION
k8s-tofu-traefik-cihlpc4q2a4a-control-plane-krz54          Ready    control-plane   22m   v1.33.2
k8s-tofu-traefik-cihlpc4q2a4a-default-worker-vcbsw-fdhbj   Ready    <none>          18m   v1.33.2
```

Autoscaling is on for the worker node group (the Cluster Autoscaler
reads the labels set at creation). `CLUSTER_NAME` is the `cluster_name`
you set in `terraform.tfvars`:

```bash
export CLUSTER_NAME=k8s
openstack coe nodegroup show $CLUSTER_NAME default-worker -c labels -f value
```

```text
{'auto_scaling_enabled': 'true', 'max_node_count': '5', 'min_node_count': '1'}
```

Check Traefik:

```bash
kubectl get pods -n traefik
```

```text
NAME                      READY   STATUS    RESTARTS   AGE
traefik-8d4cf5d76-rqtth   1/1     Running   0          16m
```

Check the JupyterHub ingress (class `traefik`) and its certificate:

```bash
kubectl get ingress -n jhub
kubectl get certificate -n jhub
```

```text
NAME         CLASS     HOSTS                                                 ADDRESS         PORTS     AGE
jupyterhub   traefik   tofu-traefik.cisXXXXXX.projects.jetstream-cloud.org   149.165.170.9   80, 443   4m59s

NAME                         READY   SECRET                       AGE
certmanager-tls-jupyterhub   True    certmanager-tls-jupyterhub   4m59s
```

When the certificate is `True`, JupyterHub is served over HTTPS. Use the
fixed floating IP in the DNS record, not the load balancer status in
`kubectl`: the service status keeps the originally assigned floating IP,
whereas the DNS record and `jupyterhub_url` point to the fixed IP (the
swap happens out of band after the load balancer is created). Verify
with the actual URL:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  https://tofu-traefik.cisXXXXXX.projects.jetstream-cloud.org/hub/login
```

```text
200
```

And confirm the hub API responds:

```bash
curl -s https://tofu-traefik.cisXXXXXX.projects.jetstream-cloud.org/hub/api
```

```text
{"version": "5.5.1"}
```

Finally, check the JupyterHub pods:

```bash
kubectl get pods -n jhub
```

```text
NAME                              READY   STATUS    RESTARTS   AGE
continuous-image-puller-26rrn     1/1     Running   0          5m37s
hub-8544f8bbd8-7xlk6              1/1     Running   0          5m37s
proxy-7cfd5f7b97-qbljs            1/1     Running   0          5m37s
user-scheduler-6995f6f4d5-h26fh   1/1     Running   0          5m37s
user-scheduler-6995f6f4d5-hlddn   1/1     Running   0          5m37s
```

### Authentication

This recipe does not configure an authenticator, so the hub runs with
the JupyterHub chart default
[DummyAuthenticator][z2jh-auth], which accepts any username and
password. That is fine for a quick test, but not for real users. Before
exposing the hub, add an authenticator, for example
[GitHub OAuth][z2jh-github] or another [OAuthenticator][z2jh-oauth], to
the JupyterHub values file (`config_standard_storage.yaml` or a
supplementary `--values` file) and re-run `tofu apply`. The
infrastructure setup in this tutorial (cluster, ingress, DNS, HTTPS)
does not change.

[z2jh-auth]: https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html
[z2jh-github]: https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#github
[z2jh-oauth]: https://zero-to-jupyterhub.readthedocs.io/en/latest/administrator/authentication.html#oauth2-based-authentication

## 5. Clean up

`tofu destroy` removes the whole stack: cluster, load balancer, floating
IP, DNS record, and the JupyterHub Helm release (JupyterHub data lives
in the cluster and is removed with it):

```bash
tofu destroy
```

## Issues and feedback

Please
[open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream)
to report any problem or give feedback.
