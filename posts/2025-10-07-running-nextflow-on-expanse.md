---
categories:
  - HPC
  - sdsc
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

When following the instructions, replace any `conda` commands with `micromamba` to use your newly installed Micromamba environment.

### 3. Verify Nextflow Installation

After installation, you can verify that Nextflow is correctly installed and using the Micromamba-provided Java by running `nextflow info`. You should see something like this:

```
Version: 25.04.8 build 5956
Created: 06-10-2025 21:19 UTC (14:19 PDT)
System: Linux 4.18.0-513.24.1.el8_9.x86_64
Runtime: Groovy 4.0.26 on OpenJDK 64-Bit Server VM 23.0.2-internal-adhoc.conda.src
Encoding: UTF-8 (UTF-8)
```

Notice the `Runtime` line, which indicates that Nextflow is using an OpenJDK version provided by Conda, ensuring compatibility and optimal performance on Expanse.

### 4. Run a Toy Example

To test your Nextflow installation, let's run a simple workflow from the Nextflow training materials. The training videos are an excellent resource for understanding Nextflow concepts: [https://training.nextflow.io/latest/hello_nextflow/01_hello_world/](https://training.nextflow.io/latest/hello_nextflow/01_hello_world/)

First, download the workflow script and input data:

```bash
wget https://github.com/nextflow-io/training/raw/refs/heads/master/hello-nextflow/solutions/3-hello-workflow/hello-workflow-4.nf
wget https://github.com/nextflow-io/training/raw/refs/heads/master/hello-nextflow/greetings.csv
```

Then, run the workflow locally on the login node (for testing purposes):

```bash
nextflow hello-workflow-4.nf
```

You should see output similar to this:

```
N E X T F L O W   ~  version 25.04.8

Launching `hello-workflow-4.nf` [soggy_monod] DSL2 - revision: 7924362939

executor >  local (7)
[ee/22f232] sayHello (3)       [100%] 3 of 3 ✔
[77/32c0db] convertToUpper (3) [100%] 3 of 3 ✔
[09/3fd893] collectGreetings   [100%] 1 of 1 ✔
There were 3 greetings in this batch
```