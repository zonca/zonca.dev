---
title: "up: One Command to Update All My AI Tools"
date: "2026-05-17"
categories: [linux, ai, tools]
---

I use a lot of AI coding assistants — Claude Code, Gemini CLI, Codex, Cline, Qwen Code, Crush, and more. Keeping them all updated was a chore: `apt upgrade` for the system, `npm install -g` for Node packages, `claude upgrade` for Claude, downloading releases for gog... I kept forgetting one or another.

So I wrote a shell function called `up` that handles everything in one shot and shows me a before/after version report so I can see exactly what changed.

## What it does

- Runs `apt upgrade` for system packages
- Updates all npm-installed AI tools (only the ones actually installed)
- Updates gog from GitHub releases
- Runs `claude upgrade` and `copilot extension upgrade`
- Prints a clean version comparison table at the end

## Self-updating

The script now lives in a [GitHub repo](https://github.com/zonca/up) and checks for updates on every run. If there's a newer version, it patches itself automatically — no manual intervention needed.

## Install

```bash
curl -o ~/.up.sh https://raw.githubusercontent.com/zonca/up/main/up.sh
echo 'source ~/.up.sh' >> ~/.bashrc
source ~/.bashrc
```

Then just run `up`.

## Scheduled runs

I have it running automatically every morning at 7am via cron, so my environment is always up to date when I start the day:

```bash
echo '0 7 * * * /bin/bash -c "source ~/.up.sh && up" >> ~/.up.log 2>&1' | crontab -
```

The repo is at [github.com/zonca/up](https://github.com/zonca/up) — PRs welcome if you want to add support for more tools.
