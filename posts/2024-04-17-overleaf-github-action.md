---
categories:
- git
- github
date: '2024-04-17'
layout: post
title: 2-way Synchronization of Overleaf and Github via a Github Action

---

In the past I wrote tutorials on how to handle Github and Overleaf, the latest for example is [this](./2023-02-02-github-overleaf.md).
However the Github button in Overleaf is fragile, it often gets disconnected for unknown reasons, and it cannot be reconnected, it forces deletion of the Github repository. Moreover, it seems it is now a Premium feature. Finally, it needs to be triggered manually, and nobody remembers to do that.

I therefore decided to write a Github Action that can be configured to run automatically every hour to pull changes from Overleaf into Github using the `git` interface, which instead seems solid.

The action also runs on Pull Requests, and in this case runs the rebase operation on Overleaf to check that there are no merge conflicts, but it does not push neither to the local branch nor to Overleaf. Therefore it is useful for contributors to manually rebase on `main` once in a while to keep the pull request current, it is not strictly necessary, we can wait for the pull request to be merged to handle that.

When the action runs on the Github `main` branch, if after the rebasing on Overleaf there are any local commits, those commits are also pushed to Overleaf (this is not a force-push, so it will fail is something is not matching, this is intendend behaviour).

The Action needs 2 secrets to be configured in the repository, `OVERLEAF_PROJECT_ID` is in the Overleaf project url `https://www.overleaf.com/project/xxxxxxxxxxxxxxxxxxxxxxxx`, `OVERLEAF_TOKEN` can be [generated in Account Settings](https://www.overleaf.com/learn/how-to/Git_integration_authentication_tokens#How_to_generate_authentication_tokens).

Here is the entire Action:

```yaml
name: Overleaf Sync with Git
on:
  schedule:
    - cron: "0 * * * *"
  push:
  workflow_dispatch:
      
jobs:
  sync-overleaf:
    name: Synchronize with Overleaf
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
          fetch-depth: 0 # need to fetch history to rebase
    - name: Configure Overleaf remote
      run: git remote add overleaf https://git:${OVERLEAF_TOKEN}@git.overleaf.com/${OVERLEAF_PROJECT_ID}
      env:
        OVERLEAF_PROJECT_ID: ${{ secrets.OVERLEAF_PROJECT_ID }}
        OVERLEAF_TOKEN: ${{ secrets.OVERLEAF_TOKEN }}
    - name: Pull changes from Overleaf
      run: git pull --rebase overleaf master 
    - name: Push changes to Github and Overleaf (only from main)
      run: git push --force origin main && git push overleaf HEAD:master
      if: ${{ github.ref == 'refs/heads/main' }}
```
