---
title: "Living with a local 27B LLM on a Mac mini: capable enough and (almost) fast enough"
date: "2026-10-13"
categories: [ai]
layout: post
---

I run an Apple M4 Pro Mac mini in the office as a private LLM server: a 27B
Qwen 3.8 model, served over my Tailscale tailnet, used every day by my coding
agent to handle emails, Trello cards, and general project work. This post is
the high-level story: what it is good at, what the speed actually feels like,
and where I would want more. The technical setup is in the
[setup post](./2026-10-13-macmini-local-llm-setup.md), and a fun comparison
against data-center hardware is in the
[comparison post](./2026-10-13-macmini-vs-nrp-datacenter.md).

What am I actually running? On the Mac mini, Ollama (a local model server)
runs Qwen 3.8 27B, an open-weights model, entirely in the machine's unified
memory. On my laptop I run **pi**, a small command-line agent: it gives the
model tools to read and edit files, run shell commands, and call services, and
it keeps the whole exchange in one session. When it processes an email or a
Trello card, the model reads the item, decides what to do, and uses those
tools to draft or act, with me approving anything that matters.

## By the numbers

| Metric | Value |
|---|---|
| First answer, cold session (model unloaded) | ~30 s |
| First answer, warm session (model resident, prompt cached) | ~2 s |
| Generation, small context | 26-33 tok/s |
| Prompt processing (prefill) | ~100 tok/s |
| Context window (practical) | 200 K |

Two of these numbers deserve an explanation. The ~30 s cold start is mostly
not the model loading (that part is ~4 s): it is the agent's own preamble.
Before the model can answer anything, the agent sends a system prompt with
instructions and tool definitions, about 3,000 tokens, and at ~100 tok/s of
prompt processing that alone costs most of the half minute. The warm ~2 s is
what you get once the model is resident and that preamble is cached: the
server keeps the processed prompt around, so each follow-up only pays for the
new tokens.

## Verdict: capable enough and (almost) fast enough

Short version: the title is the honest summary. Tool use is great: the agent
reads files, edits them, runs commands, and calls external tools and services
reliably, and the model handles the multi-step back-and-forth that interactive
work needs. Where it really shines is **project management work**: processing
Trello cards, reading and writing emails, updating notes and documentation,
one item at a time. That is what I use it for most, and it gets the job done
comfortably.

I also tried it on more complicated coding tasks, and I was quite surprised at
how good it was. That said, I also have access to much more powerful models
(GLM 5.3 and similar), so I have not tested the Mac mini as a coder
extensively, and I cannot give a genuinely solid opinion on that use case yet.

## On speed

For interactive work, about 30 tokens per second at small context is plenty:
that is faster than I read, so responses stream smoothly and the wait is
barely noticeable. The one speed bump I notice every session is the **startup
time**: about 30 seconds for a cold first answer (loading the model plus the
agent's preamble). It is a bit annoying, but honestly acceptable: 30 seconds
is fine when you are starting a real task.

To be clear, even 10 seconds of startup would already be fine. The ideal would
be an even smaller agent harness that gets to the first answer in about 5
seconds: I think that would be enough to feel instant, and it is what I am
looking for next. In practice the startup pain mostly disappears
once you are in a batch: the server keeps the model and the cached preamble
warm for hours, so when I process several emails or several Trello cards one
after the other, I pay the startup once and every following item starts
almost immediately.

So: capable enough, almost fast enough, and the tool use is great. Details on
how it is set up are in the
[next post](./2026-10-13-macmini-local-llm-setup.md).
