---
categories:
- git
- github
date: '2023-02-02'
layout: post
title: Work on Latex Document with Github and Overleaf

---

In the past I have written about [coordinating a large document using multiple overleaf documents and Github repositories](https://www.zonca.dev/posts/2021-01-28-github-overleaf-large-document).
In this post I will just layout the simpler case where we have a Latex document on Overleaf and we also want users to be able to work on it from Github and we want Github Actions to automatically build a PDF for every commit.

## Create less privileged user on Github

A concern about using Overleaf is that to have the convenience of pushing and pulling from Github, it asks for write permissions to all repositories.

So just to play it safe, it is useful to create a new user on Github, for example mine is called `@zoncaoverleafbot`, which has write access only to this repository.

It is useful to be logged in with your official Github user in your browser and be logged in inside an Incognito window with your "Overleaf bot" user.

## Create repository on Github

Let's start with a Latex document on Overleaf, for example I used the ["Astronomy & Astrophysics" template](https://www.overleaf.com/read/vtmsqrxpnhzn) for testing.

Starting with a project on Overleaf is more complicated because of permission issues, so in case you have an Overleaf project, just download it locally.

Create a new repository on Github, this should be under your "real" Github account or any organization you have access to, upload the Latex document and all ancillary files.

See for example my repository <https://github.com/zonca/overleaf_github>, you could also fork this repository under your account.

Finally, give "Write" access to your Overleaf bot user.

## Create the linked project on Overleaf

Now login to Github with your "Overleaf bot" account, then login to Overleaf.

Click on "New project" => "Import from Github", select your repository.

This will create a project on Overleaf that is automatically linked to the Github repository.

## How to edit on Overleaf

Now both you and all your collaborators, can use Overleaf to edit the document and then push to Github using your "Overleaf bot" user, they do not need to link their own Github user.

* use the Overleaf "Write"
* **Before making any edits**, click on Menu => Github => Pull changes from Github
* Make edits on Overleaf
* **Once you are finished editing**, even just for 1 or 2 hours, click on Menu => Github => Push changes to Github
* Edits will show up on Github as made by the "Overleaf bot" user , which avoids giving too much permissions to Overleaf
* Github is supposed to have the latest version of the document always

## Build the PDF on Github (Optional)

The easiest way to access the PDF is to get it from Overleaf. However, it might be useful to also have it available on Github. We can have Github actions build it and make it available as an artifact.

Customize the [`build_latex.yml`](https://github.com/zonca/overleaf_github/blob/main/.github/workflows/build_latex.yml) file to have Github actions build your PDF. 

The only downside is that the PDF is hidden inside the Github actions, to simplify access we can get a direct link to the latest PDF using the <https://nightly.link> service, just paste the URL to the `build_latex.yml`, for my repository:

* `https://github.com/zonca/overleaf_github/blob/main/.github/workflows/build_latex.yml`

This will provide a link of the form:

`https://nightly.link/zonca/overleaf_github/workflows/build_latex/main/PDF.zip`

which provides 1-click access to the latest PDF.

### Create releases with attached PDF on Github (Optional)

The Github Actions workflow also handles tagging releases, so if you create a tagged version in the repository, like `0,1` in git, for example:

    git tag -a 0.1 -m "Tagging version 0.1"
    git push --tags

This is going to create a Release on Github, which is visible on the homepage and attach the PDF to it, see [the example on my repository](https://github.com/zonca/overleaf_github/releases/tag/0.1).

To make this work, you need to grant writing permissions Github Action workflows, in the repository "Settings" => "Actions" => "General", select "Read and write permissions" under "Workflow permissions".
