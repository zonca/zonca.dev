---
layout: post
title: Execute Jupyter Notebooks not interactively
date: 2019-09-23 12:00
categories: [jupyter, notebook, condor]
slug: batch-notebook-execution
---

Over the years, I have explored how to scale up easily computation through
Jupyter Notebooks by executing them not-interactively, possibily parametrized
and remotely. This is mostly for reference.

* [`nbsubmit`](https://github.com/zonca/nbsubmit) is a Python package which has Python API to send a local notebook for execution on a remote SLURM cluster, for example Comet, see [an example](https://github.com/zonca/nbsubmit/blob/master/example/multiple_jobs/submit_multiple_jobs.ipynb). This project is not maintained right now.
* Back in 2017 I tested submitting notebooks to Open Science Grid, see [the `batch-notebooks-condor` repository](https://github.com/zonca/batch-notebooks-condor)
* Back in 2016 I created scripts to template a Jupyter Notebook and launch SLURM jobs, see [`slurm.shared.template`](https://github.com/sdsc/sdsc-summer-institute-2016/blob/master/hpc3_python_hpc/slurm.shared.template) and [`runipyloop.sh`](https://github.com/sdsc/sdsc-summer-institute-2016/blob/master/hpc3_python_hpc/runipyloop.sh)
