---
title: "Execute Pegasus Jobs on Expanse"
date: 2025-09-09
categories:
  - Expanse
  - HPC
  - ACCESS
---

## What is Pegasus?

[Pegasus](https://pegasus.isi.edu/) is a workflow management system that helps scientists and engineers execute complex computational workflows. It maps a user's abstract workflow onto available distributed resources, manages data, and handles execution failures, making it easier to run scientific applications on high-throughput computing (HTC) systems like HTCondor.

## Accessing Pegasus on ACCESS

You can access a hosted version of Pegasus through ACCESS. You will need an existing ACCESS account.

1.  Go to [https://support.access-ci.org/tools/pegasus](https://support.access-ci.org/tools/pegasus).
2.  Click on "Local shell access" to get a terminal.

## Setting up HTCondor Annex on Expanse

We will follow the documentation for HTCondor Annex, specifically the steps outlined in [https://access-ci.atlassian.net/wiki/spaces/ACCESSdocumentation/pages/564887666/HTCondor+Annex](https://access-ci.atlassian.net/wiki/spaces/ACCESSdocumentation/pages/564887666/HTCondor+Annex).

### 1. Generate SSH Key

First, generate an SSH key specifically for the annex:

```bash
ssh-keygen -f ~/.ssh/annex
```

### 2. Configure SSH

Add the following configuration to your `~/.ssh/config` file. This tells SSH to use the newly generated key for Expanse.

```
Host expanse.sdsc.edu *.expanse.sdsc.edu
   User MYUSERNAME # Replace MYUSERNAME with your Expanse username
   IdentityFile ~/.ssh/annex
```

**Permissions:** Ensure your `~/.ssh/config` file has the correct permissions (read-only for your user) to prevent errors:

```bash
chmod 600 ~/.ssh/config
```

### 3. Copy SSH Key to Expanse

Copy your public SSH key to Expanse. You will be prompted for your password and MFA code.

```bash
ssh-copy-id -i ~/.ssh/annex.pub MYUSERNAME@expanse.sdsc.edu
```

### 4. Create a Sample HTCondor Job

Before creating an annex, HTCondor requires a job to execute. Create a file named `many_hostname.sub` with the following content:

```condor
executable      = /bin/hostname
output          = out.$(Cluster).$(Process)
error           = err.$(Cluster).$(Process)
log             = log.$(Cluster)

# 1 core per task so the partitionable slot can split into many tasks
request_cpus    = 1
request_memory  = 512MB
request_disk    = 100MB

# Keep these jobs on the annex
+MayUseAWS      = False
requirements    = (AnnexName == "zonca") # You can change "zonca" to your desired annex name

queue 128
```

### 5. Submit the Sample Job

Submit the job using `condor_submit`:

```bash
condor_submit many_hostname.sub
```

### 6. Create the HTCondor Annex

Now you can create the HTCondor annex. Remember to replace `MYUSERNAME` with your Expanse username and set your `PROJECT_ID`.

```bash
export PROJECT_ID=YOUR_ALLOCATION_ID # Set the ID of your allocation on Expanse
htcondor annex create --nodes 1 --lifetime 3600 --project $PROJECT_ID $USER compute@expanse
```

### Extending or Adding Resources to the HTCondor Annex

To extend the lifetime or add more nodes to an existing HTCondor annex, use the `htcondor annex add` command:

```bash
htcondor annex add --project $PROJECT_ID --nodes 1 --lifetime 3600 $USER compute@expanse
```

### Monitoring and Output

To check the status of your HTCondor annex, use:

```bash
htcondor annex status $USER
```

During execution, you can also log in to Expanse and monitor the job using `squeue`:

```bash
squeue -u $USER
```

Once the job is completed, it will create many `out.*` files in your submission directory. Each of these files will contain the hostname of the machine where that specific job ran. Since we requested only 1 node for the annex in this example, all `out.*` files will likely contain the same hostname.

## Running Jobs with Pegasus (Unsuccessful Attempt)

I attempted to configure Pegasus to run jobs through the HTCondor annex, but I was unable to get it to work properly. I found the process of configuring Pegasus surprisingly difficult. Here's a gist of what I managed to achieve, though it did not result in a successful Pegasus workflow execution through the annex:

[https://gist.github.com/zonca/94b99a5590c43eba2f47d3514b166c88](https://gist.github.com/zonca/94b99a5590c43eba2f47d3514b166c88)
