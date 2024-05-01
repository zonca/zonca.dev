---
categories:
- kubernetes
- jetstream2
date: '2024-04-30'
layout: post
slug: flatcar-image-jetstream
title: Flatcar Container Linux on Jetstream

---

Virtual Machine images provided by the Jetstream team are fully fledged and therefore quite large.

Julien Chastang proposed the shift to a minimalist distribution to save disk space, resources and shorten deployment time, see [the relevant issue discussion on the Jetstream Gitlab organization](https://gitlab.com/jetstream-cloud/image-build-pipeline/-/issues/33).

We are mostly interested in replacing Ubuntu as the default image for our Kubespray developments, so we are [looking only at OS supported by Kubespray](https://github.com/kubernetes-sigs/kubespray?tab=readme-ov-file#supported-linux-distributions)

## Flatcar Container Linux

Best features:

* Minimalist, image is only `450 MB`
* OS specifically for running containers
* Automatic unsupervised updates

See [their docs about deploying on Openstack](https://www.flatcar.org/docs/latest/installing/cloud/openstack/), uploading to Jetstream worked out of the box using [this script](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/vm_image/upload_image.sh).

### Exosphere

The instance boots correctly on Exosphere, I can ssh into the instance as `exouser`, however, on the Dashboard the image is stuck in the "Building" phase and a passphrase is not assigned to the user.
Trying to run Docker commands fails for permission issues and without password cannot `sudo`.

### Horizon

The instance boots fine on Horizon as well, I can ssh with the user `core` using the keypair injected by Openstack.
`core` by default can execute Docker commands, so can test with:

    docker run --rm -p 80:80 -d nginx

and `curl localhost`.

Occupies minimal space:

```
df -h
Filesystem      Size  Used Avail Use% Mounted on
devtmpfs        4.0M     0  4.0M   0% /dev
tmpfs           1.5G     0  1.5G   0% /dev/shm
tmpfs           596M  556K  595M   1% /run
/dev/sda9        17G  215M   16G   2% /
sysext          1.5G   12K  1.5G   1% /usr
overlay          17G  215M   16G   2% /etc
/dev/sda6       128M  940K  123M   1% /oem
tmpfs           1.5G     0  1.5G   0% /media
tmpfs           1.5G     0  1.5G   0% /tmp
/dev/sda1       127M   59M   68M  47% /boot
tmpfs           298M     0  298M   0% /run/user/500
```

The update machinery executes without errors:

```
core@flatcarhorizon ~ $ update_engine_client -update
I0501 05:10:49.327685  1763 update_engine_client.cc:251] Initiating update check and install.
I0501 05:10:49.330926  1763 update_engine_client.cc:256] Waiting for update to complete.
LAST_CHECKED_TIME=1714540249
PROGRESS=0.000000
CURRENT_OP=UPDATE_STATUS_IDLE
NEW_VERSION=0.0.0
NEW_SIZE=0
I0501 05:10:54.688055  1763 update_engine_client.cc:194] No update available
```

Both in Horizon and Exosphere I get a warning in `dmesg`, [this is fine](https://gunshowcomic.com/648):

    [   54.197042] BTRFS warning: duplicate device /dev/sda3 devid 1 generation 33 scanned by (udev-worker) (1659)

### Kubespray

The real objective of this test is to deploy Kubernetes on Jetstream using Flatcar, following the [latest tutorial](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray) with minor modifications.

We can replace Ubuntu with Flatcar on Terraform by modifying in `cluster.tfvars`:

    image = "FlatcarContainerLinux-3815-2-2"
    ssh_user = "core"

Then in Ansible, following [the Kubespray docs](https://github.com/kubernetes-sigs/kubespray/blob/master/docs/flatcar.md), we need to set:

    bin_dir: /opt/bin

at the top of `group_vars/all/all.yml`.

Deployment time of 1 master node and 2 workers 21 minutes.

Detailed timing from Ansible:

```
kubernetes-apps/ansible : Kubernetes Apps | Lay Down CoreDNS templates -------------------------------- 33.72s
kubernetes-apps/ingress_controller/ingress_nginx : NGINX Ingress Controller | Create manifests -------- 33.61s
kubernetes/kubeadm : Join to cluster ------------------------------------------------------------------ 27.87s
kubernetes-apps/csi_driver/cinder : Cinder CSI Driver | Generate Manifests ---------------------------- 23.79s
kubernetes-apps/ansible : Kubernetes Apps | Start Resources ------------------------------------------- 22.23s
kubernetes-apps/ingress_controller/ingress_nginx : NGINX Ingress Controller | Apply manifests --------- 16.56s
kubernetes-apps/external_cloud_controller/openstack : External OpenStack Cloud Controller | Generate Manifests -- 13.77s
kubernetes-apps/csi_driver/cinder : Cinder CSI Driver | Apply Manifests ------------------------------- 12.62s
kubernetes/control-plane : kubeadm | Initialize first master ------------------------------------------ 10.90s
kubernetes-apps/csi_driver/csi_crd : CSI CRD | Generate Manifests ------------------------------------- 10.34s
kubernetes-apps/ansible : Kubernetes Apps | Lay Down nodelocaldns Template ---------------------------- 10.23s
download : download_container | Download image if required --------------------------------------------- 9.86s
kubernetes/preinstall : Ensure kube-bench parameters are set ------------------------------------------- 9.70s
etcd : reload etcd ------------------------------------------------------------------------------------- 8.40s
kubernetes/preinstall : Create kubernetes directories -------------------------------------------------- 8.25s
etcd : Check certs | Register ca and etcd admin/member certs on etcd hosts ----------------------------- 8.14s
etcd : Check certs | Register ca and etcd admin/member certs on etcd hosts ----------------------------- 7.86s
kubernetes-apps/snapshots/snapshot-controller : Snapshot Controller | Generate Manifests --------------- 6.93s
network_plugin/flannel : Flannel | Create Flannel manifests -------------------------------------------- 6.91s
kubernetes/control-plane : Renew K8S control plane certificates monthly 1/2 ---------------------------- 6.77s
```

Nodes running happily with Flatcar:

```
k get nodes -o wide
NAME                       STATUS   ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP       OS-IMAGE                                             KERNEL-VERSION   CONTAINER-RUNTIME
kubejetstream-1            Ready    control-plane   35m   v1.25.6   10.1.90.173   149.xxx.xxx.xxx   Flatcar Container Linux by Kinvolk 3815.2.2 (Oklo)   6.1.85-flatcar   containerd://1.6.15
kubejetstream-k8s-node-1   Ready    <none>          33m   v1.25.6   10.1.90.183   149.xxx.xxx.xxx   Flatcar Container Linux by Kinvolk 3815.2.2 (Oklo)   6.1.85-flatcar   containerd://1.6.15
kubejetstream-k8s-node-2   Ready    <none>          33m   v1.25.6   10.1.90.19    149.xxx.xxx.xxx   Flatcar Container Linux by Kinvolk 3815.2.2 (Oklo)   6.1.85-flatcar   containerd://1.6.15
```

Also tested deploying successfully JupyterHub, enjoy!
