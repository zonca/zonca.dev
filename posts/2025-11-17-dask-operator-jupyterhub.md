---
categories:
- kubernetes
- jetstream2
- jupyterhub
- dask
- python
date: '2025-11-17'
layout: post
title: Deploy the Dask Operator Alongside JupyterHub on Kubernetes

---

While updating my Kubernetes tooling I revisited the differences between Dask Gateway and the newer Dask Operator. Gateway acts as a multi-tenant API layer with its own auth flow, making it ideal when you need to expose Dask clusters to remote clients. The Operator, by contrast, extends Kubernetes with `DaskCluster` custom resources, so cluster lifecycles are reconciled by Kubernetes itself and are easier to manage through GitOps or namespace isolation. After reading the upstream docs and a couple of blog posts, I decided the Operator was a better match for environments where administrators already trust the in-cluster control plane and mainly need notebooks to spin up clusters on demand.

Below I captured the steps I used on the Jetstream 2 [Magnum deployment]({{< relref "posts/2024-12-11-jetstream_kubernetes_magnum.md" >}}). The official guide lives at <https://kubernetes.dask.org/en/latest/installing.html>; I am reproducing the short version here so I can keep it next to my JupyterHub notes.

## Preparation

As with my earlier Gateway setup, I assume you already have a Helm-based JupyterHub deployment, `helm` and `kubectl` configured against your cluster-admin context, and SSL terminated (ingress or load balancer both work). I keep the manifests and helper scripts in `github.com/zonca/jupyterhub-deploy-kubernetes-jetstream`, so I start from a clone of that repository on the admin workstation:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git
cd jupyterhub-deploy-kubernetes-jetstream
cd dask_operator
kubectl apply -f dask_cluster_role.yaml
cd ..
```

## Install the Dask Operator

The Helm chart supplied by the Dask project now encapsulates all CRDs and controller deployments. A single command installs it into its own namespace:

```bash
helm install \
  --repo https://helm.dask.org \
  --create-namespace \
  -n dask-operator \
  --generate-name \
  dask-kubernetes-operator
```

Helm will print the generated release name (for example, `dask-kubernetes-operator-1762815110`). You rarely need it afterwards, but you can save it in case you want to `upgrade` later instead of reinstalling.

## Validate the controller

Confirm the controller pod comes up cleanly:

```bash
kubectl get pods -A -l app.kubernetes.io/name=dask-kubernetes-operator
```

Example output from the Magnum cluster:

```
NAMESPACE       NAME                                                   READY   STATUS    RESTARTS   AGE
dask-operator   dask-kubernetes-operator-1762815110-76486fc46b-5msqb   1/1     Running   0          105m
```

If you do not see the pod, double-check that the CRDs were applied successfully (`kubectl get crds | grep dask`).

## Configure JupyterHub

Before users can request clusters we need to let the hub service account talk to the Operator and supply the right image/cluster defaults. After cloning the deployment repo above, review the relative-path configuration at [dask_operator/jupyterhub_config.yaml](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/dask_operator/jupyterhub_config.yaml) and tweak it for your environment (images, namespaces, resource limits, etc.).

Finally plug those values into the existing Helm deployment by adding another values file to `install_jhub.sh`:

```bash
bash install_jhub.sh --values dask_operator/jupyterhub_config.yaml
```

If you already pass other `--values` flags, simply append this one at the end of that command.

## Create a DaskCluster custom resource

Once the Operator is running you can define Dask clusters declaratively. The snippet below mirrors the upstream docs but trims the spec down to the essentials.

```bash
cat <<'EOF' > daskcluster.yaml
apiVersion: kubernetes.dask.org/v1
kind: DaskCluster
metadata:
  name: user-default
  namespace: jhub
spec:
  scheduler:
    image: daskdev/dask:2024.4.1
    replicas: 1
  worker:
    replicas: 2
    image: daskdev/dask:2024.4.1
    resources:
      limits:
        cpu: "2"
        memory: 4Gi
      requests:
        cpu: "1"
        memory: 2Gi
  services:
    type: ClusterIP
EOF
kubectl apply -f daskcluster.yaml
```

Replace the namespace with whichever one holds your users (each hub user can even get their own namespace if you rely on `kubespawner` profiles).

To check the cluster status:

```bash
kubectl -n jhub get daskclusters.kubernetes.dask.org user-default -o yaml | yq '.status.cluster'
```

Once the controller finishes provisioning, the `status.cluster.scheduler.address` field advertises the address you can pass to Dask clients.

## Connect from JupyterHub

Because we already run JupyterHub in the same cluster, the notebooks can talk directly to the scheduler without a Gateway in the middle. A minimal notebook cell looks like:

```python
import dask
from distributed import Client

scheduler_address = "tcp://10.233.32.144:8786"  # replace with status.cluster.scheduler.address
client = Client(scheduler_address)
client
```

If you want fully programmatic control, the `dask-kubernetes` Python package now exposes `KubeCluster` helpers for the Operator:

```python
from dask_kubernetes.operator import KubeCluster

cluster = KubeCluster(
    name="user-default",
    namespace="jhub",
    image="daskdev/dask:2024.4.1",
    worker_replicas=2,
)
cluster.adapt(minimum=1, maximum=6)
client = cluster.get_client()
```

This approach creates CRDs on behalf of the user and cleans them up when the notebook shuts down, keeping resource usage contained in the namespace quota.

## Clean up

When you want to wipe the test cluster, delete the custom resource and Helm release:

```bash
kubectl -n jhub delete daskcluster user-default
helm uninstall -n dask-operator <release-name>
```

Switching between this Operator workflow and the older Gateway stack is straightforward, but I now prefer the Operator whenever a Kubernetes-native control loop is desirable and JupyterHub already manages authentication.
