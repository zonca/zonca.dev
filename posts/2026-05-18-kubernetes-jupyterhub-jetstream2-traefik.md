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

The script uses the `kubernetes-1-33-jammy-fixed-labels` template, creates 1 control-plane node and 1 worker (both `m3.small` flavor), enables autoscaling with min 1 / max 5 workers, and polls until the cluster status is `CREATE_COMPLETE`. Cluster creation typically takes about 8 minutes.

> **Template choice**: We use the `kubernetes-1-33-jammy-fixed-labels` template rather than `kubernetes-1-33-jammy`. The default template deploys a Kubernetes dashboard app that is now defunct, which causes Magnum's post-create bookkeeping to get stuck at `CREATE_IN_PROGRESS` even though the cluster is fully functional. The `-fixed-labels` template omits the dashboard and completes cleanly. Alternatively, you can use any template with `--labels kube_dashboard_enabled=false`.

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
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-wamiv264xiet-control-plane-p2zj6          Ready    control-plane   8m22s   v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-vj9db   Ready    <none>          5m45s   v1.33.2
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

## Enable the Autoscaler

The `create_cluster.sh` script sets autoscaling labels (`auto_scaling_enabled=true`, `max_node_count=5`), but Magnum does not propagate `max_node_count` to the nodegroup. Verify this:

```bash
openstack coe nodegroup show $K8S_CLUSTER_NAME default-worker
```

You will see `max_node_count` is `None`, meaning the autoscaler is effectively disabled. Enable it by setting the max node count manually:

```bash
openstack coe nodegroup update $K8S_CLUSTER_NAME default-worker replace /max_node_count=5
```

### Test Scale Up

Create a deployment that requests enough memory to trigger the autoscaler:

```bash
kubectl create -f high_mem_dep.yaml
kubectl scale deployment high-memory-deployment --replicas=6
```

Each replica requests 4 GB of memory, so 6 replicas cannot fit on a single `m3.small` worker. The autoscaler detects the pending pods and adds nodes. You can see the scale-up event:

```bash
kubectl get events --field-selector reason=TriggeredScaleUp
```

```
LAST SEEN   TYPE     REASON             OBJECT                                        MESSAGE
3m20s       Normal   TriggeredScaleUp   pod/high-memory-deployment-844964899f-8mb4f   pod triggered scale-up: [{MachineDeployment/.../k8s-...-default-worker 1->5 (max: 5)}]
```

Within a couple of minutes, new worker nodes appear:

```bash
kubectl get nodes
```

```
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-wamiv264xiet-control-plane-p2zj6          Ready    control-plane   24m     v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-4krr8   Ready    <none>          47s     v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-87wtv   Ready    <none>          47s     v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-q8b9d   Ready    <none>          52s     v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-qxmcn   Ready    <none>          56s     v1.33.2
k8s-wamiv264xiet-default-worker-x8cxp-vj9db   Ready    <none>          22m     v1.33.2
```

The autoscaler scaled from 1 to 5 workers (the maximum). One pod remains pending because all 6 replicas cannot fit within the 5-worker limit.

### Clean Up and Observe Scale Down

Delete the test deployment so the autoscaler can return the worker pool to its minimum size:

```bash
kubectl delete deployment high-memory-deployment
```

The autoscaler takes several minutes to identify idle nodes, drain them, and terminate them. Watch the node count drop:

```bash
kubectl get nodes -w
```

You can also inspect the autoscaler's internal status to see whether a scale-down is in progress:

```bash
kubectl -n kube-system get configmap cluster-autoscaler-status -o jsonpath='{.data.status}'
```

When `scaleDown.status` shows `CandidatesPresent`, the autoscaler has identified idle nodes and is draining them. Once the process completes, the cluster returns to 1 worker node.

## Scale Manually

If you prefer not to use the autoscaler, you can scale the worker pool manually. First, make sure autoscaling is disabled by checking that `max_node_count` is `None`:

```bash
openstack coe nodegroup show $K8S_CLUSTER_NAME default-worker -c max_node_count
```

Then resize the nodegroup:

```bash
openstack coe cluster resize --nodegroup default-worker $K8S_CLUSTER_NAME 3
```

Confirm the change:

```bash
kubectl get nodes
```
