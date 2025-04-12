---
categories:
- kubernetes
- jetstream
- jupyterhub
date: '2024-12-11'
layout: post
slug: kubernetes-jupyterhub-jetstream-magnum-2024
title: Deploy Kubernetes and JupyterHub on Jetstream with Magnum and Cluster API

---

This tutorial deploys Kubernetes on Jetstream with Magnum and then
JupyterHub on top of that using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/).

The Jetstream team recently enabled the Cluster API on the Openstack deployment as the backend for Openstack Magnum to launch Kubernetes clusters. Clusters created via Magnum have several advantages compared to our [previous deployment via Kubespray](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray):

* **Quicker**: instead of configuring each VM with Ansible, VMs are launched with pre-prepared images, so deploys in about 10 minutes and scales in about 5 minutes.
* **Integrates with load balancer**: it relies on the Openstack load balancer service, so we can easily support multiple master nodes and if one of them fails, other nodes can handle incoming requests.
* **Autoscaling**: it natively supports Cluster Autoscaling, so that worker nodes are created and destroyed based on load.

## Prerequisites

First install the OpenStack and Magnum client:

    pip install python-openstackclient python-magnumclient

This tutorial used openstack 6.1.0 and python-magnumclient 4.7.0.

And create an updated app credential for the client to access the API.
Jetstream recently updated permissions, so even if you have an already working app credential, create another one 'Unrestricted (dangerous)' application credential with all permissions, including the "loadbalancer" permission, in the project where you will be creating the cluster, and source it to expose the environment variables in your local environment where you'll be running the openstack commands.

Once we have launched a cluster, we will want to manage it using standard Kubernetes tooling, any recent version should work:

* `kubectl`: see <https://kubernetes.io/docs/tasks/tools/>, this tutorial used 1.26
* `helm`: see <https://helm.sh/docs/intro/install/>, this tutorial used 3.8.1

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

See inside the file for the most commonly used parameters, the script awaits for the cluster to complete deployment successfully, it should take about 10 minutes.

The cluster consumes resources when active, it can be switched off with:

    bash delete_cluster.sh

Consider this is deleting all Jetstream virtual machines and data that could be stored in JupyterHub.

Once status is `CREATE_COMPLETE`, get the Kubernetes config file in the current folder:

    openstack coe cluster config $K8S_CLUSTER_NAME --force
    export KUBECONFIG=$(pwd)/config
    chmod 600 config

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

Confirm that there are 3 worker nodes:

    kubectl get nodes

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

## Install NGINX controller

In principle we do not need an Ingress because the Openstack Load Balancer can directly route traffic to JupyterHub. However, there is no way of getting a HTTPS certificate without an Ingress.

Install the NGINX Ingress controller with:

```bash
helm upgrade --install ingress-nginx ingress-nginx \
             --repo https://kubernetes.github.io/ingress-nginx \
             --namespace ingress-nginx --create-namespace
```



## Install JupyterHub

Finally, we can go back to the root of the repository and install JupyterHub, first create the secrets file:

    bash create_secrets.sh

The default `secrets.yaml` file assumes you are deploying on a `projects.jetstream-cloud.org` subdomain, if that is not the case, edit the file with your own domain.

    bash configure_helm_jupyterhub.sh
    bash install_jhub.sh


## Configure a subdomain

Jetstream also provides subdomains to each project as:

    xxxxxx.$PROJ.projects.jetstream-cloud.org
    
where `PROJ` is the ID of your Jestream 2 allocation:

    export PROJ="xxx000000" 

Given the public IP of the NGINX ingress controller:

    kubectl get svc -n ingress-nginx ingress-nginx-controller

If you have a custom subdomain, you can configure an A record that points to the `EXTERNAL-IP` of the service, otherwise use Openstack to create a record:

    openstack recordset create  $PROJ.projects.jetstream-cloud.org. k8s --type A --record $IP --ttl 3600

Access JupyterHub at <https://k8s.$PROJ.projects.jetstream-cloud.org>.

## Setup HTTPS

Finally, to get a valid certificate, deploy `cert-manager` with:

    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml

and a Cluster Issuer:

    kubectl create -f ../setup_https/https_cluster_issuer.yml

Now your deployment should have a valid HTTPS certificate.

## Issues and feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/) to report any issue or give feedback.
