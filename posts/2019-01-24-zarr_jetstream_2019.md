---
aliases:
- /2019/01/zarr_jetstream_2019
- /2019/01/zarr-jetstream-2019
categories:
- kubernetes
- jetstream
- zarr
date: 2019-01-24 15:00
layout: post
slug: zarr-jetstream-2019
title: Create a high performance Zarr data store with Minio and Kubernetes on Jetstream

---

I've been working on deploying a high performance object store on Jetstream using Minio.
The goal is to serve Zarr data to a Jupyterhub deployment running on the same Kubernetes cluster.

## Setup Kubernetes on Jetstream

See my [tutorial on deploying Kubernetes on Jetstream with Kubespray](../2019-02-22-jetstream_kubernetes_kubespray_282.md).

## Provision the volumes

We need to create the volumes in Openstack, we can use the `openstack` command line tool.
First we need to get the `openrc` file from the Jetstream dashboard (API Access) and source it.

    source openrc.sh

Then we can create the volumes:

    openstack volume create --size 500 --description "minio data" minio-data-1
    openstack volume create --size 500 --description "minio data" minio-data-2
    openstack volume create --size 500 --description "minio data" minio-data-3
    openstack volume create --size 500 --description "minio data" minio-data-4

## Install Minio

We can install Minio using the Helm chart.
I've created a [GitHub repository with the configuration files](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/tree/master/minio).

First create the namespace:

    kubectl create namespace minio

Then we need to create the Persistent Volumes and Persistent Volume Claims, edit `minio-pv.yaml` to match the volume IDs created above.
You can get the volume IDs with:

    openstack volume list

Then create the PVs and PVCs:

    kubectl create -f minio-pv.yaml

Then we can install Minio:

    helm repo add stable https://kubernetes-charts.storage.googleapis.com
    helm install --name minio --namespace minio -f minio-config.yaml stable/minio

## Configure the client

We can use the `mc` client to configure Minio.
First we need to port-forward the service to localhost:

    kubectl port-forward svc/minio 9000:9000 -n minio

Then we can configure `mc`:

    mc config host add minio http://localhost:9000 minio minio123

## Create a bucket

    mc mb minio/zarr

## Upload data

We can upload data using `mc`:

    mc cp -r /path/to/data minio/zarr

## Access from Python

We can access the data from Python using `s3fs` and `zarr`:

```python
import s3fs
import zarr

s3 = s3fs.S3FileSystem(
    key='minio',
    secret='minio123',
    client_kwargs={'endpoint_url': 'http://minio.minio.svc.cluster.local:9000'}
)

store = s3fs.S3Map(root='zarr/data.zarr', s3=s3, check=False)
root = zarr.group(store=store)
```

## Performance

I've tested the performance reading a 50GB Zarr array from a Jupyter Notebook running on the same cluster.
I got about 1.5 GB/s read speed, which is quite good.

## Expose to the public

We can expose Minio to the public using Ingress.
See `minio-ingress.yaml` in the repository.

You need to create a DNS record for the domain name pointing to the cluster Ingress IP.

## Access via the API

Users can get their access keys and secret keys from the Minio dashboard.
However, currently there is no integration with Keystone or other identity providers, so all users share the same credentials.

See <https://iu.jetstream-cloud.org/project/api_access/> (link removed as Jetstream 1 is retired) for how to get API access to Openstack to manage volumes.
