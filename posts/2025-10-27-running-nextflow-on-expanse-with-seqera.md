---
categories: [hpc, sdsc, nextflow]
date: '2025-10-27'
layout: post
title: Running Nextflow on Expanse with Seqera
---

This tutorial will guide you through setting up Nextflow on Expanse using the Seqera platform. [Nextflow](https://www.nextflow.io/) is a powerful and flexible workflow management system that enables scalable and reproducible scientific workflows. It allows researchers to define complex computational pipelines using a simple language, making it easy to manage data dependencies, parallelize tasks, and adapt workflows to different computing environments, from local machines to cloud platforms and HPC clusters like Expanse. Workflow systems like Nextflow are incredibly useful for ensuring reproducibility, simplifying complex analyses, and efficiently utilizing computational resources by automating the execution of multi-step processes.

Seqera Platform enhances Nextflow by providing a centralized control plane for managing and monitoring Nextflow pipelines across diverse execution environments, including HPC clusters like Expanse. It offers features such as advanced logging, resource optimization, and collaborative tools, making it easier to deploy, track, and scale complex scientific workflows.

### What is Seqera?

Seqera Labs is a bioinformatics company that provides a platform for collaborative and scalable scientific data analysis, closely associated with the Nextflow workflow management system. It helps scientists develop, debug, and execute bioinformatics pipelines, manage data, and supervise workflows, particularly in cloud environments. Key offerings include Seqera AI for pipeline code generation and analysis, and Seqera Containers for streamlining Docker and Singularity container building and access. Seqera's technologies are used across various scientific disciplines to scale analytical work.

### Seqera Academic Program

Seqera offers an Academic Program that provides free Pro-level access to the Seqera Cloud Platform for researchers, educators, and students at qualifying institutions. To be eligible, the applicant's organization must be a degree-granting educational institution, and the use of the Seqera Platform must be solely for academic research and/or teaching purposes, not for commercial use. Applicants need a user account on seqera.io using their institutional email address and an organization created within seqera.io. More details and an application form are available on the Seqera website.

Before proceeding with Seqera-specific configurations, please follow the initial setup steps outlined in our previous tutorial: [Running Nextflow on Expanse](/posts/2025-10-07-running-nextflow-on-expanse.html). This includes installing Micromamba, Nextflow, verifying the installation, and running a toy example locally. Once you have completed these foundational steps, return to this tutorial to integrate Nextflow with the Seqera Platform.

### 1. Create Seqera Account and Token

#### 1.1. Create a Seqera Account and Workspace

If you don't already have one, create an account on [Seqera Platform](https://seqera.io/). Once logged in, create a new workspace for your projects.

#### 1.2. Link Nextflow to Seqera

To allow your local Nextflow installation to communicate with the Seqera Platform, you need to set the `TOWER_ACCESS_TOKEN` environment variable. You can generate an API token from your Seqera account settings.

```bash
export TOWER_ACCESS_TOKEN="YOUR_SEQERA_API_TOKEN"
```

Add this line to your `~/.bashrc` or `~/.profile` file on Expanse to persist the token across sessions.

### 2. Launch Workflow from Nextflow CLI and Monitor

#### 2.1. Launching Workflows from the Nextflow CLI with `-with-tower`

Once your `TOWER_ACCESS_TOKEN` is set, you can launch Nextflow workflows directly from the command line using the `-with-tower` flag. This allows you to leverage Seqera's monitoring and management capabilities, as long as your local Nextflow configuration is linked to your Seqera account.

```bash
nextflow run hello-workflow-4.nf -with-tower -profile slurm_debug
```

This command will execute the workflow, and its progress will be visible in your Seqera Platform dashboard. For more details, refer to the [Nextflow training materials on using Seqera Platform to capture and monitor Nextflow jobs launched from the CLI](https://training.nextflow.io/2.0/hello_nextflow/10_hello_seqera/#1-use-seqera-platform-to-capture-and-monitor-nextflow-jobs-launched-from-the-cli).

#### 2.2. Monitor Progress in Seqera UI

After launching the workflow with `-with-tower`, navigate to your Seqera Platform dashboard in your web browser. You should see your workflow listed with its real-time status, logs, and resource utilization.

### 3. Create Compute Environment and Launch from Seqera UI

To fully leverage Seqera's capabilities for managing and executing workflows on Expanse, you need to configure a compute environment and launch pipelines directly from the Seqera UI.

#### 3.1. Configure a Compute Environment for Expanse

Within your Seqera workspace, navigate to the "Compute Environments" section and create a new one with the following details:

1.  **Name:** `expanse-compute`
2.  **Credentials:** Select `Managed identity cluster`. You will need to provide `login.expanse.sdsc.edu` as the host and configure an SSH key for authentication. This usually involves generating an SSH key pair and adding the public key to your `~/.ssh/authorized_keys` file on Expanse. **Important:** Seqera needs to be able to SSH to Expanse without a Time-based One-Time Password (TOTP). To enable this, you will need to open a ticket through ACCESS ([https://access-ci.atlassian.net/servicedesk/customer/portal/2/group/3/create/17](https://access-ci.atlassian.net/servicedesk/customer/portal/2/group/3/create/17)) to allow the Seqera IP range to bypass TOTP. You can find the exact IP range at [https://community.seqera.io/t/seqera-platform-ip-addresses/1120](https://community.seqera.io/t/seqera-platform-ip-addresses/1120).
3.  **Work directory:** First, create a directory on Expanse: `mkdir /expanse/lustre/scratch/$USER/temp_project/nextflow`. Then, in Seqera, specify the absolute path to this directory (e.g., `/expanse/lustre/scratch/your_username/temp_project/nextflow`), replacing `your_username` with your actual username.
4.  **Launch directory:** Leave this field empty.
5.  **Queue names:** Use `debug` for the head queue and `compute` for the compute queue.
6.  **Head job submit options:** In the advanced options, add: `--account=YOUR_PROJECT_ACCOUNT --time=00:30:00 --nodes=1 --ntasks=1`. Remember to replace `YOUR_PROJECT_ACCOUNT` with your actual project account.

Refer to the [Seqera documentation for HPC setup](https://docs.seqera.io/platform/compute-environments/hpc/) for more detailed instructions on each of these steps.

#### 3.2. Configure Pipeline in Seqera Launchpad

Once your compute environment is configured, you can configure a pipeline in the Seqera Launchpad:

1.  Navigate to the "Launchpad" section in your Seqera workspace.
2.  Click "Add pipeline".
3.  In "Pipeline to launch", enter: `https://github.com/zonca/expanse_nextflow`
4.  Set "Revision" to `main`.
5.  Enable the "Pull latest" button.
6.  Set "Work directory" to `/expanse/lustre/scratch/zonca/temp_project/nextflow`.
7.  In "Config profiles", select `slurm debug`. This profile is automatically pulled from the `nextflow.config` file in the repository.

#### 3.3. Launch Pipeline

After configuring the pipeline in the Launchpad, go to your Seqera dashboard. Find the `expanse_nextflow` pipeline and click "Launch". This action will submit a single job to the `debug` queue on Expanse to execute Nextflow. This Nextflow process will then submit the actual workflow jobs to the appropriate queues as defined in your pipeline. Real-time updates and logs for all jobs will flow directly into the Seqera.io UI, allowing you to monitor the entire workflow execution.

#### 3.4. Launching Workflows with the `tw` Command-Line Tool

The `tw` command-line tool is a powerful utility that allows you to interact with the Seqera Platform directly from your terminal. It provides a convenient way to launch, manage, and monitor your Nextflow workflows without needing to access the web UI. This tool can be run from your local laptop or any machine with network access to Seqera Platform, not just Expanse.

You can install the `tw` CLI by following the instructions on the [Seqera documentation](https://docs.seqera.io/platform/getting-started/install-cli/).

Once installed and configured with your `TOWER_ACCESS_TOKEN`, you can trigger workflows using a command like this:

```bash
tw launch -w org/workspace expanse_nextflow
```

Replace `org/workspace` with your actual Seqera organization and workspace name. This command will launch the `expanse_nextflow` pipeline configured in your Seqera workspace, and you can monitor its progress directly from the Seqera UI or using other `tw` commands.

### Conclusion: Impressed by Seqera

I must say I am impressed by Seqera; it is so well-built and polished. You can configure and launch pipelines, view all tasks executing in real-time in a fancy web dashboard, then dig into the logs, check resource utilization for each stage of the pipeline, check execution time task by task, and much more. It truly streamlines the management and monitoring of complex Nextflow workflows on HPC systems like Expanse.