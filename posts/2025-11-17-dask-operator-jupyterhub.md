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

If you want to avoid running `%pip install dask-kubernetes` every time a pod restarts, build your JupyterHub spawn image with `dask-kubernetes` already included so the dependency is available as soon as the notebook starts.

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

## Access the dask dashboard

One of the most important features of Dask is its dashboard, which provides real-time insight into distributed calculations. To visualize the Dask dashboard from within JupyterHub, we need to use `jupyter-server-proxy`.

A critical point is that `jupyter-server-proxy` must be baked into the single-user Docker image that JupyterHub spawns. This is because the proxy needs to be available when the user's pod starts. Installing it with `%pip install` inside a running notebook will not work, as the server proxy components are not loaded dynamically.

I have created an example single-user image derived from `scipy-notebook` that includes `jupyter-server-proxy` and other useful packages for scientific computing. The repository is available at [github.com/zonca/jupyterhub-dask-docker-image](https://github.com/zonca/jupyterhub-dask-docker-image). The image is automatically built using GitHub Actions and hosted on the GitHub Container Registry (which is a container registry similar to Docker Hub or Quay.io).

The list of available image tags is at [github.com/zonca/jupyterhub-dask-docker-image/pkgs/container/jupyterhub-dask-docker-image](https://github.com/zonca/jupyterhub-dask-docker-image/pkgs/container/jupyterhub-dask-docker-image).

To use one of these images in your JupyterHub deployment, you need to update your `config_standard_storage.yaml` file for the JupyterHub Helm chart. For example, to use a specific image tag, you would add:

```yaml
singleuser:
  image:
    name: ghcr.io/zonca/jupyterhub-dask-docker-image
    tag: "2025-11-18-018e8a6"
```

After updating your JupyterHub configuration to use a compatible image, when you create a `KubeCluster` and print the `cluster` object in your notebook, it will now include a clickable link to the Dask dashboard. The link will have a format similar to this:

`/user/YOURUSER/proxy/my-dask-cluster-scheduler.jhub:8787/status`

This allows you to directly access the dashboard and monitor your Dask cluster's activity.
