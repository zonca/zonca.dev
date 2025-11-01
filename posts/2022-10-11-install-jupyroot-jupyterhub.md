---
categories:
- jupyterhub
- kubernetes
layout: post
date: '2022-10-11'
title: Install the JupyROOT Python kernel in JupyterHub

---

After installing ROOT's conda package, for example with `micromamba`:

    micromamba create -n root -c conda-forge root python==3.8 matplotlib

and then installing the kernel for JupyterHub:

    ipython kernel install --name root --user

Unfortunately `import ROOT` gives the error:

```
ERROR in cling::CIFactory::createCI(): cannot extract standard library include paths!
Invoking:
  LC_ALL=C x86_64-conda-linux-gnu-c++   -DNDEBUG -xc++ -E -v /dev/null 2>&1 | sed -n -e '/^.include/,${' -e '/^ \/.*++/p' -e '}'
Results was:
With exit code 0
```

The fix, found after more than 1 hour of search, is at <https://root-forum.cern.ch/t/jupyroot-in-jupyterhub-cling-init-can-not-extract-standard-include-library-paths/46890>:

Edit the `kernel.json` file and modify the PATH variable:

```
{
 "argv": [
  "/home/jovyan/micromamba/envs/root/bin/python3.8",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "root",
 "language": "python",
 "metadata": {
  "debugger": true
 },
 "env": {
   "PATH": "/home/jovyan/micromamba/envs/root/bin/:${PATH}"    
 }
}
```
