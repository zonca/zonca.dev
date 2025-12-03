---
categories:
- cosmology
- planck
date: 2013-09-17 07:12
layout: post
slug: clviewer-interactive-plot-of-cmb-spectra
title: ClViewer, interactive plot of CMB spectra

---

Just a quick post to link a web application I developed this weekend: ClViewer (app no longer available).

It is an interactive plotter of CMB Angular Power Spectra, it comes loaded with the latest Planck 2013 Best fit $C_\ell$ and the WMAP 9 year Best fit.

It allows to:

* Switch between TT, TE, EE and BB (simulated with $r=0.1$)
* Log scale on X and Y axis
* Zoom on a detail of the plot
* Choose plotting $D_\ell = \frac{\ell(\ell+1)C_\ell}{2\pi}$ or just $C_\ell$
* Upload your own power spectrum (text file with columns `L TT TE EE BB` or `L TT`) and compare it with Planck/WMAP
* Share the view with a permalink (app no longer available)

For the geeks, the technology stack is:

* [Flask](http://flask.pocoo.org/) for the backend
* [D3.js](http://d3js.org/) for the plotting
* [Heroku](https://www.heroku.com/) for the hosting
* [Gist](https://gist.github.com/) for storage of uploaded spectra

It is released as Open Source on Github: <https://github.com/zonca/clviewer>
