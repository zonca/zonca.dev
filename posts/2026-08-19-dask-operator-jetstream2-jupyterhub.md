---
title: "Deploy the Dask Operator for Kubernetes on Jetstream2 and access it from JupyterHub"
date: '2026-08-19'
categories:
  - kubernetes
  - jetstream2
  - jupyterhub
  - dask
  - python
layout: post
---

**This is the newest version of the tutorial.** The older version of this post (2025-11-17) is obsolete.

This post describes how to deploy the [Dask Operator for Kubernetes](https://kubernetes.dask.org/) alongside a Helm-based JupyterHub installation on a Jetstream2 Kubernetes cluster (Magnum). The Operator provides a Kubernetes-native way to create and manage Dask clusters via custom resources, simplifying multi-tenant setups. Compared to Dask Gateway, it is more integrated into the Kubernetes ecosystem.

These commands target a Jetstream 2 [Kubernetes deployment](https://www.zonca.dev/posts/2022-03-30-jetstream2_kubernetes_kubespray) and assume you already have a running JupyterHub installed with [the JupyterHub tutorial](https://www.zonca.dev/posts/2022-03-31-jetstream2_jupyterhub). The upstream install docs are at <https://kubernetes.dask.org/en/latest/installing.html>; this is the condensed version aligned with the JupyterHub setup on Jetstream2.

## Versions tested

This tutorial was tested (2026-08-19) against:

- Kubernetes **1.33.2** (Magnum template `kubernetes-1-33-jammy-fixed-labels`)
- JupyterHub Helm chart **4.3.3**
- dask-kubernetes Operator & Python client **2026.3.0**
- dask / distributed **2026.7.1**
- jupyter-server-proxy **4.5.0**

## 1. Install the Dask Operator

Install the Operator (CRDs + controller) into its own namespace:

```bash
helm install \
  --repo https://helm.dask.org \
  --create-namespace \
  -n dask-operator \
  --generate-name \
  dask-kubernetes-operator
```

Helm prints the release name (for example, `dask-kubernetes-operator-1787187822`). Keep it if you plan to `upgrade` later instead of reinstalling.

## 2. Validate the controller

Confirm the controller pod comes up cleanly:

```bash
kubectl get pods -n dask-operator
```

If you do not see the pod, verify the CRDs are present:

```bash
kubectl get crds | grep dask
```

You should see `daskclusters`, `daskworkergroups`, `daskjobs`, and `daskautoscalers`:

```
daskautoscalers.kubernetes.dask.org
daskclusters.kubernetes.dask.org
daskjobs.kubernetes.dask.org
daskworkergroups.kubernetes.dask.org
```

> **Important**: apply the JupyterHub RBAC (next section) **before** starting a user notebook server, otherwise spawning fails with a `serviceaccount "dask-sa" not found` error.

## 3. Prepare a service account for JupyterHub

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git
cd jupyterhub-deploy-kubernetes-jetstream
cd dask_operator
kubectl apply -f dask_cluster_role.yaml
```

This creates a `dask-sa` ServiceAccount in the `jhub` namespace, a `dask-cluster-role` ClusterRole, and a binding so that user pods can create and manage Dask custom resources.

## 4. Configure JupyterHub

Apply it via the existing Helm deployment script. First edit `install_jhub.sh` in the deployment repository and add the extra `--values dask_operator/jupyterhub_config.yaml` flag to the `helm upgrade --install` line (alongside any other `--values` files you already use). Also add `--values dask_operator/jupyterhub_dask_dashboard_config.yaml` to enable the Dask dashboard proxy. Then run:

```bash
bash install_jhub.sh
```

## 5. Create a Dask cluster from JupyterHub

From JupyterHub, start a new notebook server and open a Python notebook.

In the first cell, install `dask-kubernetes` (this ensures the Operator Python client is available inside the user environment):

```python
%pip install dask-kubernetes
```

If you want to avoid running `%pip install dask-kubernetes` every time a pod restarts, build your JupyterHub spawn image with `dask-kubernetes` already included so the dependency is available as soon as the notebook starts (see the recommended image below).

In the next cell, create a Dask cluster using the Operator. The `namespace` must match the JupyterHub namespace so the spawned pods are visible and accessible to the user environment:

```python
from dask_kubernetes.operator import KubeCluster

cluster = KubeCluster(
  name="my-dask-cluster",
  namespace="jhub",                 # important: JupyterHub namespace
  image="ghcr.io/dask/dask:2026.7.1",  # pin a version matching your client
)
cluster.scale(10)
```

The scheduler/worker image should be the official Dask image `ghcr.io/dask/dask` and its version should be close to the `distributed` version in your user environment to avoid a `VersionMismatchWarning`. Mixing very different versions leads to client/scheduler/worker incompatibilities that are hard to debug.

> **Tip**: If your user image is built on a different Python minor version than the Dask image (e.g., the scipy-notebook image uses Python 3.13 while `ghcr.io/dask/dask` ships Python 3.10), you may see a benign `VersionMismatchWarning` listing only the `python` and `tornado` rows. As long as `dask` and `distributed` match, this is harmless and does not affect correctness.

Finally, display the cluster object to get a realtime view on the number of workers:

```python
cluster
```

You can see it scale with:

```bash
kubectl -n jhub get pods -l dask.org/component
```

## 6. Specify worker CPU and memory

Pass a `resources` dict directly to `KubeCluster`. This sets requests/limits for both the scheduler and the default worker group. Then scale.

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

Notice that if you have the Kubernetes Autoscaler enabled in your cluster (as in [the Kubespray tutorial](https://www.zonca.dev/posts/2022-03-30-jetstream2_kubernetes_kubespray)), it will automatically scale the number of nodes to accommodate the requested resources.

When you are done with the cluster, shut it down cleanly:

```python
cluster.close()
```

## 7. Run distributed work and connect with the Client

```python
from distributed import Client
import dask.array as da

client = Client(cluster)

x = da.random.random((10000, 10000), chunks=(1000, 1000))
x.sum().compute()
```

After you are done, close both the client and the cluster:

```python
client.close()
cluster.close()
```

## 8. Access the Dask dashboard

One of the most important features of Dask is its dashboard, which provides real-time insight into distributed calculations. To visualize the Dask dashboard from within JupyterHub, we need to use `jupyter-server-proxy`.

A critical point is that `jupyter-server-proxy` must be baked into the single-user Docker image that JupyterHub spawns. This is because the proxy needs to be available when the user's pod starts. Installing it with `%pip install` inside a running notebook will not work, as the server-proxy components are not loaded dynamically.

Ensure `install_jhub.sh` also passes `--values dask_operator/jupyterhub_dask_dashboard_config.yaml` to the `helm upgrade --install` command so JupyterHub is configured to expose the Dask dashboard through the proxy.

I maintain an example single-user image derived from Jupyter's `scipy-notebook` that includes `jupyter-server-proxy`, `dask`, and `dask-kubernetes` at current versions. The repository is [github.com/zonca/jupyterhub-dask-docker-image](https://github.com/zonca/jupyterhub-dask-docker-image), and the image is automatically built with GitHub Actions and hosted on the GitHub Container Registry.

The list of available image tags is at [github.com/zonca/jupyterhub-dask-docker-image/pkgs/container/jupyterhub-dask-docker-image](https://github.com/zonca/jupyterhub-dask-docker-image/pkgs/container/jupyterhub-dask-docker-image).

If you want the simplest maintenance flow for your own image, start from the [custom template and just edit `requirements.txt`; a GitHub Actions workflow will rebuild and publish automatically](https://www.zonca.dev/posts/2025-12-01-custom-jupyterhub-docker-image).

To use one of these images in your JupyterHub deployment, update your `config_standard_storage.yaml` file for the JupyterHub Helm chart:

```yaml
singleuser:
  image:
    name: ghcr.io/zonca/jupyterhub-dask-docker-image
    tag: "latest"
```

> **Pin the tag for reproducibility** — replace `latest` with the dated tag (e.g. `2026-08-19-<sha>`) listed in the registry after you verify it works on your deployment.

After updating your JupyterHub configuration to use a compatible image, when you create a `KubeCluster` and print the `cluster` object in your notebook, it will include a clickable link to the Dask dashboard. The link has this format:

```
/user/YOURUSER/proxy/my-dask-cluster-scheduler.jhub:8787/status
```

This lets you access the dashboard and monitor your Dask cluster's activity in real time.
