---
categories:
- jetstream
- llm
layout: post
date: 2025-09-18
slug: llm-unshelve
title: Unshelving a Jetstream 70B LLM Instance

---

Following the work documented in [PR #13](https://github.com/zonca/zonca.dev/pull/13), the `Meta-Llama-3.1-70B-Instruct-GGUF` deployment is now running on a `g3.xl` instance. The goal of this follow-up is to measure how long it takes to unshelve that virtual machine and bring the chat interface back online.

Each unshelve cycle includes attaching the `llmstorage` volume, waiting for the model weights to be available under `~/models`, and watching for the Open WebUI front end to load. I am timing the interval from issuing the unshelve command in Exosphere until the chat interface is ready to accept prompts.

When shelving the instance in Exosphere, make sure to clear the "Release IP when shelving" checkbox. Keeping the floating IP attached ensures the service comes back with the same address, which avoids reconfiguring client applications or DNS.

I'll update this post with timing results and any tuning tips once we have a few data points.

## Timing

First attempt: the instance shows as ready in Exosphere after about **2 minutes**, and the Open WebUI chat interface becomes responsive roughly **1 minute** later. In total it takes just **3 minutes** from unshelving to having the assistant ready for prompts.

Second attempt: Exosphere reports the VM ready in **1 minute 40 seconds**, and the chat UI finishes loading at **2 minutes 55 seconds** overall.

Third attempt: after updating the systemd units so Open WebUI waits for the `llama` service before starting—no more manual reconnection—the VM appears ready at **1 minute 30 seconds**, and the chat interface (with the model responding) is back **4 minutes 30 seconds** after clicking Unshelve.
