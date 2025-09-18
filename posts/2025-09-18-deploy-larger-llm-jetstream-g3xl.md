---
title: "Deploying a Larger LLM on Jetstream's g3.xl Instance"
author: "Your Name"
date: "2025-09-18"
categories: [cloud, LLM, Jetstream]
---

::: {md-component="skip"}
[Skip to
content](#deploy-a-chatgptlike-llm-service-on-jetstream){.md-skip}
:::

::: {md-component="announce"}
:::

[![logo](../../images/jetstream2-logo-white.svg)](../.. "Jetstream2 Documentation"){.md-header__button
.md-logo}

::: {.md-header__title md-component="header-title"}
::: {.md-header__ellipsis"}
::: {.md-header__topic"}
[ Jetstream2 Documentation ]{.md-ellipsis}
:::

::: {.md-header__topic md-component="header-topic"}
[ Deploying a Larger LLM on Jetstream's g3.xl Instance ]{.md-ellipsis}
:::
:::
:::

::: {.md-search md-component="search" role="dialog"}
::: {.md-search__inner role="search"}
::: {.md-search__suggest md-component="search-suggest"}
:::
:::

::: {.md-search__output"}
::: {.md-search__scrollwrap tabindex="0" md-scrollfix=""}
::: {.md-search-result md-component="search-result"}
::: {.md-search-result__meta"}
Initializing search
:::
:::
:::
:::
:::
:::

::: {.md-header__source"}
[](https://gitlab.com/jetstream-cloud/docs "Go to repository"){.md-source}

::: {.md-source__icon .md-icon"}
:::

::: {.md-source__repository"}
jetstream-cloud/docs
:::
:::

::: {.md-container md-component="container"}
::: {.md-main role="main" md-component="main"}
::: {.md-main__inner .md-grid"}
::: {.md-sidebar .md-sidebar--primary md-component="sidebar" md-type="navigation"}
::: {.md-sidebar__scrollwrap"}
::: {.md-sidebar__inner"}
[![logo](../../images/jetstream2-logo-white.svg)](../.. "Jetstream2 Documentation"){.md-nav__button
.md-logo} Jetstream2 Documentation

::: {.md-nav__source"}
[](https://gitlab.com/jetstream-cloud/docs "Go to repository"){.md-source}

::: {.md-source__icon .md-icon"}
:::

::: {.md-source__repository"}
jetstream-cloud/docs
:::
:::

-   [ Home ]{.md-ellipsis}
-   [ Status ]{.md-ellipsis}
-   [ Support and News ]{.md-ellipsis}
-   [ Getting Started ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Getting Started
    -   [[ Overview
        ]{.md-ellipsis}](../../getting-started/overview/){.md-nav__link}
    -   [[ Logging in to Jetstream2
        ]{.md-ellipsis}](../../getting-started/login/){.md-nav__link}
    -   [[ Creating your First Instance
        ]{.md-ellipsis}](../../getting-started/first-instance/){.md-nav__link}
    -   [[ Accessing your Instance
        ]{.md-ellipsis}](../../getting-started/access-instance/){.md-nav__link}
    -   [[ Volume Management
        ]{.md-ellipsis}](../../getting-started/volumes/){.md-nav__link}
    -   [[ Installing and Running Software
        ]{.md-ellipsis}](../../getting-started/software/){.md-nav__link}
    -   [[ Instance Management
        ]{.md-ellipsis}](../../getting-started/instance-management/){.md-nav__link}
    -   [[ Snapshots and Images
        ]{.md-ellipsis}](../../getting-started/snapshots/){.md-nav__link}
    -   [[ Next Steps
        ]{.md-ellipsis}](../../getting-started/next-steps/){.md-nav__link}
-   [ Jetstream2 Info ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Jetstream2 Info
    -   [[ System Overview
        ]{.md-ellipsis}](../../overview/overview-doc/){.md-nav__link}
    -   [[ Architecture and Capabilities of Jetstream2
        ]{.md-ellipsis}](../../overview/architecture/){.md-nav__link}
    -   [[ Configuration and specifications
        ]{.md-ellipsis}](../../overview/config/){.md-nav__link}
    -   [[ Network configuration and considerations
        ]{.md-ellipsis}](../../overview/network/){.md-nav__link}
-   [ Frequently Asked Questions ]{.md-ellipsis} []{.md-nav__icon
    .md-icon}
    []{.md-nav__icon .md-icon} Frequently Asked Questions
    -   [[ General FAQs
        ]{.md-ellipsis}](../../faq/general-faq/){.md-nav__link}
    -   [[ Troubleshooting
        ]{.md-ellipsis}](../../faq/trouble/){.md-nav__link}
    -   [[ Allocations ]{.md-ellipsis}](../../faq/alloc/){.md-nav__link}
    -   [[ GPU FAQs ]{.md-ellipsis}](../../faq/gpu/){.md-nav__link}
    -   [[ Security ]{.md-ellipsis}](../../faq/security/){.md-nav__link}
    -   [[ Software ]{.md-ellipsis}](../../faq/software/){.md-nav__link}
    -   [[ Gateways ]{.md-ellipsis}](../../faq/gateways/){.md-nav__link}
-   [ General Usage Information ]{.md-ellipsis} []{.md-nav__icon
    .md-icon}
    []{.md-nav__icon .md-icon} General Usage Information
    -   [[ Jetstream2 Resources
        ]{.md-ellipsis}](../resources/){.md-nav__link}
    -   [[ ACCESS Credits and Jetstream2
        ]{.md-ellipsis}](../access/){.md-nav__link}
    -   [[ Instance Flavors
        ]{.md-ellipsis}](../instance-flavors/){.md-nav__link}
    -   [[ Quotas ]{.md-ellipsis}](../quotas/){.md-nav__link}
    -   [[ Instance Management Actions
        ]{.md-ellipsis}](../instancemgt/){.md-nav__link}
    -   [[ Featured Images ]{.md-ellipsis}](../featured/){.md-nav__link}
    -   [[ Microsoft Windows on Jetstream2
        ]{.md-ellipsis}](../windows/){.md-nav__link}
-   [ Allocations ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Allocations
    -   [[ Allocations Overview
        ]{.md-ellipsis}](../../alloc/overview/){.md-nav__link}
    -   [[ Trial Allocation
        ]{.md-ellipsis}](../../alloc/trial/){.md-nav__link}
    -   [[ General Allocations
        ]{.md-ellipsis}](../../alloc/general-allocations/){.md-nav__link}
    -   [[ Education Allocations
        ]{.md-ellipsis}](../../alloc/education/){.md-nav__link}
    -   [[ Research (Maximize ACCESS) Allocations
        ]{.md-ellipsis}](../../alloc/research/){.md-nav__link}
    -   [[ Supplements (Storage/SUs)
        ]{.md-ellipsis}](../../alloc/supplement/){.md-nav__link}
    -   [[ Extensions & Renewals
        ]{.md-ellipsis}](../../alloc/renew-extend/){.md-nav__link}
    -   [[ Frequently Asked Questions
        ]{.md-ellipsis}](../../alloc/faq/){.md-nav__link}
    -   [[ Budgeting for Common Usage Scenarios
        ]{.md-ellipsis}](../../alloc/budgeting/){.md-nav__link}
    -   [[ Usage Estimation Calculator
        ]{.md-ellipsis}](../../alloc/estimator/){.md-nav__link}
-   [ Storage ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Storage
    -   [[ Storage Overview ]{.md-ellipsis}](../storage/){.md-nav__link}
    -   [[ Volumes ]{.md-ellipsis}](../volume/){.md-nav__link}
    -   [[ Manila Shares ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../manila/){.md-nav__link}
    -   [[ Object Store ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../object/){.md-nav__link}
    -   [[ File Transfer
        ]{.md-ellipsis}](../filetransfer/){.md-nav__link}
-   [ User Interfaces ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} User Interfaces
    -   [[ Overview ]{.md-ellipsis}](../../ui/){.md-nav__link}
    -   [[ Exosphere ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../../ui/exo/exo/){.md-nav__link}
    -   [[ Horizon ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../../ui/horizon/intro/){.md-nav__link}
    -   [[ CLI ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../../ui/cli/overview/){.md-nav__link}
    -   [[ CACAO ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../../ui/cacao/overview/){.md-nav__link}
-   [ General VM Operations ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} General VM Operations
    -   [[ Security ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../firewalls/){.md-nav__link}
    -   [[ Maintenance and Administration ]{.md-ellipsis}
        []{.md-nav__icon .md-icon}](../adduser/){.md-nav__link}
    -   [[ Research Software ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../jupyter/){.md-nav__link}
-   [ Software Collection ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Software Collection
    -   [[ Jetstream2 Software Collection
        ]{.md-ellipsis}](../software/){.md-nav__link}
    -   [[ Using the JS2 Software Collection - Command Line
        ]{.md-ellipsis}](../usingsoftware-cli/){.md-nav__link}
    -   [[ Using the JS2 Software Collection - Web Desktop
        ]{.md-ellipsis}](../usingsoftware-desktop/){.md-nav__link}
    -   [[ Software Licenses
        ]{.md-ellipsis}](../licenses/){.md-nav__link}
-   [ Policies and Best Practices ]{.md-ellipsis} []{.md-nav__icon
    .md-icon}
    []{.md-nav__icon .md-icon} Policies and Best Practices
    -   [[ Acceptable Usage Policies
        ]{.md-ellipsis}](../policies/){.md-nav__link}
    -   [[ Export Control Guidance
        ]{.md-ellipsis}](../export/){.md-nav__link}
    -   [[ AUPs for Jetstream2 Hosted Gateways
        ]{.md-ellipsis}](../gateways/){.md-nav__link}
    -   [[ Best Practices
        ]{.md-ellipsis}](../bestpractice/){.md-nav__link}
-   [ Special Topics ]{.md-ellipsis} []{.md-nav__icon .md-icon}
    []{.md-nav__icon .md-icon} Special Topics
    -   [[ Containers on Jetstream2 ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../docker/){.md-nav__link}
    -   [[ Terraform ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../terraform/){.md-nav__link}
    -   [[ Virtual Clusters on Jetstream2
        ]{.md-ellipsis}](../virtualclusters/){.md-nav__link}
    -   [[ Federating Gateways on Jetstream2
        ]{.md-ellipsis}](../federating/){.md-nav__link}
    -   [[ Load Balancing with OpenStack Octavia
        ]{.md-ellipsis}](../octavia/){.md-nav__link}
    -   [[ LLM Inference Service ]{.md-ellipsis} []{.md-nav__icon
        .md-icon}](../../inference-service/overview/){.md-nav__link}
    -   [[ Orientation to Running LLMs
        ]{.md-ellipsis}](../running-llm/){.md-nav__link}
    -   [ LLM and Chat Interface Deployment Tutorial ]{.md-ellipsis}
        []{.md-nav__icon .md-icon} [[ LLM and Chat Interface Deployment
        Tutorial ]{.md-ellipsis}](./){.md-nav__link
        .md-nav__link--active}
        []{.md-nav__icon .md-icon} Table of contents
        -   [[ Model choice & sizing
            ]{.md-ellipsis}](#model-choice-sizing){.md-nav__link}
        -   [[ Create a Jetstream instance
            ]{.md-ellipsis}](#create-a-jetstream-instance){.md-nav__link}
        -   [[ Load Miniforge
            ]{.md-ellipsis}](#load-miniforge){.md-nav__link}
        -   [[ Serve the model with llama.cpp (OpenAI‑compatible server)
            ]{.md-ellipsis}](#serve-the-model-with-llamacpp-openaicompatible-server){.md-nav__link}
        -   [[ Configure the chat interface
            ]{.md-ellipsis}](#configure-the-chat-interface){.md-nav__link}
            -   [[ (Optional) One-liner to create both services
                ]{.md-ellipsis}](#optional-one-liner-to-create-both-services){.md-nav__link}
        -   [[ Configure web server for HTTPS
            ]{.md-ellipsis}](#configure-web-server-for-https){.md-nav__link}
        -   [[ Connect the model and test the chat interface
            ]{.md-ellipsis}](#connect-the-model-and-test-the-chat-interface){.md-nav__link}
        -   [[ Scaling up or changing models
            ]{.md-ellipsis}](#scaling-up-or-changing-models){.md-nav__link}
:::
:::
:::

::: {.md-sidebar .md-sidebar--secondary md-component="sidebar" md-type="toc"}
::: {.md-sidebar__scrollwrap"}
::: {.md-sidebar__inner"}
[]{.md-nav__icon .md-icon} Table of contents

-   [[ Model choice & sizing
    ]{.md-ellipsis}](#model-choice-sizing){.md-nav__link}
-   [[ Create a Jetstream instance
    ]{.md-ellipsis}](#create-a-jetstream-instance){.md-nav__link}
-   [[ Load Miniforge ]{.md-ellipsis}](#load-miniforge){.md-nav__link}
-   [[ Serve the model with llama.cpp (OpenAI‑compatible server)
    ]{.md-ellipsis}](#serve-the-model-with-llamacpp-openaicompatible-server){.md-nav__link}
-   [[ Configure the chat interface
    ]{.md-ellipsis}](#configure-the-chat-interface){.md-nav__link}
    -   [[ (Optional) One-liner to create both services
        ]{.md-ellipsis}](#optional-one-liner-to-create-both-services){.md-nav__link}
-   [[ Configure web server for HTTPS
    ]{.md-ellipsis}](#configure-web-server-for-https){.md-nav__link}
-   [[ Connect the model and test the chat interface
    ]{.md-ellipsis}](#connect-the-model-and-test-the-chat-interface){.md-nav__link}
-   [[ Scaling up or changing models
    ]{.md-ellipsis}](#scaling-up-or-changing-models){.md-nav__link}
:::
:::
:::

::: {.md-content md-component="content"}
Deploying a Larger LLM on Jetstream's g3.xl Instance[¶](#deploy-a-chatgptlike-llm-service-on-jetstream "Permanent link"){.headerlink}
==============================================================================================================================

Tutorial last updated on September 18, 2025

In this tutorial we deploy a Large Language Model (LLM) on Jetstream,
run inference locally on a powerful GPU node (`g3.xl`, 40 GB VRAM),
then install a web chat interface (Open WebUI) and serve it with HTTPS using Caddy.

Before spinning up your own GPU, consider the managed [Jetstream LLM
inference
service](https://docs.jetstream-cloud.org/inference-service/overview/).
It may be more cost- and time-effective if you just need API access to
standard models.

We will deploy a larger quantized model: **Meta Llama 3.1 70B Instruct Q3_K_L (GGUF)**. This quantized 70B model requires approximately 35-40 GB of GPU memory, making it suitable for the `g3.xl` instance (40 GB VRAM). Note that this is a tight fit, and you might need to adjust `n_ctx` or consider a slightly lower quantization if you encounter out-of-memory errors.

This tutorial is adapted from work by [Tijmen de
Haan](https://www2.kek.jp/qup/en/member/dehaan.html), the author of
[Cosmosage](https://cosmosage.online/).

Model choice & sizing[¶](#model-choice-sizing "Permanent link"){.headerlink}
----------------------------------------------------------------------------

Jetstream GPU flavors (current key options):

  Instance Type   Approx. GPU Memory (GB)
  --------------- -------------------------
  g3.xl           40 (full A100)

We pick the quantized **Llama 3.1 70B Instruct Q3_K_L** variant (GGUF
format). Its VRAM residency during inference is about ~35-40 GB with
default context settings, leaving very little margin on `g3.xl`. Always
keep a couple of GB free to avoid OOM errors when increasing context
length or concurrency.

Ensure the model is an Instruct fine-tuned variant (it is) so it
responds well to chat prompts.

Create a Jetstream instance[¶](#create-a-jetstream-instance "Permanent link"){.headerlink}
------------------------------------------------------------------------------------------

Log in to Exosphere, request an Ubuntu 24 **`g3.xl`** instance (name
it `chat`) and SSH into it using either your SSH key or the passphrase
generated by Exosphere.

Load Miniforge[¶](#load-miniforge "Permanent link"){.headerlink}
----------------------------------------------------------------

A centrally provided Miniforge module is available on Jetstream images.
Load it (each new shell) and then create the two Conda environments used
below (one for the model server, one for the web UI).

::: {.highlight}
    module load miniforge
    conda init
:::

> After running `conda init`, reload your shell so `conda` is available:
> run `exec bash -l` (avoids logging out and back in).

Serve the model with `llama.cpp` (OpenAI-compatible server)[¶](#serve-the-model-with-llamacpp-openaicompatible-server "Permanent link"){.headerlink}
----------------------------------------------------------------------------------------------------------------------------------------------------

We use `llama.cpp` via the `llama-cpp-python` package, which provides an
OpenAI-style HTTP API (default port 8000) that Open WebUI can connect
to.

Create an environment and install (remember to `module load miniforge`
first in any new shell).

The last `pip install` step may take several minutes to compile
lama.cpp from source, so please be patient.

::: {.highlight}
    conda create -y -n llama python=3.11
    conda activate llama
    conda install -y cmake ninja scikit-build-core huggingface_hub
    module load nvhpc/24.7/nvhpc
    # Enable CUDA acceleration with explicit compilers, arch, release build
    CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_COMPILER=$(which nvcc) -DCMAKE_C_COMPILER=$(which gcc) -DCMAKE_CXX_COMPILER=$(which g++) -DCMAKE_CUDA_ARCHITECTURES=80 -DCMAKE_BUILD_TYPE=Release" \
        pip install --no-cache-dir --no-build-isolation --force-reinstall "llama-cpp-python[server]==0.3.16"
:::

Download the quantized GGUF file (Q4_K_M variant) from Hugging Face:
`aiqtech/Meta-Llama-3-70B-Instruct-Q4_K_M-GGUF`

::: {.highlight}
    mkdir -p ~/models
    huggingface-cli download bartowski/Meta-Llama-3.1-70B-Instruct-GGUF \
        Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf \
        --local-dir ~/models \
        --local-dir-use-symlinks False
:::

Test run (Ctrl-C to stop):

::: {.highlight}
    python -m llama_cpp.server \
        --model /home/exouser/models/Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf \
        --host 0.0.0.0 --port 8080 \
        --slots 2 \
        --n-gpu-layers -1 \
        --ctx-size 4096 \
        --batch-size 64 \
        --cache-type-k q4_0 --cache-type-v q4_0
:::

`--n_gpu_layers -1` tells `llama.cpp` to offload **all model layers** to
the GPU (full GPU inference). Without this flag the default is CPU
layers (`n_gpu_layers=0`), which results in significantly slower generation.
Full offload of this 70B Q3_K_L model plus context buffers should occupy
roughly 35-40 GB VRAM at `--ctx-size 4096` on first real requests. Given the
`g3.xl` has 40 GB VRAM, this is a tight fit. If it fails to start with an
out-of-memory (OOM) error you have a few mitigation options (apply one,
then retry):

-   Lower context length: e.g. `--ctx-size 2048` (largest single lever;
    roughly linear VRAM impact for KV cache).
-   Partially offload: replace `--n_gpu_layers -1` with a number (e.g.
    `--n_gpu_layers 20`). Remaining layers will run on CPU (slower, but
    reduces VRAM need).
-   Use a lower-bit quantization (e.g. Q2_K) or a smaller model.

You can inspect VRAM usage with `watch -n 2 nvidia-smi` after starting
the server.

Quick note on the "KV cache": During generation the model reuses
previously computed attention Key and Value tensors (instead of
recalculating them each new token). These tensors are stored per layer
and per processed token; as your prompt and conversation grow, the cache
grows linearly with the number of tokens kept in context. That's why
idle VRAM (~weights only) is lower (~35 GB) and rises toward the higher
number (up to ~40 GB here) only after longer prompts / chats.
Reducing `--ctx-size` caps the maximum KV cache size; clearing history or
restarting frees it.

If it starts without errors, create a systemd service so it restarts
automatically.

> Quick option: If you prefer a single copy/paste that creates **both**
> the `llama` and `open-webui` systemd services at once, skip the next
> two manual unit file sections and jump ahead to the subsection titled
> "(Optional) One-liner to create both services" below. You can always
> come back here for the longer, step-by-step version and
> troubleshooting notes.

Using `sudo` to run your preferred text editor, create
`/etc/systemd/system/llama.service` with the following contents:

::: {.highlight}
    [Unit]
    Description=Llama.cpp OpenAI-compatible server
    After=network.target

    [Service]
    User=exouser
    Group=exouser
    WorkingDirectory=/home/exouser
    ExecStart=/bin/bash -lc "module load nvhpc/24.7/nvhpc miniforge && conda run -n llama python -m llama_cpp.server --model /home/exouser/models/Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf --host 0.0.0.0 --port 8080 --slots 2 --n-gpu-layers -1 --ctx-size 4096 --batch-size 64 --cache-type-k q4_0 --cache-type-v q4_0"
    Restart=always

    [Install]
    WantedBy=multi-user.target
:::

Enable and start:

::: {.highlight}
    sudo systemctl enable llama
    sudo systemctl start llama
:::

Troubleshooting:

-   Logs: `sudo journalctl -u llama -f`
-   Status: `sudo systemctl status llama`
-   GPU usage: `nvidia-smi` (~35-40 GB idle right after start with full
    offload; can grow toward ~40 GB under long prompts/conversations
    as KV cache fills, potentially leading to OOM if not managed).

Configure the chat interface[¶](#configure-the-chat-interface "Permanent link"){.headerlink}
--------------------------------------------------------------------------------------------

The chat interface is provided by [Open Web UI](https://openwebui.com/).

Create the environment (in a new shell remember to
`module load miniforge` first):

::: {.highlight}
    module load miniforge
    conda create -y -n open-webui python=3.11
    conda activate open-webui
    pip install open-webui
    open-webui serve
:::

If this starts with no error, we can kill it with `Ctrl-C` and create a
service for it.

Using `sudo` to run your preferred text editor, create
`/etc/systemd/system/webui.service` with the following contents:

::: {.highlight}
    [Unit]
    Description=Open Web UI serving
    After=network.target

    [Service]
    User=exouser
    Group=exouser
    WorkingDirectory=/home/exouser

    # Activating the conda environment and starting the service
    ExecStart=/bin/bash -lc "module load miniforge && conda run -n open-webui open-webui serve"
    Restart=always
    # PATH managed by module + conda

    [Install]
    WantedBy=multi-user.target
:::

Then enable and start the service:

::: {.highlight}
    sudo systemctl enable webui
    sudo systemctl start webui
:::

### (Optional) One-liner to create both services[¶](#optional-one-liner-to-create-both-services "Permanent link"){.headerlink}

If you already created the Conda environments (`llama` and `open-webui`)
and downloaded the model, you can create, enable, and start both systemd
services (model server + Open WebUI) in a single copy/paste. Adjust
`MODEL`, `N_CTX`, `USER`, and `NVHPC_MOD` if needed before running:

::: {.highlight}
    MODEL=/home/exouser/models/Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf N_CTX=4096 USER=exouser NVHPC_MOD=nvhpc/24.7/nvhpc ; sudo tee /etc/systemd/system/llama.service >/dev/null <<EOF && sudo tee /etc/systemd/system/webui.service >/dev/null <<EOF2 && sudo systemctl daemon-reload && sudo systemctl enable --now llama webui
    [Unit]
    Description=Llama.cpp OpenAI-compatible server
    After=network.target

    [Service]
    User=$USER
    Group=$USER
    WorkingDirectory=/home/$USER
    ExecStart=/bin/bash -lc "module load $NVHPC_MOD miniforge && conda run -n llama python -m llama_cpp.server --model $MODEL --host 0.0.0.0 --port 8080 --slots 2 --n-gpu-layers -1 --ctx-size $N_CTX --batch-size 64 --cache-type-k q4_0 --cache-type-v q4_0"
    Restart=always

    [Install]
    WantedBy=multi-user.target
    EOF
    [Unit]
    Description=Open Web UI serving
    After=network.target

    [Service]
    User=$USER
    Group=$USER
    WorkingDirectory=/home/$USER
    ExecStart=/bin/bash -lc "module load miniforge && conda run -n open-webui open-webui serve"
    Restart=always

    [Install]
    WantedBy=multi-user.target
    EOF2
:::

To later change context length: edit
`/etc/systemd/system/llama.service`, modify `--n_ctx`, then run:

::: {.highlight}
    sudo systemctl daemon-reload
    sudo systemctl restart llama
:::

Configure web server for HTTPS[¶](#configure-web-server-for-https "Permanent link"){.headerlink}
------------------------------------------------------------------------------------------------

Finally we can use Caddy to serve the web interface with HTTPS.

Install [Caddy](https://caddyserver.com/). Note that the version of
Caddy available in the Ubuntu APT repositories is often outdated. Follow
[the instructions to install Caddy on
Ubuntu](https://caddyserver.com/docs/install#debian-ubuntu-raspbian).
You can copy-paste all the lines at once.

Modify the Caddyfile to serve the web interface. (Note that
`sensible-editor` will prompt you to choose a text editor; select the
number for `/bin/nano` if you aren't sure what else to pick.)

::: {.highlight}
    sudo sensible-editor /etc/caddy/Caddyfile
:::

to:

::: {.highlight}
    chat.xxx000000.projects.jetstream-cloud.org {

            reverse_proxy localhost:8080
    }
:::

Where `chat` is the name of your instance, and `xxx000000` is the
allocation code. You can find the full hostname (e.g.
`chat.xxx000000.projects.jetstream-cloud.org`) in Exosphere: open your
instance's details page, scroll to the Credentials section, and copy the
value shown under Hostname.

Then reload Caddy:

::: {.highlight}
    sudo systemctl reload caddy
:::

Connect the model and test the chat interface[¶](#connect-the-model-and-test-the-chat-interface "Permanent link"){.headerlink}
------------------------------------------------------------------------------------------------------------------------------

Point your browser to
`https://chat.xxx000000.projects.jetstream-cloud.org` and you should see
the chat interface.

Create an account, click on the profile icon on the top right and enter
the "Admin panel" section, open "Settings" then "Connections". Once you
create the first account, that will become admin, if anyone else creates
an account they will be a regular user and need to be approved by the
admin user. This is the only protection available in this setup, an
attacker could still leverage vulnerabilities on Open WebUI to gain
access. If you require more security the easiest way is to just open the
firewall (using `ufw`) to only allow connections from your IP.

Under "OpenAI API" enter the URL `http://localhost:8080/v1` and leave
the API key empty (the local llama.cpp server is unsecured by default on
localhost).

Click on the "Verify connection" button, then to "Save" on the bottom.

Finally you can start chatting with the model!

If you change context length (`--ctx-size`) or increase concurrent users
you may quickly approach the 40 GB limit of the `g3.xl` instance. Reduce
`--ctx-size` (e.g. 2048 or lower) if you encounter out-of-memory errors. For
even larger models or higher concurrency, consider specialized solutions
or future Jetstream instances with more GPU memory.

Scaling up or changing models[¶](#scaling-up-or-changing-models "Permanent link"){.headerlink}
----------------------------------------------------------------------------------------------

Want a larger model or higher quality? Options:

-   Use a higher-bit quantization (e.g., Q4_K_M or Q5_K_M) for better
    quality (needs more VRAM, potentially exceeding `g3.xl` capacity).
-   For unquantized models or even larger models, you would need an instance with more GPU memory than `g3.xl`.
-   Increase context length (each 1k tokens adds memory usage). If you
    see OOM, lower `--ctx-size`.

For production workloads, consider the managed Jetstream inference
service or frameworks like `vllm` on larger GPUs for higher throughput.

[September 18, 2025]{.git-revision-date-localized-plugin
.git-revision-date-localized-plugin-date
title="September 18, 2025 12:00:00 UTC"}
:::
:::

Back to top
:::

[](../running-llm/){.md-footer__link .md-footer__link--prev}

::: {.md-footer__button .md-icon"}
:::

::: {.md-footer__title"}
[ Previous ]{.md-footer__direction}

::: {.md-ellipsis"}
Orientation to Running LLMs
:::
:::

::: {.md-footer__button .md-icon"}
:::

[](../../tutorial/classroom/overview/){.md-footer__link
.md-footer__link--next}

::: {.md-footer__title"}
[ Next ]{.md-footer__direction}

::: {.md-ellipsis"}
Overview
:::
:::

::: {.md-footer__button .md-icon"}
:::

::: {.md-footer-meta .md-typeset"}
::: {.md-footer-meta__inner .md-grid"}
::: {.md-copyright"}
::: {.md-copyright__highlight"}
Copyright © 2025 The Trustees of Indiana University
:::

Made with [Material for
MkDocs](https://squidfunk.github.io/mkdocs-material/)
:::
:::
:::
:::

::: {.md-dialog md-component="dialog"}
::: {.md-dialog__inner .md-typeset"}
:::
:::
