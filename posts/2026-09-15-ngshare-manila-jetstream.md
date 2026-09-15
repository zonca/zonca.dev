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

This tutorial shows how to deploy **nbgrader** with **ngshare** on Jetstream Kubernetes where ngshare's SQLite database lives on a **Manila CephFS share** instead of a Cinder volume.

It is the storage-backend update of the original ngshare tutorial: [Deploy nbgrader on Jetstream with ngshare (Kubernetes)](./2026-02-04-nbgrader-ngshare-jetstream.md).

## Why use Manila for ngshare

ngshare keeps its SQLite database on a **ReadWriteMany** PVC (in case of multiple replicas or shared access). The default Cinder CSI driver on Jetstream registers `fsGroupPolicy: ReadWriteOnceWithFSType`, so per the CSI spec `fsGroup` is applied only to ReadWriteOnce claims; RWX volumes are mounted with root ownership, and ngshare fails with:

```
sqlite3.OperationalError: unable to open database file
```

The previous workaround was a root initContainer fixing ownership and mode (see the old tutorial's Troubleshooting section).

Manila CephFS volumes mounted through the **CephFS CSI driver** register `fsGroupPolicy: File`, so `fsGroup` is honored also for RWX mounts. ngshare then works out of the box, without initContainers. I verified this on 2026-09-15 on a fresh Jetstream2 cluster: the ngshare pod starts, runs its alembic migrations and creates the SQLite DB with fsGroup 1000 applied. Reusable test manifests are in the repository at `nbgrader/ngshare-standalone-repro-manila/`.

## Prerequisites

* A running Magnum cluster on Jetstream (see [Deploy Kubernetes on Jetstream2 with Magnum and Cluster API](/posts/2026-08-20-kubernetes-jetstream2-magnum)).
* OpenStack credentials loaded, plus `openstack`, `kubectl`, and `helm`.
* This repository cloned locally.

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

```
149.165.158.38:6789,149.165.158.22:6789,149.165.158.54:6789,149.165.158.70:6789,149.165.158.86:6789:/volumes/_nogroup/<share-id>/<path>
```

The part before the first `:` are the Ceph monitors; the rest is the share path (use only `/volumes/...` in the PV).

## Step 2: Configure access to the cluster

From the repository root, with OpenStack credentials loaded:

```bash
export K8S_CLUSTER_NAME=k8s
bash kubernetes_magnum/configure_kubectl_locally.sh
export KUBECONFIG=$(pwd)/config
kubectl get nodes
```

## Step 3: Install the CephFS CSI driver

Edit `manila/cephfs-csi-values.yaml` with:

* `<CEPH_FSID>`: any stable ID string, e.g. `manila-cephfs` (it only needs to match the PV, see the next step)
* `<ACCESS_RULE_NAME>`: the access rule name (`ngshare-rw`, no `client.` prefix)
* `<ACCESS_KEY>`: the access key from Step 1
* the `monitors` list from the export location

Then install in `kube-system` (the nodeStageSecretRef of the PV below points there):

```bash
helm repo add ceph-csi https://ceph.github.io/csi-charts/
helm repo update
helm upgrade --install ceph-csi-cephfs ceph-csi/ceph-csi-cephfs \
  --namespace kube-system \
  -f manila/cephfs-csi-values.yaml
```

Verify the driver is registered and pods run:

```bash
kubectl get csidriver cephfs.csi.ceph.com
kubectl -n kube-system get pods | grep ceph-csi-cephfs
```

Expected `fsGroupPolicy`: `File`.

## Step 4: Create the StorageClass, PV and PVC

This repo ships templates in `nbgrader/ngshare-standalone-repro-manila/`:

* `00-storageclass.yaml`: `manila-cephfs` StorageClass with `provisioner: kubernetes.io/no-provisioner`
* `01-pv.yaml`: static PV (fill `<SHARE_ID>` and `<SHARE_PATH>`)
* `02-pvc.yaml`: claim bound via `selector`

Fill `01-pv.yaml`:

* `<SHARE_ID>`: the Manila share UUID (any unique string is fine as `volumeHandle`)
* `<SHARE_PATH>`: `/volumes/_nogroup/...` from Step 1
* `clusterID` must equal the `<CEPH_FSID>` used in Step 3

Apply:

```bash
kubectl create namespace jhub --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f nbgrader/ngshare-standalone-repro-manila/00-storageclass.yaml
kubectl apply -f nbgrader/ngshare-standalone-repro-manila/01-pv.yaml
kubectl apply -f nbgrader/ngshare-standalone-repro-manila/02-pvc.yaml
kubectl -n jhub get pvc ngshare-manila-repro-pvc
```

Expected: PVC `Bound`, access modes `RWX`.

Why a `no-provisioner` StorageClass: the ngshare Helm chart creates its own PVC and we bind it statically with a `selector`. A StorageClass with a real provisioner would make the controller attempt dynamic provisioning, and the CephFS provisioner rejects PVC selectors with `claim Selector is not supported`.

## Step 5: Install ngshare

Use the values file `nbgrader/ngshare-manila-config.yaml`: it points the chart PVC at the static PV via `pvc.selector`, uses `storageClassName: manila-cephfs`, and contains no initContainer.

Edit it (token, admins) and install:

```bash
helm install ngshare ngshare/ngshare \
  --namespace jhub \
  -f nbgrader/ngshare-manila-config.yaml
```

Verify:

```bash
kubectl -n jhub get pods -l app.kubernetes.io/instance=ngshare
kubectl -n jhub logs deploy/ngshare --tail=20
```

Expected: pod `1/1 Running`, log shows alembic migrations (`Context impl SQLiteImpl`, `Running upgrade -> aa00db20c10a, Init`) and no permission errors. The SQLite database is created on the Manila volume with fsGroup ownership:

```bash
kubectl -n jhub exec deploy/ngshare -- sh -c 'id; ls -ld /srv/ngshare; ls -l /srv/ngshare'
```

## Step 6: Register ngshare in JupyterHub and enable nbgrader

Same as the original tutorial:

1. Add the ngshare service snippet from `nbgrader/jhub-ngshare-service.yaml` to your JupyterHub values and redeploy.
2. Add `nbgrader/jhub-singleuser-nbgrader.yaml` so user pods have `nbgrader` and `ngshare_exchange`.

See steps 2 to 4 of [Deploy nbgrader on Jetstream with ngshare (Kubernetes)](./2026-02-04-nbgrader-ngshare-jetstream.md).

## Notes

* No initContainer is required: the Manila CephFS volume honors `fsGroup` on RWX claims.
* The ngshare PVC is standalone metadata storage; 10 GiB is plenty for typical classes.
* The `nbgrader/ngshare-standalone-repro-manila/` folder contains a standalone repro (same ngshare runtime conditions) if you want to verify a fresh setup before deploying.

## Troubleshooting

**PVC stuck Pending, event `claim Selector is not supported`**: the StorageClass has a real provisioner. Recreate it with `provisioner: kubernetes.io/no-provisioner` as in `00-storageclass.yaml`.

**PVC Pending after the PV was previously bound and released**: clear the `claimRef` on the PV:

```bash
kubectl patch pv ngshare-manila-pv --type=merge -p '{"spec":{"claimRef":null}}'
```

**Pod stuck ContainerCreating with Ceph mount errors**: check the `secret` referenced by `nodeStageSecretRef` exists in `kube-system`, and that `rootPath` is only the `/volumes/...` part of the export location.

**Old sqlite error still appears**: make sure the ngshare pod uses the Manila PVC and that the volume directory is not a leftover Cinder mount. Delete the ngshare pod so it re-creates the DB on the new volume:

```bash
kubectl -n jhub delete pod -l app.kubernetes.io/instance=ngshare
```
