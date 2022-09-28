---
aliases:
- /2022/09/migrate-fastpages-quarto-preserve-history
date: '2022-09-27'
layout: post
title: Migrate from fastpages to quarto preserving git history

---

https://nbdev.fast.ai/tutorials/blogging.html#migrating-from-fastpages

Inspired by [this tutorial about `git`](https://medium.com/@ayushya/move-directory-from-one-repository-to-another-preserving-git-history-d210fa049d4b), even if I simplified a bit the procedure.

* Create a new repository
* Initialize the website/blog based on quarto
* In the same repository we create another branch which points to the old fastpages-powered blog:

```
git remote add old git@github.com:you/yourfastpagesrepo.git
git fetch old
git checkout -b oldposts old/master
```

* Then we only keep the history of the `_posts` folder

    git filter-branch --subdirectory-filter _posts  -- --all

* Finally we move it into a folder

    mkdir oldposts
    mv * oldposts
    git add .
    git commit -m "move posts into folder"

* Now we can merge it back into the quarto branch

```
git checkout main
git merge oldposts --allow-unrelated-histories
git mv oldposts/* posts/
```

* If necessary, repeat this step with the `_notebooks` folder

Modify `nbdev_migrate`

in `_fp_convert`, I don't have categories in my urls, so I modified the line about aliases into:

    fm['aliases'] = [f'{fs'}]
