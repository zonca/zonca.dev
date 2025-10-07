---
categories: [hpc, sdsc]
date: '2025-10-07'
layout: post
title: Running Nextflow on Expanse
---

This tutorial will guide you through setting up Nextflow on Expanse. [Nextflow](https://www.nextflow.io/) is a powerful and flexible workflow management system that enables scalable and reproducible scientific workflows. It allows researchers to define complex computational pipelines using a simple language, making it easy to manage data dependencies, parallelize tasks, and adapt workflows to different computing environments, from local machines to cloud platforms and HPC clusters like Expanse. Workflow systems like Nextflow are incredibly useful for ensuring reproducibility, simplifying complex analyses, and efficiently utilizing computational resources by automating the execution of multi-step processes.

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

The workflow consists of the following steps:

1.  **`sayHello` process**: Takes individual greetings (e.g., from a CSV file) and creates a separate output file for each greeting, containing the greeting text.
2.  **`convertToUpper` process**: Takes the output files from `sayHello`, reads their content, converts the text to uppercase, and writes the uppercase text to new files.
3.  **`collectGreetings` process**: Gathers all the uppercase files produced by `convertToUpper`, concatenates their content into a single output file, and also counts how many greetings were processed in total.

In summary, the workflow reads a list of greetings, processes each one by converting it to uppercase, and then combines all the uppercase greetings into a single result file, finally reporting the total count.

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

To run Nextflow on the compute nodes, you need to submit a Slurm job. This approach is useful if you have many tiny jobs that can all run within the resources of a single node. However, the true power of Nextflow lies in its ability to coordinate multiple Slurm jobs, which can execute on different queues or even require specialized resources like GPUs or multiple nodes for different stages of a workflow. First, identify your available allocation using `expanse-client user`:

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

### 6. Run with Slurm Executor

Nextflow can also manage the submission of individual tasks as separate Slurm jobs, allowing you to leverage the cluster's resources more effectively. In this mode, Nextflow runs on the login node, but each process within the workflow is submitted as an independent Slurm job. This setup often utilizes node-local scratch (fast SSD) for temporary files, with results passed between tasks.

Nextflow uses configuration profiles to define different execution environments. The `expanse_nextflow` repository includes a `nextflow.config` file with a `slurm_debug` profile tailored for this purpose. This profile limits parallelism to 1 job at a time due to debug queue limits, but this restriction can be removed when using the shared or compute queues. You can inspect the `nextflow.config` file to see the specific configurations.

To run the workflow using the Slurm executor with the `slurm_debug` profile, execute the following command on the login node:

```bash
nextflow run hello-workflow-4.nf -profile slurm_debug
```

You should see output similar to this, indicating that the executor is `slurm`:

```
N E X T F L O W   ~  version 25.04.8

Launching `hello-workflow-4.nf` [tender_fermi] DSL2 - revision: 7924362939

executor >  slurm (7)
[bb/5d01f1] sayHello (1)       [100%] 3 of 3 ✔
[a1/f76925] convertToUpper (3) [100%] 3 of 3 ✔
[d0/a2e7e6] collectGreetings   [100%] 1 of 1 ✔
There were 3 greetings in this batch
Completed at: 07-Oct-2025 11:02:52
Duration    : 1m 22s
CPU hours   : (a few seconds)
Succeeded   : 7
```

### 7. Run with Singularity

Nextflow seamlessly integrates with container technologies like Singularity, allowing you to define your workflow's execution environment in a portable and reproducible way. On Expanse, this is particularly useful for managing dependencies and ensuring consistent results across different computing environments.

The `expanse_nextflow` repository's `nextflow.config` file already includes a profile that enables Singularity. To leverage this, you simply need to uncomment the `containers` line within your Nextflow workflow file (e.g., `hello-workflow-4.nf`). Before executing the workflow, ensure you load the Singularity module by running `module load singularitypro`. The environment will be automatically propagated to the Slurm job.

Once enabled, processes like `convertToUpper` will no longer run natively on the host system but will instead execute inside a specified Singularity container. The Singularity image is cached on the first run and then reused for subsequent executions, saving time and resources. For this tutorial, we are using a standard Ubuntu container maintained by SDSC's Marty Kandes, available through his [naked-singularity](https://github.com/mkandes/naked-singularity) project. This ensures that the `convertToUpper` process runs in a consistent and isolated environment.

To run the workflow with Singularity, first uncomment the `containers` line in `hello-workflow-4.nf` (if it's commented out). Then, execute Nextflow with the appropriate profile (e.g., `slurm_debug` if you're still testing on the debug queue):

```bash
nextflow run hello-workflow-4.nf -profile slurm_debug
```

You should observe that the `convertToUpper` process now executes within the Singularity container, providing a robust and reproducible execution environment.