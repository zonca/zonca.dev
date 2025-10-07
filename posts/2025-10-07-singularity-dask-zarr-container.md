---
aliases:
- /2025/10/singularity-dask-zarr-container
categories:
- singularity
- python
date: '2025-10-07'
layout: post
title: Building Singularity Containers with Conda Environments from requirements.txt

---

This post introduces a method for building Singularity containers that include a Conda environment based on a `requirements.txt` file. This approach provides a reproducible and portable environment for any Python project.

## Key Capabilities:

*   **Automated Environment Setup:** Easily create a Conda environment within a Singularity container using a `requirements.txt` file.
*   **Reproducible Environments:** Ensure consistent execution of your Python projects across different systems.
*   **Streamlined Workflow:** Leverage GitHub Actions for automated container builds and hosting on GitHub Container Registry.

## Getting Started:

This container is built using Apptainer (formerly Singularity) via GitHub Actions, ensuring a streamlined and automated process. Python dependencies are managed through `requirements.txt`, which is used to create a Conda environment inside the container. The resulting container image is hosted on the GitHub Container Registry, allowing for easy pulling and deployment.

You can pull the container using:
```bash
singularity pull oras://ghcr.io/zonca/singularity_dask_zarr:latest
```

For more details, including building and testing instructions, please refer to the GitHub repository: [https://github.com/zonca/singularity_dask_zarr](https://github.com/zonca/singularity_dask_zarr)