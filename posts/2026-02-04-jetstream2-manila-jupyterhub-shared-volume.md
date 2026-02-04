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
- **Access key** (one read/write and one read-only)

These are shown in the “Mount Your Share” section on the share status page.

## 2. Create the Kubernetes secret (edit `manila/ceph-secret.yml`)

Open `manila/ceph-secret.yml` and replace the key with your **Access key**. Use the read/write key for a shared writable mount, or the read-only key if you plan to mount it read-only:

```bash
sed -n '1,120p' manila/ceph-secret.yml
```

Apply it:

```bash
kubectl apply -f manila/ceph-secret.yml
```

## 3. Install the CephFS CSI driver (required on Kubernetes 1.31+)

If your pod shows `failed to get Plugin from volumeSpec ... err=no volume plugin matched`, your cluster does not have the CephFS volume plugin installed. Kubernetes 1.31 removed the in-tree CephFS plugin, so you must install the CephFS CSI driver.

Download the Ceph CSI manifests in a local folder:

```bash
git clone --depth 1 --branch v3.15.0 https://github.com/ceph/ceph-csi ceph-csi
```

Create the CSI config and secret. Use the same Manila access rule name and key:

```bash
KEY=$(kubectl get secret -n jhub ceph-secret -o jsonpath="{.data.key}" | base64 -d)
cat <<EOF > ceph-csi-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ceph-csi-config
  namespace: default
data:
  config.json: |-
    [
      {
        "clusterID": "<CEPH_FSID>",
        "monitors": [
          "149.165.158.38:6789",
          "149.165.158.22:6789",
          "149.165.158.54:6789",
          "149.165.158.70:6789",
          "149.165.158.86:6789"
        ]
      }
    ]
---
apiVersion: v1
kind: Secret
metadata:
  name: csi-cephfs-secret
  namespace: default
stringData:
  userID: <ACCESS_RULE_NAME>
  userKey: ${KEY}
EOF
kubectl apply -f ceph-csi-config.yaml
```

Replace `<CEPH_FSID>` with the Ceph cluster FSID (ask Jetstream support if you do not have a way to query it).

Install the CephFS CSI components (these use the `default` namespace):

```bash
kubectl apply -f ceph-csi/deploy/cephfs/kubernetes/csidriver.yaml
kubectl apply -f ceph-csi/deploy/cephfs/kubernetes/csi-provisioner-rbac.yaml
kubectl apply -f ceph-csi/deploy/cephfs/kubernetes/csi-nodeplugin-rbac.yaml
kubectl apply -f ceph-csi/deploy/ceph-conf.yaml
kubectl apply -f ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin-provisioner.yaml
kubectl apply -f ceph-csi/deploy/cephfs/kubernetes/csi-cephfsplugin.yaml
```

Verify the CSI pods are running:

```bash
kubectl -n default get pods -l app=csi-cephfsplugin-provisioner
kubectl -n default get pods -l app=csi-cephfsplugin
```

## 4. Configure a test pod (edit `manila/ceph-pod.yml`)

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

## 5. Mount the share in all JupyterHub user pods (edit `manila/jupyterhub_manila.yaml`)

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
