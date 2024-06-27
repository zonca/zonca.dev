---
categories:
- python
date: '2024-06-27'
layout: post
title: Conditional authentication on a single endpoint with FastAPI
---

Building [on my previous tutorial](2024-05-29-fastapi-sso-github-organization.md), I have now implemented a toy FastAPI application which requires authentication based on query parameters.

In this simple example `/protected/0` does not require authentication, while `/protected/1` gives permissions denied.

Once the users logs in successfully via Github using `/auth/login` and is member of the right Github organization, they can now access also the `/protected/1` endpoint.

[See the implementation in this Gist](https://gist.github.com/zonca/12a6b41fb53574a6a469f6a93d7db013)
