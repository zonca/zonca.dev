---
categories:
- kubernetes
- jetstream
- jupyterhub
- nbgrader
date: '2026-09-15'
layout: post
title: "Deploy ngshare on Jetstream with a Manila volume (Kubernetes)"
---

This tutorial shows how to deploy **nbgrader** with **ngshare** on Jetstream
Kubernetes where ngshare's SQLite database lives on a **Manila CephFS share**
instead of a Cinder volume.

It is the storage-backend update of the original ngshare tutorial:
[Deploy nbgrader on Jetstream with ngshare (Kubernetes)](./2026-02-04-nbgrader-ngshare-jetstream.md).

## Why use Manila for ngshare

ngshare keeps its SQLite database on a **ReadWriteMany** PVC (in case of
multiple replicas or shared access). The default Cinder CSI driver on
Jetstream registers `fsGroupPolicy: ReadWriteOnceWithFSType`, so per the CSI
spec `fsGroup` is applied only to ReadWriteOnce claims; RWX volumes are
mounted with root ownership, and ngshare fails with:

```text
sqlite3.OperationalError: unable to open database file
```

The previous workaround was a root initContainer fixing ownership and mode
(see the old tutorial's Troubleshooting section).

Manila CephFS volumes mounted through the **CephFS CSI driver** register
`fsGroupPolicy: File`, so `fsGroup` is honored also for RWX mounts. ngshare
then works out of the box, without initContainers. I verified this on
2026-09-15 on a fresh Jetstream2 cluster: the ngshare pod starts, runs its
alembic migrations and creates the SQLite DB with fsGroup 1000 applied. All
manifests below live in the
[jupyterhub-deploy-kubernetes-jetstream](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream)
deployment repository, and the reusable test case is at
`nbgrader/ngshare-standalone-repro-manila/`.

## Prerequisites

* A running Magnum cluster on Jetstream (see
  [Deploy Kubernetes on Jetstream2 with Magnum and Cluster API](./2026-08-20-kubernetes-jetstream2-magnum.md)).
* OpenStack credentials loaded, plus `openstack`, `jq`, `kubectl`, and `helm`.
* The deployment repository cloned locally:
  `git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git`
  (all commands below run from its root).

## Step 1: Create a Manila share

Create a 10 GiB CEPHFS share and a cephx access rule:

```bash
openstack share create --name ngshare --share-type cephfsnativetype CEPHFS 10
while [ "$(openstack share show ngshare -f value -c status)" != "available" ]; do sleep 5; done
openstack share access create --access-level rw ngshare cephx ngshare-rw
```

Extract the mount details (monitors + path, access key):

```bash
openstack share show ngshare -f json | jq -r '.export_locations[0].path'
openstack share access list ngshare -f value -c "Access To" -c "Access Key"
```

The path looks like:

```text
149.165.158.38:6789,149.165.158.22:6789,149.165.158.54:6789,149.165.158.70:6789,149.165.158.86:6789:/volumes/_nogroup/<share-id>/<path>
```

The Ceph monitors are the comma-separated `host:port` entries up to the colon
that immediately precedes `/volumes/...`; the share path is everything from
`/volumes/...` onward (use only that part in the PV).

## Step 2: Configure access to the cluster

From the deployment repository root, with OpenStack credentials loaded:

```bash
export K8S_CLUSTER_NAME=k8s
bash kubernetes_magnum/configure_kubectl_locally.sh
export KUBECONFIG=$(pwd)/config
kubectl get nodes
```

## Step 3: Install the CephFS CSI driver

Copy the values template to a **local, gitignored** file (never edit the
tracked template, it holds the share access key):

```bash
cp manila/cephfs-csi-values.yaml manila/cephfs-csi-values.local.yaml
```

Fill `manila/cephfs-csi-values.local.yaml` with:

* `<CEPH_FSID>`: any stable ID string, e.g. `manila-cephfs` (it only needs to
  match the PV, see the next step)
* `<ACCESS_RULE_NAME>`: the access rule name (`ngshare-rw`, no `client.` prefix)
* `<ACCESS_KEY>`: the access key from Step 1
* the `monitors` list from the export location

Then install in `kube-system` (the nodeStageSecretRef of the PV below points
there):

```bash
helm repo add ceph-csi https://ceph.github.io/csi-charts/
helm repo update
helm upgrade --install ceph-csi-cephfs ceph-csi/ceph-csi-cephfs \
  --namespace kube-system \
  -f manila/cephfs-csi-values.local.yaml
```

Verify the driver is registered and pods run:

```bash
kubectl get csidriver cephfs.csi.ceph.com -o jsonpath='{.spec.fsGroupPolicy}'
kubectl get csidriver cephfs.csi.ceph.com
kubectl -n kube-system get pods | grep ceph-csi-cephfs
```

Expected `fsGroupPolicy`: `File`.

## Step 4: Create the StorageClass, PV and PVC

This repo ships templates for the ngshare Manila PV:

* `nbgrader/ngshare-standalone-repro-manila/00-storageclass.yaml`:
  `manila-cephfs` StorageClass with `provisioner: kubernetes.io/no-provisioner`
* `nbgrader/ngshare-manila-pv.yaml`: static PV (fill `<SHARE_ID>` and `<SHARE_PATH>`)

Fill `ngshare-manila-pv.yaml`:

* `<SHARE_ID>`: the Manila share UUID (any unique string is fine as `volumeHandle`)
* `<SHARE_PATH>`: `/volumes/_nogroup/...` from Step 1
* `clusterID` must equal the `<CEPH_FSID>` used in Step 3

Apply the StorageClass and PV (do not create a PVC here: the ngshare Helm
chart creates its own PVC in Step 5, and a static PV can be bound only once):

```bash
kubectl create namespace jhub --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f nbgrader/ngshare-standalone-repro-manila/00-storageclass.yaml
kubectl apply -f nbgrader/ngshare-manila-pv.yaml
kubectl get pv ngshare-manila-pv
```

Expected: PV `Available`, access modes `RWX`.

Why a `no-provisioner` StorageClass: the ngshare Helm chart creates its own
PVC and we bind it statically with a `selector`. A StorageClass with a real
provisioner would make the controller attempt dynamic provisioning, and the
CephFS provisioner rejects PVC selectors with
`claim Selector is not supported`.

## Step 5: Install ngshare

Add the ngshare Helm repository and use the values file
`nbgrader/ngshare-manila-config.yaml`: it points the chart PVC at the static
PV via `pvc.selector`, uses `storageClassName: manila-cephfs`, and contains no
initContainer.

Edit it (token, admins) and install:

```bash
helm repo add ngshare https://libretexts.github.io/ngshare-helm-repo/
helm repo update
helm install ngshare ngshare/ngshare \
  --namespace jhub \
  -f nbgrader/ngshare-manila-config.yaml
```

Verify the PVC bound and the pod running:

```bash
kubectl -n jhub get pvc ngshare-pvc
kubectl -n jhub get pods -l app.kubernetes.io/instance=ngshare
kubectl -n jhub logs deploy/ngshare --tail=20
```

Expected: pod `1/1 Running`, log shows alembic migrations
(`Context impl SQLiteImpl`, `Running upgrade -> aa00db20c10a, Init`) and no
permission errors. The SQLite database is created on the Manila volume with
fsGroup ownership:

```bash
kubectl -n jhub exec deploy/ngshare -- sh -c 'id; ls -ld /srv/ngshare; ls -l /srv/ngshare'
```

## Step 6: Register ngshare in JupyterHub and enable nbgrader

Same as the original tutorial:

1. Add the ngshare service snippet from
   `nbgrader/jhub-ngshare-service.yaml` to your JupyterHub values and redeploy.
2. Add `nbgrader/jhub-singleuser-nbgrader.yaml` so user pods have `nbgrader` and `ngshare_exchange`.

See steps 2 to 4 of [Deploy nbgrader on Jetstream with ngshare (Kubernetes)](./2026-02-04-nbgrader-ngshare-jetstream.md).

## Notes

* No initContainer is required: the Manila CephFS volume honors `fsGroup` on
  RWX claims.
* The ngshare PVC is standalone metadata storage; 10 GiB is plenty for
  typical classes.
* The `nbgrader/ngshare-standalone-repro-manila/` folder contains a standalone
  repro (same ngshare runtime conditions) if you want to verify a fresh setup
  before deploying. It uses its own PV (`ngshare-repro-pv`) and **its own
  Manila share or subdirectory**: never point it at the same share/path as the
  deployed ngshare volume, because its with-init variant recursively `chown`s
  the mount.

## Troubleshooting

**PVC stuck Pending, event `claim Selector is not supported`**: the
StorageClass has a real provisioner. Recreate it with
`provisioner: kubernetes.io/no-provisioner` as in `00-storageclass.yaml`.

**PVC Pending after the PV was previously bound and released**: clear the
`claimRef` on the PV:

```bash
kubectl patch pv ngshare-manila-pv --type=merge -p '{"spec":{"claimRef":null}}'
```

**Pod stuck ContainerCreating with Ceph mount errors**: check the `secret`
referenced by `nodeStageSecretRef` exists in `kube-system`, and that
`rootPath` is only the `/volumes/...` part of the export location.

**Old sqlite error still appears**: make sure the ngshare pod uses the Manila
PVC and that the volume directory is not a leftover Cinder mount. Delete the
ngshare pod so it re-creates the DB on the new volume:

```bash
kubectl -n jhub delete pod -l app.kubernetes.io/instance=ngshare
```
