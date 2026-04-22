---
categories:
- kubernetes
- openstack
- jupyterhub
date: '2026-04-22'
layout: post
title: "Deploying JupyterHub on OpenStack Magnum with OpenTofu"
---

In this tutorial, we will walk through the process of deploying a production-ready JupyterHub on OpenStack Magnum using **OpenTofu**. 

### What you get at the end

By following this guide, you will have:

* A fully functional **Kubernetes cluster** provisioned via OpenStack Magnum.
* A **public Floating IP** automatically bound to an Nginx Ingress Controller.
* Automatic **HTTPS certificates** provided by Let's Encrypt and Cert-Manager.
* A customized **JupyterHub** installation accessible via a professional subdomain (e.g., `jhub-test.cis230085.projects.jetstream-cloud.org`).
* A **modular OpenTofu configuration** that is easy to maintain and reproduce.

---

## 1. Prerequisites

### Install OpenTofu

If you don't have OpenTofu installed, you can install it using the official script:

```bash
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install.sh | sh
```

Alternatively, on Linux with snap: `snap install opentofu --classic`.

### Clone the Material

All the OpenTofu recipes and configuration templates are available in the following repository:

```bash
git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream
cd jupyterhub-deploy-kubernetes-jetstream/tofu_magnum
```

### Get OpenStack Credentials

You need an "Application Credential" to allow OpenTofu to manage resources on your behalf:

1. Log in to your OpenStack Dashboard (e.g., Jetstream2 Horizon).
2. Navigate to **Identity** -> **Application Credentials**.
3. Create a new credential and download the **OpenStack RC** file.
4. Save it as `app-cred-openrc.sh` in the root of the cloned repository.
5. Source it in your terminal:
   ```bash
   source app-cred-openrc.sh
   ```

---

## 2. Configuration

All the details of your cluster—such as name, number of nodes, machine sizes (flavors), and your JupyterHub subdomain—are controlled via a single file: `terraform.tfvars`.

### Edit your settings

Navigate to the deployment directory and create/edit your `terraform.tfvars`:

```bash
cd full_stack_https
cp terraform.tfvars.example terraform.tfvars
```

**Key variables to customize:**

* `cluster_name`: The name of your Magnum cluster.
* `node_count`: Initial number of worker nodes.
* `worker_flavor`: The machine type (e.g., `m3.small`).
* `subdomain`: The prefix for your URL (e.g., `my-hub`).
* `letsencrypt_email`: Your email for HTTPS certificate notifications.

---

## 3. Deployment

### Initialize and Apply

First, initialize the OpenTofu workspace to download the necessary providers and modules:

```bash
tofu init
```

Then, deploy the entire stack:

```bash
tofu apply
```

OpenTofu will first provision the Kubernetes VMs via Magnum, then automatically set up the networking, DNS, and finally install the Helm charts for Ingress and JupyterHub.

**Sample Cluster Creation Output:**

```text
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Creating...
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Still creating... [1m0s elapsed]
...
module.kubernetes_cluster.openstack_containerinfra_cluster_v1.cluster: Creation complete after 9m30s
```

**Sample Helm Installation Output:**

```text
null_resource.install_jupyterhub (local-exec): Release "jhub" does not exist. Installing it now.
null_resource.install_jupyterhub: Creation complete after 1m24s

Apply complete! Resources: 14 added, 0 changed, 0 destroyed.

Outputs:
jupyterhub_url = "https://jhub-test.cis230085.projects.jetstream-cloud.org"
```

---

## 4. Verification

Once the command finishes, your JupyterHub should be live! You can verify the status of the internal pods using `kubectl`:

```bash
export KUBECONFIG=./config
kubectl get pods -n jhub
```

**Expected Result:**

```text
NAME                              READY   STATUS    RESTARTS   AGE
cm-acme-http-solver-pbwzf         1/1     Running   0          85s
hub-5545f479f9-fjqcd              1/1     Running   0          85s
proxy-5766564b84-hbtwr            1/1     Running   0          85s
```

## Conclusion

Using OpenTofu to manage JupyterHub on OpenStack Magnum provides a clean, automated way to handle both infrastructure and applications. By using the modular setup provided in this tutorial, you can easily scale your hub or replicate the deployment for different projects.
