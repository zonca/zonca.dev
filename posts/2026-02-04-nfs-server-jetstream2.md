---
categories:
- kubernetes
- jetstream
- jupyterhub
- linux
date: '2026-02-04'
layout: post
title: Deploy a NFS server to share data between JupyterHub users on Jetstream
---

This is an updated version of my [2023 tutorial](https://www.zonca.dev/posts/2023-02-06-nfs-server-kubernetes-jetstream) on deploying a NFS server to share data between JupyterHub users on Jetstream.

The recommended way to deploy Kubernetes on Jetstream is now using [Magnum and Cluster API](https://www.zonca.dev/posts/2024-12-11-jetstream_kubernetes_magnum.html). Please refer to that guide for the latest instructions on launching and managing Kubernetes clusters on Jetstream. This tutorial has been updated to reflect this change, but the NFS server deployment steps remain the same.

---

This tutorial shows how to create a data volume on Jetstream and share it using a NFS server to all JupyterHub users.  
All JupyterHub users run as the `jovyan` user, so each folder in the shared filesystem can be either read-only or writable by every user. The main concern is that a user could delete by mistake data of another user, however the users still have access to their own home folder.

## What you get (and what you do not)

* You get a **shared** filesystem mounted at `/share` inside each user pod.
* Users keep their **home directories** as usual; `/share` is additional.
* The NFS server is deployed **inside the cluster** as a pod with a persistent volume.

## Prerequisites

* A working Kubernetes cluster on Jetstream (Magnum + Cluster API).
* `kubectl` configured to talk to the cluster.
* JupyterHub deployed (Helm chart), or ready to deploy.
* This repository cloned locally.

# Deploy Kubernetes and JupyterHub

The recommended method is now [via Magnum and Cluster API](https://www.zonca.dev/posts/2024-12-11-jetstream_kubernetes_magnum.html).  
If you are still using Kubespray, see the [older tutorial](https://www.zonca.dev/posts/2023-02-06-nfs-server-kubernetes-jetstream).

# Deploy the NFS server

Clone as usual the repository with all the configuration files:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd nfs
```

By default the NFS server is configured both for reading and writing, and then using the filesystem permissions we can make some or all folders writable.

In `nfs_server.yaml` we use the image [itsthenetwork/nfs-server-alpine](https://hub.docker.com/r/itsthenetwork/nfs-server-alpine/), check their documentation for more configuration options.

We create a deployment with a replica number of 1 instead of creating directly a pod, so that in case servers are rebooted or a node dies, Kubernetes will take care of spawning another pod.

Some configuration options you might want to edit:

* I named the shared folder `/share`
* In case you are interested in sharing read-only, uncomment the `READ_ONLY` flag.
* In the persistent volume claim definition `create_nfs_volume.yaml`, modify the volume size (default is 10 GB)
* Select the right IP in `service_nfs.yaml` for either Magnum or Kubespray (or you can delete the line to be assigned an IP by Kubernetes), this is an arbitrary IP, it just needs to be in the same subnet of other Kubernetes services. You can find it looking at the output of `kubectl get services`. So you could have 2 NFS servers in the same cluster with 2 different IPs.
* You can check the IP range for a cluster using:
  
  ```bash
  kubectl cluster-info dump | grep service-cluster-ip-range
  ```

For Magnum clusters, the service CIDR usually looks like `172.24.0.0/13`. Pick an unused IP in that range and set it in:

* `nfs/service_nfs.yaml` (the Service `clusterIP`)
* `nfs/jupyterhub_nfs.yaml` (the NFS `server` IP)
* `nfs/test_nfs_mount.yaml` (the test pod `server` IP, optional but recommended)

If you remove the `clusterIP` line, Kubernetes will assign an IP automatically; in that case, you must read it with `kubectl get svc nfs-service` and then set that IP in `jupyterhub_nfs.yaml` and `test_nfs_mount.yaml`.

First we create the PersistentVolumeClaim:

```bash
kubectl create -f create_nfs_volume.yaml
```

then the service and the pod:

```bash
kubectl create -f service_nfs.yaml
kubectl create -f nfs_server.yaml
```

I separated them so that later on we more easily delete the NFS server, but keep all the data on the (potentially large) NFS volume:

```bash
kubectl delete -f nfs_server.yaml
```

## Check the NFS server is running

```bash
kubectl get pods -l role=nfs
kubectl get svc nfs-service
```

## Test the NFS server

Edit `test_nfs_mount.yaml` to set the right IP for the NFS server, then:

```bash
kubectl create -f test_nfs_mount.yaml
```

and access the terminal to test:

```bash
export N=default #set namespace
bash ../terminal_pod.sh test-nfs-mount
df -h
```

```
172.24.46.63:/  9.8G     0  9.8G   0% /share
```

We have the root user, we can use the terminal to copy or rsync data into the shared volume.
We can also create writable folders owned by the user `1000` which maps to `jovyan` in JupyterHub:

```bash
sh-4.2# mkdir readonly_folder
sh-4.2# touch readonly_folder/aaa
sh-4.2# mkdir writable_folder
sh-4.2# chown 1000:100 writable_folder
sh-4.2# ls -l /share
```

```
total 24
drwx------. 2 root root  16384 Jul 10 06:32 lost+found
drwxr-xr-x. 2 root root   4096 Jul 10 06:43 readonly_folder
drwxr-xr-x. 2 1000 users  4096 Jul 10 06:43 writable_folder
```

## Preserve the data volume across redeployments

The NFS data volume could contain a lot of data that you would want to preserve in case you need to completely tear down the Kubernetes cluster.

First we find out what is the ID of the `PersistentVolume` associated with the NFS volume:

```bash
kubectl get pv | grep nfs
```

```
pvc-ee1f02aa-11f8-433f-806f-186f6d622a30   10Gi       RWO            Delete           Bound    default/nfs-share-folder-claim   standard                5m55s
```

Then you can save the `PersistentVolume` and the `PersistentVolumeClaim` to YAML:

```bash
kubectl get pvc nfs-share-folder-claim -o yaml > existing_nfs_volume_claim.yaml
kubectl get pv pvc-ee1f02aa-11f8-433f-806f-186f6d622a30 -o yaml > existing_nfs_volume.yaml
```

Next we can delete the servers directly from Openstack, be careful not to delete the `PersistentVolume` or the `PersistentVolumeClaim` in Kubernetes or the underlying volume in Openstack will be deleted, also do not delete the namespace associated with those resources.

Finally redeploy everything, and instead of launching `create_nfs_volume.yaml`, we create first the `PersistentVolume` then the `PersistentVolumeClaim`:

```bash
kubectl create -f existing_nfs_volume.yaml
kubectl create -f existing_nfs_volume_claim.yaml
```

# Mount the shared filesystem on JupyterHub

Set the NFS server IP in `jupyterhub_nfs.yaml`, then add this line to `install_jhub.sh` (just before the last line, the file is located in the parent folder):

```bash
--values nfs/jupyterhub_nfs.yaml \
```

Then run `install_jhub.sh` to have the NFS filesystem mounted on all JupyterHub single user containers:

```bash
cd ..
bash install_jhub.sh
```

If JupyterHub was already running, make sure users stop and start their servers (or you restart user pods) so the new `/share` mount is picked up.

## Test in Jupyter

Now connect to JupyterHub and check in a terminal:

```bash
jovyan@jupyter-zonca2:/share$ pwd
/share
jovyan@jupyter-zonca2:/share$ whoami
jovyan
jovyan@jupyter-zonca2:/share$ touch readonly_folder/ccc
touch: cannot touch 'readonly_folder/ccc': Permission denied
jovyan@jupyter-zonca2:/share$
jovyan@jupyter-zonca2:/share$ touch writable_folder/ccc
jovyan@jupyter-zonca2:/share$ ls -l writable_folder/
total 0
-rw-r--r--. 1 jovyan root 0 Jul 10 06:50 ccc
```

## Troubleshooting

* If the mount hangs after you restart the NFS server, restart user pods so they remount the volume.
* If you see `bad option; ... /sbin/mount.<type> helper program`, install NFS client packages on nodes (Kubespray does this automatically).
* If the Service IP is wrong, you will see mount timeouts. Double-check `service_nfs.yaml` and `jupyterhub_nfs.yaml`.

# Expose a SSH server to copy data to the shared volume

See also the [2023 version of this tutorial for more details on the SSH server setup](https://www.zonca.dev/posts/2023-02-06-nfs-server-kubernetes-jetstream#expose-a-ssh-server-to-copy-data-to-the-shared-volume).
