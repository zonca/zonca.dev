---
categories:
- python
- jupyter
date: '2024-05-28'
layout: post
title: Jupyter Notebook frontmatter for Quarto to download source notebook
---

[Quarto](https://quarto.org/) is one of the best platforms to create statically generated blogs with Markdown and Jupyter Notebooks.

I switched `zonca.dev` to Quarto [back in 2022](./2022-09-27-migrate-fastpages-quarto-preserve-history.md).

It is convenient to give the possibility to users to download the `.ipynb` source of a page when that page is generated from a Jupyter Notebook, so that they can execute it themselves.

Quarto supports this out of the box using this frontmatter as the first cell of a Notebook (in Raw format):

```
---
layout: post
toc: true
format:
  html: default
  ipynb: default
date: '2024-05-28'
categories:
- category1
- category2
---
```
