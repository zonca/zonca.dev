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

   The OpenStack client creates and manages the cluster, the Magnum client manages cluster templates, the Octavia client manages load balancers, and the Designate client manages DNS records.

   This tutorial used python-openstackclient 9.0.0, python-magnumclient 4.8.1, python-octaviaclient 3.11.1, and python-designateclient 6.3.0.

2. **Create an App Credential**:
   Create an application credential through [Horizon](https://js2.jetstream-cloud.org/) under [Identity → Application credentials](https://js2.jetstream-cloud.org/identity/application_credentials/).
   Choose "Unrestricted" and include all permissions, notably "loadbalancer", in the project where you will create the cluster. Download the `openrc` file and source it:

   ```bash
   source app-cred-XXXX-openrc.sh
   ```

3. **Install Kubernetes Tooling**:
   Once the cluster is launched, manage it using standard Kubernetes tools:
   - `kubectl`: see <https://kubernetes.io/docs/tasks/tools/>, this tutorial used 1.35.
   - `helm`: see <https://helm.sh/docs/intro/install/>, this tutorial used 3.18.

## Create the Cluster with Magnum

Check the available cluster templates:

```bash
openstack coe cluster template list
```

Clone the repository with all the configuration files:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd jupyterhub-deploy-kubernetes-jetstream/kubernetes_magnum
```

Create a cluster:

```bash
export K8S_CLUSTER_NAME=k8s
bash create_cluster.sh
```

The script uses the `kubernetes-1-33-jammy` template, creates 1 control-plane node and 1 worker (both `m3.small` flavor), enables autoscaling with min 1 / max 5 workers, and polls until the cluster status is `CREATE_COMPLETE`.

> **Note**: The first time you create a cluster (or after a long period of inactivity), deployment can take 2–2.5 hours, likely because the images are not cached in OpenStack. After that, clusters should deploy in about 10 minutes.

> **Known Issue**: The Magnum cluster status may remain `CREATE_IN_PROGRESS` even after the nodegroups are fully ready. If `kubectl get nodes` shows all nodes as `Ready`, the cluster is functional and you can proceed — you do not need to wait for the status to flip to `CREATE_COMPLETE`. You can also check nodegroup status with `openstack coe nodegroup list $K8S_CLUSTER_NAME`, which tends to update faster than the cluster-level status.

In case of errors, check the error message with:

```bash
openstack coe cluster show $K8S_CLUSTER_NAME -f json | jq '.status_reason'
```

The cluster consumes resources when active. To delete it:

```bash
bash delete_cluster.sh
```

**Warning**: This deletes all Jetstream virtual machines and any data stored in JupyterHub.

Once the nodes are ready, retrieve the Kubernetes config file:

```bash
openstack coe cluster config $K8S_CLUSTER_NAME --force
export KUBECONFIG=$(pwd)/config
chmod 600 config
```

Verify that `kubectl` commands work:

```bash
kubectl get nodes
```

You should see output like:

```
NAME                                          STATUS   ROLES           AGE   VERSION
k8s-bexqcu3lzfdo-control-plane-4lqmn          Ready    control-plane   13m   v1.33.2
k8s-bexqcu3lzfdo-default-worker-x6654-nk2s7   Ready    <none>          10m   v1.33.2
```

Check storage classes (Magnum provides Cinder-backed persistent volumes by default):

```bash
kubectl get storageclass
```

```
NAME                PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
default (default)   cinder.csi.openstack.org   Retain          WaitForFirstConsumer   true                   12m
replicated-hdd      cinder.csi.openstack.org   Retain          WaitForFirstConsumer   true                   12m
```
