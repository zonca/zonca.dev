---
categories:
- jupyterhub
- jetstream
- kubernetes
- git
- github
date: '2023-09-27'
layout: post
title: Deploy Github Authenticator in JupyterHub

---

**Updated June 2024**: added more options to config file

Quick reference on how to deploy the Github Authenticator in JupyterHub,
the main reference is [the Zero to JupyterHub docs](https://z2jh.jupyter.org/en/latest/administrator/authentication.html#github).

For maintaining the single-user image used by this setup, the easiest path is the [custom template where you only update `requirements.txt` and let GitHub Actions rebuild and publish](https://www.zonca.dev/posts/2025-12-01-custom-jupyterhub-docker-image).

First create a Oauth app on Github, see under "Settings" and "Developer options", set your Hub Callback url, see for example the configuration file below.

Save this configuration file as `config_github_auth.yaml` following [the template available on Github](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/github/config_github.yaml)

See the comments in the file for other interesting configuration options, and check [the OAuthenticator documentation for more](https://oauthenticator.readthedocs.io/en/latest/reference/api/gen/oauthenticator.github.html#module-oauthenticator.github).

Add the configuration file to the `helm upgrade --install` call as `--values config_github_auth.yaml`, you can have multiple `--values` arguments.
