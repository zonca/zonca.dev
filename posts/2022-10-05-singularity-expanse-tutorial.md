---
date: '2022-10-05'
layout: post
title: Singularity on Expanse tutorial

---

As one of my last tasks in XSEDE, I updated and improved the tutorial about running Singularity containers in the HPC system Espanse at my institution the [San Diego Supercomputer Center](https://sdsc.edu).

The new version of the tutorial is available on the [Github repository `zonca/expanse_singularity`](https://github.com/zonca/expanse_singularity)

See the `README.md` file for the table of contents linking to the subsection.

The most important changes were focused on using pre-built containers, either from DockerHub or from the repository maintained by SDSC's Marty Kandes, and on building custom images either via Sylabs Builder, a cloud-based service that builds containers on demand, or using a Virtual Machine on Jetstream 2, the NSF-funded Openstack cloud deployment.
