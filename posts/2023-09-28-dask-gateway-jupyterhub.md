---
categories:
- kubernetes
- jetstream2
- jupyterhub
- dask
- python
- jetstream
date: '2023-09-28'
layout: post
title: Deploy Dask Gateway with JupyterHub on Kubernetes

---

In this tutorial we will install [Dask Gateway](https://gateway.dask.org/index.html), currently version `2023.9.0`, on Kubernetes and configure JupyterHub so
Jupyter Notebook users can launch private Dask cluster and connect to them.

I assume to start from a Kubernetes cluster already running and
JupyterHub deployed on top of it via Helm. And SSL encryption also activated (it isn't probably necessary, but I haven't tested that).
I tested on Jetstream 2, but the recipe should be agnostic of that.

## Preparation

Clone on the machine you use to run `helm` and `kubectl` the repository
with the configuration files and scripts:

	git clone https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/

## Launch dask gateway

We can install version 2023.9.0 with:

	$ bash install_dask-gateway.sh

You might want to check `config_dask-gateway.yaml` for extra configuration options, but for initial setup and testing it shouldn't be necessary.

After this you should see the 3 dask gateway pods running, e.g.:

	$ kubectl -n jhub get pods
	NAME                                       READY   STATUS    RESTARTS   AGE
	api-dask-gateway-64bf5db96c-4xfd6          1/1     Running   2          23m
	controller-dask-gateway-7674bd545d-cwfnx   1/1     Running   0          23m
	traefik-dask-gateway-5bbd68c5fd-5drm8      1/1     Running   0          23m

## Modify the JupyterHub configuration

Only 2 options need to be changed in JupyterHub:

* We need to run a image which has the same version of `dask-gateway` we installed on Kubernetes (currently `0.9.0`)

If you are using my `install_jhub.sh` script to deploy JupyterHub,
you can modify it and add another `values` option at the end, `--values dask_gateway/config_jupyterhub.yaml`.

You can modify the image you are using for Jupyterhub in `dask_gateway/config_jupyterhub.yaml`.

To assure that there are not compatibility issues, the "Client" (JupyterHub session), the dask gateway server, the scheduler and the workers should all have the same version of Python and the same version of `dask`, `distributed` and `dask_gateway`. If this is not possible, you can test different combinations and they might work.

Then redeploy JupyterHub:

	bash install_jhub.sh && cd dask_gateway && bash install_dask-gateway.sh

Login to JupyterHub, get a terminal and first check if the service is working:

    >  curl http://traefik-dask-gateway/services/dask-gateway/api/health

Should give:

    {"status": "pass"}

if `curl` is not available in your image, you can do the same in a Python Notebook:

    import requests
    requests.get("http://traefik-dask-gateway/services/dask-gateway/api/health").content

## Identify the dask gateway address

Jetstream 2 now supports "Load Balancing as a service", therefore the dask gateway address gets a public IP that can be accessed from outside, this is very convenient for users viewing the Dask Dashboard.

First let's get the IP:

    kubectl --namespace=jhub get service traefik-dask-gateway
    NAME                   TYPE           CLUSTER-IP     EXTERNAL-IP       PORT(S)        AGE
    traefik-dask-gateway   LoadBalancer   10.233.43.51   149.165.xxx.xxx   80:32752/TCP   36m

External IP is the address to be used in the next section.

## Create a dask cluster

You can now login to JupyterHub and check you can connect properly to `dask-gateway`:

```python
from dask_gateway import Gateway
gateway = Gateway(
    address="http://xxx.xxx.xxx.xxx",
    auth="jupyterhub")
gateway.list_clusters()
```

Then create a cluster and use it:

```python
cluster = gateway.new_cluster()
cluster.scale(2)
client = cluster.get_client()
```

Client is a standard `distributed` client and all subsequent calls to dask will go
through the cluster.

Printing the `cluster` object gives the link to the Dask dashboard.

For a full example see [this Jupyter Notebook](https://gist.github.com/zonca/e5aff9b8a1aa525b772cb2532cd720d0)

(Click on the `Raw` button to download notebook and upload it to your session).
