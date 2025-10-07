---
categories:
- python
- hpc
- sdsc
date: 2023-08-16 15:00
layout: post
slug: python-for-hpc-tutorial
title: Tutorial on Python for HPC at the SDSC Summer Institute

---

Each August the San Diego Supercomputer Center organizes a week-long summer school that teaches a large number of topics related to Supercomputing and AI to early career scientists.

For the past ~10 year I have been teaching "Python for HPC", this year tutorial is mostly based on `numba` and `dask`.

See the "Summer Institute" Github repository for all the notebooks I have used:

* <https://github.com/sdsc/sdsc-summer-institute-2023/tree/main/4.2a_python_for_hpc>

Notice another couple of interesting resources:

* [the Manifest to build the Singularity image used for the tutorial on the Expanse supercomputer](https://github.com/sdsc/sdsc-summer-institute-2023/blob/main/4.2a_python_for_hpc/singularity/Singularity.anaconda3-dask-numba)
* [scripts to launch Dask on Expanse](https://github.com/sdsc/sdsc-summer-institute-2023/tree/main/4.2a_python_for_hpc/dask_slurm)
* The Singularity container is available to all Expanse users at `/expanse/lustre/projects/sds166/zonca/dask-numba-si23.sif`
