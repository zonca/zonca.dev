---
categories:
  - hpc
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

First, clone the example repository:

```bash
git clone https://github.com/zonca/expanse_nextflow
cd expanse_nextflow
```

This workflow processes a CSV file containing greetings, converts them to uppercase, and then collects them. For more details, refer to the [Nextflow training materials](https://training.nextflow.io/2.4.0/hello_nextflow/03_hello_workflow/).

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

### 5. Run in a single Slurm job

To run Nextflow on the compute nodes, you need to submit a Slurm job. First, identify your available allocation using `expanse-client user`:

```bash
expanse-client user
```

This will show your available allocations, for example:

```
 Resource  expanse 

╭───┬───────┬───────┬─────────┬──────────────┬──────┬───────────┬─────────────────╮
│   │ NAME  │ STATE │ PROJECT │ TG PROJECT   │ USED │ AVAILABLE │ USED BY PROJECT │
├───┼───────┼───────┼─────────┼──────────────┼──────┼───────────┼─────────────────┤
│ 1 │ zonca │ allow │ sdsxxx  │ TG-XXXX │  706 │     25000 │             761 │
╰───┴───────┴───────┴─────────┴──────────────┴──────┴───────────┴─────────────────╯
```

From this output, you can see that `sdsxxx` is the project and `TG-XXXX` is the TG project. You will use these in your Slurm script.

Create a file named `nextflow_job.sh` with the following content:

```bash
#!/bin/bash
#SBATCH --job-name=nextflow_test
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4GB
#SBATCH --time=00:10:00
#SBATCH --account=sdsxxx
#SBATCH --export=ALL
#SBATCH --output=nextflow_job.out
#SBATCH --error=nextflow_job.err

# Load micromamba and activate nextflow environment
source ~/.bashrc
micromamba activate nf-env

# Run Nextflow
nextflow expanse_nextflow/hello-workflow-4.nf
```

Submit the job using `sbatch`:

```bash
sbatch nextflow_job.sh
```

You can monitor the job status with `squeue -u $USER` and check the output in `nextflow_job.out` and `nextflow_job.err` once the job completes.