---
categories:
- github
date: '2025-01-29'
layout: post
title: Save Jupyterlite Notebooks to GitHub
---

## Introduction

JupyterLite runs entirely inside the browser, which means it doesn't have access to the underlying operating system. Its storage is persistent across restarts of the machine but could be deleted if the browser cache is cleared.

In this tutorial we demonstrate how to authenticate to Github in the browser interactively without pre-generating a token and how to save a snapshot of a notebook to a GitHub repository.

To authenticate with GitHub, we use a device auth flow, the same used by the `gh` CLI, i.e. you get a code, paste that into Github.

## Device Auth Flow

Due to security restrictions in the browser, we need to have a service deployed that submits requests to the GitHub API. See the tutorial [Authenticate to GitHub in the Browser with the Device Flow](./2025-01-29-github-auth-browser-device-flow.md) on how to deploy that on Render.com.

## Steps to Authenticate and Save Notebooks

1. Go to [JupyterLab](https://jupyter.org/try-jupyter/lab/).
1. Upload the 3 files `github_auth_py.ipynb`, `github_uploader.py`, `test_save_notebook.ipynb` from the repository <https://github.com/zonca/github_auth_proxy_render/tree/main/python>
2. Execute `github_auth_py.ipynb`. This notebook will perform the device auth flow and store a token.
3. Next, execute `test_save_notebook.ipynb`. This notebook demonstrates how to execute a notebook and then save it into a GitHub repository with a timestamp, ensuring a snapshot of the notebook is permanently stored on GitHub. This is using the Github API directly to upload a file to a repository.

I also tested using `PyGithub`, `pygit2` and `dulwich`, but none of them worked in JupyterLite.

## Conclusion

This is just a prototype to explore the capabilities and a starting point for thinking about strategies to deal with the ephemeral storage provided by JupyterLite.