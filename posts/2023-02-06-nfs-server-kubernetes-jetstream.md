---
categories:
- kubernetes
- jetstream
- jupyterhub
- linux
date: '2023-02-06'
layout: post
title: Deploy a NFS server to share data between JupyterHub users on Jetstream

---

> **Update:** See the [2025 updated tutorial for deploying NFS on Jetstream with Kubernetes](https://www.zonca.dev/posts/2025-02-01-nfs-server-kubernetes-jetstream) for the latest instructions.

This tutorial is a minor update of <https://www.zonca.dev/posts/2020-07-10-nfs-server-kubernetes-jetstream>.

Also consider that a more robust and low-maintenance way of providing shared data volumes is [to rely on Manila shares provided by Jetstream 2, see the tutorial](https://www.zonca.dev/posts/2022-12-05-jetstream2-kubernetes-manila)

In this tutorial I'll show how to create a data volume on Jetstream and share it
using a NFS server to all JupyterHub users.
All JupyterHub users run as the `jovyan` user, therefore each folder in the shared
filesystem can be either read-only, or writable by every user.
The main concern is that a user could delete by mistake data of another user,
however the users still have access to their own home folder.

# Deploy Kubernetes and JupyterHub

I assume here you already have a deployment of JupyterHub on top of Kubernetes on Jetstream, currently, the recommended method [is via Kubespray 2.18](https://www.zonca.dev/posts/2022-03-30-jetstream2_kubernetes_kubespray).


# Deploy the NFS server

Clone as usual the repository with all the configuration files:

    git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
    cd nfs

By default the NFS server is configured both for reading and writing,
and then using the filesystem permissions we can make some or all folders writable.

In `nfs_server.yaml` we use the image [itsthenetwork/nfs-server-alpine](https://hub.docker.com/r/itsthenetwork/nfs-server-alpine/), check their documentation for more configuration options.

We create a deployment with a replica number of 1 instead of creating directly a pod, so that in case servers are rebooted
or a node dies, Kubernetes will take care of spawning another pod.

Some configuration options you might want to edit:

* I named the shared folder `/share`
* In case you are interested in sharing read-only, uncomment the `READ_ONLY` flag.
* In the persistent volume claim definition `create_nfs_volume.yaml`, modify the volume size (default is 10 GB)
* Select the right IP in `service_nfs.yaml` for either Magnum or Kubespray (or you can delete the line to be assigned an IP by Kubernetes), this is an arbitrary IP, it just needs to be in the same subnet of other Kubernetes services. You can find it looking at the output of `kubectl get services`. So you could have 2 NFS servers in the same cluster with 2 different IPs.

First we create the PersistentVolumeClaim:

    kubectl create -f create_nfs_volume.yaml

then the service and the pod:

    kubectl create -f service_nfs.yaml
    kubectl create -f nfs_server.yaml

I separated them so that later on we more easily delete the NFS server,
but keep all the data on the (potentially large) NFS volume:

    kubectl delete -f nfs_server.yaml

## Test the NFS server

Edit `test_nfs_mount.yaml` to set the right IP for the NFS server,
then:

    kubectl create -f test_nfs_mount.yaml

and access the terminal to test:

    export N=default #set namespace
    bash ../terminal_pod.sh test-nfs-mount
    df -h

    ...
    10.254.204.67:/       9.8G   36M  9.8G   1% /share
    ...

We have the root user, we can use the terminal to copy or rsync data into the shared volume.
We can also create writable folders owned by the user `1000` which maps to `jovyan`
in JupyterHub:

```
sh-4.2# mkdir readonly_folder
sh-4.2# touch readonly_folder/aaa
sh-4.2# mkdir writable_folder
sh-4.2# chown 1000:100 writable_folder
sh-4.2# ls -l /share
total 24
drwx------. 2 root root  16384 Jul 10 06:32 lost+found
drwxr-xr-x. 2 root root   4096 Jul 10 06:43 readonly_folder
drwxr-xr-x. 2 1000 users  4096 Jul 10 06:43 writable_folder
```

## Preserve the data volume across redeployments

The NFS data volume could contain a lot of data that you would want to preserve in case you
need to completely tear down the Kubernetes cluster.

First we find out what is the ID of the `PersistentVolume` associated with the NFS volume:

```
kubectl get pv | grep nfs
pvc-ee1f02aa-11f8-433f-806f-186f6d622a30   10Gi       RWO            Delete           Bound    default/nfs-share-folder-claim   standard                5m55s
```

Then you can save the `PersistentVolume` and the `PersistentVolumeClaim` to YAML:

```
kubectl get pvc nfs-share-folder-claim -o yaml > existing_nfs_volume_claim.yaml
kubectl get pv pvc-ee1f02aa-11f8-433f-806f-186f6d622a30 -o yaml > existing_nfs_volume.yaml
```

Next we can delete the servers directly from Openstack, be careful not to delete the `PersistentVolume` or
the `PersistentVolumeClaim` in Kubernetes or the underlying volume in Openstack will be deleted, also
do not delete the namespace associated with those resources.

Finally redeploy everything,
and instead of launching `create_nfs_volume.yaml`, we create first the `PersistentVolume` then the `PersistentVolumeClaim`:

```
kubectl create -f existing_nfs_volume.yaml
kubectl create -f existing_nfs_volume_claim.yaml
```

# Mount the shared filesystem on JupyterHub

Set the NFS server IP in `jupyterhub_nfs.yaml`, then add this line to `install_jhub.sh` (just before the last line, the file is located in the parent folder):

    --values nfs/jupyterhub_nfs.yaml \

Then run `install_jhub.sh` to have the NFS filesystem mounted on all JupyterHub single user containers:

    cd ..
    bash install_jhub.sh

## Test in Jupyter

Now connect to JupyterHub and check in a terminal:

```
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

# Expose a SSH server to copy data to the shared volume

The main restriction is that the only way to copy data to the read-only folders
is through Kubernetes.
Next we will deploy a SSH server which mounts the container and whose user can
become root to manage permissions and copy data.
We will also expose this service externally so that people with the right
SSH certificate can login.

First edit `ssh_server.yaml`:

* Set the NFS server IP
* Set the string of the `PUBLIC_KEY` to the SSH key which will be able to access
* Optionally, you can modify username and ports
* See the [`linuxserver/openssh-server` documentation for other options](https://hub.docker.com/r/linuxserver/openssh-server)

Deploy the pod (also here we create a Deployment with a replica number of 1):

    kubectl create -f ssh_server.yaml

Open the Horizon interface, go to "Security groups", open the `$CLUSTER-k8s-master` group,
which we use to open ports on the master instance, and add a new rule to open port
`30022` for Ingress TCP traffic.

## Test the SSH server

From a machine external to Jetstream:

    ssh -i path/to/private/key -p 30022 datacopier@js-xxx-xxx.jetstream-cloud.org

```
Welcome to OpenSSH Server

ssh-server:~$ whoami
datacopier
ssh-server:~$ sudo su
ssh-server:/config# whoami
root
ssh-server:/config# cd /share
ssh-server:/share# ls
lost+found  readonly_folder  writable_folder
ssh-server:/share# touch readonly_folder/moredata
ssh-server:/share#
```

# Troubleshooting

* Consider that if you reboot or re-create the NFS server, the user pods need to be restarted, otherwise the NFS volume hangs.
* If you get the error `bad option; for several filesystems (e.g. nfs, cifs) you might need a /sbin/mount.<type> helper program.`, it means you do not have a NFS client on the host. Make sure you install the right package, for Ubuntu/Debian it is `nfs-common`. This should be taken care of by Kubespray if using my deployment tutorial.
