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

| Prompt | Mac mini | NRP |
|---|---|---|
| 2-4 K tokens | ~101 tok/s | - |
| 5 K tokens (TTFB) | - | ~0.75 s (~14.5 K tok/s est.) |
| 50 K tokens (TTFB) | 578 s | 33.7 s |
| 100 K tokens (TTFB) | 854 s | 37.9 s |
| 150 K tokens (TTFB) | 605 s (prefix-cached) | 41.8 s |

Prefill is memory-bandwidth bound, and here the datacenter wins by 15-35×: the
M4 Pro moves ~273 GB/s while an A100-class GPU moves multiple TB/s from HBM,
and vLLM additionally pipelines/chunks the prefill. (NRP's TTFB includes
network and scheduling, so the real prefill speed is even higher.)

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

My setup: I run the Mac mini as the always-on private server for daily agent
work, and I keep NRP as the fast, long-context option when the prompt is huge.
