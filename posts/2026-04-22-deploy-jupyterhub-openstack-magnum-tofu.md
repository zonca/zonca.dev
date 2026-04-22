---
categories:
- kubernetes
- openstack
- jupyterhub
date: '2026-04-22'
layout: post
title: "Deploying JupyterHub on OpenStack Magnum with OpenTofu"
---

In this tutorial, we will walk through the process of deploying a production-ready JupyterHub on OpenStack Magnum using **OpenTofu**. This approach provides a modular, declarative, and reproducible way to manage your Kubernetes infrastructure and the applications running on it.

## Prerequisites

- Access to an OpenStack cloud (e.g., Jetstream2)
- OpenTofu installed locally
- OpenStack credentials sourced in your environment

## The Modular Architecture

We use a shared OpenTofu module to manage the core Magnum cluster logic. This allows us to easily switch between a basic Kubernetes deployment and a full JupyterHub stack.

### 1. Creating a Basic Kubernetes Cluster

First, we define a simple cluster using our shared module. OpenTofu allows us to specify the desired state, such as node counts and flavors.

```hcl
module "kubernetes_cluster" {
  source = "./modules/cluster"

  cluster_name = "k8s-tofu-only"
  node_count   = 2
  flavor       = "m3.small"
}
```

When we run `tofu apply`, OpenTofu communicates with the Magnum API to provision the VMs and set up the Kubernetes control plane.

**Sample Output:**
```text
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Creating...
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Still creating... [1m0s elapsed]
...
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Creation complete after 9m33s [id=CLUSTER_UUID]
module.kubernetes_cluster.local_file.kubeconfig: Creating...
module.kubernetes_cluster.local_file.kubeconfig: Creation complete after 0s [id=CONFIG_SHA]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

### 2. Deploying the Full JupyterHub Stack

For a full deployment, we extend the configuration to include networking (Floating IPs), DNS, and the necessary Helm charts.

```hcl
module "kubernetes_cluster" {
  source = "../modules/cluster"
  cluster_name = "k8s-tofu-jhub"
}

# ... Additional resources for Floating IP, DNS, Ingress, and JupyterHub
```

The process automatically handles the installation of:
- **Ingress-Nginx**: For load balancing and external access.
- **Cert-Manager**: For automated HTTPS certificates via Let's Encrypt.
- **JupyterHub**: Using the official Helm chart.

**Helm Installation Output:**
```text
null_resource.install_ingress (local-exec): Release "ingress-nginx" does not exist. Installing it now.
null_resource.install_ingress: Creation complete after 32s [id=INGRESS_ID]

null_resource.install_jupyterhub (local-exec): Release "jhub" does not exist. Installing it now.
null_resource.install_jupyterhub: Creation complete after 1m24s [id=JHUB_ID]

Apply complete! Resources: 14 added, 0 changed, 0 destroyed.

Outputs:
jupyterhub_url = "https://jhub-test.example.projects.jetstream-cloud.org"
```

## Verification

Once the deployment is complete, you can verify the status of your JupyterHub pods:

```bash
export KUBECONFIG=./config
kubectl get pods -n jhub
```

**Output:**
```text
NAME                              READY   STATUS    RESTARTS   AGE
cm-acme-http-solver-pbwzf         1/1     Running   0          85s
hub-5545f479f9-fjqcd              1/1     Running   0          85s
proxy-5766564b84-hbtwr            1/1     Running   0          85s
```

## Conclusion

Using OpenTofu to manage JupyterHub on OpenStack Magnum provides a clean separation between infrastructure and application logic. This modular setup is easy to maintain, scale, and reproduce across different projects.

For the full source code and refactored Tofu recipes, visit the [jupyterhub-deploy-kubernetes-jetstream](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) repository.
