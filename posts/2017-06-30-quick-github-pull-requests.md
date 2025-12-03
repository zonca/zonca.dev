---
categories:
- git
- github
date: 2017-06-30 11:00
layout: post
slug: quick-github-pull-requests
title: How to create pull requests on Github

---

Pull Requests are the web-based version of sending software patches via email to code maintainers.
They allow a contributor that has no access to a code repository to submit a code change to the repository administrator that can review and merge it.

I cannot find a guide to making pull requests on Github with the web interface, often using the command line is overkill for small changes.

Here is a quick tutorial:

1. Create a user on [Github](https://github.com/) if you don't have one and login
2. Go to the repository page, e.g. <https://safdsafdsa.com>
3. Click on the "Fork" button on the top right
    * This creates a copy of the repository that belongs to you in your account
4. Now you are in your copy of the repository, find the file you want to edit and click on it.
    * For the SDSC summer institute, click on `participants.md`
5. Click on the Pen icon to Edit the file
6. Make your changes
    * Add your name and your github username to the list
7. Scroll down to "Commit changes"
8. Write a description of the change, e.g. "Added Andrea Zonca to participants"
9. Click "Commit changes"
    * This saves the change in your copy of the repository
10. Click on "Pull Request" on the top right of the files list (above "Latest commit ...")
11. Click on "Create Pull Request" green button
    * This sends an email to the administrator
    * Now you just have to wait for the administrator to accept your change
12. Once the administrator accepts your Pull Request you will receive an email
13. You can see the closed Pull Request at <https://safdsafdsa.com>, where `N` is the number of the PR.
