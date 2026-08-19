---
title: "OpenStack image sharing between projects on Jetstream2: a tested cheat-sheet"
date: '2026-08-19'
categories:
  - jetstream2
  - openstack
layout: post
---

I recently needed to share a Magnum cluster node image with a colleague on a different Jetstream2
allocation. There are a few ways to do it and the documentation is confusing, so I tested every
command live against Jetstream2 OpenStack (Image v2 API). Here is what actually works, with only
commands verified live.

Context: two projects. I own the image; my colleague needs to see and boot it. The example image
here is `snapshot-image-name`, replace with your own image id.

## Option 1: community visibility (recommended, simplest)

Community images are visible and bootable by every project on the cloud. It does not even show up in
everyone's image list by default, but it can still be used to create servers, which is all Magnum
cares about.

As the owner:
```bash
openstack image set --community <image-id>
```

Note: `openstack image set --visibility community` does NOT work. It fails with "Image v1 option no
longer supported in Image v2". Use the `--community` flag.

Verify:
```bash
openstack image show <image-id> -f value -c visibility
```
output: `community`

I proved another project can actually boot a community image owned by a different project: I created
a server from it with `auto_allocated_network` and it reached ACTIVE with an IP address
(10.1.90.87). No membership step needed.

Reverting:
```bash
openstack image set --private <image-id>
```

## Option 2: shared visibility plus member (more steps, needs the recipient)

This is what "sharing" usually means, and it has an extra step that is easy to miss: the recipient
must accept the membership.

As the owner:
```bash
openstack image set --shared <image-id>
openstack image add project <image-id> <recipient-project-id>
```

`openstack image add project` works as the owner, but it only creates a pending membership:
```bash
openstack image member list <image-id>
```
`status = pending`

Only the recipient can accept (the owner gets a 403 "You are not authorized to complete
modify_member action"):
```bash
openstack image set --accept <image-id>
```
(replace `image-id` with the image you were shared)

If the image should no longer be shared:
```bash
openstack image remove project <image-id> <recipient-project-id>
```

## The gotcha that started this post

My colleague ran `openstack image set --shared <image-id>` and told me to look. But the image never
became visible to me: setting shared visibility alone does not create any membership. The missing
steps were `image add project`, and then my `image set --accept`. Community visibility avoids both.

How to find your project id
```bash
openstack token issue -f value -c project_id
```

All commands above were tested live on Jetstream2 OpenStack (Image API v2, `python-openstackclient
9.0.0`). The owner-side commands work with a standard project user credential; the accept step must
be run by the recipient project.
