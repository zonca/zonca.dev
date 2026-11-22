---
title: "A coding-agent adapter on a local 27B model: what it changes on Trello, email and a small script"
date: 2026-11-22
categories: [ai, llm, python]
layout: post
description: "Hugging Face's pi-adapted Qwen 3.8 27B claims fewer turns per task. On a Mac mini where prefill runs at 100 tok/s, turns are the cost, so I merged the adapter into the base weights, kept multi-token prediction working, and measured both models on three real tasks."
---

Hugging Face published
[harness-hub/Qwen3.8-27B-pi-adapted](https://huggingface.co/harness-hub/Qwen3.8-27B-pi-adapted), a
LoRA for [Qwen 3.8 27B](https://huggingface.co/Qwen/Qwen3.8-27B) trained with reinforcement learning
inside the [pi](https://github.com/earendil-works/pi) coding agent. Its card claims SWE-bench Pro
(hard 51) from 39.2% to 64.7%, Terminal-Bench 2.1 from 39.5% to 55.8%, and, the number I care about,
**fewer than half the turns per solved task**. Benchmarks on another machine with a frontier model
are interesting; the turn count is the one that transfers, because of how a local model spends its
time.

On my [Mac mini LLM server](./2026-10-13-macmini-local-llm-setup.md) prefill runs at about 100 tok/s
and decode at about 28 tok/s. An agent turn re-sends the whole conversation, so a turn that adds 3k
tokens of tool output costs 30 s of prefill before the model writes anything, and the generated
tokens are the cheap part. Halving the number of turns halves that cost, in a way that no sampling
parameter or quantization tweak can.

So the question here is narrow and answerable: **with the adapter merged in, does the same model do
the same real work in fewer turns, and does it still run at the same speed per token?** This post
answers both, on three tasks from my own workload.

## The two models

[zonca/Qwen3.8-27B-pi-adapted-merged](https://huggingface.co/zonca/Qwen3.8-27B-pi-adapted-merged) is
the base checkpoint with the adapter merged in float16, 55.6 GB in 18 shards. The [previous
post](./2026-11-21-qwen38-pi-adapted-merged-fp16.md) covers why the merge is stored as float16
rather than bfloat16 and why a GGUF would have been a mistake; the short version is that the delta
falls below bfloat16's resolution and that a GGUF conversion drops the multi-token prediction head,
which is where the decode speed comes from.

Both models are served by the same Ollama 0.40.12 on the Mac mini, on the MLX engine, at `nvfp4`,
with the same context window, the same sampling parameters and the same chat template; the tag
`qwen3.8-pi:27b-nvfp4` was created by cloning the Modelfile of the base tag and changing the `FROM`
line. Everything below was measured from nebula over the tailnet, so the client, the network and the
harness are identical for the two models.

## First: did the merge cost anything per token?

Before asking whether the adapter helps, it has to be established that importing a merged checkpoint
did not break the engine. Two things could have gone wrong: the MTP head could have been dropped
during `ollama create`, and the float16 to `nvfp4` quantization of weights that had been changed by
1e-4 could have washed out the adapter.

The MTP head is intact. The configuration that `ollama create` wrote for the new tag lists all 15
`mtp.*` tensors (from `mtp.fc.weight` and `mtp.pre_fc_norm_embedding.weight` down to the norms and
projections of `mtp.layers.0`), and the server prints `speculative decode stats` lines while it
serves the new tag, which it could not do without the head. The decode rate is the third piece of
evidence, because that is what the head buys:

| model | cold load | decode | prefill (2k) | prefill (8k) | artifact |
|---|---|---|---|---|---|
| `qwen3.8:27b-nvfp4` | 5.3 s | **28.7** tok/s | 103 tok/s | 100 tok/s | 18.17 GB |
| `qwen3.8-pi:27b-nvfp4` | 5.9 s | **21.0** tok/s | 106 tok/s | 103 tok/s | 21.57 GB |

Prefill is identical, to within the noise of the measurement, which is the important half: the
prompt-processing path, the chat template and the context window all behave as before. Decode is
**about a quarter slower** (27% on the 256-token runs above, 24% on the longer ones below), and
rather than leave it at that I decomposed it, because a decode rate is two numbers multiplied
together:

    decode rate = tokens accepted per forward pass x forward passes per second

The server logs both faces of that product (`speculative decode stats` gives iterations, drafts and
accepted tokens), so three runs per model, alternating order, unloaded before each run, with a fixed
prompt, a fixed seed and 512 tokens to generate:

| | base | merged | ratio |
|---|---|---|---|
| tokens per forward pass | 2.35 | 1.88 | 0.80 |
| milliseconds per forward pass | 85.3 | 91.8 | 1.08 |
| decode | 26.9 tok/s | 20.4 tok/s | 0.76 |
| acceptance | 0.71 | 0.81 | |
| effective bandwidth | 213 GB/s | 235 GB/s | |

Four fifths of the loss is the first line, not the second: the merged model accepts fewer tokens per
pass, not because its speculative decoder is worse but because it drafts shallower. The base tag
settles at 2.0 to 2.3 draft tokens per position with a ceiling of 3 or 4; the merged tag starts at
1.4 and settles at 1.0 with a ceiling of 2, while its acceptance at that depth goes *up*, to 0.81.
That is what an untouched draft head looks like next to a changed policy: the multi-token prediction
head was copied through the merge and never trained against the adapter, so its first guess about
what this model says next is still good and its second and third are not, and the engine's adaptive
depth controller notices and stops asking for them.

The remaining fifth is size: held at the base model's 85 ms per pass, the merged tag would decode at
22.0 tok/s, so 5% of the loss is bytes. The size has a specific cause. `-q nvfp4` does not mean four
bits everywhere. Ollama's create-side policy keeps the quantization-sensitive `v_proj`, `k_proj` and
`down_proj` at 8 bits (`mxfp8`) in the first and last eighth of the layers and in every third layer
in between, and it does the same for `lm_head`; everything else gets 4-bit NVFP4. Comparing the two
manifests tensor by tensor:

| tensors | base | merged | difference |
|---|---|---|---|
| 64 `mlp.down_proj` | 3.209 GB | 5.883 GB | +2.674 |
| `lm_head` | 0.715 GB | 1.311 GB | +0.596 |
| 16 `k_proj` plus 16 `v_proj` | 0.094 GB | 0.174 GB | +0.079 |
| 15 `mtp.*` | 0.239 GB | 0.286 GB | +0.047 |
| `gate_proj`, `up_proj`, `q_proj`, `o_proj`, linear attention, vision, embeddings | 13.9 GB | 13.9 GB | 0.000 |

The 1.83 ratio in that table is exact: 0.5625 bytes per parameter for NVFP4 at a group size of 16,
1.03125 for `mxfp8` at a group size of 32. The base tag does not pay it because it was not created
from a float16 checkpoint at all: it was imported from NVIDIA's already-quantized NVFP4 release,
where those tensors are 4 bits like everything else.

So the slowdown is expected, and both halves of it are consequences of decisions rather than bugs:
one comes from the adapter training without the draft head, the other from the local conversion
spending 3.4 GB on precision for the tensors the policy considers fragile. That second choice can be
undone, by quantizing uniformly to 4 bits with `mlx-lm` and importing the result, and it would buy
back the 5% of decode time that the extra bytes cost. On a model whose entire point is to reproduce
an adapter's behaviour, trading precision on its most sensitive projections for 5% of decode speed
is not obviously a good trade, so I left it alone.

So the answer to the first question is split. Prefill, the path that dominates an agent workload, is
unaffected. Decode lost about a quarter, which is real but is paid per generated token, and the
tasks below show that the merged model generates far fewer of them. A decode rate near 15 tok/s
would have meant the speculative decoder had silently stopped working; that is the failure this
measurement rules out.

## Then: does it turn fewer times?

pi, and only pi: the adapter was trained inside pi, so measuring it inside another harness would mix
the adapter with the harness. Three tasks from my own workload, run non-interactively with
`pi -p --mode json`, each in a fresh empty directory, one run per model:

- **Trello:** read one real card (name, description, all comments), say what it is about, name the
  one next action, and flag anything stale in it.
- **Email:** read one real Gmail thread of six messages and summarize it, draft the next reply,
  and list any open question the draft leaves unanswered.
- **Coding:** write a small Python module plus its pytest tests in the current directory, run the
  tests, report the result.

The Trello and email tasks run with only the `bash` and `read` tools and an explicit instruction not
to change anything, so the agent cannot move a card or send mail while being measured. The card and
the thread were frozen for the duration: no comment was added to the card between the two runs,
because that would have changed what the second model read.

What the harness records is what an agent actually costs on a machine like this: **turns** (model
calls), **prompt tokens processed** (the sum of the input tokens of every turn, which is the prefill
work), **generated tokens** and **wall clock** for the whole task.

| task | model | wall | turns | tool calls | prompt tok | gen tok |
|---|---|---|---|---|---|---|
| Trello | base | 272 s | 4 | 5 | 11392 | 3840 |
| Trello | merged | **143 s** | 5 | 4 | 5139 | 1766 |
| Email | base | 268 s | 12 | 12 | 7754 | 3197 |
| Email | merged | **168 s** | 10 | 9 | 6878 | 1895 |
| Coding | base | 75 s | 4 | 4 | 2945 | 1322 |
| Coding | merged | **75 s** | 3 | 3 | 2778 | 990 |

Read it as ratios of merged over base: the Trello task took **0.53x** the wall clock, the email
thread **0.63x**, the coding task **1.00x**.

The turns did not fall. The adapter card claims fewer than half the turns per solved task and that
did not happen here: 5 against 4 on the Trello task, 10 against 12 on the email thread, 3 against 4
on the coding task, which nets out to roughly parity. Whatever the adapter learned, it is not fewer
model calls on this kind of work.

What did change is how much each turn carries. The merged model generated **46%** of the base
model's tokens on the Trello task and **59%** on the email thread, and it kept fewer tokens in each
turn's context (5139 against 11392 prompt tokens on Trello). On a machine where a long answer at 21
tok/s costs ten seconds per hundred words, that is where the wall clock goes. The base model
deliberates at length before it answers; the adapted one reaches the same conclusions in about half
the words.

The coding task is the control for that interpretation. It is short, it is dominated by writing
files and running pytest rather than by generation, and there the two models finished in the same
time to the second, 75 s, even though the merged model used one turn fewer and generated a quarter
fewer tokens. When the work is not generation, the adapter has nothing to save.

## Quality, checked where it can be checked objectively

Wall clock and turn counts say nothing about whether the work was right. One of the three tasks has
an objective check, so it was performed:

- **The coding task.** Both models produced `shardcheck.py` and its tests. I re-ran `pytest` in
  each directory after the agent exited, and both pass, 5 tests each. The merged model's answer
  was shorter and the code was equally correct.
- **The Trello card.** Both identified the card's state (published, numerically verified,
  acceptance test outstanding) and proposed the same next action, running the acceptance test on
  the Mac. Both repeated the card's own then-stale reference to the scripts being "in a gist",
  which is what the card said when they read it.
- **The email thread.** Both summarized the same decisions (dates fixed at 21 to 23 September 2027
  at SDSC, publication done, a dedicated site planned with neither owner nor date) and both listed
  the same open items.

Those last two were read and judged, which is not a measurement, so they are reported as an
observation and not as a score. The observation is consistent across the run: the merged model wrote
about half as much to arrive at the same conclusions, which is where its wall-clock advantage comes
from.

## Limitations, stated plainly

- **One run per task per model.** Three tasks and two models is a demonstration, not a study. A
  turn count that differs by one turn could be sampling noise; the same task always reading better
  with one model is what would make it convincing, and that needs more tasks, not more runs of
  these.
- **Thinking was left on.** The adapter was trained with thinking off, but pi talks to the model
  through Ollama's OpenAI-compatible endpoint and does not send `think: false` there, so both
  models reasoned before answering. That is identical on both sides, so the comparison holds, but
  it inflates the generated-token counts for both and it is not how I would run the adapter in
  production.
- **One machine, one quantization.** These numbers are for `nvfp4` on an M4 Pro with 48 GB. The
  adapter is a weight change, so the relative token counts should survive a different quantization
  better than the wall clock does.
- **The tasks are mine.** A Trello card about a model release, a thread about a conference date
  and a shard-index utility are representative of my agent workload and of nothing else.

## Reproduce it

The tools are in [zonca/lora-merge-tools](https://github.com/zonca/lora-merge-tools):
`bench_ollama.py` for the per-token numbers and `bench_pi.py` with `bench_tasks.json` for the agent
numbers, which also reuses a measured baseline with `--baseline-results` so the second model costs
only the second set of runs.

```bash
python bench_ollama.py --url http://127.0.0.1:11434 \
    --models qwen3.8:27b-nvfp4 qwen3.8-pi:27b-nvfp4

python bench_pi.py --model-a macmini/qwen3.8:27b-nvfp4 \
                   --model-b macmini/qwen3.8-pi:27b-nvfp4 \
                   --tasks bench_tasks.json --out results.json
```

## What I took from it

On this machine, on these three tasks, the adapter does not deliver what its card promotes: turns
per task were unchanged, so the mechanism the card describes is not what showed up. What it delivers
is terseness, and on a local model that is worth something concrete. On the two reading tasks it cut
the time I wait to 53% and 63% of the base model's, with answers of the same quality, because it
spends about half the tokens thinking out loud.

Against that: decode is about a quarter slower per token, and the artifact is 3.4 GB larger. If the
reply is long, the adapter is a loss. If the work is reading, summarizing and deciding, it is a
clear gain.

So the arrangement I am keeping on the Mac mini is both tags: `qwen3.8-pi:27b-nvfp4` for triage and
summarization loops, where it finishes in about half the time, and `qwen3.8:27b-nvfp4` for anything
where the output itself is the product, where the base model is still the faster one. Neither is a
coding-benchmark winner on this hardware, because a short coding task is not bounded by generation.

The limitation that matters is the one this measurement cannot address: three tasks, one run each.
The failure mode that would make the merged model worse in practice is a shorter answer that quietly
misses something, and one Trello card and one email thread are not enough to rule that out. The next
step worth doing is ten cards through both models, counting what the short answers leave out, rather
than more repetitions of these three.
