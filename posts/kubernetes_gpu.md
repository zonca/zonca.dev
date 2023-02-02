---
categories:
- jetstream2
- jupyterhub
layout: post
date: '2023-01-23'
title: Deploy Kubernetes on Jetstream 2 with GPU support

---

The Jetstream 2 cloud system includes 90 GPU nodes with 4 NVIDIA A100 each](https://docs.jetstream-cloud.org/overview/config/)

`group_vars/all/docker.yml`

it is required by kubespray nvidia

| NVIDIA-SMI 510.85.02    Driver Version: 510.85.02    CUDA Version: 11.6     |

uncommented nvidia in `group_vars/k8s_cluster/k8s-cluster.yml`
and added the node name 

https://github.com/NVIDIA/k8s-device-plugin#configure-containerd
