---
categories:
- kubernetes
- jetstream
- jupyterhub
- nbgrader
date: '2026-02-04'
layout: post
title: Deploy nbgrader on Jetstream with ngshare (Kubernetes)
---

This tutorial shows how to deploy **nbgrader** on Jetstream using **ngshare**, a service designed to make nbgrader work on Kubernetes without a shared filesystem exchange. This is the recommended approach for Kubernetes deployments.

We will:

* Deploy `ngshare` via Helm.
* Configure JupyterHub to register the ngshare service.
* Install `ngshare_exchange` and `nbgrader` in the singleuser image (using an existing image).
* Set a placeholder course ID.

## Why ngshare

nbgrader's default exchange assumes a shared filesystem between user pods. Kubernetes does not provide that by default, so ngshare replaces the exchange mechanism with a REST API.

## Prerequisites

* A working Kubernetes cluster on Jetstream (Magnum + Cluster API).
* JupyterHub deployed with the Helm chart.
* `kubectl` and `helm` configured.
* This repository cloned locally.

## Storage sizing for ngshare

ngshare stores **metadata only** (users, courses, submissions metadata), not the actual notebook files.

* Typical classes: **1–5 Gi** is plenty.
* Large classes or many submissions: **10 Gi** is safe.

## Step 1: Install ngshare (Helm)

Add the Helm repo and create a minimal `config.yaml`:

```bash
helm repo add ngshare https://libretexts.github.io/ngshare-helm-repo/
helm repo update
```

Use the template in this repo and edit it:

* `nbgrader/ngshare-config.yaml`

Install into the same namespace as JupyterHub (here `jhub`):

```bash
helm install ngshare ngshare/ngshare \
  --namespace jhub \
  -f ngshare-config.yaml
```

At the end of the Helm install, ngshare prints the **exact JupyterHub config snippet** you should add. Keep it; we will use it in the next step.

## Step 2: Register ngshare in JupyterHub

Add the ngshare service snippet to your JupyterHub values:

* `nbgrader/jhub-ngshare-service.yaml`

If you keep your Helm values in `config_standard_storage.yaml`, add the block there.  
Then add the values file to `install_jhub.sh` (just before the last line), and re-deploy by running:

```bash
bash install_jhub.sh
```

Verify the ngshare service:

* JupyterHub → Control Panel → Services → **ngshare**
* If you see a 403, try with an admin user (ngshare enforces admin-only access to some endpoints).

## Step 3: Enable nbgrader in the singleuser image

You need `nbgrader` and `ngshare_exchange` inside every user pod.  
This tutorial uses the standard Jupyter Docker Stacks image and installs the packages at startup.

Use the template in this repo:

* `nbgrader/jhub-singleuser-nbgrader.yaml`

Replace `COURSE_ID` with your course (e.g. `course101`).

If you want a custom image instead, see:  
`https://www.zonca.dev/posts/2025-12-01-custom-jupyterhub-docker-image`

After updating the values, add the file to `install_jhub.sh` and re-deploy:

```bash
bash install_jhub.sh
```

## Step 4: Validate in JupyterHub

In a user pod:

```bash
python -m pip show nbgrader ngshare-exchange
nbgrader list
```

If the exchange is correctly configured, `nbgrader list` should not error and should use ngshare as the exchange backend.

## Step 5: Allow private IPs for ngshare (Z2JH 2.0+)

If you are using a Z2JH version that enforces network policies by default, ensure user pods can reach the ngshare service:

```yaml
singleuser:
  networkPolicy:
    egressAllowRules:
      privateIPs: true
```

## Step 6: Create the course and roster

Use `ngshare-course-management` (installed with `ngshare_exchange`) to create the course and add instructors/students.  
Creating a course requires an **admin** user.

```bash
ngshare-course-management create_course course101 instructor1
ngshare-course-management add_student course101 student1
```

## Notes

* Use **ngshare** for nbgrader exchange on Kubernetes.
* Use a dedicated course ID per class (set in `nbgrader_config.py`).
* To manage students and instructors, use the `ngshare-course-management` CLI installed with `ngshare_exchange` rather than the formgrader UI.
