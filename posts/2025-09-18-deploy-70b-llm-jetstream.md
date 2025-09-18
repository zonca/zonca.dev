---
categories:
- jetstream
- llm
layout: post
date: 2025-09-18
slug: deploy-70b-llm-jetstream
title: Deploy a 70B LLM to Jetstream

---

Deploying large language models on Jetstream is getting easier thanks to the official [Jetstream LLM guide](https://docs.jetstream-cloud.org/general/llm/). Here I follow that walkthrough but scale the hardware and model so we can run something far more capable than the defaults.

Instead of the suggested `g3.medium` instance, spin up a `g3.xl` virtual machine. This flavor maps to an entire NVIDIA A100 with 40 GB of GPU memory, which comfortably fits the `Meta-Llama-3.1-70B-Instruct-GGUF` checkpoint. The steps below highlight the few adjustments needed to provision the larger VM and load the bigger model; everything else matches the upstream documentation.

The quantized 70B weights weigh in at about 37 GB, so reserve enough storage. From Exosphere create a 100 GB volume named `llmstorage`, attach it to the instance, and confirm it shows up under `/media/volume/llmstorage/`. Keeping the model files on that volume makes it easy to swap or resize later. From your home directory point `~/models` at the mounted volume so every tool reads and writes there:

```bash
ln -s /media/volume/llmstorage/ ~/models
```

Pull the quantized weights to the VM using the `huggingface-cli` utility so they live on the attached volume and are ready for serving:

```bash
huggingface-cli download \
    bartowski/Meta-Llama-3.1-70B-Instruct-GGUF \
    Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf \
    --local-dir ~/models \
    --local-dir-use-symlinks False
```

With the model staged locally, start the `llama-cpp-python` server in chat mode so clients can reach it over HTTP. The command below assumes the default Jetstream username (`exouser`) and keeps everything on GPU for maximum throughput:

```bash
python -m llama_cpp.server \
    --model /home/exouser/models/Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf \
    --chat_format llama-3 \
    --n_ctx 4096 \
    --n_gpu_layers -1 \
    --n_batch 128 \
    --n_threads 16 \
    --port 8000
```

To make the services persistent, export the configuration values and use this one-liner to register both the model server and Open WebUI with `systemd`:

```bash
MODEL=/home/exouser/models/Meta-Llama-3.1-70B-Instruct-Q3_K_L.gguf \
N_CTX=4096 \
USER=exouser \
NVHPC_MOD=nvhpc/24.7/nvhpc \
sudo tee /etc/systemd/system/llama.service >/dev/null <<'EOF' && \
sudo tee /etc/systemd/system/webui.service >/dev/null <<'EOF2' && \
sudo systemctl daemon-reload && \
sudo systemctl enable --now llama webui
[Unit]
Description=Llama.cpp OpenAI-compatible server
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=/home/$USER
ExecStart=/bin/bash -lc "module load $NVHPC_MOD miniforge && conda run -n llama python -m llama_cpp.server --model $MODEL --chat_format llama-3 --n_ctx $N_CTX --n_batch 128 --n_gpu_layers -1 --n_threads 16 --port 8000"
Restart=always

[Install]
WantedBy=multi-user.target
EOF
[Unit]
Description=Open Web UI serving
Wants=network-online.target
After=network-online.target llama.service
Requires=llama.service
PartOf=llama.service

[Service]
User=exouser
Group=exouser
WorkingDirectory=/home/exouser
Environment=OPENAI_API_BASE_URL=http://localhost:8000/v1
Environment=OPENAI_API_KEY=local-no-key
ExecStartPre=/bin/bash -lc 'for i in {1..600}; do /usr/bin/curl -sf http://localhost:8000/v1/models >/dev/null && exit 0; sleep 1; done; echo "llama not ready" >&2; exit 1'
ExecStart=/bin/bash -lc 'source /etc/profile.d/modules.sh 2>/dev/null || true; module load miniforge; conda run -n open-webui open-webui serve --port 8080'
Restart=on-failure
RestartSec=5
TimeoutStartSec=600
Type=simple

[Install]
WantedBy=multi-user.target
EOF2
```
