---
categories: [hpc, sdsc]
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

### 1. Running Workflows with Seqera Platform

Instead of manually submitting Slurm jobs, we will now leverage the Seqera Platform to manage and execute our Nextflow workflows on Expanse. This provides a centralized interface for monitoring, collaboration, and advanced resource management.

#### 1.1. Create a Seqera Account and Workspace

If you don't already have one, create an account on [Seqera Platform](https://seqera.io/). Once logged in, create a new workspace for your projects.

#### 1.2. Configure a Compute Environment for Expanse

Within your Seqera workspace, you need to configure a compute environment that connects to Expanse. Follow these steps:

1.  **Name:** `expanse-compute`
2.  **Credentials:** Select `Managed identity cluster`. You will need to provide `login.expanse.sdsc.edu` as the host and configure an SSH key for authentication. This usually involves generating an SSH key pair and adding the public key to your `~/.ssh/authorized_keys` file on Expanse.
3.  **Work directory:** First, create a directory on Expanse: `mkdir /expanse/lustre/scratch/$USER/temp_project/nextflow`. Then, in Seqera, specify the absolute path to this directory (e.g., `/expanse/lustre/scratch/your_username/temp_project/nextflow`), replacing `your_username` with your actual username.
4.  **Launch directory:** Leave this field empty.
5.  **Queue names:** Use `compute` for both the default queue and any other relevant queue settings.

Refer to the [Seqera documentation for HPC setup](https://docs.seqera.io/platform/compute-environments/hpc/) for more detailed instructions on each of these steps.

#### 1.3. Link Nextflow to Seqera

To allow your local Nextflow installation to communicate with the Seqera Platform, you need to set the `TOWER_ACCESS_TOKEN` environment variable. You can generate an API token from your Seqera account settings.

```bash
export TOWER_ACCESS_TOKEN="YOUR_SEQERA_API_TOKEN"
```

Add this line to your `~/.bashrc` or `~/.profile` file on Expanse to persist the token across sessions.

#### 1.4. Run a Workflow via Seqera

Now, you can run your Nextflow workflow and have Seqera manage its execution on Expanse. The `-w` flag specifies the Seqera workspace, and the `-profile` flag can still be used for local Nextflow configurations.

```bash
nextflow run hello-workflow-4.nf -w YOUR_SEQERA_WORKSPACE_ID -profile slurm_debug
```

Replace `YOUR_SEQERA_WORKSPACE_ID` with the actual ID of your workspace in Seqera. You can find this in the URL when you are in your workspace (e.g., `https://platform.seqera.io/your_username/YOUR_SEQERA_WORKSPACE_ID`).

Seqera will now orchestrate the submission of your Nextflow workflow to Expanse, and you can monitor its progress, view logs, and manage resources directly from the Seqera Platform web interface.

### 2. Advanced Seqera Features: Slurm Executor and Singularity Integration

Seqera Platform seamlessly integrates with Nextflow's executors and container technologies, simplifying the management of complex workflows on HPC systems like Expanse.

#### 2.1. Slurm Executor Management

When you run a Nextflow workflow through Seqera, and your compute environment is configured for Slurm, Seqera automatically handles the submission of individual Nextflow tasks as separate Slurm jobs. This means you don't need to manually configure `nextflow.config` profiles for Slurm execution on the login node. Seqera's compute environment configuration takes care of mapping Nextflow processes to appropriate Slurm resources, queues, and accounts.

Seqera provides a rich interface to monitor these individual Slurm jobs, view their logs, and track resource consumption, offering a significant advantage over managing raw Slurm output files.

#### 2.2. Singularity Container Integration

Seqera also streamlines the use of container technologies like Singularity. If your Nextflow workflow specifies a container image (e.g., `container 'ubuntu:latest'`), Seqera will ensure that the specified Singularity image is pulled and used for the relevant processes on Expanse. You typically configure the container registry and any necessary authentication within your Seqera compute environment settings.

This eliminates the need for manual `module load singularitypro` commands or complex `nextflow.config` adjustments for container runtime. Seqera ensures that the correct container environment is set up for each task, promoting reproducibility and portability of your workflows.

For example, if your `nextflow.config` or workflow file includes:

```groovy
process convertToUpper {
    container 'docker.io/ubuntu:latest'
    // ... other process definitions
}
```

Seqera will handle the pulling and execution of the `ubuntu:latest` Singularity image on Expanse for the `convertToUpper` process, provided your compute environment is correctly configured to access Docker Hub or a mirrored registry.
