---
categories:
- python
- healpy
date: '2024-07-17'
layout: post
title: Run (part of) healpy in the browser with pyodide
---

Thanks to the help of [`@VeerioSDSC`](https://github.com/VeerioSDSC) and [Rick Wagner](https://github.com/rpwagner), I have been able to run part of `healpy` in the browser.
For now only tested reading FITS maps and plotting with `projview`.

Compiling the C++ and Cython extensions was difficult so for experimental purposes we opted for stripping `healpy` of all extensions making it a pure Python package, see <https://github.com/healpy/pyhealpy>

Then it is possible to build a wheel of `healpy` compiled to Javascript with `pyodide` and `emscripten`, see: 
<https://github.com/healpy/pyhealpy/blob/pyhealpy/README.md>

Once the wheel is available it is possible to load it in a web page and use it,
see the page source at:

[`index.html` for plotting a fits map in the browser](https://github.com/healpy/pyhealpy/blob/pyhealpy/index.html)

See the [generated website](https://healpy.github.io/pyhealpy/), open the Developer console to see the logs.

Details on [how to use Github Actions to build and deploy](https://github.com/healpy/pyhealpy/blob/pyhealpy/.github/workflows/pyodide.yml).

![Screenshot](healpy_pyodide_screenshot.png)

## JupyterLite

We can also run JupyterLite in the browser and import this package, see a preliminary test at:

<https://github.com/healpy/pyhealpy/tree/pyhealpy/jupyterlite>

it is deployed at <https://healpy.github.io/pyhealpy/jup/lab/index.html>

This allows to run JupyterLite, load healpy, read maps loaded into JupyterLite with `healpy`, it is also possible to use [`jupyterlab-open-url-parameter`](https://jupyterlab-contrib.github.io/jupyterlab-open-url-parameter.html) to retrieve a map at runtime. However there are several limitations:

* loading maps via fromUrl is very slow and works only for tiny maps, even a 30 MB map is too large and makes JupyterLite hang for minutes
* `pyhealpy` only supports maps in `ring` ordering, maps in `nest` ordering require `ring2nest` functionality which is not imported from the C++ package.
