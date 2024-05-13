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

Let's review the disk space occupied on a `m3.medium` worker with Ubuntu Minimal before running Ansible:

```
ubuntu@kubejetstream-k8s-node-1:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        58G  831M   58G   2% /
tmpfs            15G     0   15G   0% /dev/shm
tmpfs           5.9G  484K  5.9G   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs           3.0G  4.0K  3.0G   1% /run/user/1000
```

and after Kubernetes has being installed (from 800 MB to 6.8 GB):

```
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        58G  6.8G   52G  12% /
tmpfs            15G     0   15G   0% /dev/shm
tmpfs           5.9G  2.1M  5.9G   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/1a777fcf86f2e982969b83f78302bb19427470995262032dabe0384af26d202b/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/1331d819ef46d1d4ee94cd1faa58c0965e6c63b25d5fd69bb86e5b1769c9041e/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/6c6a245269c66d8a7ba69d31e590e9e807d17d19acfe9d2a251daa6b73127b78/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/2ed3c7de52d4c63e3a4df8e00486f4fcde91634891708e88aaf506256c2637c7/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/03b1e64d75fd951f7aefa050746717baa3811636636254132d4d11758c1a239c/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/bda38bc2b547cd4bdeca1aa7653fdf6483da2fbb8b69abbda2a35a3d93b982a8/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/3288593c52f5a21fec4be1222326d22f65612c61135e289addab1fe11b423334/shm
shm              64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/e9fd081509ca17913118ae4c69a80dc7cd50ea3a14469a90bc7e63ff5ff36c6f/shm
tmpfs           3.0G  4.0K  3.0G   1% /run/user/1000
```

Here is instead the comparison with the default Jetstream Ubuntu 22 image:

```
Filesystem                                                                                                                                                                                       Size  Used Avail Use% Mounted on
udev                                                                                                                                                                                              15G     0   15G   0% /dev
tmpfs                                                                                                                                                                                            3.0G  1.2M  3.0G   1% /run
/dev/sda1                                                                                                                                                                                         58G  8.8G   50G  16% /
tmpfs                                                                                                                                                                                             15G     0   15G   0% /dev/shm
tmpfs                                                                                                                                                                                            5.0M     0  5.0M   0% /run/lock
tmpfs                                                                                                                                                                                             15G     0   15G   0% /sys/fs/cgroup
/dev/loop0                                                                                                                                                                                        64M   64M     0 100% /snap/core20/2264
/dev/loop1                                                                                                                                                                                        92M   92M     0 100% /snap/lxd/24061
/dev/sda15                                                                                                                                                                                       105M  6.1M   99M   6% /boot/efi
/dev/loop2                                                                                                                                                                                        39M   39M     0 100% /snap/snapd/21465
tmpfs                                                                                                                                                                                            3.0G  4.0K  3.0G   1% /run/user/1000
xxxxxxxxxxxx          9.8T  493G  9.3T   5% /software
```

After having installed Kubernetes (from 8.8 GB to 13):

```
                      Size  Used Avail Use% Mounted on
udev                                                                                                                                                                                              15G     0   15G   0% /dev
tmpfs                                                                                                                                                                                            3.0G  3.0M  3.0G   1% /run
/dev/sda1                                                                                                                                                                                         58G   13G   46G  23% /
tmpfs                                                                                                                                                                                             15G     0   15G   0% /dev/shm
tmpfs                                                                                                                                                                                            5.0M     0  5.0M   0% /run/lock
tmpfs                                                                                                                                                                                             15G     0   15G   0% /sys/fs/cgroup
/dev/loop0                                                                                                                                                                                        64M   64M     0 100% /snap/core20/2264
/dev/loop1                                                                                                                                                                                        92M   92M     0 100% /snap/lxd/24061
/dev/sda15                                                                                                                                                                                       105M  6.1M   99M   6% /boot/efi
/dev/loop2                                                                                                                                                                                        39M   39M     0 100% /snap/snapd/21465
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/c0fc748f6469ded859983f821e8f167691b52a529bdc5e9a1269646ab1d1466f/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/5c853382c912e5cddd3dc6c726bce09fdbec753a89b60b6cf334214c34216cbc/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/1d5f384f212ecf62aafa44e8cd1dbabf5bc0fa28aeb10759da9e372494d82661/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/7d8ab2baa7b00523538b0921b0fc6c9d6aee1d121db8752fdb38bdce877784b7/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/1669d88641a2eafd7dc3c841e9f71ef6014d61bd986bc527e899b2b972837279/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/7d0ded66f7e811fdb0fee58dba737494aca1e36510f8291d7ebca5f5a3ad9824/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/4ec65ad53b8ab3391a04cc2442fa3278b114fbe4791ca1b24cc7db213be8f896/shm
shm                                                                                                                                                                                               64M     0   64M   0% /run/containerd/io.containerd.grpc.v1.cri/sandboxes/2bb33f80ec8afc1639dd57094dbbd9c59e97640cb10df557f68d3bd8582a10f1/shm
tmpfs                                                                                                                                                                                            3.0G  4.0K  3.0G   1% /run/user/1000
xxxxxxxxxxxx          9.8T  493G  9.3T   5% /software
```
