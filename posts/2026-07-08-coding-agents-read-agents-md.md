---
title: "Ensuring CLI coding agents read AGENTS.md"
date: 2026-07-08
categories: [ai, tools]
layout: post
---

When working with CLI coding agents such as Codex, Claude, Antigravity, Qwen, and OpenCode,
the agent may not automatically process the `AGENTS.md` file in the repository.

To ensure the agent reads the necessary context and instructions, the most reliable method is to
explicitly reference the file in the first request. Adding `@AGENTS.md` to the initial prompt
guarantees that the agent processes the file before executing any tasks. This method works
consistently across different CLI agents.
