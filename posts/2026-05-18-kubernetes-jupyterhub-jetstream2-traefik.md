---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-05-18'
layout: post
slug: kubernetes-jupyterhub-jetstream2-traefik-2026
title: Deploy Kubernetes and JupyterHub on Jetstream2 with Magnum, Cluster API, and Traefik
---

This guide demonstrates how to deploy Kubernetes on Jetstream2 with Magnum and then install JupyterHub on top using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/).

Jetstream2 uses the Cluster API as the backend for Magnum, making it faster and more straightforward to launch Kubernetes clusters. This tutorial uses [Traefik](https://doc.traefik.io/traefik/) as the ingress controller, replacing `ingress-nginx` which has been [retired](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/). Traefik supports both the standard Kubernetes Ingress API and the newer Gateway API, making it a forward-compatible choice.

## Advantages of Magnum-Based Deployments

Magnum-based clusters offer several benefits over [Kubespray](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray):

- **Faster Deployment**: Instead of using Ansible to configure each VM, Magnum uses pre-prepared images. Clusters typically deploy in about 10 minutes, and workers can scale up in around 5 minutes.
- **Load Balancer Integration**: The OpenStack load balancer service provides easy support for multiple master nodes, ensuring high availability.
- **Autoscaling**: The Cluster Autoscaler can automatically add or remove worker nodes based on workload.

## Prerequisites

1. **Install OpenStack and Magnum Clients**:
   ```bash
   pip install python-openstackclient python-magnumclient python-octaviaclient python-designateclient
   ```

   The OpenStack client is used to create and manage the cluster, the Magnum client is used to create the cluster template, and the Octavia client is used to manage the load balancer. The Designate client is used to manage DNS records.

   This tutorial used python-openstackclient 8.1.0, python-magnumclient 4.8.1, python-octaviaclient 3.11.1, and python-designateclient 6.3.0.

2. **Create an App Credential**:
   Create an application credential for the client to access the API through [Horizon](https://js2.jetstream-cloud.org/) under [Identity → Application credentials](https://js2.jetstream-cloud.org/identity/application_credentials/).
   Create an "Unrestricted" application credential with all permissions, including the "loadbalancer" permission, in the project where you will be creating the cluster. Download the `openrc` file and source it to expose the environment variables in your local environment where you'll be running the `openstack` commands.

3. **Install Kubernetes Tooling**:
   Once the cluster is launched, manage it using standard Kubernetes tools:
   - `kubectl`: see <https://kubernetes.io/docs/tasks/tools/>, this tutorial used 1.30.
   - `helm`: see <https://helm.sh/docs/intro/install/>, this tutorial used 3.17.

## Create the Cluster with Magnum

Check the cluster templates available:

```bash
openstack coe cluster template list
```

List clusters (initially empty):

```bash
openstack coe cluster list
```

Clone the repository with all the configuration files on the machine you will use the Jetstream API from, typically your laptop:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd jupyterhub-deploy-kubernetes-jetstream/kubernetes_magnum
```

Create a cluster:

```bash
export K8S_CLUSTER_NAME=k8s
bash create_cluster.sh
```

See inside `create_cluster.sh` for the most commonly used parameters. The script waits for the cluster to complete deployment, which should take about 10 minutes.

> **Note**: The first time you create a cluster (or after a long period of inactivity), deployment can take 2–2.5 hours, likely because the images are not cached in OpenStack. After that, clusters should deploy in about 10 minutes.

In case of errors, check the error message with:

```bash
openstack coe cluster show $K8S_CLUSTER_NAME -f json | jq '.status_reason'
```

The cluster consumes resources when active. To delete it:

```bash
bash delete_cluster.sh
```

**Warning**: This deletes all Jetstream virtual machines and any data stored in JupyterHub.

Once the status is `CREATE_COMPLETE`, retrieve the Kubernetes config file:

```bash
openstack coe cluster config $K8S_CLUSTER_NAME --force
export KUBECONFIG=$(pwd)/config
chmod 600 config
```

Verify that `kubectl` commands work:

```bash
kubectl get nodes
```

Expected output:

```
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-mbbffjfee7zs-control-plane-6rn2z          Ready    control-plane   2m22s   v1.30.4
k8s-mbbffjfee7zs-control-plane-nw4cc          Ready    control-plane   41s     v1.30.4
k8s-mbbffjfee7zs-control-plane-w9jln          Ready    control-plane   5m8s    v1.30.4
k8s-mbbffjfee7zs-default-worker-jb5lm-gvvjm   Ready    <none>          2m21s   v1.30.4
```
