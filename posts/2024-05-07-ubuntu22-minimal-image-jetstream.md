---
categories:
- kubernetes
- jetstream2
date: '2024-05-07'
layout: post
slug: ubuntu22-minimal-image-jetstream
title: Ubuntu 22.04 Minimal on Jetstream

---

Virtual Machine images provided by the Jetstream team are fully fledged and therefore quite large.

Julien Chastang proposed the shift to a minimalist distribution to save disk space, resources and shorten deployment time, see [the relevant issue discussion on the Jetstream Gitlab organization](https://gitlab.com/jetstream-cloud/image-build-pipeline/-/issues/33).

We are mostly interested in replacing Ubuntu as the default image for our Kubespray developments, so we are [looking only at OS supported by Kubespray](https://github.com/kubernetes-sigs/kubespray?tab=readme-ov-file#supported-linux-distributions)

I previously tested the [container-specific Flatcar image](./2024-04-30-flatcar-image-jetstream.md), now testing Ubuntu 22.04 Minimal.

## Ubuntu 22.04 Minimal cloud image

Best features:

* Minimalist, image is less than `200 MB`
* It's Ubuntu, everyone is familiar with it
* Wide support (for example GPU virtualization used in Jetstream should work)
* Automatic updates

Downloaded from <https://cloud-images.ubuntu.com/minimal/releases/jammy/release/>

The name of the image is `Ubuntu2204Minimal`, it is set as a Community image ([script to load image to Openstack](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/vm_image/upload_image_ubuntu.sh):

```
openstack image list --community | grep Minimal
| 0fa9f3b4-d29f-4f68-a8a7-16bf44ffae69 | Ubuntu2204Minimal                                   | active      |
```

### GPU support

While Ubuntu potentially supports GPUs, the default image from Ubuntu does not.
We need [some specific customization](https://gitlab.com/jetstream-cloud/image-build-pipeline/-/blob/main/ansible/roles/js2-specific/tasks/Ubuntu-22.yml?ref_type=heads#L120-167) on the image.

Therefore we would need to create a GPU-specific minimal version that also includes the GPU drivers.

### Exosphere

The instance boots correctly on Exosphere, I can ssh into the instance as `exouser`.

It looks like Exosphere installs another 1.4GB of packages, so disk usage is higher compared to Horizon, anyway still tiny compared to a full-featured Ubuntu.

```
df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        20G  2.5G   17G  13% /
tmpfs           1.5G     0  1.5G   0% /dev/shm
tmpfs           600M  672K  599M   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs           300M  4.0K  300M   1% /run/user/1000
```

### Horizon

All normal, boots fine, usual login with the `ubuntu` user and the Openstack keypair.

Occupies minimal space:

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        20G  1.1G   19G   6% /
tmpfs           1.5G     0  1.5G   0% /dev/shm
tmpfs           600M  460K  599M   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs           300M  4.0K  300M   1% /run/user/1000
```

No warnings in `dmesg`.

### Kubespray

The real objective of this test is to deploy Kubernetes on Jetstream with this smaller image, following the [latest tutorial](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray) with minor modifications.

We can replace the official Ubuntu with the minimal image on Terraform by modifying in `cluster.tfvars`:

    image = "Ubuntu2204Minimal"

With the minimal image, Kubespray gives the error:

    modprobe: FATAL: Module ip_vs_sh not found in directory /lib/modules/5.15.0-1058-kvm\n"

the simple workaround is to set:

    kube_proxy_mode: iptables

instead of 

    kube_proxy_mode: ipvs

in `inventory/kubejetstream/group_vars/k8s_cluster/k8s-cluster.yml`


CPU Nodes are fine, but GPU nodes as expected do not work.

```
k get nodes -o wide
NAME                              STATUS     ROLES           AGE   VERSION   INTERNAL-IP   EXTERNAL-IP      OS-IMAGE             KERNEL-VERSION    CONTAINER-RUNTIME
kubejetstream-1                   Ready      control-plane   20m   v1.25.6   10.1.90.167   149.165.174.34   Ubuntu 22.04.4 LTS   5.15.0-1058-kvm   containerd://1.6.15
kubejetstream-k8s-node-nf-cpu-1   Ready      <none>          18m   v1.25.6   10.1.90.186   <none>           Ubuntu 22.04.4 LTS   5.15.0-1058-kvm   containerd://1.6.15
kubejetstream-k8s-node-nf-cpu-2   Ready      <none>          18m   v1.25.6   10.1.90.5     <none>           Ubuntu 22.04.4 LTS   5.15.0-1058-kvm   containerd://1.6.15
kubejetstream-k8s-node-nf-gpu-1   NotReady   <none>          18m   v1.25.6   10.1.90.230   <none>           Ubuntu 22.04.4 LTS   5.15.0-1058-kvm   containerd://1.6.15
```

Did not feel it was necessary to test JupyterHub, I'm confident it will work.
