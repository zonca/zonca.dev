---
title: "Convenience Script for System & CLI Updates"
date: "2026-01-10"
categories: [linux, ai]
---

I use a simple bash alias to keep my environment in sync with one command. It handles standard system updates and refreshes my core AI tools—the **Gemini** and **Codex** CLIs.

To keep the process smooth, the script includes a quick cleanup of temporary directories, which helps avoid those common `ENOTEMPTY` rename errors that can occasionally stall `npm` global updates.

### The Alias

Add this to your `.bashrc` or `.zshrc`:

```bash
alias up="sudo apt update && sudo apt upgrade -y && rm -rf \$(npm config get prefix)/lib/node_modules/@google/.gemini-cli-* \$(npm config get prefix)/lib/node_modules/.codex-cli-* && npm install -g @google/gemini-cli codex-cli"
```

---

### How it works:

* **System:** Runs `apt update` and `upgrade`.
* **Cleanup:** Dynamically finds your npm path and clears stale temporary folders.
* **Tools:** Reinstalls the latest versions of `@google/gemini-cli` and `codex-cli`.

You can find the full version and implementation notes here:

👉 **[Convenience Update Alias on GitHub Gist](https://gist.github.com/zonca/d840426702ff406b9547fb17d0465ffd)**
