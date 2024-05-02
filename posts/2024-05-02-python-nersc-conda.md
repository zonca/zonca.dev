---
categories:
- python
- nersc
date: '2024-05-02'
layout: post
title: Setup a conda environment at NERSC

---

NERSC recommends to use the ["Global Common"](https://docs.nersc.gov/filesystems/global-common/) to store Conda environments, because it is optimized to store lots of small files. Consider that it is mounted read-only on computing nodes.
The filesystem is organized by groups, so choose one of your groups:

    groups

for example for me it is the `cmb` group.

    GROUP=cmb
    mkdir -p /global/common/software/$GROUP/$USER/conda
    cd ~
    ln -s /global/common/software/$GROUP/$USER c

So we can access it quickly under `~/c`.


Then we create a Conda environment with `mamba`, specifying the version of python and other packages:

    export ENV=pycmb
    module load conda
    mamba create --prefix /global/common/software/$GROUP/$USER/conda/$ENV python==3.10 numpy astropy matplotlib ipykernel numba  pytest toml cython scipy namaster -c conda-forge

We can also set that path for `conda` to automatically search into, this will pickup also future Conda environments on the same path:

    conda config --append envs_dirs /global/common/software/$GROUP/$USER/conda

Moreover, this will be the default location for new environments, so we will be able to create other environments just with:

    mamba create --name onlypython python==3.11

And they will be automatically created in "Global Common Software".

We do not want that long path in our prompt, so (this is necessary if you created the environment with `--name`):

    conda config --set env_prompt '({name}) '

So we can activate the environment specifying only the name:

    conda activate $ENV

In order to use it also on `Jupyter@NERSC` you will need to register the kernel:

    ipython kernel install --name $ENV --user

Tip for CMB people, make sure you build `healpy` from source to get the best performance on Spherical Harmonics Transforms:

    CC=gcc CXX=g++ CFLAGS="-fPIC -O3 -march=native" CXXFLAGS="-fPIC -O3 -march=native" pip3 install --user --no-binary healpy --ignore-installed healpy
