---
categories:
- jupyterhub
- jetstream
- kubernetes
aliases:
- gw23
date: '2023-10-11'
layout: post
title: Gateways 2023 tutorial about Dask and JupyterHub on Kubernetes on Jetstream

---

## Tutorial

* [Tutorial slides](https://docs.google.com/presentation/d/1ZPvA-ybYHxBn5ky2mPbeLNnZzMJs6t9-UWtz3EdRHPA/edit?usp=sharing)
* Jupyter notebooks on Github:[`zonca/dask-jetstream-tutorial`](https://github.com/zonca/dask-jetstream-tutorial)
* Tutorial notebooks complete with output cells as executed after the tutorial, in a [gist](https://gist.github.com/zonca/ab3f9f3db475331f6d8d68731636a70e)

### Tutorial recording

[Video on Youtube](https://www.youtube.com/watch?v=GqyK_fwrKRo)

## Support

I have funding from Jetstream to help developers deploy Kubernetes and any related service to Jetstream, [please contact me](https://www.sdsc.edu/research/researcher_spotlight/zonca_andrea.html) if you need any help or even just to check if any of this could fit your use-case.

## Deployment of the tutorial infrastructure

Here is the reference to all the step-by-step tutorial on how to deploy the infrastructure used in the tutorial:

* [Deployment of Kubernetes via Kubespray on Jetstream 2](./2023-07-19-jetstream2_kubernetes_kubespray.md) 
* [Deploy JupyterHub on top of Kubernetes](https://www.zonca.dev/posts/2022-03-31-jetstream2_jupyterhub.html)
* [Install `cert-manager` to provide HTTPS support](./2023-09-26-https-kubernetes-letsencrypt.md)
* [Github Authentication](./2023-10-27-jupyterhub-github-authentication.md)
* [Dask Gateway](./2023-09-28-dask-gateway-jupyterhub.md)
* [Configure access to object store](https://www.zonca.dev/posts/2022-04-04-zarr_jetstream2)
