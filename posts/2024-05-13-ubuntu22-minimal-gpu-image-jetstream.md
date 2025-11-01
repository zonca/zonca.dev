---
categories:
- kubernetes
- jetstream2
- jetstream
date: '2024-05-13'
layout: post
slug: ubuntu22-minimal-image-gpu-jetstream
title: Ubuntu 22.04 Minimal on Jetstream with GPU Support

---

Just notes on how to create a Ubuntu 22.04 image with GPU support

First create an image with Ubuntu Minimal from Horizon

Associate a floating IP and save it in an environment variable we will use later:

    export IP=xxx.xxx.xxx.xxx

The default kernel of Ubuntu minimal does not work with the Nvidia GPU proprietary driver,
it [gives the same error detailed in this issue](https://gitlab.com/jetstream-cloud/image-build-pipeline/-/issues/35)

Therefore we need to install another kernel with the headers, this occupies more than 2 GB because it grabs many other libraries:

    ssh ubuntu@$IP
    sudo apt update
    sudo apt install linux-image-generic-hwe-22.04
    sudo reboot
    sudo apt install linux-headers-$(uname -r) dkms

## Install the GPU driver

We can use the Ansible recipe created by the Jetstream team.
I created a branch which only installs the GPU driver.

    git clone --single-branch --branch ubuntu_minimal_gpu https://gitlab.com/zonca/jetstream-image-build-pipeline.git

Due to licensing issues, the NVIDIA GPU driver for Jetstream can only be accessed by members of the Jetstream team.
The files need to be copied to the `nvidia_driver` subfolder 

Execute `run.sh`

## Check

No need to reboot again, SSH into the instance, check:

```
nvidia-smi
Tue May 14 01:15:22 2024       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.129.03             Driver Version: 535.129.03   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  GRID A100X-8C                  On  | 00000000:00:06.0 Off |                    0 |
| N/A   N/A    P0              N/A /  N/A |      1MiB /  8192MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|  No running processes found                                                           |
+---------------------------------------------------------------------------------------+
```

## Disk usage

Just installing the kernel brings more than 2 GB of packages

```
df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        58G  4.7G   54G   9% /
tmpfs           7.4G     0  7.4G   0% /dev/shm
tmpfs           3.0G  704K  3.0G   1% /run
tmpfs           5.0M     0  5.0M   0% /run/lock
/dev/sda15      105M  6.1M   99M   6% /boot/efi
tmpfs           1.5G  4.0K  1.5G   1% /run/user/1000
```
