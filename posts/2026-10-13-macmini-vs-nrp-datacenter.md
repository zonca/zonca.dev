---
title: "Same 27B model, two worlds: Mac mini vs a data-center GPU"
date: "2026-10-13"
categories: [ai]
layout: post
---

How much does datacenter hardware buy you over an Apple Silicon dev box? I had
the rare chance to measure it without confounds: the [NRP managed LLM
service](https://nrp.ai/documentation/userdocs/ai/llm-managed/) hosts
**Qwen3.8-27B** (api name `qwen3-small`) in bf16 on their Nautilus GPU fleet,
and my Mac mini (setup described in
[this post's PR](https://github.com/zonca/zonca.dev/pull/142)) serves the **same
model** quantized to NVFP4 on the MLX engine. Same weights, same task, two very
different machines.

## The two hosts

| | Mac mini | NRP |
|---|---|---|
| Compute | Apple M4 Pro (unified 48 GB) | NRP-managed NVIDIA GPUs (A100-class, 80 GB HBM) |
| Memory bandwidth | ~273 GB/s | 2 TB/s+ (HBM) |
| Data type | NVFP4 (4-bit, 18 GB) | bf16 native (54 GB) |
| Engine | Ollama + MLX, MTP speculative decoding | vLLM, chunked prefill |
| Context | 200,000 (native 262,144) | 1,000,000 (262K native, YaRN-extended) |
| Access | private tailnet | public OpenAI-compatible API, free for researchers |
| Price | ~$1,800 one-time (new, 2026) | free (NSF-funded NRP service) |

The NRP fleet serves many models (see the
[catalog](https://nrp.ai/documentation/userdocs/ai/llm-managed/models/)); the docs
note, e.g., a 120B model fits "on a single A100 or two RTX A6000", so the 27B
bf16 checkpoint sits on similar 80 GB-class GPUs.

## Method

- **Local:** direct `/api/generate`; timings from the server
  (`prompt_eval_duration`, `eval_duration`), so no client overhead.
- **NRP:** `/v1/chat/completions` streaming with thinking disabled
  (`chat_template_kwargs: {enable_thinking: false}`) and a `cache_salt`; decode
  speed measured from stream timings (samples are small, 25-42 tokens, because
  the model ends its answer early).
- Same lorem-ipsum prompts at every context length.

## Results

### pi startup (first answer)

| Host | Cold (model unloaded) | Warm (KV cache) |
|---|---|---|
| Mac mini | 30.7 s | 1.9 s |
| NRP | 2.9 s | 2.9 s |

The NRP server is always warm and its prefill is fast, so the agent's first
answer lands in ~3 s; on the Mac mini a cold first session costs half a minute,
but once the model is resident and the prefix is cached, pi comes back in ~2 s.

### Prefill (ingesting the prompt)

Local prefill is measured server-side: ~101 tok/s for short prompts (the clock
here is memory bandwidth, and NRP's prefill is in a different league: A100-class
HBM at multiple TB/s plus vLLM chunked prefill, versus ~273 GB/s on the M4 Pro).
NRP's API does not expose server-side prefill timings, so I do not report a
prefill number for it; the practical consequence shows up in the pi startup
test above.

### Generation (decode) at growing context

| Context in KV | Mac mini | NRP |
|---|---|---|
| short | 29-33 tok/s | - |
| 50 K | 13.1 tok/s | 28.0 tok/s |
| 100 K | 10.7 tok/s | 24.1 tok/s |
| 150 K | 7.9 tok/s | 10.4 tok/s |

Generation is where the gap almost disappears. Both are bandwidth bound per
token, and the two sides trade advantages: the Mac mini reads 4-bit weights
(NVFP4 is about a quarter of the bytes of bf16) and gets MTP speculative
decoding (drafting 2-3 tokens per step, measured acceptance 0.8-0.94); NRP has
far more memory bandwidth but reads bf16 weights and serves without the MTP
speedup. The result is that decode is a wash at 50-100 K, and NRP stays ahead
at 150 K. On both sides generation degrades with context (every token attends
over the whole prefix), which is the same quadratic-ish behavior, just with a
different floor.

## What this means in practice

- If your work is **latency of long prompts or huge context**, the data center
  wins decisively: 15-35× prefill, and a 1 M context window that a 48 GB Mac
  cannot allocate (262 K is the native limit and swaps at max).
- If your work is **interactive agents with short-ish context** (the pi startup
  test), the Mac mini is completely fine once warm, and it is private, free,
  quota-free, and revocable-free for server-side policies.
- NRP is also free for researchers and requires only a token from
  [nrp.ai/llmtoken](https://nrp.ai/llmtoken/) and a namespace with the LLM flag;
  it is a shared fleet, so other tenants can add variance.
- On price: the Mac mini was a **~$1,800 one-time purchase** (no per-token or
  monthly fees, and no data leaves your machine), while NRP is free for
  researchers but is a shared, hosted service. After a few months of daily
  agent use the hardware is already the cheaper option, and it keeps working
  without a token, a namespace, or a network egress path.

## What the NRP side would cost to replicate

Estimating what the NRP LLM service costs is hard (it is NSF-funded shared
infrastructure), but the hardware alone gives a sense of scale. A single
Qwen3.8-27B bf16 model needs roughly 54 GB of weights, so about **2x A100 80 GB
GPUs** (or one heavily constrained), and a full catalog like NRP's (Qwen 180B,
deepseek 304B, glm 753B, kimi 1T and more) means tens of GPUs. Order-of-magnitude
in cloud-rental terms:

| Component (catalog-scale) | Estimate |
|---|---|
| GPUs (roughly 25-40 A100/H100-class, 24/7 reserved rate ~$1.5-3/h each) | ~$30-60K/month |
| Fast local storage for weights (~1-2 TB NVMe per host) | ~$1-3K/month |
| Shared storage, network, load balancer, monitoring | ~$1-2K/month |
| Staff to run the fleet and the gateway | the biggest real cost |
| As a single model (qwen3-small only) | ~$2-3K/month (2x A100, reserved) |

So a Mac mini at ~$1,800 is roughly **six months of one GPU's equivalent**; the
whole NRP operation is more like a small datacenter budget, which is why it is
funded by NSF awards (e.g., CNS-1730158, OAC-2112167) rather than billed
per-user. For a single researcher, NRP is the free option; for a lab that needs
many hours of private inference, the $1,800 box amortizes fast.

My setup: I run the Mac mini as the always-on private server for daily agent
work, and I keep NRP as the fast, long-context option when the prompt is huge.
