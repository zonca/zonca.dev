---
categories:
- kubernetes
- jetstream
- jupyterhub
- nbgrader
date: '2026-03-03'
layout: post
title: Deploy nbgrader on Jetstream with a Manila exchange disk (Kubernetes)
---

This tutorial shows how to deploy **nbgrader** on Jetstream Kubernetes using a **shared Manila disk** mounted on all JupyterHub user pods.

This is for the setup where:

* You already created a Magnum cluster named `k8s`.
* You already created a Jetstream-managed Manila share named `nbgraderexchange` (via Exosphere).
* You want nbgrader's default **filesystem exchange** (no `ngshare`).

We will:

* Configure `kubectl` for the Magnum cluster.
* Mount the existing Manila share into all JupyterHub user pods at `/share`.
* Configure nbgrader to use `/share/nbgrader/exchange`.
* Run the full instructor/student workflow (`release`, `fetch`, `submit`, `collect`, `autograde`).

## Why this approach

nbgrader's native exchange expects a shared filesystem visible from both instructor and student pods.  
A Manila share mounted as `ReadWriteMany` provides exactly that.

## Prerequisites

* A running Magnum cluster named `k8s`.
* JupyterHub deployed with Helm.
* A Manila share already created.
* This repository cloned locally.
* OpenStack credentials (`*openrc*.sh`) and local `.venv` available.

## Step 1: Configure access to the Magnum cluster

From the repo root:

```bash
source ./app-cred-coe-202504-openrc.sh
source .venv/bin/activate
export K8S_CLUSTER_NAME=k8s
bash kubernetes_magnum/configure_kubectl_locally.sh
export KUBECONFIG=$(pwd)/config
kubectl get nodes
```

You should see nodes from your `k8s` cluster.

## Step 2: Prepare the existing Manila share as a Kubernetes RWX volume

This repo includes templates for Jetstream Manila CephFS:

* `manila/cephfs-csi-values.yaml`
* `manila/cephfs-csi-pv.yaml`
* `manila/cephfs-csi-pvc.yaml`

Get mount info from the existing Exosphere share:

```bash
bash manila/generate_mount_command.sh nbgraderexchange
```

Use the output to fill placeholders in `manila/cephfs-csi-values.yaml` and `manila/cephfs-csi-pv.yaml`:

* `<CEPH_FSID>` (any stable ID string is fine, but it must match in both files)
* `<ACCESS_RULE_NAME>`
* `<ACCESS_KEY>`
* `<SHARE_PATH>` as **path only** (`/volumes/...`), not the full `mon1,mon2:/volumes/...` string

Install CephFS CSI (if not already installed) and create PV/PVC:

```bash
helm repo add ceph-csi https://ceph.github.io/csi-charts/ || true
helm repo update
helm upgrade --install ceph-csi-cephfs ceph-csi/ceph-csi-cephfs \
  --namespace kube-system \
  -f manila/cephfs-csi-values.yaml

kubectl create namespace jhub --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f manila/cephfs-csi-pv.yaml
kubectl apply -f manila/cephfs-csi-pvc.yaml
kubectl -n jhub get pvc manila-cephfs
```

Important for `manila/cephfs-csi-pv.yaml`:

* Add `fsName: "cephfs"` under `volumeAttributes`.
* Keep `clusterID` aligned with `manila/cephfs-csi-values.yaml`.
* Ensure `nodeStageSecretRef.namespace` matches where `csi-cephfs-secret` exists.

If the chart created `csi-cephfs-secret` in `kube-system` but your PV references `default`, copy it once:

```bash
kubectl -n kube-system get secret csi-cephfs-secret -o yaml \
  | sed 's/namespace: kube-system/namespace: default/' \
  | kubectl apply -f -
```

Expected PVC status:

```
NAME            STATUS   VOLUME             CAPACITY   ACCESS MODES
manila-cephfs   Bound    manila-cephfs-pv   50Gi       RWX
```

## Step 3: Mount the Manila share in all JupyterHub user pods

Use the values file already in this repo:

* `manila/jupyterhub_manila.yaml`

It mounts the shared PVC at `/share` for every user pod.

Verify JupyterHub exists in `jhub` namespace:

```bash
helm list -n jhub
```

If no `jhub` release is present yet, deploy JupyterHub first, then continue.

Add this values file to `install_jhub.sh` (before the last line):

```
--values manila/jupyterhub_manila.yaml \
```

Re-deploy:

```bash
bash install_jhub.sh
```

Then stop and start existing user servers so they pick up the new mount.

## Step 4: Install nbgrader and configure filesystem exchange

Use this file from the repo:

* `nbgrader/jhub-singleuser-nbgrader-filesystem.yaml`

Replace `COURSE_ID` with your course ID (example: `course101`).

Add this file to `install_jhub.sh`:

```
--values nbgrader/jhub-singleuser-nbgrader-filesystem.yaml \
```

Re-deploy:

```bash
bash install_jhub.sh
```

Then stop and start existing user servers so the `postStart` hook re-runs and writes the updated `nbgrader_config.py`.

## Step 5: Validate the shared mount and initialize exchange folders

Open a JupyterHub terminal as an instructor/admin user:

```bash
python -m pip show nbgrader
mkdir -p /share/nbgrader/exchange
mkdir -p /share/nbgrader/exchange/course101/inbound
mkdir -p /share/nbgrader/exchange/course101/outbound
mkdir -p /share/nbgrader/exchange/course101/feedback
chmod -R 0777 /share/nbgrader/exchange
ls -la /share/nbgrader/exchange/course101
```

If `/share` is mounted but writing fails with `Permission denied`, run a one-time permission bootstrap pod:

```bash
kubectl -n jhub apply -f nbgrader/manila-exchange-permissions-pod.yaml
kubectl -n jhub logs manila-exchange-permissions
kubectl -n jhub delete pod manila-exchange-permissions
```

Then open a different user server and confirm the same files are visible:

```bash
ls -la /share/nbgrader/exchange/course101
```

## Step 6: Instructor workflow (create + release)

As instructor:

```bash
nbgrader quickstart course101
cp -r /path/to/jupyterhub-deploy-kubernetes-jetstream/nbgrader/quickstart-source/ps1 /home/jovyan/course101/source/
cd /home/jovyan/course101
nbgrader generate_assignment ps1 --force
nbgrader db student add student1
nbgrader release_assignment ps1 --force
```

## Step 7: Student workflow (list + fetch + submit)

As `student1`:

```bash
nbgrader list
nbgrader fetch_assignment ps1
nbgrader submit /home/jovyan/course101/ps1
```

Expected output includes `course101 ps1` in `nbgrader list` and a successful submit message.

## Step 8: Instructor workflow (collect + autograde)

As instructor:

```bash
cd /home/jovyan/course101
nbgrader collect ps1
nbgrader autograde ps1
```

## Notes

* This tutorial uses nbgrader's **filesystem exchange** on a shared Manila disk.
* No `ngshare` service or `ngshare_exchange` package is required.
* The important part is that all user pods mount the same RWX path and permissions allow read/write for instructor and students.

## Troubleshooting

If `nbgrader fetch_assignment` or `submit` fails with permission errors:

```bash
chmod -R 0777 /share/nbgrader/exchange
```

If user pods don't see `/share`, confirm both values files were included in `install_jhub.sh` and run `bash install_jhub.sh` again.

If the Manila PVC is not `Bound`, re-check placeholders in:

* `manila/cephfs-csi-values.yaml`
* `manila/cephfs-csi-pv.yaml`

If pods are stuck in `ContainerCreating` with Ceph mount errors:

* `missing required field fsName`: add `fsName: "cephfs"` in `manila/cephfs-csi-pv.yaml`.
* `mount error 3 = No such process`: `rootPath` is wrong; use only `/volumes/...` path.
* `failed to find the secret csi-cephfs-secret in namespace default`: align `nodeStageSecretRef.namespace` with the namespace where the secret exists.
