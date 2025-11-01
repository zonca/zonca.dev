---
categories:
- jetstream2
- jupyterhub
- kubernetes
- jetstream
layout: post
date: '2024-02-08'
title: Deploy Kubernetes on Jetstream 2 with GPU support

---

This work has been supported by Indiana University and is cross-posted on the <a href="https://docs.jetstream-cloud.org/general/k8sgpu" rel="canonical">Jetstream 2 official documentation website</a>.

Thanks to work by [Ana Espinoza](https://github.com/ana-v-espinoza), the standard recipe now supports GPUs out of the box and also supports hybrid clusters where some nodes are standard CPU nodes and some nodes have GPU.

The Jetstream 2 cloud includes [90 GPU nodes with 4 NVIDIA A100 each](https://docs.jetstream-cloud.org/overview/config/){target=\_blank}.
If we want to leverage the GPUs inside Kubernetes pods, for example JupyterHub users, we both need to have a GPU-enabled ContainerD runtime and a compatible Docker image based off NVIDIA images.

## Deploy Kubernetes with NVIDIA runtime

Kubespray has built-in support for NVIDIA runtime, in a previous version of this tutorial I had a specific branch dedicated to supporting a cluster where all worker nodes had GPUs.

Therefore it is just a matter of following the [standard Kubespray deployment tutorial](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray){target=\_blank}, configuring properly the variables in `cluster.tfvars` following the comments available there.
In summary, for a GPU-only cluster we only set:

     supplementary_node_groups = "gpu-node"

Instead for a hybrid cluster we need to set the number of worker nodes to zero and instead list explicitly all the nodes we want Terraform to create, specifying their name and if they should have a GPU or not.

If we deploy a hybrid GPU-CPU cluster in the default configuration from `cluster.tfvars`, we will have 2 CPU and 2 GPU nodes:

```
> kubectl get nodes
NAME                              STATUS   ROLES           AGE   VERSION
kubejetstream-1                   Ready    control-plane   44m   v1.25.6
kubejetstream-k8s-node-nf-cpu-1   Ready    <none>          43m   v1.25.6
kubejetstream-k8s-node-nf-cpu-2   Ready    <none>          43m   v1.25.6
kubejetstream-k8s-node-nf-gpu-1   Ready    <none>          43m   v1.25.6
kubejetstream-k8s-node-nf-gpu-2   Ready    <none>          43m   v1.25.6
```

Next we need to install the `k8s-device-plugin`, at the moment it is just necessary to execute:

    kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.4/nvidia-device-plugin.yml

However, make sure you check the latest [`k8s-device-plugin` documentation](https://github.com/NVIDIA/k8s-device-plugin){target=\_blank}.

For testing, you can run a simple GPU job, this is requesting a GPU, so it will automatically run on a GPU node if we have an hybrid cluster:

```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: gpu-pod
spec:
  restartPolicy: Never
  containers:
    - name: cuda-container
      image: nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda10.2
      resources:
        limits:
          nvidia.com/gpu: 1 # requesting 1 GPU
  tolerations:
  - key: nvidia.com/gpu
    operator: Exists
    effect: NoSchedule
EOF
```

and check the logs:

    kubectl logs gpu-pod

The output should be:

```
[Vector addition of 50000 elements]
Copy input data from the host memory to the CUDA device
CUDA kernel launch with 196 blocks of 256 threads
Copy output data from the CUDA device to the host memory
Test PASSED
Done
```

## Access GPUs from JupyterHub

A Docker image derived from the NVIDIA Tensorflow image is available [on DockerHub as `zonca/nvidia-tensorflow-jupyterhub`](https://hub.docker.com/r/zonca/nvidia-tensorflow-jupyterhub){target=\_blank}, the relevant [Dockerfile is available on Github](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/gpu/nvidia-tensorflow-jupyterhub/Dockerfile){target=\_blank}.

Also notice that this is configured to run JupyterHub `3.0.0` which should be used in conjunction with the Zero to JupyterHub Helm chart version `2.0.0`.

Then it is just a matter of modifying the `install_jhub.sh` script to pickup the additional configuration file by adding:

    --values gpu/jupyterhub_gpu.yaml

Notice that some Docker images designed for GPU do not work on CPU, for example the official `tensorflow` image (as tested in February 2024). The image used here works fine on either type of node.

## Test execution on GPU

For testing, I have modified the Tensorflow tutorial for beginners to run on GPU, it is available [in this Gist](https://gist.github.com/zonca/3da7896544da9881fe9081a441964a26){target=\_blank}.

You can download it to your local machine and upload it to the GPU-enabled single user instance on Jetstream.

During execution, the 3rd cell should show the available GPU device:

    [PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]

then the Notebook should execute to completion with no errors, printing for each operation the device which executed it, i.e. the GPU. After checking that commands are properly executed on GPU, you should comment out `tf.debugging.set_log_device_placement(True)` to speed-up training.

## Hybrid cluster: avoid CPU pods running on GPU nodes

One problem of the above configuration is that users requesting a CPU pod could be spawned on a GPU node, therefore occupying resources that might be useful for GPU users.
A possible fix is to taint all the GPU nodes creating a simple script to apply this command to all GPU nodes:

    kubectl taint node kubejetstream-k8s-node-nf-gpu-1 "gpu=true:NoSchedule"

Then, I have already added a toleration to the GPU profile of `jupyterhub_gpu.yaml`, so now only users that select the GPU profile will spwan on GPU nodes.
