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

- `manila/ceph-secret.yml` for the CephFS secret
- `manila/ceph-pod.yml` for a quick mount test
- `manila/jupyterhub_manila.yaml` for the Z2JH Helm values snippet

## 1. Create a Manila share in Exosphere

Exosphere supports Manila shares as an **Experimental feature**. Enable Experimental features in Exosphere settings, then create a share from the allocation dashboard (Create → Share). After creation, open the share’s status page and copy:

- **Share path**
- **Access rule name**
- **Access key**

These are shown in the “Mount Your Share” section on the share status page.

## 2. Create the Kubernetes secret (edit `manila/ceph-secret.yml`)

Open `manila/ceph-secret.yml` and replace the key with your **Access key**:

```bash
sed -n '1,120p' manila/ceph-secret.yml
```

Apply it:

```bash
kubectl apply -f manila/ceph-secret.yml
```

## 3. Configure a test pod (edit `manila/ceph-pod.yml`)

Before mounting into JupyterHub, test with a simple pod. Edit `manila/ceph-pod.yml` and set:

- `monitors`: use the monitor list and ports from Exosphere
- `user`: set to **Access rule name**
- `path`: set to **Share path**

Apply it and verify access:

```bash
kubectl apply -f manila/ceph-pod.yml
kubectl exec --stdin -n jhub --tty ceph -- /bin/bash
cd /mnt/cephfs
```

If you want a shared read/write directory for users, create it and assign `jovyan` ownership:

```bash
mkdir readwrite
chown 1000:100 readwrite
```

## 4. Mount the share in all JupyterHub user pods (edit `manila/jupyterhub_manila.yaml`)

Edit `manila/jupyterhub_manila.yaml` to match the same **monitors**, **Access rule name**, and **Share path** you used above. The file already contains a correct CephFS volume configuration.

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
