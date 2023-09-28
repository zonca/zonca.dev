---
categories:
- jupyterhub
- jetstream
- kubernetes
date: '2023-09-27'
layout: post
title: Deploy Github Authenticator in JupyterHub

---

Quick reference on how to deploy the Github Authenticator in JupyterHub,
the main reference is [the Zero to JupyterHub docs](https://z2jh.jupyter.org/en/latest/administrator/authentication.html#github).

First create a Oauth app on Github, see under "Settings" and "Developer options", set your Hub Callback url, see for example the configuration file below.

Next add to your YAML JupyterHub configuration file:


```
hub:
  config:
    GitHubOAuthenticator:
      client_id: xxxxxxxxxxxxxxxxxxxx
      client_secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      oauth_callback_url: https://kubejetstream-1.xxx000000.projects.jetstream-cloud.org/hub/ oauth_callback
      allow_all: false
    JupyterHub:
      authenticator_class: github
      admin_access: true
      admin_users:
        - zonca
```

Switch `allow_all` to `true` to allow any valid Github user to be able to login (this took me some time to figure out...)
