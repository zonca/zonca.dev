---
title: "Merging a coding-agent LoRA into Qwen 3.8 27B, and why the dtype you save it in matters"
date: 2026-11-21
categories: [ai, llm, python]
layout: post
description: "How to merge a PEFT LoRA into a 27B sharded checkpoint one shard at a time, why saving the result as bfloat16 silently discards most of the adapter, and how the float16 merged checkpoint becomes a native MLX nvfp4 model on an M4 Pro."
---

Hugging Face published a LoRA adapter for [Qwen 3.8 27B](https://huggingface.co/Qwen/Qwen3.8-27B)
trained with reinforcement learning inside the [pi](https://github.com/earendil-works/pi) coding
agent:
[harness-hub/Qwen3.8-27B-pi-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-pi-adapted).
On its own card it lifts SWE-bench Pro (hard 51) from 39.2% to 64.7% and Terminal-Bench 2.1 from
39.5% to 55.8%, and it gets there in fewer than half the turns per task. The turn count is the
interesting number for me: on my [Mac mini LLM server](./2026-10-13-macmini-local-llm-setup.md) the
cost of an agent run is turns multiplied by prompt prefill at roughly 100 tok/s, so halving the
turns halves the wall clock in a way that no sampling or quantization tweak can.

The adapter ships as a 640 MB PEFT checkpoint, not as a merged model. Merging is easy in
principle, `W + (alpha / r) * B @ A` per adapted matrix, and `PeftModel.merge_and_unload()` does it
in one line. Two things about that one line cost me a day of reading, so this post is about those
two things and about the merged checkpoint I published from them:
[zonca/Qwen3.8-27B-pi-adapted-merged](https://huggingface.co/zonca/Qwen3.8-27B-pi-adapted-merged).

## Trap one: bfloat16 quietly throws the adapter away

The default dtype of a 27B model is bfloat16, and saving a merged checkpoint in the base dtype is
what everybody does. For this adapter it does not work. A LoRA delta is tiny: in the checkpoint I
merged, the RMS of the delta is about 1e-5 against weights whose absolute maximum is between 0.1 and
0.9, so each weight moves by roughly 1e-4. bfloat16 has 8 explicit mantissa bits, which at a
magnitude of 0.3 is a resolution of about 2e-3. The change is an order of magnitude below the
resolution of the format it is being written into, so most of it rounds away.

An independent merge of the same adapter
([dawidvdh/Qwen3.8-27B-pi-adapted-oQ4e-mtp](https://huggingface.co/dawidvdh/Qwen3.8-27B-pi-adapted-oQ4e-mtp))
measured exactly this: written back as bfloat16, only 65 to 82% of the delta survives, with a
relative error of 0.61 to 0.73; written as float16, 99.9 to 100% survives, relative error 0.10 to
0.16. The merge has to happen in float32 and be stored in **float16**. float16 has a narrower
exponent range, but these are model weights of order one, so nothing overflows.

The pleasant side effect is that the tensors the adapter does not touch can be upcast exactly:
bfloat16 has the wider range but the shorter mantissa, so every normal bfloat16 value is
representable in float16 without loss. In my build that check is part of the verification, and it
passes bit for bit.

## Trap two: the container format decides whether the accelerator survives

The second trap is the target format, and it is specific to Apple Silicon. The model ships with a
multi-token prediction head (15 `mtp.*` tensors in the base checkpoint). On the MLX engine that head
drafts several tokens ahead and the model verifies them in one pass, which is where the 30+ tok/s
decode on a 48 GB M4 Pro comes from; without it the memory bandwidth alone allows about 15 tok/s.

A GGUF conversion does not carry the MTP head, so a GGUF merge is a merge with half the decode
speed. What does carry it is Ollama's native MLX path: on Ollama the `nvfp4` quantization is always
the MLX engine, and `ollama create` preserves the `mtp.*` tensors (it did not for a while, that was
[ollama#17019](https://github.com/ollama/ollama/issues/17019), fixed in July 2026 by
[ollama#16919](https://github.com/ollama/ollama/pull/16919)).

So the artifact worth publishing is not a GGUF and not somebody's four-bit MLX build. It is the
**merged float16 checkpoint**, which lets each user produce whichever of the two they want, and
which is the only input that makes the Apple Silicon path possible.

## Merging 55 GB on a machine with 11 GB of RAM

`merge_and_unload()` wants the whole base model in memory: 55.6 GB as bfloat16, more as float32.
My build machine has 11 GB. That is not a blocker if the merge is written as a streaming job
instead of a library call:

- read `model.safetensors.index.json`, which maps every tensor name to its shard;
- for each shard: read one tensor at a time through `safetensors.safe_open`, add its float32 delta,
  cast to float16, and append it to the output file;
- write the output shard with a streaming writer (header first, then tensors), because
  `safetensors` wants the whole dictionary in memory and I do not have it.

Peak memory is then one tensor plus its delta, under 1 GB even for the 17408 by 5120 `up_proj`
matrices, and peak disk is two shards. The same loop works on a laptop with 16 GB, which is the
point: the merge is not a GPU job.

The adapter maps cleanly onto the base: 256 LoRA pairs, `q_proj`, `k_proj`, `v_proj`, `o_proj` on
the 16 full-attention layers and `gate_proj`, `up_proj`, `down_proj` on all 64 layers of this hybrid
attention model, with `r = 32`, `alpha = 64`, so scale 2.0. The script asserts that every adapter
module found a base tensor and refuses to run if one is left over, which is the failure mode that
matters: a silent mismatch produces a model that loads, generates, and is just not the one you
trained.

## The download is the other half of the job

Fetching the base was the part that nearly stopped the build. A plain request for
`resolve/main/model-00001-of-00018.safetensors` came back at 1 to 2 MB/s, which is nine hours for
55 GB, while the same file fetched as 100 MB byte ranges came back at 25 to 40 MB/s per request. So
the downloader sends a queue of ranges to a pool of twelve curl workers, resumes any range that
stalls (curl gives up after 25 s below 200 kB/s), checks each finished file against the sha256 the
Hub reports, and assembles the chunks in order. The whole base takes about half an hour that way.
That is `hf_get.py`, in the same gist.

## Verifying instead of hoping

A merge is arithmetic, so it can be checked exactly rather than sampled. For every shard the build
recomputes each merged tensor independently, with `einsum` instead of `matmul`, and demands a
bit-identical float16 result; it also demands that every tensor the adapter does not touch is
bit-identical to the base upcast to float16, that shapes and dtypes match, and that the shard index
still describes the files on disk. All 18 shards pass. The per-tensor delta has an RMS between
1.2e-5 and 2.9e-5 and an absolute maximum of 5.8e-4, the size the adapter's own description
implies.

The scripts are [in this gist](https://gist.github.com/zonca/4095cbb7a05019efc2bf9b8db6a6212b) and
take any sharded checkpoint and any PEFT LoRA, so they are not specific to Qwen.

## The published checkpoint

[zonca/Qwen3.8-27B-pi-adapted-merged](https://huggingface.co/zonca/Qwen3.8-27B-pi-adapted-merged):
18 shards, 55.6 GB, float16, Apache 2.0, same tensor names and same shard boundaries as the base, so
the base index applies unchanged. Every shard was hashed locally, uploaded, and compared against the
sha256 the Hub reports before the local copy was deleted.

## On the Mac mini

The last step runs on the Mac, not here:

```bash
hf download zonca/Qwen3.8-27B-pi-adapted-merged --local-dir Qwen3.8-27B-pi-merge
printf 'FROM ./Qwen3.8-27B-pi-merge\n' > Modelfile
ollama create qwen3.8-pi:27b-nvfp4 -q nvfp4 -f Modelfile
ollama show qwen3.8-pi:27b-nvfp4
```

`ollama show` must report the MTP layers in the artifact, and the server log must keep printing
`speculative decode stats` lines, which is the same canary I use for the base model. Keep the
context window at 32768 and send `"think": false`, because the adapter was trained with thinking
off.

## What is still unmeasured

Everything above is about producing a faithful checkpoint. I have not benchmarked the model yet:
the numbers quoted at the top are the adapter author's, under pi, on software-engineering tasks. My
own workload on that machine is Trello and email agent loops driven by opencode and pi, where the
adapter's gains are plausible (it is a tool-efficiency gain, not a coding trick) but unproven. That
comparison, on the actual cards, with prefill, decode, turn counts and wall clock, is the next post.
