---
categories:
- git
- github
date: '2023-03-16'
layout: post
title: Work on a Latex Document in Github Codespaces

---

I was exploring using Github Codespaces instead of Overleaf to work on a Latex document.

The most important missing component is the Latex editor, and the other downside is that it is free only for 90 hours per month (with a Pro academic account).
However, the other useful features of Overleaf are present:

* Works in the browser
* Syntax highlights Latex
* Editing of Latex source
* Integrate with version control
* Search and add citations from bibfile
* Builds the PDF automatically
* Shows preview of the PDF
* Shows error messages at the right line of the source file

On top of that, Codespace is a full machine, so you could run a Python script or a Jupyter Notebook to generate images for example.

See a screenshot of the environment

![Github codespaces with Latex Workshop](github_codespace_latex.png)

## How to set Github Codespaces for Latex

On the repository where you store the Latex project, click on the `Code` button and open a new Codespace.

In the terminal, install the Latex environment:

```
sudo apt install texlive texlive-science texlive-latex-extra latexmk
```

In the "Extensions" window, install the extension "Latex Workshop".

Open the "Tex" menu on the left bar to build the project with `latexmk` and open a tab within VS Code to visualize the PDF.
