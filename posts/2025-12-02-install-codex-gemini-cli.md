---
title: "How to install codex and gemini cli"
author: "Andrea Zonca"
date: "2025-12-02"
categories: [ai]
---

When installing `@google/gemini-cli` or `@openai/codex` using `npm`, you might encounter permission errors with the default global installation command.

The simplest way to avoid this is to install the packages in your local user directory by providing `~/.local` as a prefix.

```bash
npm install --global --prefix ~/.local @google/gemini-cli
npm install --global --prefix ~/.local @openai/codex
```

Executable files will be placed in `~/.local/bin`. This directory is typically already in your `PATH`.

If it's not, you can add it to your `PATH` by adding the following line to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`):

```bash
export PATH=$HOME/.local/bin:$PATH
```

Then, reload your shell configuration (e.g., `source ~/.bashrc`) or open a new terminal.
