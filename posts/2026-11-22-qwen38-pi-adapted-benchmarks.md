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
slower, and the first measurement said 27%, which is a single number from a single kind of text, so
I repeated it over four kinds of content before believing it.

A decode rate is two numbers multiplied together, and Ollama logs both:

    decode rate = tokens accepted per forward pass x forward passes per second

Four prompts (explanatory prose, code, an enumerative list, and creative writing at temperature 1),
two repetitions each, models interleaved and unloaded before every run, 400 tokens generated:

| content | model | decode | tokens/pass | ms/pass | acceptance |
|---|---|---|---|---|---|
| prose | base | 27.2 tok/s | 2.36 | 86.7 | 0.70 |
| prose | merged | 20.2 tok/s | 1.94 | 96.0 | 0.79 |
| code | base | 30.9 tok/s | 2.77 | 89.7 | 0.87 |
| code | merged | 22.7 tok/s | 2.80 | 123.2 | 0.90 |
| enumeration | base | 26.2 tok/s | 2.31 | 88.3 | 0.66 |
| enumeration | merged | 19.3 tok/s | 1.78 | 92.0 | 0.73 |
| creative | base | 23.2 tok/s | 1.83 | 78.8 | 0.60 |
| creative | merged | 18.4 tok/s | 1.70 | 92.7 | 0.65 |

| content | decode ratio | tokens/pass ratio | ms/pass ratio |
|---|---|---|---|
| prose | 0.74 | 0.82 | 1.11 |
| code | 0.74 | 1.01 | 1.37 |
| enumeration | 0.74 | 0.77 | 1.04 |
| creative | 0.79 | 0.93 | 1.18 |

The decode ratio is the stable number: 0.74, 0.74, 0.74, 0.79. The adapted model is about a quarter
slower to generate, whatever it is generating. What is not stable is the split, and that is what
makes the mechanism visible.

On code the adapted model keeps exactly the base model's draft depth (2.80 against 2.77 tokens per
pass) and every pass is 1.37 times slower. That is the cleanest measurement of the weight cost: same
work per pass, 19% more bytes, 37% more time. The extra time beyond the bytes is the second finding
of this exercise, and it points at the 8-bit tensors not being free: `mxfp8` is a different kernel
path from the `nvfp4` matvec the engine runs for everything else, and it appears to cost more per
byte than the format it replaces here.

On enumeration the adapted model drafts shallower (1.78 against 2.31 tokens per pass) and its passes
are only 1.04 times slower, because a pass that verifies fewer draft tokens does less work. The two
effects cancel: fewer tokens per pass, cheaper passes, same 0.74 overall. My first explanation, that
four fifths of the slowdown was drafting and one fifth bytes, was an artifact of measuring one
content type. The honest version is that the two trade off, with the total landing at 0.75 in every
case.

Where the extra bytes come from is unchanged, and the manifests pin it down exactly. `-q nvfp4` does
not mean four bits everywhere. Ollama's create-side policy keeps the quantization-sensitive `v_proj`,
`k_proj` and `down_proj` at 8 bits (`mxfp8`) in the first and last eighth of the layers and in every
third layer in between, and does the same for `lm_head`; everything else gets NVFP4:

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

So the slowdown is expected in the sense that both of its causes follow from decisions rather than
bugs, and it is not a broken speculative decoder: prefill is untouched and MTP runs on both tags. It
is also avoidable, in part: quantizing uniformly to 4 bits with `mlx-lm` before the import would
remove the byte and kernel penalty, at the price of the precision the policy deliberately keeps on
the model's most sensitive projections. On a model whose entire point is reproducing an adapter's
behaviour I did not think that was a good trade, so I left it alone.

## Then: does it turn fewer times?

pi, and only pi: the adapter was trained inside pi, so measuring it inside another harness would mix
the adapter with the harness. Five tasks from my own workload, each run twice per model, with the
models interleaved inside every repetition so that a change in machine state cannot favour one of
them, and a fresh directory per run:

- **Trello, two different cards:** read one real card (name, description, all comments), summarize
  it, name the one next action, and flag anything stale.
- **Email:** read one real six-message Gmail thread, summarize it, draft the next reply, and list
  the open questions the draft leaves unanswered.
- **Coding, two tasks:** write a module plus its tests from a specification, and separately fix a
  bug in a module so that its existing tests pass.

The Trello and email tasks run with only the `bash` and `read` tools, and the prompt says plainly
not to move, comment on or send anything, so the agent cannot change my board or my inbox while it
is being measured. The two coding tasks are checked objectively after the agent exits: `pytest` for
both, plus a sha256 of the test file, so "make the tests pass" cannot quietly become "edit the
tests".

| task | model | wall, two runs (s) | turns | prompt tok | gen tok | check |
|---|---|---|---|---|---|---|
| Trello, long card | base | 362, 262 | 4, 4 | 14369 | 3977 | |
| Trello, long card | merged | 232, 286 | 5, 4 | 10600 | 2864 | |
| Trello, short card | base | 143, 134 | 4, 4 | 8540 | 1256 | |
| Trello, short card | merged | 126, 150 | 4, 4 | 8120 | 1042 | |
| Email thread | base | 255, 382 | 7, 10 | 15433 | 3642 | |
| Email thread | merged | 138, 199 | 5, 7 | 8862 | 1458 | |
| Coding, write it | base | 71, 82 | 3, 3 | 2758 | 1222 | 2/2 |
| Coding, write it | merged | 110, 83 | 5, 3 | 2984 | 1332 | 2/2 |
| Coding, fix the bug | base | 53, 57 | 4, 4 | 3292 | 564 | 2/2 |
| Coding, fix the bug | merged | 92, 59 | 6, 4 | 3422 | 800 | 2/2 |

Summing the per-task medians, the merged model spends 737 s against 900 s (0.82 of the time) and
generates 7494 tokens against 10662 (0.70). That single pair of numbers would make this look like a
clear win, and the per-task rows say why it is not that simple.

**The gain is concentrated where the base model rambles.** On the email thread the merged model
finishes in 53% of the time, on the long Trello card in 83%, and on the short Trello card in 100%.
Generated tokens follow the same pattern, 0.40, 0.72 and 0.83. Those are the tasks with a lot of
text to read and a summary to write, which is where the base model spends thousands of tokens
thinking out loud before it answers.

**On the coding tasks it loses.** 1.27 times the wall clock on writing a module, 1.36 on fixing a
bug, and there the generated tokens go *up*, not down (1.09 and 1.42). Both models solve both tasks
in both runs, so this is not a quality difference: it is the merged model taking an extra turn (5
against 3, 6 against 4) in the slower runs, and on a task that only takes a minute one extra turn
costs more than terser prose saves.

**Turns never fell.** 4 against 4, 4 against 4, 7 against 5 in the two email runs, 3 against 5, 4
against 6. The adapter card's headline, fewer than half the turns per solved task, does not
reproduce on this workload at all, and the mechanism it implies is not the one at work.

**The variance is large enough to matter.** The base model took 255 s and 382 s on the same email
thread; 362 s and 262 s on the same Trello card. With two runs per cell, a per-task ratio is a
direction, not a measurement. The pooled totals are steadier because the errors partly cancel, and
the coding result is consistent (slower in three of four comparisons, equal in the fourth).

This is a correction of what I first published. My first pass used three tasks, one run each, and
reported 0.53 on Trello, 0.63 on email and 1.00 on coding. With five tasks, two repetitions and
interleaved models, Trello moved to 0.83, email held at 0.53, and coding flipped to a loss. The
first numbers were not wrong so much as under-sampled: one run per cell cannot rank two models whose
own spread is 20 to 50%.

## Quality, checked where it can be checked objectively

Wall clock says nothing about whether the work was right, so every task carries its own check where
one exists.

- **Both coding tasks, both models, every run.** Eight of eight runs pass their own tests when
  re-run after the agent exits: `pytest` in the directory the agent worked in, plus, for the
  bug-fix task, a sha256 comparison proving the test file was not touched. Two models, two tasks,
  two repetitions, no failures, and the merged model's extra turn did not buy it anything
  measurable in quality.
- **The two Trello cards.** Both models summarized the state correctly and proposed the same next
  action, rotating the exposed Hugging Face token. One of them also reported the decode slowdown
  as 7% where the measurement says 25%, which is the kind of error a pass/fail check does not
  catch and a reader does.
- **The email thread.** Both produced the same summary of the decisions and the same list of open
  questions.

The coding checks are objective. The two reading tasks were read and judged, which is not a
measurement, so they are reported as an observation.

## Limitations, stated plainly

- **Two runs per cell.** The base model took 255 s and 382 s on the same email thread, and 362 s
  and 262 s on the same Trello card. A per-task ratio from two runs is a direction, not a
  measurement; the pooled totals are steadier because the errors partly cancel, and the coding
  result is consistent in three of four comparisons.
- **The Trello cards changed between the two campaigns.** The first pass read the long card before
  the benchmark comment was added to it, so those numbers are not comparable with these and only
  the second campaign appears above.
- **Thinking was left on.** The adapter was trained with thinking off, but pi talks to the model
  through Ollama's OpenAI-compatible endpoint and does not send `think: false` there, so both
  models reasoned before answering. That is identical on both sides, so the comparison holds, but
  it inflates the generated-token counts for both and it is not how I would run the adapter in
  production.
- **One machine, one quantization.** These numbers are for `nvfp4` on an M4 Pro with 48 GB. The
  adapter is a weight change, so the relative token counts should survive a different quantization
  better than the wall clock does.
- **The tasks are mine.** Two Trello cards, one email thread and two small coding tasks are
  representative of my agent workload and of nothing else.

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

The adapter is a terseness adapter, not a turn-reduction adapter. Turns per task did not fall
anywhere in this workload, which is the mechanism its card promotes; what it does is stop the model
from thinking out loud at length before answering. On a machine where decode is the slow path, that
buys real time when the task is dominated by generation: on the email thread it finishes in 53% of
the base model's wall clock, on the long Trello card in 83%. Across the five tasks it is 18% less
wall clock and 30% fewer generated tokens.

It does not win everywhere. On the short Trello card it is a wash. On the two coding tasks it is
1.27 and 1.36 times slower, with more generated tokens, because it occasionally takes an extra turn
and a one-minute task has no room for that. Both models solve both coding tasks in every run, so
this is speed, not quality.

Against that: decode is about a quarter slower per token, across prose, code, lists and creative
writing, because the local `nvfp4` conversion keeps 8-bit tensors that NVIDIA's prequantized release
does not, and the artifact is 3.4 GB larger.

So the arrangement I am keeping on the Mac mini is both tags. `qwen3.8-pi:27b-nvfp4` for the
reading and summarization loops that dominate my agent work, where it is up to twice as fast, and
`qwen3.8:27b-nvfp4` for coding tasks and anything whose output is long, where the base model is
faster and the merged one has nothing to add.

The measurement I would do next is not more repetitions of these tasks but a different question:
whether the shorter answers ever leave something out. Ten Trello cards through both models, read
side by side, counting what the short summaries miss. That is the failure mode this design cannot
detect, and it is the one that would matter if I started trusting the faster tag with the real
queue.
