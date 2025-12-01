---
categories:
- jupyterhub
- python
date: '2025-12-01'
layout: post
title: Custom JupyterHub Docker image template
---

I published a template that builds a ready-to-use JupyterHub single-user image with common scientific Python tooling and JupyterHub-friendly defaults: <https://github.com/zonca/custom-jupyterhub-docker-image>. Clone it, adjust `requirements.txt` (or the Dockerfile/env files) in GitHub, and a GitHub Actions workflow automatically builds and publishes a new image for you—no local Docker needed. See the README in that repo for the full list of packages, build steps, and CI workflow details.

How to use it in JupyterHub:

- Build or pull the image, then point your spawner at it, e.g. `c.DockerSpawner.image = "ghcr.io/your-org/custom-jupyterhub-docker-image:TAG"` (or the equivalent field for your spawner/Helm chart).
- Restart JupyterHub so new servers launch with the custom image.

Using the GitHub template model: click “Use this template” on the repository to create your own copy (no fork history), edit the Dockerfile or environment as needed, then push to your org/user namespace.

GitHub can also host the resulting Docker images via GitHub Container Registry; publishing and pulling docs: <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>.
