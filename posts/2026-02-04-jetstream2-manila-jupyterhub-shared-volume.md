---
categories:
- kubernetes
- jetstream2
- jupyterhub
date: '2026-02-04'
layout: post
title: Create a Manila Share in Exosphere and Mount It for All JupyterHub Users
---

This tutorial shows how to create a Manila share in Exosphere and mount it into all JupyterHub single-user pods on Jetstream 2. This provides a ReadWriteMany (RWX) shared filesystem suitable for shared datasets and tools.

## 0. Clone the JupyterHub deployment repo and locate the Manila examples

These steps reuse the example manifests included in the JupyterHub deployment repository:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream.git
cd jupyterhub-deploy-kubernetes-jetstream
ls manila
```

You will use:

- `manila/cephfs-csi-values.yaml` for the CephFS CSI Helm chart values
- `manila/cephfs-csi-pv.yaml` for the static PV
- `manila/cephfs-csi-pvc.yaml` for the static PVC
- `manila/cephfs-csi-test-pod.yaml` for a quick mount test
- `manila/jupyterhub_manila.yaml` for the Z2JH Helm values snippet

## 1. Create a Manila share in Exosphere

Exosphere supports Manila shares as an **Experimental feature**. Enable Experimental features in Exosphere settings, then create a share from the allocation dashboard (Create → Share). After creation, open the share’s status page and copy:

- **Share path**
- **Access rule name**
- **Access key** (one read/write and one read-only)

These are shown in the “Mount Your Share” section on the share status page.

## 2. Install CephFS CSI with Helm (required on Kubernetes 1.31+)

Kubernetes 1.31 removed the in-tree CephFS plugin, so you must use the CephFS CSI driver. This tutorial uses the official Helm chart.

First, edit `manila/cephfs-csi-values.yaml` with your Manila values:

```bash
sed -n '1,120p' manila/cephfs-csi-values.yaml
```

Fill in:

- `<CEPH_FSID>`: Ceph cluster FSID (request from Jetstream support)
- `<ACCESS_RULE_NAME>`: the Manila access rule name (no `client.` prefix)
- `<ACCESS_KEY>`: read/write or read-only key, depending on the mount you want

Install the chart:

```bash
helm repo add ceph-csi https://ceph.github.io/csi-charts
helm repo update
helm upgrade --install ceph-csi-cephfs ceph-csi/ceph-csi-cephfs \
  --namespace default --create-namespace \
  --values manila/cephfs-csi-values.yaml
```

Verify the CSI pods are running:

```bash
kubectl -n default get pods -l app=csi-cephfsplugin-provisioner
kubectl -n default get pods -l app=csi-cephfsplugin
```

## 3. Create a static PV/PVC for the Manila share

Edit the files below to add your **CEPH_FSID** and **Share path** (the path portion after the monitors):

```bash
sed -n '1,200p' manila/cephfs-csi-pv.yaml
sed -n '1,200p' manila/cephfs-csi-pvc.yaml
```

Apply them:

```bash
kubectl apply -f manila/cephfs-csi-pv.yaml
kubectl apply -f manila/cephfs-csi-pvc.yaml
```

## 4. Test the mount with a pod

```bash
kubectl apply -f manila/cephfs-csi-test-pod.yaml
kubectl exec --stdin -n jhub --tty cephfs-csi-test -- /bin/sh
cd /mnt/cephfs
```

If you want a shared read/write directory for users, create it and assign `jovyan` ownership:

```bash
mkdir readwrite
chown 1000:100 readwrite
```

## 5. Mount the share in all JupyterHub user pods (edit `manila/jupyterhub_manila.yaml`)

Edit `manila/jupyterhub_manila.yaml` to reference the PVC created above. The file already contains a `persistentVolumeClaim` reference.

Then upgrade JupyterHub:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub --create-namespace \
  --values config_standard_storage.yaml \
  --values secrets.yaml \
  --values manila/jupyterhub_manila.yaml
```

Users will now see `/share` inside their notebooks, and it will be shared across all users and all nodes.

## Notes and cautions

- Manila shares are optimized for shared data and software. Metadata-heavy workloads can be problematic, so avoid workflows that create or modify huge numbers of small files.
- If you need the raw mount command for a VM (outside Kubernetes), Exosphere provides it on the share status page.
