---
aliases:
- /2020/05/jetstream_kubernetes_magnum
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2020-05-21'
layout: post
slug: kubernetes-jupyterhub-jetstream-magnum
title: Deploy Kubernetes and JupyterHub on Jetstream with Magnum

---

This tutorial deploys Kubernetes on Jetstream with Magnum and then
JupyterHub on top of that using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/).

The Jetstream team recently enabled the Cluster API on the Openstack deployment as the backend for Openstack Magnum to launch Kubernetes clusters. Clusters created via Magnum have several advantages compared to our [previous deployment via Kubespray](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray):

* **Quicker**: instead of configuring each VM with Ansible, VMs are launched with pre-prepared images, so spin up within minutes
* **Integrates with load balancer**: it relies on the Openstack load balancer service, so we can easily support multiple master nodes and if one of them fails, other nodes can handle incoming requests.
* **Autoscaling**: it natively supports Cluster Autoscaling, so that worker nodes are created and destroyed based on load.

## Setup access to the Jetstream API

First install the OpenStack and Magnum client:

    pip install python-openstackclient python-magnumclient

Jetstream recently updated permissions, so even if you have an already working app credential, create another one 'Unrestricted (dangerous)' application credential with all permissions, including the "loadbalancer" permission, in the project where you will be creating the cluster, and source it to expose the environment variables in your local environment where you'll be running the openstack commands.


## Create the cluster with Magnum

Check out the cluster templates available:

    openstack coe cluster template list

List clusters (initially empty):

    openstack coe cluster list

As usual, checkout the repository with all the configuration files on the machine you will use the Jetstream API from, typically your laptop.

    git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
    cd jupyterhub-deploy-kubernetes-jetstream
    cd kubernetes_magnum

A cluster can be created with:

    export K8S_CLUSTER_NAME=k8s
    bash create_cluster.sh

See inside the file for the most commonly used parameters.

The cluster consumes resources when active, it can be switched off with:

    bash delete_cluster.sh

Consider this is deleting all Jetstream virtual machines and data that could be stored in JupyterHub.

List clusters again. You should see your cluster now. Once status is `CREATE_COMPLETE`, get the Kubernetes config file:

    eval $(openstack coe cluster config $K8S_CLUSTER_NAME)
    chmod 600 config

`eval` is used because the command returns the correct `export KUBECONFIG` statement.

Now the usual `kubectl` commands should work:

```bash
> kubectl get nodes
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-mbbffjfee7zs-control-plane-6rn2z          Ready    control-plane   2m22s   v1.30.4
k8s-mbbffjfee7zs-control-plane-nw4cc          Ready    control-plane   41s     v1.30.4
k8s-mbbffjfee7zs-control-plane-w9jln          Ready    control-plane   5m8s    v1.30.4
k8s-mbbffjfee7zs-default-worker-jb5lm-gvvjm   Ready    <none>          2m21s   v1.30.4
```

## Scale manually

List the node groups:

    openstack coe nodegroup list $K8S_CLUSTER_NAME

Increase number of worker nodes:

    openstack coe cluster resize --nodegroup default-worker $K8S_CLUSTER_NAME 3

Confirm that there are 3 worker nodes: kubectl get nodes

## Enable the autoscaler

We can enable the autocaler setting the `max_node_count` property on the `default-worker` nodegroup:

    openstack coe nodegroup update $K8S_CLUSTER_NAME default-worker replace /max_node_count=5

Now we can test the autoscaler,

```bash
kubectl create -f high_mem_dep.yaml
kubectl scale deployment high-memory-deployment --replicas 6
```

In the log of the pods we can notice that this triggered creation of more nodes:

      Normal   TriggeredScaleUp        113s  cluster-autoscaler  pod triggered scale-up: [{MachineDeployment/magnum-83bd0e70b4ba4cd092c2fb82b1ce06fb/k8s-mbbffjfee7zs-default-worker 2->5 (max: 5)}]

And in fact, within a couple of minutes:

    > kubectl get nodes
    NAME                                          STATUS   ROLES           AGE    VERSION
    k8s-mbbffjfee7zs-control-plane-6rn2z          Ready    control-plane   26m    v1.30.4
    k8s-mbbffjfee7zs-control-plane-nw4cc          Ready    control-plane   25m    v1.30.4
    k8s-mbbffjfee7zs-control-plane-w9jln          Ready    control-plane   29m    v1.30.4
    k8s-mbbffjfee7zs-default-worker-jb5lm-cpsqx   Ready    <none>          94s    v1.30.4
    k8s-mbbffjfee7zs-default-worker-jb5lm-dqww9   Ready    <none>          91s    v1.30.4
    k8s-mbbffjfee7zs-default-worker-jb5lm-gvvjm   Ready    <none>          26m    v1.30.4
    k8s-mbbffjfee7zs-default-worker-jb5lm-pmptm   Ready    <none>          5m4s   v1.30.4
    k8s-mbbffjfee7zs-default-worker-jb5lm-sss6b   Ready    <none>          97s    v1.30.4

We still have 1 pending pod but the autoscaler has a limit of 5 workers, so it won't launch other nodes:

    > kubectl get pods
    NAME                                     READY   STATUS    RESTARTS   AGE
    high-memory-deployment-85785c87d-4zbrv   1/1     Running   0          4m5s
    high-memory-deployment-85785c87d-5xtvq   0/1     Pending   0          4m5s
    high-memory-deployment-85785c87d-6ds4c   1/1     Running   0          4m5s
    high-memory-deployment-85785c87d-qhclc   1/1     Running   0          4m5s
    high-memory-deployment-85785c87d-qxlf2   1/1     Running   0          4m5s
    high-memory-deployment-85785c87d-rk8sb   1/1     Running   0          5m8s

## Test Persistent Volumes

Magnum comes with a default storage class for persistent volumes which relies on Openstack Cinder, we can test with a simple pod:

    kubectl create -f ../alpine-persistent-volume.yaml
    kubectl describe pod alpine

## Install JupyterHub

Finally, we can go back to the root of the repository and install JupyterHub, first create the secrets file:

    bash create_secrets.sh

    bash configure_helm_jupyterhub.sh
    bash install_jhub.sh

After a few minutes, you can find out what is the public IP created by the Openstack Load Balancer service for JupyterHub:

    kubectl -n jhub get service proxy-public

We can connect with our browser to that IP and verify if JupyterHub is working, however we cannot login given we do not have a domain setup.

## Configure a subdomain

Jetstream also provides subdomains to each project as:

    xxxxxx.$PROJ.projects.jetstream-cloud.org
    
where `PROJ` is the ID of your Jestream 2 allocation:

    export PROJ="xxx000000" 

Given the public IP of the JupyterHub service we tested before:

    openstack recordset create  $PROJ.projects.jetstream-cloud.org. k8s --type A --record $IP --ttl 3600

## Setup HTTPS

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml

Still working on getting Cert-Manager working with Load Balancer instead of Ingress

## Issues and feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/) to report any issue or give feedback.
