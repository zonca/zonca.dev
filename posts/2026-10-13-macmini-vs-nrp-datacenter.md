---
title: "Same 27B model, two worlds: Mac mini vs a data-center GPU"
date: "2026-10-13"
categories: [ai]
layout: post
---

How much does datacenter hardware buy you over an Apple Silicon dev box? Fun
coincidence: the [NRP managed LLM
service](https://nrp.ai/documentation/userdocs/ai/llm-managed/) hosts
**Qwen3.8-27B** (api name `qwen3-small`) in bf16 on their Nautilus GPU fleet,
and my Mac mini (the high-level story is in the
[experience post](./2026-10-13-macmini-local-llm-experience.md), the full
setup in the [setup post](./2026-10-13-macmini-local-llm-setup.md)) serves the
**same model** quantized to NVFP4 on the MLX engine. Same weights, same task, two
very different machines, so it is a fun apples-to-apples comparison.

## The two hosts

| | Mac mini | NRP |
|---|---|---|
| Compute | Apple M4 Pro (unified 48 GB) | NRP-managed NVIDIA GPUs (A100-class, 80 GB HBM) |
| Memory bandwidth | ~273 GB/s | 2 TB/s+ (HBM) |
| Data type | NVFP4 (4-bit, 18 GB) | bf16 native (54 GB) |
| Engine | Ollama + MLX, MTP speculative decoding | vLLM, chunked prefill |
| Context | 200,000 (native 262,144) | 1,000,000 (262,144 native, YaRN-extended) |
| Access | private tailnet | public OpenAI-compatible API, free for researchers |
| Price | ~$1,800 one-time (new, 2026) | free (NSF-funded NRP service) |

The NRP fleet serves many models (see the
[catalog](https://nrp.ai/documentation/userdocs/ai/llm-managed/models/)); the docs
note, e.g., a 120B model fits "on a single A100 or two RTX A6000", so the 27B
bf16 checkpoint sits on similar 80 GB-class GPUs.

Two rows of the table deserve a note. The data types are two precisions of the
same weights: bf16 is the native 2-byte format (~54 GB), NVFP4 is a 4-bit
quantization (~18 GB) that trades a little quality for a lot of memory, and it
is what lets a 27B model fit comfortably in 48 GB. The engines differ too:
both speak the OpenAI-compatible API, but vLLM is the datacenter serving
stack (continuous batching, chunked prefill, prefix caching), while Ollama
with the MLX engine is the simplest way to run models natively on Apple
Silicon. The context column: NRP stretches the model's native 262,144-token
window to 1 M with YaRN, a rope-scaling method that extends a trained window;
the Mac mini stops at the native size because that is what 48 GB of memory
can hold.

## Method

- **Local:** direct `/api/generate`; timings from the server
  (`prompt_eval_duration`, `eval_duration`), so no client overhead.
- **NRP:** `/v1/chat/completions` streaming with thinking disabled
  (`chat_template_kwargs: {enable_thinking: false}`) and a `cache_salt`; decode
  speed measured from stream timings (samples are small, 25-102 tokens, because
  the model ends its answer early).
- Same lorem-ipsum prompts at every context length.

Fairness caveat: this is not a controlled benchmark. The two sides differ in
quantization (NVFP4 vs bf16), inference engine (Ollama/MLX vs vLLM), and serving
environment (a dedicated little machine vs a shared, multi-tenant GPU fleet
where my requests share capacity with other users, and the NRP timings include
network round-trip). It is simply the comparison I had access to: the same 27B
model, available both locally and on a managed service, with numbers measured
on each side as honestly as I could.

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

Local prefill is measured server-side: ~101 tok/s for short prompts, which is
the M4 Pro memory-bandwidth floor (~273 GB/s). NRP's API does not expose
server-side prefill timings, so I do not report a number for it; its A100-class
HBM (multiple TB/s) plus vLLM's chunked prefill (processing the prompt in
chunks so one long request does not block the whole GPU) puts it in a
different league, and you can see the practical effect in the pi startup test
above.

### Generation (decode) at growing context

| Context in KV | Mac mini | NRP |
|---|---|---|
| short (2.8K prompt) | 28-33 tok/s | ~38 tok/s |
| 50 K | 13.1 tok/s | 28.0 tok/s |
| 100 K | 10.7 tok/s | 24.1 tok/s |
| 150 K | 7.9 tok/s | 10.4 tok/s |

Generation is where the gap is smaller. Every generated token requires reading
the whole model from memory once, so both sides are bandwidth bound per token,
and they trade advantages: the Mac mini reads 4-bit weights (NVFP4 is about
a quarter of the bytes of bf16) and gets MTP speculative decoding (drafting 2-3
tokens per step, measured acceptance 0.8-0.94); NRP has much more memory
bandwidth but reads bf16 weights and serves without the MTP speedup. The result:
NRP is somewhat faster at short context (~38 vs ~30 tok/s), both land close at
50-100 K, and NRP stays a bit ahead at 150 K. On both sides generation degrades
with context (every token attends over the whole prefix), same behavior,
different floor.

## What this means in practice

- If your work is **latency of long prompts or huge context**, the data center
  wins: the same cold-session agent test lands in ~3 s instead of ~31 s, prefill
  there is easily an order of magnitude faster, and NRP offers a 1 M context
  window that a 48 GB Mac cannot allocate (262,144 is the native limit and it
  swaps at the max).
- If your work is **interactive agents with short-ish context** (the pi startup
  test), the Mac mini is fine once warm, and it is private, quota-free, and
  nothing leaves your machine.
- NRP is free for researchers, needs only a token from
  [nrp.ai/llmtoken](https://nrp.ai/llmtoken/) and a namespace with the LLM flag,
  and it is a shared fleet, so other tenants can add variance.

## What the NRP side would cost to buy

A single Qwen3.8-27B bf16 model needs roughly 54 GB of weights, so about
**2× A100 80 GB GPUs** is the realistic minimal setup (a full catalog like NRP's
would be tens of GPUs). Buying that equivalent today (current list prices):

| Component (purchase) | Estimate |
|---|---|
| 2× NVIDIA A100 80 GB (new, ~$9-13K each) | ~$18-26K |
| Minimal server: 1U EPYC/Xeon, 256 GB RAM, 2 TB NVMe, 2× 2400 W PSU | ~$6-9K |
| Total one-time | **~$25-35K** |

That is 14-19× the Mac mini's ~$1,800, before putting it in a rack: the GPU
server draws ~1.2-1.5 kW under load (and ~300-500 W idle) versus the Mac mini's
tens of watts idle, so running the GPU box also needs real power and cooling.
This is why NRP is funded by NSF awards (e.g., CNS-1730158, OAC-2112167) and
shared across researchers instead of being bought per lab. For a single lab,
the $1,800 Mac mini provides private 27B inference with no quota and no per-user
token; for a research group with heavy, high-concurrency or multi-model needs,
the GPU server is the right tool.

My setup: I run the Mac mini as the always-on private server for daily agent
work, and I keep NRP as the fast, long-context option when the prompt is huge.
