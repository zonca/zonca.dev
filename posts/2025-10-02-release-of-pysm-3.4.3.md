---
categories:
- openscience
- pysm
- python
date: '2025-10-02'
layout: post
title: PySM 3.4.3 Released
---

PySM version 3.4.3 is now live. Install it from [PyPI](https://pypi.org/project/pysm3/) or upgrade existing environments with `pip install --upgrade pysm3`. Full details are available in the [GitHub release notes](https://github.com/galsci/pysm/releases/tag/3.4.3).

Highlights in this release include:

- Documentation and citation updates now reference the published PanEx ApJ paper ([#227](https://github.com/galsci/pysm/pull/227)).
- The radio galaxies catalog underpinning the `rg2` model has the correct ordering and a shape compatible with `numpy.polyval`, improving reliability of radio source simulations ([#225](https://github.com/galsci/pysm/pull/225)).
- The CMB dipole component is finalized with fresh tests, documentation, and preset refinements so the new `dip` presets are ready for production workflows ([#220](https://github.com/galsci/pysm/pull/220)).
- A comprehensive implementation of the CMB dipole model rolls out the `dip1` and `dip2` components, extends unit coverage, refines test output, and fixes monopole/dipole handling in `CMBLensed` ([#215](https://github.com/galsci/pysm/pull/215)).

Let us know how PySM 3.4.3 works for your simulations, and file issues or discussion topics on the [galsci/pysm repository](https://github.com/galsci/pysm) if you run into anything unexpected.
