---
categories:
- kubernetes
- jetstream
date: '2026-05-18 08:00:00'
layout: post
slug: kubernetes-jetstream2-magnum
title: Deploy Kubernetes on Jetstream2 with Magnum and Cluster API (1 of 4)
---

This post is part of a series on deploying JupyterHub on Jetstream2:

1. **Deploy Kubernetes on Jetstream2**
2. [Install Traefik Ingress Controller](/posts/kubernetes-jetstream2-traefik)
3. [Deploy JupyterHub](/posts/kubernetes-jetstream2-jupyterhub)
4. [Setup HTTPS with cert-manager](/posts/kubernetes-jetstream2-certmanager)

Jetstream2 uses the Cluster API as the backend for Magnum, making it faster and more straightforward to launch Kubernetes clusters. This guide walks through creating a cluster, configuring autoscaling, and verifying the deployment.

## Advantages of Magnum-Based Deployments

Magnum-based clusters offer several benefits over [Kubespray](/posts/kubernetes-jetstream2-kubespray):

- **Faster Deployment**: Instead of using Ansible to configure each VM, Magnum uses pre-prepared images. Clusters typically deploy in about 10 minutes, and workers can scale up in around 5 minutes.
- **Load Balancer Integration**: The OpenStack load balancer service provides easy support for multiple master nodes, ensuring high availability.
- **Autoscaling**: The Cluster Autoscaler can automatically add or remove worker nodes based on workload.

## Prerequisites

1. **Install OpenStack and Magnum Clients**:
   ```bash
   pip install python-openstackclient python-magnumclient python-octaviaclient python-designateclient
   ```

   The OpenStack client creates and manages the cluster, the Magnum client manages cluster templates, the Octavia client manages load balancers, and the Designate client manages DNS records.

   This tutorial used python-openstackclient 9.0.0, python-magnumclient 4.8.1, python-octaviaclient 3.14.0, and python-designateclient 6.3.0.

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

The script uses the `kubernetes-1-33-jammy-fixed-labels` template, creates 1 control-plane node and 1 worker (both `m3.small` flavor), enables autoscaling with min 1 / max 5 workers, and polls until the cluster status is `CREATE_COMPLETE`. Cluster creation typically takes about 10 minutes.

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

## Autoscaling

The `create_cluster.sh` script creates the cluster with the label `auto_scaling_enabled=true` and `max_node_count=5`, which activates the Cluster Autoscaler. You can override the maximum before creating the cluster:

```bash
export MAX_NODE_COUNT=10
bash create_cluster.sh
```

After the cluster is created, verify the label on the nodegroup:

```bash
openstack coe nodegroup show $K8S_CLUSTER_NAME default-worker -c labels -c min_node_count -c max_node_count
```

```
| Field          | Value                                                                          |
+----------------+--------------------------------------------------------------------------------+
| labels         | {'auto_scaling_enabled': 'true', 'min_node_count': '1', 'max_node_count': '5'} |
| max_node_count | None                                                                           |
| min_node_count | 1                                                                              |
```

Note that `max_node_count` on the nodegroup shows `None` even though the label is set to 5. This is a Magnum quirk — the nodegroup field and the label are separate. **The autoscaler reads the label value**, not the nodegroup field, so it is active and capped at 5 regardless. This means there is no need to run `openstack coe nodegroup update` to set `max_node_count` — the label set at cluster creation time is sufficient. To change the maximum, set `MAX_NODE_COUNT` before running `create_cluster.sh`.

### Test Scale Up

Create a deployment that requests enough memory to trigger the autoscaler:

```bash
kubectl create -f high_mem_dep.yaml
kubectl scale deployment high-memory-deployment --replicas=6
```

Each replica requests 4 GB of memory, so 6 replicas cannot fit on a single `m3.small` worker. The autoscaler detects the pending pods and adds nodes. Check the scale-up event:

```bash
kubectl get events --field-selector reason=TriggeredScaleUp
```

```
LAST SEEN   TYPE     REASON             OBJECT                                        MESSAGE
2m19s       Normal   TriggeredScaleUp   pod/high-memory-deployment-844964899f-ngldm   pod triggered scale-up: [{MachineDeployment/.../k8s-...-default-worker 1->5 (max: 5)}]
```

Within a few minutes, new worker nodes appear:

```bash
kubectl get nodes
```

```
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-2yo5qznljser-control-plane-g7nk4          Ready    control-plane   15m     v1.33.2
k8s-2yo5qznljser-default-worker-m2pp7-2mq6z   Ready    <none>          2m40s   v1.33.2
k8s-2yo5qznljser-default-worker-m2pp7-bc6jv   Ready    <none>          2m37s   v1.33.2
k8s-2yo5qznljser-default-worker-m2pp7-kp28n   Ready    <none>          2m30s   v1.33.2
k8s-2yo5qznljser-default-worker-m2pp7-t2nsg   Ready    <none>          15m     v1.33.2
k8s-2yo5qznljser-default-worker-m2pp7-tzjdn   Ready    <none>          2m31s   v1.33.2
```

The autoscaler scaled from 1 to 5 workers (the maximum set in the label). One pod remains pending because all 6 replicas cannot fit within the 5-worker limit.

### Clean Up and Observe Scale Down

Delete the test deployment so the autoscaler can return the worker pool to its minimum size:

```bash
kubectl delete deployment high-memory-deployment
```

The autoscaler takes several minutes to identify idle nodes, drain them, and terminate them. Watch the node count drop:

```bash
kubectl get nodes -w
```

You can inspect the autoscaler's internal status to see whether a scale-down is in progress:

```bash
kubectl -n kube-system get configmap cluster-autoscaler-status -o jsonpath='{.data.status}'
```

When `scaleDown.status` shows `CandidatesPresent`, the autoscaler has identified idle nodes and is draining them. Once the process completes, the cluster returns to 1 worker node.

## Scale Manually

If you prefer not to use the autoscaler, you can scale the worker pool manually. Resize the nodegroup:

```bash
openstack coe cluster resize --nodegroup default-worker $K8S_CLUSTER_NAME 3
```

Confirm the change:

```bash
kubectl get nodes
```

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) to report any issue or give feedback.
