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

## 1. Create a Manila share in Exosphere

Exosphere supports Manila shares as an **Experimental feature**. Enable Experimental features in Exosphere settings, then create a share from the allocation dashboard (Create → Share). After creation, open the share’s status page and copy:

- **Share path**
- **Access rule name**
- **Access key**

These are shown in the “Mount Your Share” section on the share status page.

## 2. Create the Kubernetes secret

Create a secret in the JupyterHub namespace (replace values from Exosphere):

```bash
kubectl -n jhub create secret generic ceph-secret \
  --from-literal=key='<ACCESS_KEY_FROM_EXOSPHERE>'
```

## 3. Configure a test pod (optional but recommended)

Before mounting into JupyterHub, test with a simple pod:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ceph
  namespace: jhub
spec:
  containers:
  - name: cephfs-pod
    image: httpd:buster
    volumeMounts:
    - mountPath: "/mnt/cephfs"
      name: cephfs
  volumes:
  - name: cephfs
    cephfs:
      monitors:
      - <MON1>:<PORT>
      - <MON2>:<PORT>
      - <MON3>:<PORT>
      - <MON4>:<PORT>
      - <MON5>:<PORT>
      user: <ACCESS_RULE_NAME>
      secretRef:
        name: ceph-secret
      readOnly: false
      path: "<SHARE_PATH>"
```

Apply it and verify access:

```bash
kubectl apply -f ceph-pod.yml
kubectl exec --stdin -n jhub --tty ceph -- /bin/bash
cd /mnt/cephfs
```

If you want a shared read/write directory for users, create it and assign `jovyan` ownership:

```bash
mkdir readwrite
chown 1000:100 readwrite
```

## 4. Mount the share in all JupyterHub user pods

Add this to your Z2JH Helm values (for example in `manila/jupyterhub_manila.yaml`):

```yaml
singleuser:
  storage:
    extraVolumes:
      - name: manila-share
        cephfs:
          monitors:
          - <MON1>:<PORT>
          - <MON2>:<PORT>
          - <MON3>:<PORT>
          - <MON4>:<PORT>
          - <MON5>:<PORT>
          user: <ACCESS_RULE_NAME>
          secretRef:
            name: ceph-secret
          readOnly: false
          path: "<SHARE_PATH>"
    extraVolumeMounts:
      - name: manila-share
        mountPath: /share
        readOnly: false
```

Then upgrade JupyterHub:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub --create-namespace \
  --values config_standard_storage.yaml \
  --values secrets.yaml \
  --values manila/jupyterhub_manila.yaml
```

Users will now see `/share` inside their notebooks, and it will be shared across all users and all nodes.

## 5. Is this similar to nbgrader?

Yes. nbgrader’s “exchange” directory needs a shared RWX filesystem so instructors and students can access the same files concurrently. A Manila-backed CephFS share provides exactly that shared filesystem layer, so it’s a good fit for nbgrader’s exchange directory.

## Notes and cautions

- Manila shares are optimized for shared data and software. Metadata-heavy workloads can be problematic, so avoid workflows that create or modify huge numbers of small files.
- If you need the raw mount command for a VM (outside Kubernetes), Exosphere provides it on the share status page.
