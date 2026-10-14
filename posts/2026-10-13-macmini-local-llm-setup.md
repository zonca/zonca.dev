---
title: "Mac mini as a private LLM server: the technical setup"
date: "2026-10-13"
categories: [ai]
layout: post
---

This is the technical companion to the
[experience post](/posts/2026-10-13-macmini-local-llm-experience): how the Mac
mini is set up, how every service runs, and where the configuration lives.
The benchmark details (prefill, decode, context stress test, agent context
sizes) are here too. The data-center comparison is in the
[comparison post](/posts/2026-10-13-macmini-vs-nrp-datacenter).

## The machine and the model

- **Hardware:** Apple M4 Pro, 48 GB unified memory, headless (no GUI login
  session, only SSH + Tailscale).
- **Server:** [Ollama](https://ollama.com) 0.40.3 with the Apple **MLX** engine.
- **Model:** **Qwen 3.8 27B NVFP4**, 18 GB, 262 K native context, vision, MTP
  head. Upstream
  [nvidia/Qwen3.8-27B-NVFP4](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4)
  (quantized from [Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B),
  Apache 2.0).

The model uses **MLX/NVFP4** tensor format with multi-token prediction (MTP):
the model drafts several tokens ahead and the runner verifies them in one step.
No draft model is needed, and an MTP head cannot stack with a separate drafter.

## Running Ollama as a service on a headless Mac

The usual advice is `brew services start ollama`, but a Mac without a GUI login
has no `gui/501` launchd domain, and brew services fails with
`launchctl ... Domain does not support specified action` (error 125). A user
LaunchAgent only starts at login. The reliable solution is a **system launchd
daemon** that runs as user `zonca` at boot:

- `/Library/LaunchDaemons/com.ollama.serve.plist`, with `RunAtLoad` and
  `KeepAlive`; logs go to `/tmp/ollama.log` and `/tmp/ollama.err.log`.
- Tuned environment: `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KV_CACHE_TYPE=q8_0`,
  `OLLAMA_KEEP_ALIVE=48h` (the model stays resident),
  `OLLAMA_CONTEXT_LENGTH=200000`, `OLLAMA_LLM_LIBRARY=mlx_metal_v3`.

Manage it with `sudo launchctl bootout system/com.ollama.serve` and
`sudo launchctl bootstrap system /Library/LaunchDaemons/com.ollama.serve.plist`.
Note that `kickstart -k` restarts the process but does not re-read a modified
plist: after an edit, use `bootout` plus `bootstrap`.

## Not a single open port, except over Tailscale

The mini sits on the office LAN, where port 22 and 11434 should not be
reachable. Two mechanisms do that:

1. **Ollama bound to the tailnet IP:** `OLLAMA_HOST=100.91.172.9:11434` in the
   plist, so the server listens only on the Tailscale address.
2. **pf firewall for SSH:** macOS sshd is launchd socket-activated and always
   creates a `*:22` socket (its `ListenAddress` in sshd_config is ignored). A
   pf anchor allows ports 22 and 11434 only on the tailnet interface `utun0`
   (plus loopback) and blocks them everywhere else. macOS does not enable pf
   automatically, so a second daemon (`com.zonca.pfctl-enable`) runs `pfctl -e`
   at boot.

A listener audit shows only `launchd *:22` (pf-filtered),
`ollama 100.91.172.9:11434`, and Tailscale's own sockets.

**Sharing with colleagues:** Tailscale device sharing (admin console, Machines,
Share this machine) gives each invited person access to only the Mac mini, with
end-to-end encryption, quarantined direction (responds to inbound only), and
instant revocation. For Ollama the OpenAI-compatible endpoint just works:
point the client at the tailnet hostname with port 11434.

## Benchmarks (2026-10-13)

Measured directly against Ollama's API (`/api/generate`), model warm, memory
bandwidth bound. Context during the benchmark: the server is configured with
`OLLAMA_CONTEXT_LENGTH=200000`, while the model natively supports 262,144
tokens.

| Metric | Result |
|---|---|
| Prefill, 2039-token prompt | 20.1 s (~101 tok/s) |
| Prefill, 4044-token prompt | 40.3 s (~100 tok/s) |
| Decode, predictable prose, 256 tokens | 28.7 tok/s |
| Decode, random hex, 512 tokens | 32.7 tok/s |
| MTP acceptance (measured across runs) | 0.80-0.94 |
| Cold model load (after full unload) | ~4 s |

Prefill is stable at ~100 tok/s regardless of length: the M4 Pro memory
bandwidth floor for a 27B dense hybrid.

### Context stress test

I stress-tested the context limit with growing prompts while watching memory
and swap:

| Context | Prefill | Result |
|---|---|---|
| 65 K | 78.6 tok/s | no swap, fine |
| 131 K | 104.5 tok/s | no swap, fine |
| 192 K | ~60 tok/s | no swap, fine |
| 262 K (native max) | collapses to ~25 tok/s | swaps up to ~6 GB, unusable |

So 200 K is the practical default on 48 GB: no swapping, and the only cost of
the larger window is slower prefill and generation at long context.

### The agent benchmark that matters: context size

For a coding agent the real cost is how much context it burns on its first
request: on this machine, 10 K tokens of preamble means an extra minute of
waiting per new session. Same trivial question, first-request token count as
seen by Ollama:

| Agent | Version | First request context | Time |
|---|---|---|---|
| **pi** (pi-coding-agent) | 1.2.0 | **2,828 tokens** | 29 s |
| goose | 1.54.0 | 4,716 tokens | 55 s |
| opencode | 1.19.0 | 8,956 tokens | 103 s |
| crush | 0.98.1 | 12,950 tokens | 120 s |

**pi** is the lightest: built-in read/bash/edit/write tools, Agent Skills
support, MCP, and still under 3 K tokens of initial context, so the first
answer comes in about half a minute instead of two. goose has tool calling and
extensions but not the Agent Skills standard; crush supports both but its
context is larger than opencode's. For a local model, context size is the
bottleneck, so pi wins.

## Configuration files

The complete configuration (launchd plist, pf anchor, pf-enable daemon, and the
OpenAI-compatible provider configs for pi, goose, and crush) is in this
[gist](https://gist.github.com/zonca/fdb12050fb7af8a092d1dbae10a2bf0e).
