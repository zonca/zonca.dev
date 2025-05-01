---
categories:
- pysm
- cmb
date: '2025-05-01'
layout: post
title: BK18 Added to Panexp Model Suite and New Websky Radio Source Models in PySM 3.4.1
---

Following up on my [previous post about Panexp model suite simulations](./2025-03-30-panexp-model-suite-planck-wmap.md), there have been several important updates:

## BK18 Simulation Now Available

The BK18 experiment has been added to the available Panexp model suite simulations. You can find details and download links here:

[Panexp BK18 Simulation Documentation](https://github.com/simonsobs/map_based_simulations/tree/main/mbs-s0020-20250423#readme)

## New Websky Radio Source Models in PySM 3.4.1

The latest PySM release (3.4.1) introduces two new Websky radio-source models:

- **rg2**: Brightest sources, beam-convolved on the fly with `pixell`
- **rg3**: Pre-simulated background to be interpolated

**Note:** If you plan to use the `rg2` model, please update `pixell` to version 0.28.4 or later.

## Updated Simulations

All the latest five simulations (SO, WMAP, Planck, BK18, and component separation) now include simulations of `rg1`, `rg2`, and `rg3`. Additionally, all of them (except the component separation simulation, due to space constraints) now provide new combined maps of Galactic foregrounds plus Websky (`rg2`, `rg3`, `ksz1`, `tsz1`, `cib1`).

For full details and access to the data, see:

[Available Simulations Documentation](https://github.com/simonsobs/map_based_simulations/tree/main?tab=readme-ov-file#available-simulations)