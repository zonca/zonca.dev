---
aliases:
- /2020/03/kill-jupyter-notebook
categories:
- python
- jupyter
date: '2020-03-12'
layout: post
slug: kill-jupyter-notebook
title: Kill Jupyter Notebook servers

---

Just today I learned how to properly stop previously running Jupyter Notebook
servers, here for future reference:

    jupyter notebook stop

This is going to print all the ports of the currently running servers.
Choose which ones to stop then:

    jupyter notebook stop PORTNUMBER
