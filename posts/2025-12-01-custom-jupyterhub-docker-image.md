---
categories:
- jupyterhub
- python
date: '2025-12-01'
layout: post
title: Custom JupyterHub Docker image template
---

Overview: <https://github.com/zonca/custom-jupyterhub-docker-image> is a template that ships a JupyterHub-ready single-user image with common scientific Python tooling and sensible defaults. You edit `requirements.txt` (or Dockerfile/env files) directly in GitHub, and the built-in GitHub Actions workflow auto-builds and publishes a new image—no local Docker required. See the README for the detailed package list and CI steps.

How to use it in JupyterHub:

- Build or pull the image, then point your spawner at it, e.g. `c.DockerSpawner.image = "ghcr.io/your-org/custom-jupyterhub-docker-image:TAG"` (or the equivalent field for your spawner/Helm chart).
- Restart JupyterHub so new servers launch with the custom image.

Adopt it via GitHub templates: click “Use this template” to create your own copy (no fork history), tweak the Dockerfile or environment files, and push to your namespace to trigger the build.

Where the image lives: the workflow can publish to GitHub Container Registry. Publish/pull docs: <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>.
