---
categories:
- jupyter
- teaching
- python
date: '2026-05-18'
layout: post
title: "Do You Need JupyterHub for Your Workshop? JupyterLite Runs Python Entirely in the Browser"
---

You're organizing a Python workshop or teaching a class that uses Jupyter notebooks.
The first question that comes up is almost always the same: **how do I get everyone running notebooks without spending an hour on installation?**

The traditional answer has been JupyterHub — a server that hosts Jupyter for all your participants.
But there's a simpler option that works for many scenarios: **JupyterLite**, which runs Python entirely in the browser with zero server infrastructure.

## JupyterHub: Powerful but Demanding

JupyterHub (https://jupyter.org/hub) is the gold standard for multi-user notebook hosting.
It gives every participant their own isolated Jupyter server, with full access to the host's Python environment, filesystem, and computing resources.

**When you need JupyterHub:**

- Your workshop requires **GPU access** or heavy computation
- Participants need to work with **large datasets** that don't fit in browser memory
- You need **persistent storage** across sessions
- You're running **custom kernels** (R, Julia, etc.) beyond Python
- Your code requires **network access** to external APIs or databases during execution
- You need to run code that depends on **native system libraries** not available in WebAssembly

The trade-off? JupyterHub requires a server (cloud VM, Kubernetes cluster, or HPC system), ongoing maintenance, and someone to manage it.
If you're deploying on cloud infrastructure, I've written about [deploying JupyterHub on OpenStack Magnum with OpenTofu](/posts/2026-04-22-deploy-jupyterhub-openstack-magnum-tofu/) — it works well, but it's not trivial.

## JupyterLite: Zero Server, Zero Installation

JupyterLite (https://github.com/jupyterlite/jupyterlite) takes a completely different approach: it runs a full Python environment compiled to **WebAssembly** directly in the browser.
No server, no installation, no setup time — participants just open a URL and start coding.

**JupyterLite is ideal when:**

- You want **zero setup time** — participants open a link and start coding immediately
- You're teaching **introductory Python** with standard scientific packages
- Your workshop is **short** (a few hours) and doesn't need persistent storage
- You don't have infrastructure budget or time to set up a server
- You want participants to **continue practicing at home** without installing anything
- You need **offline capability** — once loaded, notebooks work without internet

### Scientific Python in the Browser

A common concern is whether the browser-based Python environment can handle real scientific computing.
Thanks to **Pyodide** (the Python-in-WebAssembly runtime that powers JupyterLite), many of the most important scientific Python packages work out of the box — including packages with C extensions that have been compiled to WebAssembly:

| Package | What It Does | C Extensions? |
|---------|-------------|---------------|
| **NumPy** | Array computing, linear algebra | Yes |
| **SciPy** | Scientific algorithms, optimization, statistics | Yes |
| **Matplotlib** | Plotting and visualization | Yes |
| **Pandas** | Data manipulation and analysis | Yes (via NumPy) |
| **scikit-learn** | Machine learning | Yes |

These five packages cover the vast majority of introductory scientific Python curricula.
In fact, the entire Software Carpentry Python Novice curriculum — both the Inflammation and Gapminder tutorials — runs perfectly in JupyterLite because it only needs NumPy, Matplotlib, and Pandas.

Other notable packages available in Pyodide include **scikit-image**, **statsmodels**, **sympy**, and **astropy**.
You can check the full list of available packages in the [Pyodide documentation](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

### What Doesn't Work (Yet)

JupyterLite has some limitations you should be aware of:

- **Network access from Python**: The browser security model restricts raw socket access, so packages like `astroquery` that make direct HTTPS connections won't work
- **HDF5 support**: `h5py` and `pytables` are not currently available in Pyodide
- **Very large datasets**: Browser memory is limited (typically 2-4 GB per tab)
- **GPU computing**: No CUDA or GPU access from WebAssembly
- **Persistent filesystem**: Data saved in the notebook disappears when you close the tab (though you can download notebooks)
- **Custom kernels**: Only Python (via Pyodide) and JavaScript kernels are available

## A Real Example: Software Carpentry Tutorials on JupyterLite

To demonstrate that JupyterLite works for real teaching material, I've deployed the Software Carpentry Python tutorials as a live JupyterLite site:

https://zonca.github.io/jupyterlite-carpentry/lab/

This site includes two complete tutorials converted from the original Carpentries markdown episodes into interactive notebooks:

- **Python Novice: Inflammation** — Introduction to Python using inflammation data analysis (NumPy, Matplotlib)
- **Python Novice: Gapminder** — Introduction to Python using Gapminder GDP data (Pandas, Matplotlib)

The source code for this deployment is at https://github.com/zonca/jupyterlite-carpentry — it uses GitHub Pages with a GitHub Actions workflow that builds the JupyterLite site automatically on every push to main.
The tutorial content is licensed under [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) following the original Software Carpentry licensing.

### How the Deployment Works

The entire deployment is surprisingly simple:

1. **Notebooks and data** live in a `content/` directory
2. `jupyter lite build --contents content` compiles them into a static JupyterLite site
3. The built `_output/` directory is deployed to GitHub Pages via Actions
4. Participants access the site at `https://<username>.github.io/<repo>/lab/`

That's it. No Kubernetes, no Helm charts, no SSL certificates, no user authentication.
The entire site is just static files served by GitHub.

## Decision Guide: JupyterHub or JupyterLite?

| | JupyterLite | JupyterHub |
|---|---|---|
| **Setup effort** | Minutes (push to GitHub) | Hours to days |
| **Server cost** | Free (GitHub Pages) | Cloud VM costs |
| **Installation** | None for participants | None for participants |
| **Python packages** | Pyodide subset | Full conda/pip |
| **Data size** | Small (< 100 MB) | Unlimited |
| **Computation** | Browser-only | Full server resources |
| **Persistence** | Download only | Persistent home directory |
| **Network access** | Limited | Full |
| **Offline** | Works after loading | Requires connection |
| **Maintenance** | None | Ongoing |

**My recommendation:** Start with JupyterLite for introductory workshops and short courses.
If your curriculum fits within the Pyodide package ecosystem (and most introductory Python does), you'll save enormous amounts of setup time and infrastructure cost.
Graduate to JupyterHub only when you need capabilities that the browser can't provide.

## Getting Started

To create your own JupyterLite deployment with custom notebooks:

```bash
pip install jupyterlite-pyodide-kernel jupyterlite
jupyter lite build --contents /path/to/your/notebooks
jupyter lite serve
```

Or fork https://github.com/zonca/jupyterlite-carpentry and replace the notebooks with your own — the GitHub Actions workflow will build and deploy automatically.
