---
categories:
- kubernetes
- jetstream2
date: '2025-03-26'
layout: post
title: Deployment of BinderHub by Project Pythia on Jetstream 2
---

## Project Pythia's BinderHub Deployment

Project Pythia has recently published a blog post about their deployment of BinderHub on Jetstream 2. This blog post discusses Project Pythia's efforts to address "Jupyter notebook obsolescence" by creating reproducible computational environments for geoscience education and workflows. The team deployed a BinderHub on NSF-funded Jetstream2 cloud infrastructure using OpenStack and Kubernetes, enabling scalable resource allocation for workshops and large datasets. By leveraging Terraform and cloud-agnostic infrastructure tools, they streamlined deployment while navigating limitations in OpenStack Magnum. The project highlights the importance of sustainable, community-driven solutions for open geoscience collaboration.

You can read their detailed blog post here: [Project Pythia BinderHub Deployment](https://2i2c.org/blog/2025/jetstream-binderhub/)

## My Contribution

I am happy to have participated in this effort by doing preliminary work on the deployment of Kubernetes and BinderHub on Jetstream 2. My earlier tutorial on [Deploying BinderHub on top of Kubernetes on Jetstream 2](./2022-11-15-binderhub-jetstream2.md) provided some of the groundwork that helped make Project Pythia's deployment possible.

It's exciting to see the continued development and implementation of these tools to support the scientific community.