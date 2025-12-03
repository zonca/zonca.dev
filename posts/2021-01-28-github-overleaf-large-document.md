---
categories:
- git
- github
- latex
- overleaf
date: '2021-01-28'
layout: post
title: Handle a large LaTeX document on Overleaf with a free account

---

Overleaf is a great tool for collaborative writing of LaTeX documents. However, the free account has a limit of 60 seconds for the compilation time.
This is usually enough for a paper, but if you have a large document, like a thesis or a report, it might take longer to compile.

One solution is to split the document in chapters and compile them separately, but then you loose the cross-references.

Another solution is to use Github Actions to compile the document on every push.

I have created a repository with a working example: <https://github.com/zonca/overleaf_largedoc_main>

## Setup

* Create a repository on Github
* Link it to Overleaf (you need a paid account for this, or you can use the git link which is available for free accounts too, see [the documentation](https://www.overleaf.com/learn/how-to/Git_integration))
* Add the `.github/workflows/main.yml` file from my example repository
* Push to Github

Now every time you push to Github (or sync from Overleaf), the document will be compiled and the PDF will be available as an artifact.

See the logs of a successful run: (link removed as Github Action logs expire)

## How it works

The workflow uses a Docker container with a full TexLive installation, so it has all the packages you might need.
It uses `latexmk` to compile the document, which automatically handles dependencies and runs `pdflatex` / `bibtex` as many times as needed.

You can customize the `main.yml` file to change the document name or add extra packages.
