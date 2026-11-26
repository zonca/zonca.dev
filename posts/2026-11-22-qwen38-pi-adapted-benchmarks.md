---
title: "A coding-agent adapter on a local 27B model: what it changes on Trello, email and a small script"
date: 2026-11-22
categories: [ai, llm, python]
layout: post
description: "Hugging Face's pi-adapted Qwen 3.8 27B claims fewer turns per task. On a Mac mini where prefill runs at 100 tok/s, turns are the cost, so I merged the adapter into the base weights, kept multi-token prediction working, and measured both models on five real tasks."
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
answers both, on five tasks from my own workload.

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
slower, and the first measurement said 27% from one kind of text, so I repeated it over four kinds
of content, ten runs per cell, models interleaved and unloaded before every run, 400 tokens each:

| content | base (min-max) | merged (min-max) | ratio median | ratio range | merged slower |
|---|---|---|---|---|---|
| prose | 27.4 tok/s (26.8-27.7) | 20.2 (20.1-20.2) | 0.739 | 0.728-0.754 | 100/100 |
| code | 31.0 (30.5-31.2) | 22.7 (21.6-22.8) | 0.732 | 0.694-0.747 | 100/100 |
| enumeration | 26.1 (25.9-26.4) | 19.3 (19.2-19.4) | 0.741 | 0.729-0.747 | 100/100 |
| creative | 23.6 (23.2-24.2) | 18.6 (18.4-18.7) | 0.788 | 0.758-0.803 | 100/100 |

Across all 400 base-against-merged pairings the median ratio is 0.740, the interquartile range 0.735
to 0.757, the extremes 0.694 and 0.803, and every single pairing is slower. The machine is steady
too: within a model, run-to-run spread is 1 to 2%. So the adapted model generates at about three
quarters of the base model's rate, and that is the one number in this post that two repetitions, ten
repetitions and four kinds of content all agree on.

The split is a different story. A decode rate is tokens accepted per forward pass multiplied by
forward passes per second, and the server logs both:

| content | tokens/pass ratio | ms/pass ratio | acceptance, base to merged |
|---|---|---|---|
| prose | 0.802 | 1.085 | 0.71 to 0.80 |
| code | 1.004 | 1.370 | 0.87 to 0.90 |
| enumeration | 0.769 | 1.038 | 0.66 to 0.73 |
| creative | 0.926 | 1.178 | 0.63 to 0.67 |

On code the merged model's draft depth is identical to the base model's (1.004 of its tokens per
pass) and every forward pass is 1.37 times slower on 19% more bytes. That is the weight and kernel
cost with the drafting effect removed, and it points at the 8-bit tensors not being free: `mxfp8` is
a different kernel path from the `nvfp4` matvec the engine runs for the rest of the model, and it
appears to cost more per byte than the format it replaces.

On the other three kinds of content the merged model drafts shallower (0.77 to 0.93 of the base
model's tokens per pass) and its passes are only 1.04 to 1.18 slower, because a pass that verifies
fewer draft tokens does less work. The product lands at 0.74 either way. Acceptance is higher on the
merged model everywhere, so the speculative decoder is not degraded; it drafts fewer tokens because
the MTP head was copied through the merge and never trained against the adapter, so it predicts the
base model's continuation and the engine's adaptive depth controller settles lower.

Where the extra bytes come from is unchanged, and the manifests pin it down exactly. `-q nvfp4` does
not mean four bits everywhere. Ollama's create-side policy keeps the quantization-sensitive
`v_proj`, `k_proj` and `down_proj` at 8 bits (`mxfp8`) in the first and last eighth of the layers
and in every third layer in between, and does the same for `lm_head`; everything else gets NVFP4:

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
the adapter with the harness. Five tasks from my own workload, ten runs per model, with the models
interleaved inside every repetition so that a change in machine state cannot favour one of them, and
a fresh directory per run:

- **Trello, two different cards:** read one real card (name, description, all comments), summarize
  it, name the one next action, and flag anything stale.
- **Email:** read one real six-message Gmail thread, summarize it, draft the next reply, and list
  the open questions the draft leaves unanswered.
- **Coding, two tasks:** write a module plus its tests from a specification, and separately fix a
  bug in a module so that its existing tests pass.

The Trello and email tasks run with only the `bash` and `read` tools, and the prompt says plainly
not to move, comment on or send anything, so the agent cannot change my board or my inbox while it
is being measured. The coding tasks are checked objectively after the agent exits: `pytest` in the
directory the agent worked in, plus a sha256 of the test file for the bug fix, so "make the tests
pass" cannot quietly become "edit the tests".

| task | base, median (range) | merged, median (range) | ratio | pairings merged wins |
|---|---|---|---|---|
| Trello, long card | 238 s (179-322) | 199 s (148-252) | 0.82 | 75/100 |
| Trello, short card | 190 s (121-288) | 139 s (123-211) | 0.78 | 77 of 100 |
| Email thread | 227 s (129-1001) | 204 s (127-1013) | 0.92 | 55 of 100 |
| Coding, write it | 78 s (61-102) | 115 s (80-162) | 1.33 | 15 of 100 |
| Coding, fix the bug | 56 s (46-68) | 56 s (54-71) | 1.04 | 44 of 100 |

Ten runs per cell means a hundred ways to pair a base run with a merged run, so each ratio is a
distribution rather than a point, and the last column is how often the merged model was faster.
Across all 500 pairings the median ratio is 0.96 with an interquartile range of 0.76 to 1.23, which
is a fair summary of "it depends on the task".

Totals over the fifty runs per model:

| | base | merged | ratio |
|---|---|---|---|
| wall clock | 9237 s | 8296 s | 0.90 |
| prompt tokens processed | 394901 | 396065 | 1.00 |
| generated tokens | 119980 | 76167 | 0.64 |
| turns | 269 | 263 | 0.98 |

**The generated tokens are where the effect is.** The merged model writes 0.64 of the base model's
tokens overall, and per task the medians are 0.62, 0.40, 0.66, 1.28 and 0.81: much less on the
reading tasks, more on the coding-from-specification task. Total prompt tokens are identical,
though, which surprised me: fewer and shorter answers do not shrink the conversation, because
reading a card or a thread costs what it costs regardless of how briefly the model replies.

**The wall clock gain is real but modest, and it depends on the task.** On the two Trello cards the
merged model is 18% and 22% faster and wins three quarters of the pairings, which is the clearest
result in the campaign. On the email thread the two medians are 227 s and 204 s with almost complete
overlap: a tie, not a win. On the coding task it is 33% slower and wins 15 pairings out of 100,
because it takes nearly twice the turns (median 5.5 against 3) and generates more tokens (1.28) for
the same result; both models pass the tests in every run. The bug fix is a tie.

**Turns fall only where the reading is long.** Median turns: 4 to 3 on the long card, 5 to 4 on the
short one, 8 to 8.5 on the email thread, 3 to 5.5 on the coding task, 4 to 4 on the bug fix. The
adapter card claims fewer than half the turns per solved task; here it is a small win on two tasks
and a clear loss on another.

## Three passes at the same measurement

This section exists because the number moved every time I measured it, and the movement is the most
useful thing I learned.

| pass | design | Trello, long card | Email | Coding |
|---|---|---|---|---|
| first | 3 tasks, 1 run each | 0.53 | 0.63 | 1.00 |
| second | 5 tasks, 2 runs each | 0.83 | 0.53 | 1.27 |
| third | 5 tasks, 10 runs each | 0.82 | 0.92 | 1.33 |

The coding result settled quickly and the Trello result settled at about 0.82. The email result went
from 0.63 to 0.53 to 0.92, which is not the adapter changing but the sample: email runs range from
129 s to 1001 s for the base model and 127 s to 1013 s for the merged one, because some runs wander
into an extra reading turn or a compaction. With one run per cell the ratio is whatever those two
draws happened to be. My first pass drew a 382 s base run against a 138 s merged run and concluded
"1.6 times faster"; ten runs say the medians are 227 s and 204 s.

So the honest headline is not the one the first pass gave: the adapter makes this model about 10%
faster overall on my agent workload, closer to 20% on Trello triage, a wash on email and bug fixing,
and noticeably slower on writing code from a specification. What it reliably does is write less,
which is worth real time only when the task is dominated by writing.

## Quality, checked where it can be checked objectively

Wall clock says nothing about whether the work was right, so every task carries a check where one
exists.

- **The coding tasks, all forty runs.** Two tasks, two models, ten runs each: every single run
  passes its own tests when re-run after the agent exits, and the bug-fix task also proves the
  test file was not touched, by sha256. The merged model's extra turns on the
  write-from-specification task bought nothing that a test can see.
- **The two Trello cards.** Across the runs I read, both models produced the same shape of answer:
  what the card is, what is done, what the next action is (rotate the exposed Hugging Face token,
  merge the blog post pull request), and that the card is overdue and still in the wrong list. The
  merged model got there in fewer turns and fewer tokens.
- **The email thread.** Same decisions, same open questions, in both models. One earlier run of
  the merged model reported the decode slowdown as 7% where the measurement says 26%, which is the
  kind of error no check catches and a reader does.

The coding checks are objective. The two reading tasks were read and judged, which is not a
measurement, so they are reported as an observation.

## Limitations, stated plainly

- **Ten runs per cell, and the tails matter.** The email task ranges from 129 s to 1001 s on the
  base model and 127 s to 1013 s on the merged one, because some runs wander into an extra reading
  turn. Its median ratio of 0.92 comes from distributions that almost completely overlap, so it is
  a tie and not a small win. The coding and Trello results are tighter and deserve more
  confidence.
- **The first campaign is not comparable with the others.** It ran before the benchmark comment
  was added to the long Trello card, so those numbers describe a different task. Campaigns two and
  three read the same card with the same comments.
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
`decode_decompose.py` for the per-token numbers, which splits the rate into tokens per pass and
passes per second and sweeps four kinds of content, and `bench_pi.py` with `bench_tasks.json` for
the agent numbers. Both interleave the two models and write their results after every run, so a
long campaign survives an interruption.

```bash
python bench_ollama.py --url http://127.0.0.1:11434 \
    --models qwen3.8:27b-nvfp4 qwen3.8-pi:27b-nvfp4 --reps 10 --sweep

python bench_pi.py --model-a macmini/qwen3.8:27b-nvfp4 \
                   --model-b macmini/qwen3.8-pi:27b-nvfp4 \
                   --tasks bench_tasks.json --repeat 10 --out results.json
```

## What I took from it

The adapter is a terseness adapter. It writes 64% of the base model's tokens and makes very nearly
the same number of turns (269 against 263 over fifty runs each). On a machine where decode is the
slow path, writing less is worth real time, but only in proportion to how much of the task is
writing, and that is a smaller fraction than I assumed.

The final numbers, from ten runs per cell: 10% less wall clock overall, 18% and 22% on the two
Trello cards, a tie on the email thread, 4% slower on the bug fix, and 33% slower on writing a
module from a specification. Decode is 26% slower per token, from the 8-bit tensors that the local
`nvfp4` conversion keeps and NVIDIA's prequantized release does not, and the artifact is 3.4 GB
larger.

So the arrangement on the Mac mini is both tags, with a narrower division of labour than I first
described: `qwen3.8-pi:27b-nvfp4` for reading and summarizing, where it is up to a fifth faster, and
`qwen3.8:27b-nvfp4` for code, where it is a third slower at the same quality, and for anything whose
output is long.

The lesson that outlives the model comparison is about the measurement. Three passes, with one, two
and ten runs per cell, gave 0.53, 0.83 and 0.82 on Trello and 0.63, 0.53 and 0.92 on email. The
tasks did not change; the sampling did. If I had stopped at the first pass I would have published
"1.6 to 1.9 times faster", which is wrong by a factor of two in the direction that flatters the
thing I built.

The measurement I would do next is not more repetitions of these tasks but a different question:
whether the shorter answers ever leave something out. Ten Trello cards through both models, read
side by side, counting what the short summaries miss. That is the failure mode this design cannot
detect, and it is the one that would matter if I started trusting the faster tag with the real
queue.
