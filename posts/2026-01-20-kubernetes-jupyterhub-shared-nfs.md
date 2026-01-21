---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2026-01-20'
layout: post
title: Setting Up Shared NFS Home Directories & Shared Data for JupyterHub on Kubernetes
---

This tutorial provides a walkthrough on how to set up a shared NFS server for JupyterHub users' home directories and shared data.

Standard OpenStack volumes (Cinder) are typically block devices that can only be attached to a single node (ReadWriteOnce), which requires JupyterHub to dynamically attach and detach volumes as users log in and out. This can slow down the login process.

By using a shared NFS server backed by a single OpenStack volume, all user home directories reside on a single shared filesystem (ReadWriteMany). This avoids the overhead of attaching volumes per user, significantly improving login speeds. It also allows for easy creation of shared data directories accessible by all users.

This setup has been tested on the [Magnum deployment](./2024-12-11-jetstream_kubernetes_magnum.md) on Jetstream 2.

**Prerequisites:**
- Access to the OpenStack CLI.
- `kubectl` and `helm` installed and configured.

## 1. Environment Setup

Define these variables at the start of your session to automate the subsequent commands.

```bash
# Configuration Variables
export CLUSTER=k8s2                        # Your cluster name
export NFS_NAMESPACE=jupyterhub-home-nfs   # Namespace for the NFS server
export JH_NAMESPACE=jhub                   # Namespace where JupyterHub runs
export VOLUME_SIZE=500                     # Size in GB
export VOLUME_NAME="${CLUSTER}-nfs-homedirs"
```

## 2. Infrastructure: Create OpenStack Volume

Create the underlying block storage volume and capture its ID.

```bash
# Create the volume
openstack volume create --size $VOLUME_SIZE $VOLUME_NAME

# Capture the Volume ID into a variable
export VOLUME_ID=$(openstack volume show $VOLUME_NAME -f value -c id)
echo "Created Volume ID: $VOLUME_ID"
```

## 3. Deploy In-Cluster NFS Server

Generate the Helm values file using the Volume ID and deploy the NFS server.

```bash
# Generate values-nfs.yaml
cat <<EOF > values-nfs.yaml
fullnameOverride: ""
nfsServer:
  enableClientAllowlist: false
quotaEnforcer:
  enabled: true
  config:
    QuotaManager:
      hard_quota: 10   # per-user hard quota in GiB
      uid: 1000
      gid: 100
      paths: ["/export"]
prometheusExporter:
  enabled: true
openstack:
  enabled: true
  volumeId: "$VOLUME_ID"
EOF

# Install the Helm Chart
helm upgrade --install jupyterhub-home-nfs \
  oci://ghcr.io/2i2c-org/jupyterhub-home-nfs/jupyterhub-home-nfs \
  --namespace $NFS_NAMESPACE --create-namespace \
  --values values-nfs.yaml
```

The expected output is:

```
Release "jupyterhub-home-nfs" does not exist. Installing it now.
Pulled: ghcr.io/2i2c-org/jupyterhub-home-nfs/jupyterhub-home-nfs:1.2.0
Digest: sha256:6179de023c62a2e8e6e6ebb6a92c8210a1b7ac7a1470fcaf784d419e342c4618
NAME: jupyterhub-home-nfs
LAST DEPLOYED: Tue Jan 20 16:17:45 2026
NAMESPACE: jupyterhub-home-nfs
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
NFS Server has been deployed.
Using dynamic provisioning.

Your NFS server is now available inside the cluster at the following address:
home-nfs.jupyterhub-home-nfs.svc.cluster.local
```

Wait for the service to be ready, then capture the internal ClusterIP.

```bash
# Get the NFS Server ClusterIP
export NFS_CLUSTER_IP=$(kubectl get svc -n $NFS_NAMESPACE home-nfs -o jsonpath='{.spec.clusterIP}')
echo "NFS Cluster IP: $NFS_CLUSTER_IP"
```

## 4. Configure Kubernetes Storage (PV & PVC)

Create the PersistentVolume (pointing to the NFS IP) and the PersistentVolumeClaim (for JupyterHub to use).

```bash
# Generate PV and PVC configuration
cat <<EOF > jhub-nfs-pv-pvc.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jupyterhub-home-nfs
spec:
  capacity:
    storage: 1Mi # Dummy value, actual space determined by backend
  accessModes: [ReadWriteMany]
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
    - vers=4.1
    - proto=tcp
    - rsize=1048576
    - wsize=1048576
    - timeo=600
    - hard
    - retrans=2
    - noresvport
  nfs:
    server: $NFS_CLUSTER_IP
    path: /
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: home-nfs
  namespace: $JH_NAMESPACE
spec:
  accessModes: [ReadWriteMany]
  volumeName: jupyterhub-home-nfs
  storageClassName: ""
  resources:
    requests:
      storage: 1Mi
EOF

# Apply configuration
kubectl apply -f jhub-nfs-pv-pvc.yaml
```

## 5. (Optional) Initialize Shared Data Directory

If you want a shared folder accessible by all users (e.g., `/share`), run this one-time job to create the directory with the correct permissions.

```bash
# Generate Job configuration
cat <<EOF > init-shared-dir.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: init-home-nfs-shared
  namespace: $JH_NAMESPACE
spec:
  backoffLimit: 1
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: init
          image: busybox:1.36
          command:
            - /bin/sh
            - -c
            - |
              set -eu
              mkdir -p /mnt/_shared
              chown 1000:100 /mnt/_shared
              chmod 0775 /mnt/_shared
              # Set setgid so new files inherit group ownership (gid 100)
              chmod g+s /mnt/_shared
              ls -ld /mnt/_shared
          volumeMounts:
            - name: home-nfs
              mountPath: /mnt
      volumes:
        - name: home-nfs
          persistentVolumeClaim:
            claimName: home-nfs
EOF

# Run and cleanup the job
kubectl apply -f init-shared-dir.yaml
kubectl wait --for=condition=complete job/init-home-nfs-shared -n $JH_NAMESPACE --timeout=60s
kubectl logs -n $JH_NAMESPACE job/init-home-nfs-shared
kubectl delete -n $JH_NAMESPACE job/init-home-nfs-shared
```

## 6. Update JupyterHub Configuration

Add the following configuration to your JupyterHub Helm chart values (e.g., `config_standard_storage.yaml` or similar).

**For Home Directories + Shared Folder:**

```yaml
singleuser:
  storage:
    type: none
    extraVolumes:
      - name: home-nfs
        persistentVolumeClaim:
          claimName: home-nfs
    extraVolumeMounts:
      - name: home-nfs
        mountPath: /home/jovyan
        subPath: "{username}"
      # Optional: Shared Directory
      - name: home-nfs
        mountPath: /share
        subPath: "_shared"
```

## 7. Apply Changes

Upgrade JupyterHub to apply the new storage configuration.

```bash
# Example upgrade command
bash install_jhub.sh
```

## 8. Verify NFS mount from a single-user pod

Once connected to your single-user instance (for example, via the notebook terminal), run the following to create test files and verify mounts:

```bash
jovyan@jupyter-zonca:~$ touch test_home
jovyan@jupyter-zonca:~$ touch /share/test_shared
jovyan@jupyter-zonca:~$ mount | grep nfs
```

Example output showing both `/share` and `/home` as NFS mounts:

```
172.31.235.50:/_shared on /share type nfs4 (rw,relatime,vers=4.1,rsize=1048576,wsize=1048576,namlen=255,hard,noresvport,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=10.1.90.61,local_lock=none,addr=172.31.235.50)
172.31.235.50:/zonca on /home/jovyan type nfs4 (rw,relatime,vers=4.1,rsize=1048576,wsize=1048576,namlen=255,hard,noresvport,proto=tcp,timeo=600,retrans=2,sec=sys,clientaddr=10.1.90.61,local_lock=none,addr=172.31.235.50)
```

This confirms both the home directory and the shared directory are NFS mounts.
