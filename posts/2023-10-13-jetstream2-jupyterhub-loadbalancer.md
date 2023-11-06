---
categories:
- kubernetes
- jetstream2
date: '2023-11-06'
draft: true
layout: post
slug: jupyterhub-jetstream2-loadbalancer
title: Deploy JupyterHub on Jetstream 2 with a Load Balancer

---

The main weakness of the [deployment of Kubernetes and JupyterHub on Jetstream 2](./2023-07-19-jetstream2_kubernetes_kubespray.md) is that it supports only 1 master node and the public IP of that node is used to connect to JupyterHub. Therefore in case of issues on that instance, the whole deployment is not reachable.

It has been a few months that the Jetstream 2 team has made available Octavia, a load balancing service for Openstack.
Relying on Octavia, we can publish a Kubernetes service, like JupyterHub, on another IP which is independent of the IPs of the Openstack instances.
This also allows us to run multiple master nodes to have more resilience against malfunctioning instances.

Compared to the normal deployment mentioned above we need just a few steps to make use of this service:

* before running `ansible`, edit `inventory/$CLUSTER/group_vars/k8s_cluster/addons.yml` and comment out all the configuration related to `Ingress`.
* reserve a floating ip you would like to use for JupyterHub

        openstack floating ip create public

* edit the JupyterHub Helm configuration file `secrets.yaml`, add:

        proxy:
          service:
            loadBalancerIP: 149.xxx.xxx.xxx

* redeploy JupyterHub
* check that the public IP has been assigned with:

        kubectl -n jhub get svc proxy-public
        kubectl -n jhub describe svc proxy-public
