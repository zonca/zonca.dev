`group_vars/all/docker.yml`
Uncomment
    docker_storage_options: -s overlay2

it is required by kubespray nvidia

| NVIDIA-SMI 510.85.02    Driver Version: 510.85.02    CUDA Version: 11.6     |

uncommented nvidia in `group_vars/k8s_cluster/k8s-cluster.yml`
and added the node name 

https://github.com/NVIDIA/k8s-device-plugin#configure-containerd
