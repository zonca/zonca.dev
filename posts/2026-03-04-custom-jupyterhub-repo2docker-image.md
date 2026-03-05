---
categories:
- jupyterhub
- python
date: '2026-03-04'
layout: post
title: Auto-build JupyterHub images with repo2docker and GitHub Actions
---

Build and publish a JupyterHub-ready image directly from GitHub using `repo2docker`.

The main goal is to update your JupyterHub software stack by editing `environment.yml` only.
Use this when you run a JupyterHub and need frequent environment updates, for example for classes, workshops, or shared research platforms.
Instead of hand-maintaining a full Dockerfile, you change the Conda environment file in Git and CI builds, validates, and publishes a new Hub-ready image tag.

Template repository: <https://github.com/zonca/custom-jupyterhub-repo2docker-image>  
Previous Dockerfile-based repository: <https://github.com/zonca/custom-jupyterhub-docker-image>  
Latest integration run: <https://github.com/zonca/custom-jupyterhub-repo2docker-image/actions/runs/22652277154>

How this differs from the Dockerfile approach:

- With the Dockerfile repo, most customization happens in `Dockerfile` layers.
- With this repo2docker template, most customization happens in `environment.yml` (and optional `postBuild`).
- Dockerfiles give maximum low-level control; repo2docker reduces maintenance for standard scientific Python environments.
- This template also adds a separate Z2JH integration workflow that runs after image build to validate real JupyterHub startup.

repo2docker files used in this workflow:

- `environment.yml`: Conda environment definition (packages/channels).
- `requirements.txt`: Optional pip packages.
- `apt.txt`: Optional Ubuntu packages installed with `apt`.
- `postBuild`: Optional build-time shell script (compile assets, install extras).
- `start`: Optional runtime startup script.

In short: edit these files in Git, push, and CI produces a JupyterHub-usable image tag for your Helm config.

Quick start:

1. Create your own repository from the template.
2. Edit `environment.yml` with your packages.
3. Push to `main`.
4. Let GitHub Actions build and publish your image to GHCR.

The workflow also signs images with Cosign, produces an SBOM, and adds build provenance.

Use in Z2JH (`config.yaml`):

```yaml
singleuser:
  image:
    name: ghcr.io/zonca/custom-jupyterhub-repo2docker-image
    tag: 2026-03-04-320a95e
  cmd: jupyterhub-singleuser
  defaultUrl: /lab
```

Why set `cmd: jupyterhub-singleuser` explicitly:

- It guarantees the pod starts the JupyterHub-aware server process.
- It avoids image/entrypoint defaults that can leave pods running but not usable from Hub.

Deploy:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub \
  --create-namespace \
  --values config.yaml
```

Tagging strategy:

- `latest` for quick validation
- `YYYY-MM-DD-<shortsha>` for reproducible production deploys

CI flow:

1. `image.yml`: build, test, push, sign, and attest.
2. `z2jh-integration.yml`: run a real Hub test on Kind after a successful image workflow.
