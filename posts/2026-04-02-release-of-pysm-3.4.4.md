---
categories:
- openscience
- pysm
- python
date: '2026-04-02'
layout: post
title: PySM 3.4.4 Released with New SZ Models and NumPy 2 Support
---

PySM 3.4.4 is now published on [PyPI](https://pypi.org/project/pysm3/3.4.4/). This release is mostly about extending the Sunyaev-Zeldovich model suite and making sure PySM works cleanly with NumPy 2.

The main addition is a new set of SZ presets:

- `tsz2`: thermal SZ from the [Agora simulations](https://doi.org/10.1093/mnras/stae1031), based on the BAHAMAS hydrodynamical simulations, available at `Nside=8192`
- `tsz3`: lensed thermal SZ from the Agora simulations, also at `Nside=8192`
- `tsz4`: thermal SZ from [HalfDome 0.1](https://doi.org/10.48550/arXiv.2407.17462), generated with xgpaint and Battaglia16 profiles, with 11 realizations available through `template_name` seeds `100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120`
- `ksz2`: kinetic SZ from the Agora simulations at `Nside=8192`
- `ksz3`: lensed kinetic SZ from the Agora simulations at `Nside=8192`

The published PySM documentation now includes the notebook I added to compare the WebSky and Agora SZ templates:

<https://pysm3.readthedocs.io/en/latest/preprocess-templates/verify_templates/compare_websky_agora_sz.html>

If you want the short reference page for these presets, see the SZ section in the models documentation:

<https://pysm3.readthedocs.io/en/latest/models.html#sunyaev-zeldovich-emission>

On the compatibility side, PySM 3.4.4 adds NumPy 2 support by replacing the deprecated `np.trapz` call with `numpy.trapezoid`. This is the main change needed for users upgrading scientific Python environments to NumPy 2 while keeping PySM in their pipeline.

The full release notes are on GitHub:

<https://github.com/galsci/pysm/releases/tag/3.4.4>
