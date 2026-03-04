---
categories:
- jupyterhub
- python
date: '2026-03-04'
layout: post
title: Auto-build JupyterHub images with repo2docker and GitHub Actions
---

Overview: Instead of maintaining a `Dockerfile`, you can build a JupyterHub-ready single-user image from repository configuration files (`environment.yml`, optional `postBuild`) using `repo2docker`. This keeps customization simple while still producing reproducible images for Zero to JupyterHub (Z2JH).

Template repository: <https://github.com/zonca/custom-jupyterhub-repo2docker-image>

Working CI example run: <https://github.com/zonca/custom-jupyterhub-repo2docker-image/actions/runs/22650073814>

How it works:

1. Edit `environment.yml` to add packages.
2. Push to GitHub.
3. GitHub Actions builds the image with `repo2docker`, runs JupyterHub smoke tests, and publishes to GHCR on `main`.
4. The workflow signs images with Cosign, generates an SBOM, and attests build provenance.

Suggested image tags:

- `latest` for quick testing
- `YYYY-MM-DD-<shortsha>` for reproducible JupyterHub deployments

How to use in Z2JH (`config.yaml`):

```yaml
singleuser:
  image:
    name: ghcr.io/zonca/custom-jupyterhub-repo2docker-image
    tag: 2026-03-04-c588129
  cmd: jupyterhub-singleuser
  defaultUrl: /lab
```

Then deploy:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub \
  --create-namespace \
  --values config.yaml
```

Why this is useful:

- Lower maintenance than Dockerfiles for common scientific stacks
- Fast iteration by editing only `environment.yml`
- Security and provenance integrated into CI by default
- Clear path from template repository to production JupyterHub image
