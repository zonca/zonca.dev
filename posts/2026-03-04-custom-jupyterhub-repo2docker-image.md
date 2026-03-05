---
categories:
- jupyterhub
- python
date: '2026-03-04'
layout: post
title: Auto-build JupyterHub images with repo2docker and GitHub Actions
---

*This guide explains how to automatically build a custom, JupyterHub-ready Docker image directly from GitHub using `repo2docker`, without having to write a complicated Dockerfile from scratch.*

### The Problem

If you run a JupyterHub—whether it's for a university class, a workshop, or a shared research platform—your users will need specific Python packages installed. 

Usually, customizing this software stack means writing a full `Dockerfile` by hand. Writing Dockerfiles can be complex, and maintaining them over time as packages change requires specialized knowledge of Docker commands and Linux server administration.

### The Solution: repo2docker

Instead of writing a `Dockerfile` from scratch, we can use a tool created by the Jupyter project called [repo2docker](https://repo2docker.readthedocs.io/). 

The goal of `repo2docker` is simple: it looks at standard configuration files (like `environment.yml` for Conda, or `requirements.txt` for pip) and automatically turns them into a fully functional Docker image. 

With this approach, **you only need to update your list of packages in GitHub, and "Continuous Integration" (CI) pipelines will automatically build, test, and publish a new image ready for your JupyterHub.**

### Using the Template Repository

To make this as easy as possible, I have created a template repository that has everything set up for you:

*   **Template repository:** <https://github.com/zonca/custom-jupyterhub-repo2docker-image>  
*   **Previous Dockerfile-based repository:** <https://github.com/zonca/custom-jupyterhub-docker-image> *(for comparison)*
*   **Latest integration run:** <https://github.com/zonca/custom-jupyterhub-repo2docker-image/actions/runs/22652277154>

#### How this differs from the traditional Dockerfile approach

*   **Dockerfile approach:** You have maximum control over the environment, but you spend your time managing lower-level server details inside Docker layers.
*   **repo2docker approach:** You spend your time specifying scientific packages in an `environment.yml` file. It drastically reduces maintenance, especially for standard scientific Python environments.

#### The configuration files

When using this template, you'll mainly interact with these simple files:

*   `environment.yml`: The main Conda environment definition (for your Python packages and channels).
*   `requirements.txt`: Optional pip packages.
*   `apt.txt`: Optional Ubuntu system packages installed with `apt`.
*   `postBuild`: An optional shell script for anything that needs to be compiled or run after packages are installed.
*   `start`: An optional script that runs when the server starts up.

### Quick Start Guide

Here is all you need to do to get your custom JupyterHub image building:

1.  **Create your repository:** Go to the [template repository](https://github.com/zonca/custom-jupyterhub-repo2docker-image) and click the "Use this template" button to create your own copy on GitHub.
2.  **Add your packages:** Edit the `environment.yml` file in your new repository to include the software your users need.
3.  **Save your changes:** Commit and push these changes to the `main` branch.
4.  **Automatic Build:** GitHub Actions will automatically detect the changes, build the image, and publish it securely to the GitHub Container Registry (GHCR). 

*Security bonus: The automated workflow also digitally signs the images with Cosign and produces security artifacts (SBOMs) to ensure your supply chain is secure.*

### Deploying Your Image to JupyterHub

Once GitHub Actions successfully builds your image, you can tell your JupyterHub (which typically runs on Kubernetes using Zero to JupyterHub / Z2JH) to start using it. 

You configure this in your JupyterHub `config.yaml` file:

```yaml
singleuser:
  image:
    name: ghcr.io/YOUR_GITHUB_USERNAME/custom-jupyterhub-repo2docker-image
    tag: 2026-03-04-320a95e
  cmd: jupyterhub-singleuser
  defaultUrl: /lab
```

*Note on Tags:* GitHub automatically creates unique tags based on the date and a short commit code (e.g., `2026-03-04-320a95e`). This guarantees you are running the exact version you just built. Avoid using the `latest` tag in production environments!

*Note on the `cmd` setting:* We explicitly set `cmd: jupyterhub-singleuser`. This guarantees the pod correctly starts the JupyterHub-aware server process and prevents any default settings from leaving the pod running but unusable from the Hub.

Finally, deploy the updated configuration using Helm:

```bash
helm upgrade --install jhub jupyterhub/jupyterhub \
  --namespace jhub \
  --create-namespace \
  --values config.yaml
```

### Advanced Automated Testing

To make sure you never accidentally publish a broken image, the template includes a real-world integration test. 

After your new image is built, a separate GitHub workflow (`z2jh-integration.yml`) spins up a miniature Kubernetes cluster using `kind`, installs JupyterHub, and actually makes sure a real Hub can start up using your successfully built image workflow!
