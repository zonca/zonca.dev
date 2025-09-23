---
categories:
- openstack
- jetstream
layout: post
date: 2025-09-22
slug: openstack-unshelver-demo
title: OpenStack Unshelver Demo
image: posts/img/openstack-unshelver-demo-thumbnail.jpg

---

I recently vibe-coded a lightweight web application that revives shelved OpenStack instances on demand. The stack is intentionally minimal: a FastHTML frontend, GitHub for authentication, and the OpenStack SDK orchestrated through a YAML configuration that lists the instances the team cares about. I exercised the workflow against my Jetstream 2 project, and the video below captures the current experience end to end.

![OpenStack Unshelver demo thumbnail](https://img.youtube.com/vi/xdVKyStD55M/hqdefault.jpg)

<iframe width="560" height="315" src="https://www.youtube.com/embed/xdVKyStD55M" title="OpenStack Unshelver demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Demo breakdown

The walkthrough starts with a quick tour of the interface: after the app boots locally, it hands control to GitHub for sign-in and then lands you on the Unshelver dashboard. The YAML configuration is doing the heavy lifting behind the scenes—defining which GitHub organization is allowed through the door and which OpenStack instances appear in the catalog.

For the moment the application focuses solely on unshelving. The featured instance is a vanilla Caddy web server that exposes a `/health` endpoint returning `{ "status": "healthy" }`. That heartbeat gives the app a predictable signal to poll while the VM transitions from shelved to active. Triggering “Unshelve Start” launches the workflow: the backend calls the OpenStack SDK, tracks the instance status, and rechecks `/health` at a steady cadence until the service responds.

Once OpenStack confirms the instance is running, the interface offers a one-click path into the workload. In the demo that simply reveals Caddy’s default status page, but the same flow can wake up something more substantial—for example, the large language model documented in [Timing the Unshelving of a Jetstream 70B LLM Instance](2025-09-18-llm-unshelve.md).
