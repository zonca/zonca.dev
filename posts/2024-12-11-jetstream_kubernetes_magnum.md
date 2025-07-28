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

**UPDATED 2025-04-14**: Added echo test  
**UPDATED 2025-04-12**: Set a fixed IP address for the NGINX Ingress controller.

This guide demonstrates how to deploy Kubernetes on Jetstream with Magnum and then install JupyterHub on top using [zero-to-jupyterhub](https://zero-to-jupyterhub.readthedocs.io/). Jetstream recently enabled the Cluster API on its OpenStack deployment as the backend for Magnum, making it faster and more straightforward to launch Kubernetes clusters.

## Advantages of Magnum-Based Deployments

Magnum-based clusters offer several benefits over [Kubespray](https://www.zonca.dev/posts/2023-07-19-jetstream2_kubernetes_kubespray):

- **Faster Deployment**: Instead of using Ansible to configure each VM, Magnum uses pre-prepared images. Clusters typically deploy in about 10 minutes, and workers can scale up in around 5 minutes.  
- **Load Balancer Integration**: The OpenStack load balancer service provides easy support for multiple master nodes, ensuring high availability.  
- **Autoscaling**: The Cluster Autoscaler can automatically add or remove worker nodes based on workload.

## Prerequisites

1. **Install OpenStack and Magnum Clients**:
   ```bash
   pip install python-openstackclient python-magnumclient python-octaviaclient
   ```

The OpenStack client is used to create and manage the cluster, the Magnum client is used to create the cluster template, and the Octavia client is used to manage the load balancer.

This tutorial used OpenStack 6.1.0, python-magnumclient 4.7.0, and python-octaviaclient 3.3.0.

2. **Create an Updated App Credential**:
    Create an updated app credential for the client to access the API through [Horizon](https://js2.jetstream-cloud.org/) under [Identity - Application credentials](https://js2.jetstream-cloud.org/identity/application_credentials/).
    Jetstream recently updated permissions, so even if you have an already working app credential, create another one 'Unrestricted (dangerous)' application credential with all permissions, including the "loadbalancer" permission, in the project where you will be creating the cluster, download the `openrc` file and source it to expose the environment variables in your local environment where you'll be running the openstack commands.

3. **Install Kubernetes Tooling**:
   Once the cluster is launched, manage it using standard Kubernetes tools. Any recent version should work:
   - `kubectl`: see <https://kubernetes.io/docs/tasks/tools/>, this tutorial used 1.26.
   - `helm`: see <https://helm.sh/docs/intro/install/>, this tutorial used 3.8.1.

## Create the Cluster with Magnum

Check out the cluster templates available:

```bash
openstack coe cluster template list
```

List clusters (initially empty):

```bash
openstack coe cluster list
```

As usual, checkout the repository with all the configuration files on the machine you will use the Jetstream API from, typically your laptop:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd jupyterhub-deploy-kubernetes-jetstream
cd kubernetes_magnum
```

A cluster can be created with:

```bash
export K8S_CLUSTER_NAME=k8s
bash create_cluster.sh
```

See inside the file for the most commonly used parameters. The script awaits for the cluster to complete deployment successfully, which should take about 10 minutes.

At this point, decide if you prefer to use autoscaling or not. Autoscaling means that the cluster will automatically add (up to a predefined maximum) or remove worker nodes based on the load on Kubernetes. This is the recommended way to run JupyterHub, as it will automatically scale up and down based on the number of users and their activity. With manual scaling, you run a command to add or remove nodes. Scaling always refers to the worker nodes; the control plane cannot be scaled, so we recommend using 3 control plane nodes for redundancy.

In case of errors, you can check the error message with:

    openstack coe cluster show k8s -f json | jq '.status_reason'

The cluster consumes resources when active, it can be switched off with:

The first time this is executed, and then again if not executed for a while, it will take a lot more time to deploy, between 2 and 2.5 hours, probably because the images are not cached in the OpenStack cloud. After that first execution, it should regularly deploy in 10 minutes.

The cluster consumes resources when active. It can be switched off with:

```bash
bash delete_cluster.sh
```

Consider this deletes all Jetstream virtual machines and data that could be stored in JupyterHub.

Once the status is `CREATE_COMPLETE`, get the Kubernetes config file in the current folder:

```bash
openstack coe cluster config $K8S_CLUSTER_NAME --force
export KUBECONFIG=$(pwd)/config
chmod 600 config
```

Now the usual `kubectl` commands should work:

```bash
> kubectl get nodes
NAME                                          STATUS   ROLES           AGE     VERSION
k8s-mbbffjfee7zs-control-plane-6rn2z          Ready    control-plane   2m22s   v1.30.4
k8s-mbbffjfee7zs-control-plane-nw4cc          Ready    control-plane   41s     v1.30.4
k8s-mbbffjfee7zs-control-plane-w9jln          Ready    control-plane   5m8s    v1.30.4
k8s-mbbffjfee7zs-default-worker-jb5lm-gvvjm   Ready    <none>          2m21s   v1.30.4
```

## Scale Manually

Scaling manually only works if autoscaling is disabled.

List the node groups:

```bash
openstack coe nodegroup list $K8S_CLUSTER_NAME
```

Increase the number of worker nodes:

```bash
openstack coe cluster resize --nodegroup default-worker $K8S_CLUSTER_NAME 3
```

Confirm that there are 3 worker nodes:

```bash
kubectl get nodes
```

## Enable the Autoscaler

Even if we specify a max node count of 5 in the `create_cluster.sh` script, this is not propagated to the nodegroup. See:

```bash
openstack coe nodegroup show $K8S_CLUSTER_NAME default-worker
```

While `min_node_count` is set to 1, `max_node_count` is set to None, which means that the autoscaler is still disabled.

We can enable it by setting the `max_node_count` property on the `default-worker` nodegroup manually:

```bash
openstack coe nodegroup update $K8S_CLUSTER_NAME default-worker replace /max_node_count=5
```

Now we can test the autoscaler with a simple deployment that uses 4 GB of memory for each replica:

```bash
kubectl create -f high_mem_dep.yaml
kubectl scale deployment high-memory-deployment --replicas 6
```

In the log of the pods, we can notice that this triggered the creation of more nodes:

```bash
Normal   TriggeredScaleUp        113s  cluster-autoscaler  pod triggered scale-up: [{MachineDeployment/magnum-83bd0e70b4ba4cd092c2fb82b1ce06fb/k8s-mbbffjfee7zs-default-worker 2->5 (max: 5)}]
```

And in fact, within a couple of minutes:

```bash
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
```

We still have 1 pending pod, but the autoscaler has a limit of 5 workers, so it won't launch other nodes:

```bash
> kubectl get pods
NAME                                     READY   STATUS    RESTARTS   AGE
high-memory-deployment-85785c87d-4zbrv   1/1     Running   0          4m5s
high-memory-deployment-85785c87d-5xtvq   0/1     Pending   0          4m5s
high-memory-deployment-85785c87d-6ds4c   1/1     Running   0          4m5s
high-memory-deployment-85785c87d-qhclc   1/1     Running   0          4m5s
high-memory-deployment-85785c87d-qxlf2   1/1     Running   0          4m5s
high-memory-deployment-85785c87d-rk8sb   1/1     Running   0          5m8s
```

## Test Persistent Volumes

Magnum comes with a default storage class for persistent volumes which relies on OpenStack Cinder. We can test with a simple pod:

```bash
kubectl create -f ../alpine-persistent-volume.yaml
kubectl describe pod alpine
```

## Install NGINX Controller

In principle, we do not need an Ingress because the OpenStack Load Balancer can directly route traffic to JupyterHub. However, there is no way of getting an HTTPS certificate without an Ingress.

Install the NGINX Ingress controller with:

```bash
helm upgrade --install ingress-nginx ingress-nginx \
             --repo https://kubernetes.github.io/ingress-nginx \
             --namespace ingress-nginx --create-namespace
```

### Use a Fixed IP Address

Notice that deploying the NGINX ingress controller will create a new OpenStack Load Balancer, which will be assigned a random IP address. This address will be lost when the NGINX ingress controller is deleted or the cluster is deleted.

To use a fixed IP address, first create a floating IP in OpenStack:

```bash
openstack floating ip create public
export IP=<FLOATING_IP>
```

Find the ID of the NGINX Load Balancer:

```bash
openstack loadbalancer list
export LB=<LOAD_BALANCER_ID>
```

Find the ID of the VIP port:

```bash
LB_VIP_PORT_ID=$(openstack loadbalancer show $LB -c vip_port_id -f value)
```

Find the existing IP:

```bash
EXISTING_FIP=$(openstack floating ip list --port $LB_VIP_PORT_ID -c ID -f value)
```

Remove it:

```bash
openstack floating ip unset --port $EXISTING_FIP
```

And associate the new floating IP:

```bash
openstack floating ip set --port $LB_VIP_PORT_ID $IP
```

## Configure a Subdomain

In case you do not have access to a custom domain, you can use the Jetstream subdomain for your project. The subdomain is available to all projects on Jetstream, and it is a good way to test your deployment without having to configure a custom domain.

Jetstream provides subdomains to each project as:

```bash
xxxxxx.$PROJ.projects.jetstream-cloud.org
```

where `PROJ` is the ID of your Jetstream 2 allocation (all lowercase):

```bash
export PROJ="xxx000000"
```

First, get the public IP of the NGINX ingress controller:

```bash
export IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

If you have a custom subdomain, you can configure an A record that points to the `EXTERNAL-IP` of the service. Otherwise, use OpenStack to create a record:

```bash
export SUBDOMAIN="k8s"
openstack recordset create  $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN --type A --record $IP --ttl 3600
```

Access JupyterHub at <https://k8s.$PROJ.projects.jetstream-cloud.org>.

## Test the NGINX Ingress Controller

We have a deployment of a simple toy application to test that Kubernetes, the NGINX ingress, and the domain are working correctly.

First, associate a subdomain to the IP address of the NGINX ingress controller:

```bash
export SUBDOMAIN="testpage"
openstack recordset create $PROJ.projects.jetstream-cloud.org. $SUBDOMAIN --type A --record $IP --ttl 3600
kubectl create -f echo-test.yaml
```

Now you should be able to connect to:

<http://testpage.$PROJ.projects.jetstream-cloud.org>

If everything is working properly, you should see "Testing NGINX Ingress on Jetstream!" in the browser.

## Install JupyterHub

Finally, we can go back to the root of the repository and install JupyterHub. First, create the secrets file:

```bash
bash create_secrets.sh
```

The default `secrets.yaml` file assumes you are deploying on a `projects.jetstream-cloud.org` subdomain. If that is not the case, edit the file with your own domain.

```bash
bash configure_helm_jupyterhub.sh
bash install_jhub.sh
```

## Setup HTTPS

Finally, to get a valid certificate, deploy `cert-manager` with:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.16.2/cert-manager.yaml
```

and a Cluster Issuer:

```bash
kubectl create -f ../setup_https/https_cluster_issuer.yml
```

Now your deployment should have a valid HTTPS certificate.

## Issues and Feedback

Please [open an issue on the repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/) to report any issue or give feedback.
