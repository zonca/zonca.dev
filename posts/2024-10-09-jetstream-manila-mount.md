---
categories:
- kubernetes
- jetstream2
date: '2024-10-09'
layout: post
slug: jetstream-manila-mount
title: Generate script to mount a Manila share

---

Jetstream 2 makes creating volumes that are shared across instances as easy as creating standard volumes.
This is provided by the Manila service, which creates volumes based on the Ceph file system that can be mounted simultaneously on multiple Jetstream 2 Virtual Machines.

Exosphere, the Jetstream 2 user friendly UI, is able to create and manage shares, and has the convenient feature that it prints out a command that can be executed in a Jetstream virtual machines to mount a Manila share.

This functionality could be useful also outside of Exosphere, for example if we are creating Manila shares programmatically via the Jetstream API.

Therefore I have created a script that generates the same command.

The only requirement is the Openstack Manila client:

    pip install python-manilaclient

I tested with `python-manilaclient-5.0.0`

We assume we have already created both the Manila share and an access rule (the access rule is created automatically by Exosphere, it needs to be explicitely created if using the CLI).

The script [`generate_mount_command.sh`](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream/blob/master/manila/generate_mount_command.sh) is available in the usual [Github repository](https://github.com/zonca/jupyterhub-deploy-kubernetes-jetstream) under `manila/`.

It is executed from a client with Openstack-CLI installed with:

    SHARENAME="test_share"
    bash generate_mount_command.sh $SHARENAME

This will generate a command of the form:

```bash
curl https://jetstream2.exosphere.app/exosphere/assets/scripts/mount_ceph.py | sudo python3 - mount \
--access-rule-name='test_share-rw' \
--access-rule-key='xxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
--share-path='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
--share-name='test_share'
```

This can be executed at the command line in a Jetstream 2 VM, which does not require any access to the Openstack API.
