---
date: '2023-04-01'
layout: post
title: Get a Letsencrypt certificate for Dreamhost with certbot

---

Dreamhost has discontinued offering free Letsecrypt certificated in their shared hosting.

However, they support pasting a manually created certificate, so we can generate one
on a different machine with the manual mode of `certbot` and then deploy it.

The issue that costed me 1 hour today is that `certbot` generated a ECDSA key by default
instead of RSA, so here the script to generate the right key,
just run:

    export DOMAIN=www.yourdomain.com

and the script:

<script src="https://gist.github.com/zonca/3bfe7bceb1f7b1a01c2048361aaf87cd.js"></script>
