---
categories:
- singularity
- git
- github
date: '2022-11-03'
layout: post
title: Build and host Singularity containers on Github

---

I present a demo repository configured to build Singularity containers using Github actions and then host them using the Github container registry:

* <https://github.com/zonca/singularity_github_ci/>

See how the [Github action workflow](https://github.com/zonca/singularity_github_ci/blob/main/.github/workflows/native-install.yml) is configured, based on the [Singularity Builder GitHub CI](https://github.com/singularityhub/github-ci).

See the [logs of a Ubuntu container build process](https://github.com/zonca/singularity_github_ci/runs/6718361783?check_suite_focus=true).

Once the container is built, it is shown [in the "Packages" section of the Github repository](https://github.com/zonca/singularity_github_ci/pkgs/container/singularity_github_ci), it can then be pulled locally with:

    singularity pull oras://ghcr.io/zonca/singularity_github_ci:ubuntu-20.04

