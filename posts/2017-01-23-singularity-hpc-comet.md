---
aliases:
- /2017/01/singularity-hpc-comet
categories:
- singularity
- comet
- xsede
date: 2017-01-23 11:00
layout: post
slug: singularity-hpc-comet
title: Using Singularity on SDSC Comet

---

The [San Diego Supercomputer Center](http://sdsc.edu) has recently deployed [Singularity](http://singularity.lbl.gov/) on Comet.
This allows any user to execute containers in a batch job.

Singularity allows to pack a full operating system and its applications into a single image file, copy it to Comet and execute it seamlessly.
For example if you have a workflow that runs on Ubuntu and needs some packages that are difficult to install on CentOS (the OS of Comet), you can build a Ubuntu image on your laptop, install what you need and then run it on Comet.

Most of the documentation available online for Singularity refers to the upcoming version 2.3, instead currently on Comet we have version 2.2.1, so some commands are slightly different.

## Build the image

You need a Linux machine to build a Singularity image, if you have Mac or Windows, you need to install Vagrant and Virtualbox and run a Linux Virtual Machine. Singularity provides a script to do this easily, see [the docs](http://singularity.lbl.gov/docs-build-container).

Once you have a Linux terminal, you can create an image, I had issues with the size of the image so I recommend using `ext3` instead of `squashfs`:

    singularity create -s 4000 --fs ext3 ubuntu.img

`4000` is the size in MB.

Then you can bootstrap the image using a definition file, for example `ubuntu.def`:

    BootStrap: debootstrap
    OSVersion: xenial
    MirrorURL: http://archive.ubuntu.com/ubuntu/

    %post
        sed -i 's/main/main restricted universe/g' /etc/apt/sources.list
        apt-get update
        apt-get -y install python-numpy

With:

    sudo singularity bootstrap ubuntu.img ubuntu.def

If you need to modify the image, you can open a shell inside the image with:

    sudo singularity shell -w ubuntu.img

The `-w` option allows to write into the image, so you can install new packages with `apt-get`.

## Execution on Comet

Copy the image to Comet (e.g. `scp` or `rsync` or Globus) to your scratch folder `/oasis/scratch/comet/$USER/temp_project`.

Login to Comet and request an interactive node:

    srun --pty --nodes=1 --ntasks-per-node=24 -p compute -t 00:30:00 --wait 0 /bin/bash

Load the module:

    module load singularity

Execute a command inside the image:

    singularity exec /oasis/scratch/comet/$USER/temp_project/ubuntu.img cat /etc/issue

This should print: `Ubuntu 16.04.1 LTS \n \l`.

You can notice that you are running with your own user, not root, and your home folder is automatically mounted in the container, so you can access your data.

## Access other folders

If you want to access your scratch folder, you need to create the folder inside the image (once):

    sudo singularity exec -w ubuntu.img mkdir -p /oasis

Then, on Comet, you can specify to bind mount that folder:

    singularity exec -B /oasis /oasis/scratch/comet/$USER/temp_project/ubuntu.img ls /oasis/scratch/comet/$USER/temp_project

## MPI

It is also possible to run MPI jobs with Singularity, but you need to install the same version of MPI inside the container and on the host system.
On Comet we use `mvapich2/2.1` or `openmpi_ib/1.10.2`.

## Documentation

See the [official Singularity documentation](http://singularity.lbl.gov/docs-home) and the [SDSC User Portal](https://portal.xsede.org/sdsc-comet) (needs login) for more details.

Allocations on Comet are available to any US researcher, see [XSEDE Allocations](link removed as XSEDE is retired).
