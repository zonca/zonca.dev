---
categories:
- jetstream
- llm
date: '2026-03-11'
layout: post
title: Testing the Jetstream llama.cpp tutorial on g3.medium
---

This is a follow-up to the tutorial
[Deploy a ChatGPT-like LLM on Jetstream with llama.cpp](./2025-09-30-jetstream-llm-llama-cpp.md).
I ran that tutorial end to end on a fresh Jetstream Ubuntu 24 `g3.medium` instance and wrote down the parts that worked as expected, the parts that needed clarification, and the rough performance observed on the tested setup.

If you want the full walkthrough, start from the original tutorial:
[Deploy a ChatGPT-like LLM on Jetstream with llama.cpp](./2025-09-30-jetstream-llm-llama-cpp.md)

## Result

The deployment works end to end on Jetstream.

On the tested VM I was able to:

* build `llama-cpp-python==0.3.16` with CUDA support
* download `Meta-Llama-3.1-8B-Instruct.Q3_K_M.gguf`
* serve the model locally with `llama_cpp.server`
* install and launch Open WebUI
* expose the chat interface publicly with Caddy and HTTPS

The tested external URL was:

* `https://chat.cis230085.projects.jetstream-cloud.org`

## Corrections and clarifications

These are the main points I would keep in mind while following the original tutorial.

### 1. Get the public hostname from Exosphere

Do not rely on `hostname -f` on the VM to discover the public HTTPS hostname.
On the tested instance, the VM reported only an internal hostname, while the public DNS name needed for Caddy and HTTPS was the Exosphere hostname:

* `chat.cis230085.projects.jetstream-cloud.org`

### 2. Initialize Lmod before loading modules

On the tested Ubuntu 24 image, `module` was not immediately available in a plain shell until Lmod was initialized.

Use:

```bash
source /etc/profile.d/lmod.sh
module load miniforge
```

The same applies before loading `nvhpc/24.7/nvhpc`.

### 3. `nvhpc` must be loaded at runtime too

Loading `nvhpc/24.7/nvhpc` is required not only while building `llama-cpp-python`, but also when running `llama_cpp.server`.

Without the module loaded at runtime, `llama_cpp` failed to import with:

```text
libcudart.so.12: cannot open shared object file
```

### 4. `conda run` is more reliable in non-interactive shells

For interactive shell use, `conda activate` is fine.
For scripting, `nohup`, SSH one-liners, or `systemd`, `conda run -n ENV ...` is more robust because it does not depend on shell initialization.

### 5. Open WebUI installation is large

The `open-webui` install worked, but it pulled in a large dependency set and took noticeably longer than the `llama-cpp-python` build.
That is normal for this setup; it is not necessarily a sign that something is wrong.

## Performance on the tested setup

Tested configuration:

* instance type: `g3.medium`
* image: Ubuntu 24
* model: `Meta-Llama-3.1-8B-Instruct.Q3_K_M.gguf`
* full GPU offload: `--n_gpu_layers -1`
* context length: `--n_ctx 8192`

Short local chat-completion requests generated about **85-90 tokens/second** after warm-up.

In practice, that feels very fast for interactive chat, closer to the “instant response” feel of a non-reasoning assistant than a slow step-by-step model.

As usual, throughput will drop with:

* longer prompts
* larger context windows
* more concurrent users
* heavier quantizations or larger models

## Suggested service layout

If you want the deployment to stay up after logout or reboot, make sure you complete the `systemd` section of the original tutorial for both:

* `llama.service`
* `webui.service`

During testing, manually launching the components worked for validation, but the persistent setup only becomes reliable once those services are installed and enabled.

## Final note

The original tutorial remains the main walkthrough:
[Deploy a ChatGPT-like LLM on Jetstream with llama.cpp](./2025-09-30-jetstream-llm-llama-cpp.md)

This follow-up is meant as a tested companion with the details that became obvious only while running the full deployment on a fresh VM.
