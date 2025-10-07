---
categories:
  - hpc
  - nextflow
date: '2025-10-07'
layout: post
title: Running Nextflow on Expanse
---

This tutorial will guide you through setting up Nextflow on Expanse.

### 1. Install Micromamba

Expanse uses an older version of Anaconda, so we'll install Micromamba for a more up-to-date and isolated environment. Follow the official Micromamba installation guide: [https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)

**Important:** When prompted for the `Prefix location?`, use a path in your scratch space. You can get the correct path by running: `echo /expanse/lustre/scratch/$USER/temp_project/micromamba`. Note that you cannot use `$USER` directly in the prompt; you must replace it with the actual path obtained from the `echo` command.

After installation, make sure to configure your `bash` shell. You will need to log out and log back in, or source your `~/.bashrc` file for the changes to take effect.

### 2. Install Nextflow

Once Micromamba is set up, you can install Nextflow in a new environment called `nf-env`. This approach is particularly beneficial on Expanse because the system's default Java version might be too old for Nextflow. Micromamba will install a recent Java version isolated within your `nf-env` environment, ensuring compatibility.

Follow the instructions on the official Nextflow installation page: [https://www.nextflow.io/docs/latest/install.html](https://www.nextflow.io/docs/latest/install.html)

Here's how you can do it using Micromamba:

```bash
micromamba create -n nf-env nextflow
micromamba activate nf-env
```