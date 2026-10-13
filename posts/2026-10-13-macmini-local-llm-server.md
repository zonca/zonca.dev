---
title: "Mac mini as a private local LLM server: setup, benchmarks, and choosing pi"
date: "2026-10-13"
categories: [ai]
layout: post
---

An Apple M4 Pro Mac mini (48 GB unified memory) now runs my private LLM server in
the office. It is managed entirely over SSH, reachable only through my private
[Tailscale](https://tailscale.com) tailnet, and it serves an 18 GB vision language
model with an OpenAI-compatible API. This post describes the setup and, more
interestingly, the benchmark that made me pick **pi** over opencode and crush as
the coding agent for it.

## The machine and the model

- **Hardware:** Apple M4 Pro, 48 GB unified memory, headless (no GUI login
  session, only SSH + Tailscale).
- **Server:** [Ollama](https://ollama.com) 0.40.3 with the Apple **MLX** engine.
- **Model:** **Qwen 3.8 27B NVFP4**, 18 GB, 262 K native context, vision, MTP
  head. Upstream
  [nvidia/Qwen3.8-27B-NVFP4](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4)
  (quantized from [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B),
  Apache 2.0).

The model uses **MLX/NVFP4** tensor format with multi-token prediction (MTP),
which Ollama's MLX runner uses for self-speculative decoding: the model drafts
several tokens ahead and the runner verifies them in one step. No draft model is
needed, and the MTP head cannot stack with a separate draftsman.

## Running Ollama as a service on a headless Mac

The usual advice is `brew services start ollama`, but a Mac mini without a GUI
login has no `gui/501` launchd domain, and `brew services` fails with
`launchctl ... Domain does not support specified action` (error 125). A user
LaunchAgent only starts at login. The reliable solution is a **system launchd
daemon** that runs as the user `zonca` at boot:

- `/Library/LaunchDaemons/com.ollama.serve.plist` (in the
  [gist](https://gist.github.com/zonca/fdb12050fb7af8a092d1dbae10a2bf0e)) with
  `RunAtLoad` and `KeepAlive`; logs go to `/tmp/ollama.log` and
  `/tmp/ollama.err.log`.
- Tuned environment: `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0`,
  `OLLAMA_KEEP_ALIVE=48h` (the model stays resident),
  `OLLAMA_CONTEXT_LENGTH=65536`, `OLLAMA_LLM_LIBRARY=mlx_metal_v3`.

Manage it with `sudo launchctl bootout system/com.ollama.serve` and
`sudo launchctl bootstrap system /Library/LaunchDaemons/com.ollama.serve.plist`.
Note that `kickstart -k` restarts the process but does not re-read a modified
plist: after editing it, use `bootout` plus `bootstrap`.

## Not a single open port, except over Tailscale

The mini sits on the office LAN, where I did not want port 22 or 11434 reachable.
Two mechanisms do that:

1. **Ollama bound to the tailnet IP:** `OLLAMA_HOST=100.91.172.9:11434` in the
   plist, so the server listens only on the Tailscale address.
2. **pf firewall for SSH:** macOS sshd is launchd socket-activated and always
   creates a `*:22` socket (its `ListenAddress` in sshd_config is ignored). A pf
   anchor ([gist](https://gist.github.com/zonca/fdb12050fb7af8a092d1dbae10a2bf0e))
   allows ports 22 and 11434 only on the tailnet interface `utun0` (plus
   loopback) and blocks them from everything else. macOS does not enable pf
   automatically, so a second daemon (`com.zonca.pfctl-enable`) runs `pfctl -e`
   at boot.

A listener audit shows only `launchd *:22` (pf-filtered),
`ollama 100.91.172.9:11434`, and Tailscale's own sockets.

**Sharing with colleagues:** Tailscale device sharing (admin console, Machines,
Share this machine) gives each invited person access to only the Mac mini, with
end-to-end encryption, quarantined direction (responds to inbound only), and
instant revocation. There is no way to expose services to the public internet.
(For Ollama specifically the OpenAI-compatible endpoint just works:
`base_url = http://zoncamini:11434/v1`.)

## Fresh benchmarks (2026-10-13)

Measured directly against Ollama's API (`/api/generate`), model warm, memory
bandwidth bound. Context size during the benchmark: the server is configured
with `OLLAMA_CONTEXT_LENGTH=65536`, while the model natively supports 262,144
tokens.

| Metric | Result |
|---|---|
| Prefill, 2039-token prompt | 20.1 s (~101 tok/s) |
| Prefill, 4044-token prompt | 40.3 s (~100 tok/s) |
| Decode, predictable prose, 256 tokens | 28.7 tok/s |
| Decode, random hex, 512 tokens | 32.7 tok/s |
| MTP acceptance (measured across runs) | 0.80-0.94 |
| Cold model load (after full unload) | ~4 s |

Prefill is stable at ~100 tok/s for any prompt length: the M4 Pro memory
bandwidth floor for a 27B dense hybrid. Decode runs at 26-33 tok/s with MTP;
interestingly, this run measured higher acceptance on random content (0.94) than
on predictable prose (0.80-0.83).

## The agent benchmark that matters: context size

tok/s is nice, but for a coding agent the real cost is how much context it burns
on its first request: on an 18 GB model at ~100 tok/s, 10 K tokens of preamble
means an extra minute of waiting on every new session. I pointed several agents
at the same local endpoint and asked the same trivial question; the context size
is the token count of the first request as seen by Ollama:

| Agent | Version | First request context | Time |
|---|---|---|---|
| **pi** (pi-coding-agent) | 1.2.0 | **2,828 tokens** | 29 s |
| goose | 1.54.0 | 4,716 tokens | 55 s |
| opencode | 1.19.0 | 8,956 tokens | 103 s |
| crush | 0.98.1 | 12,950 tokens | 120 s |

**pi** is the lightest: built-in read/bash/edit/write tools, Agent Skills
support, MCP, and still under 3 K tokens of initial context, so the first answer
comes in about half a minute instead of two. goose has tool calling and
extensions but not the Agent Skills standard; crush supports both but its context
is larger than opencode's. For a local model, context size is the bottleneck, so
pi wins.

## Configuration files

The complete configuration (launchd plist, pf anchor, pf-enable daemon, and the
OpenAI-compatible provider configs for pi, goose, and crush) is in this
[gist](https://gist.github.com/zonca/fdb12050fb7af8a092d1dbae10a2bf0e).
