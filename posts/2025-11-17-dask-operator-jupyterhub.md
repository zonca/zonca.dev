---
categories:
- kubernetes
- jetstream2
- jupyterhub
- python
date: '2025-11-17'
layout: post
title: Deploy the Dask Operator for JupyterHub on Kubernetes
---

This post describes how to deploy the [Dask Operator for Kubernetes](https://kubernetes.dask.org/en/latest/operator.html) alongside a Helm-based JupyterHub installation. The Operator provides a Kubernetes-native way to create and manage Dask clusters via custom resources, simplifying multi-tenant setups, it is therefore more integrated into the Kubernetes ecosystem compared to Dask Gateway.

These commands target a Jetstream 2 [Magnum deployment]({{< relref "posts/2024-12-11-jetstream_kubernetes_magnum.md" >}}). The upstream install docs are at <https://kubernetes.dask.org/en/latest/installing.html>; this is the condensed version aligned with the JupyterHub setup on Jetstream 2.

## Preparation

Assumptions:

- Helm-based JupyterHub deployment already running.
- `helm` and `kubectl` configured with cluster-admin permissions.
- SSL termination in place


## Install the Dask Operator

Install the Operator (CRDs + controller) into its own namespace:

```bash
helm install \
  --repo https://helm.dask.org \
  --create-namespace \
  -n dask-operator \
  --generate-name \
  dask-kubernetes-operator
```

Helm prints the release name (for example, `dask-kubernetes-operator-1762815110`). Keep it if you plan to `upgrade` later instead of reinstalling.

## Validate the controller

Confirm the controller pod comes up cleanly:

```bash
kubectl get pods -A -l app.kubernetes.io/name=dask-kubernetes-operator
```

If you do not see the pod, verify the CRDs are present:

```bash
kubectl get crds | grep dask
```

## Prepare a service account for JupyterHub

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git
cd jupyterhub-deploy-kubernetes-jetstream
cd dask_operator
kubectl apply -f dask_cluster_role.yaml
```

## Configure JupyterHub

Apply it via the existing Helm deployment script. First edit `install_jhub.sh` in the deployment repository and add the extra `--values dask_operator/jupyterhub_config.yaml` flag to the `helm upgrade --install` line (alongside any other `--values` files you already use). Then run:

```bash
bash install_jhub.sh
```

## Create a Dask cluster from JupyterHub


From JupyterHub, start a new notebook server and open a Python notebook.

In the first cell, install `dask-kubernetes` (this ensures the Operator Python client is available inside the user environment):

```python
%pip install dask-kubernetes
```

In the next cell, create a Dask cluster using the Operator. The `namespace` must match the JupyterHub namespace so the spawned pods are visible and accessible to the user environment:

```python
from dask_kubernetes.operator import KubeCluster

cluster = KubeCluster(
  name="my-dask-cluster",
  namespace="jhub",            # important: JupyterHub namespace
  image="ghcr.io/dask/dask:latest",
)
cluster.scale(10)
```

Finally, display the cluster object to get a realtime view on the number of workers:

```python
cluster
```

## Specify worker CPU and memory

Simpler: pass a `resources` dict directly to `KubeCluster`. This sets requests/limits for both scheduler and the default worker group. Then scale.

```python
from dask_kubernetes.operator import KubeCluster

cluster = KubeCluster(
  name="my-dask-cluster-resources",
  namespace="jhub",
  resources={
    "requests": {"cpu": "2", "memory": "2Gi"},
    "limits": {"cpu": "2", "memory": "2Gi"},
  },
  n_workers=0,  # start with zero, then scale explicitly
)
cluster.scale(5)  # create 5 workers with 2 CPU / 2Gi each
cluster
```

Different sizes? Add another worker group with its own resources:

```python
cluster.add_worker_group(
  name="highmem",
  n_workers=2,
  resources={"requests": {"memory": "8Gi"}, "limits": {"memory": "8Gi"}},
)
cluster.scale(4, worker_group="highmem")  # scale that group
```

Use `cluster.scale(N, worker_group="groupname")` to change replicas for a specific group later.

Notice that if you have the the Kubernetes Autocaler enabled in your cluster, it will automatically scale the number of nodes to accommodate the requested resources.
