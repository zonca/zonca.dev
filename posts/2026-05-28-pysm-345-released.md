---
categories:
- python
- astronomy
- pysm
date: '2026-05-28'
layout: post
title: "PySM 3.4.5: HalfDome TSZ model, scipy pin removed, Python 3.9 dropped"
---

PySM 3.4.5 is now available on [PyPI](https://pypi.org/project/pysm3/3.4.5/) and [GitHub](https://github.com/galsci/pysm/releases/tag/3.4.5).

Changes in this release:

- **HalfDome TSZ model** (`tsz4`) — thermal SZ emission from the [HalfDome simulations](https://doi.org/10.48550/arXiv.2407.17462), eleven realizations available at Nside=8192. See the [tsz4 documentation](https://pysm3.readthedocs.io/en/latest/models.html).
- **Relaxed SciPy upper bound** — removed the `scipy < 1.15` pin. This was a workaround for a [healpy bug](https://github.com/healpy/healpy/issues/987) with scipy 1.15+, fixed in [healpy 1.18.1](https://github.com/healpy/healpy/releases/tag/1.18.1). PySM now requires `healpy >= 1.18.1`.
- **Dropped Python 3.9 support** — EOL since October 2025, and healpy >= 1.18.1 only ships wheels for Python >= 3.10.

Code: [github.com/galsci/pysm](https://github.com/galsci/pysm)

Upgrade with:

```
pip install --upgrade pysm3
```
