---
categories:
- python
date: '2024-05-29'
layout: post
title: Authenticate FastAPI endpoints with a Github organization
---

[FastAPI](https://fastapi.tiangolo.com/) is a framework that simplifies building APIs in Python.
Authentication via Google, Github and many more is provided by [FastAPI-SSO](https://tomasvotava.github.io/fastapi-sso/).

We can also combine this with [PyGithub](https://pygithub.readthedocs.io/en/latest/introduction.html) to check if the user is a member of a specific organization and handle permissions on specific objects provided by an endpoint.

[See the implementation in this Gist](https://gist.github.com/zonca/21c78b1bbbb920035b84e480e976f9b3)

Notice that on [from your Developer Settings on Github](https://github.com/settings/apps) you both need to create an OAuth app (with `http://localhost:5000/auth/callback` callback) and a Personal Access Token (classic) with `read:orgs` scope to query group membership and store all their credentials in `github_env.sh`.

Once the app is running, try accessing <http://127.0.0.1:5000/protected>, you should first get "Not authenticated", now login at <http://localhost:5000/auth/login>, you should be redirected to Github for authentication, then you should see if you are or not a member of the `ORG` organization as defined in the source file.
