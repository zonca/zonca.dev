---
title: "Video: best practices for AI-assisted coding with GitHub, tests and CI"
date: 2026-11-11
categories: [ai, llm, github, tools]
layout: post
description: "A 52 minute video with five demos of coding with an AI agent under version control, tests and continuous integration, using OpenCode and free NRP models."
---

This video covers the same material as my seminar "Best Practices for AI-Assisted Coding: GitHub, Testing, and
Continuous Integration" (November 6, 2026), recorded from scratch for YouTube. It shows, on a small real
project, how to work with an AI coding agent without losing control of your code: an `AGENTS.md` file and
permissions, precise prompts and plan mode, tests, continuous integration, and subagents with separate roles.
The demos use [OpenCode](https://opencode.ai) with the free models of the
[National Research Platform](https://nrp.ai) (NRP), but the practices apply to any agent: Claude Code, Codex,
Copilot CLI.

<iframe width="560" height="315" src="https://www.youtube.com/embed/xEojDVgHsHw" title="Best Practices for AI-Assisted Coding: GitHub, Testing, and Continuous Integration" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Watch it on YouTube: [youtu.be/xEojDVgHsHw](https://youtu.be/xEojDVgHsHw). Long agent waits are cut, and a card
shows how much real time passed.

## Set up the agent first

To follow along on your own machine, start from the companion post
[Set up an AI coding agent with free NRP models](./2026-11-06-set-up-ai-coding-agent-free-nrp-models.md):
NRP API key, OpenCode installation and configuration, permission rules and which model to pick.

## The demo repository

Every demo runs on the same small Python package, which reads weather station data and computes daily
statistics: [github.com/zonca/weather-agent-demo](https://github.com/zonca/weather-agent-demo).
Each demo starts from a tag and ends at the next one, so you can check out any step and try it yourself:

```bash
git clone https://github.com/zonca/weather-agent-demo
cd weather-agent-demo
git checkout checkpoint-2   # the state at the start of demo 3
```

| Demo | Starts from | Ends at |
|---|---|---|
| 1. The agent learns the project | `checkpoint-0` | `checkpoint-1` |
| 2. Asking and steering | `checkpoint-1` | `checkpoint-2` |
| 3. Tests catch what you would miss | `checkpoint-2` | `checkpoint-3` |
| 4. Continuous integration | `checkpoint-3` | `checkpoint-4` |
| 5. Subagents keep the tutorial working | `checkpoint-4` | `checkpoint-5` |

## What is in the video

* [0:00](https://youtu.be/xEojDVgHsHw?t=0) Introduction: why version control, tests and CI matter more, not
  less, when an agent writes the code
* [3:29](https://youtu.be/xEojDVgHsHw?t=209) Keeping secrets away from the agent: what permissions can and cannot
  block
* [4:52](https://youtu.be/xEojDVgHsHw?t=292) Which NRP model to use
* [6:43](https://youtu.be/xEojDVgHsHw?t=403) Demo 1, the agent learns the project: `/init`, `AGENTS.md`, permission
  rules
* [13:48](https://youtu.be/xEojDVgHsHw?t=828) Demo 2, asking and steering: a vague prompt against a precise one,
  plan mode, reading the diff, and data from Google Drive with `gog`
* [21:58](https://youtu.be/xEojDVgHsHw?t=1318) Demo 3, tests catch what you would miss: a failing test first, then
  the fix, in a pull request that closes the issue
* [29:54](https://youtu.be/xEojDVgHsHw?t=1794) Demo 4, continuous integration: GitHub Actions, the agent reads the
  CI logs with `gh` and fixes the failure, `main` protected
* [37:07](https://youtu.be/xEojDVgHsHw?t=2227) Demo 5, subagents keep the tutorial working: a tester and a fixer
  agent check the README in a loop
* [48:18](https://youtu.be/xEojDVgHsHw?t=2898) Recap and takeaways

The eight takeaways, as a checklist for any agent, are at the end of the
[setup post](./2026-11-06-set-up-ai-coding-agent-free-nrp-models.md#checklist).

## Questions and collaborations

Questions and feedback on the demos are welcome as issues in the
[demo repository](https://github.com/zonca/weather-agent-demo/issues).
I lead the Scientific Computing Applications group at the San Diego Supercomputer Center: we help research groups
build software for AI systems and high performance computing, and collaborate on proposals: see my
[SDSC page](https://www.sdsc.edu/research/researcher_spotlight/zonca_andrea.html) to get in touch.
