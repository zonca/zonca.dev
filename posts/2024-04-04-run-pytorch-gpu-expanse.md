---
date: '2024-04-04'
layout: post
title: Run PyTorch with GPU support on Expanse
categories:
- hpc
- jupyter

---

In this tutorial we will create a Python environment with PyTorch and see how to get Jupyterlab running on a GPU node.

First of all we want to create an isolated Python environment, I generally favor `micromamba`, see [the documentation on how to install it](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html#automatic-install)

Once installed, create an environment:

    micromamba create -n pytorch python==3.10 jupyterlab

Do not install `pytorch` with Mamba, it won't recognize the GPU, not sure why.

Install `pytorch` with `pip`:

    micromamba activate pytorch
    pip install pytorch

The tool to launch JupyterLab on Expanse currently doesn't support mamba, so the easiest way is to activate this environment at login, therefore add:

    micromamba activate pytorch

at the end of `.bashrc`.

Finally we can launch a job on the GPU-shared partition with Galyleo to get JupyterLab proxied to a public url:

    /cm/shared/apps/sdsc/galyleo/galyleo.sh launch -Q -p gpu-shared -A sds166 -t 120 -c 8 -M 16 -G 1 -j lab

Check in a Notebook that `pytorch` detects the GPU:

    import torch
    torch.cuda.is_available()
