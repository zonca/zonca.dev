---
title: "Fixing Clipboard Issues with Opencode in Byobu/Tmux over SSH on Chromebook"
date: "2026-04-13"
categories:
  - linux
---

## The Problem

When using a Chromebook (Crostini) and connecting via SSH to a remote server, you might encounter a frustrating clipboard issue. Copy-paste works perfectly when running `opencode` alone, and it works fine when using `byobu` alone. However, when you run `opencode` *inside* a `byobu` session, copy-paste operations suddenly stop working.

## Technical Environment Details

* **Client:** Chromebook running Linux via Crostini
* **Connection:** SSH to a remote server
* **Tools:** `byobu` (using `tmux` backend), `opencode`
* **Clipboard utility:** `wl-copy` is available but fails because there is no `WAYLAND_DISPLAY` available on the remote server.

## Root Cause Analysis

The root cause of this issue lies in how `tmux` (which powers `byobu`) handles clipboard operations. When running over SSH, there is no Wayland or X11 display available on the remote server. While `opencode` might successfully attempt to use OSC-52 escape sequences to copy to the local clipboard, `tmux` acts as a middleman and actively blocks these clipboard escape sequences by default, preventing them from reaching your local terminal emulator.

## What Didn't Work

Before finding the correct solution, I tried a few approaches that failed:

1. **X11 Forwarding (`ssh -X` or `ssh -Y`):** I tried enabling X11 forwarding to pass the clipboard through. This failed because Crostini uses Wayland natively, and relying on XWayland for clipboard synchronization over SSH introduces latency and doesn't play well with `tmux`.
2. **Modifying `config.json` Clipboard Settings:** I looked into `opencode`'s configuration files to force different clipboard backends, but this did not bypass the `tmux` barrier.

## The Final Working Solution

The fix requires configuring `tmux` to allow clipboard sequences to pass through. Add the following lines to your `~/.tmux.conf` file on the remote server:

```tmux
set -g set-clipboard on
set-option -g allow-passthrough on
```

After saving the file, reload your `tmux` configuration by running:

```bash
tmux source-file ~/.tmux.conf
```

## Why This Works: Understanding OSC-52

The magic behind this solution is **OSC-52** (Operating System Command 52). It is an ANSI escape sequence that allows a remote application to send text directly to the local terminal emulator's clipboard, bypassing the need for X11 forwarding or complex SSH tunnels.

When you copy text in `opencode`, it can output an OSC-52 escape sequence.
* `set -g set-clipboard on` tells `tmux` to use the clipboard.
* `set-option -g allow-passthrough on` is the crucial part: it enables `tmux` to pass the OSC-52 escape sequences directly through to your local terminal (in this case, your Chromebook's terminal emulator). Once the sequence reaches your terminal emulator, it handles injecting the copied text into your Chromebook's local clipboard.

## Troubleshooting

If you are still experiencing issues after applying the solution above, check the following:

1. **Check Terminal Emulator Support:** Ensure your local terminal emulator supports OSC-52. The default Crostini terminal does, but if you are using an alternative terminal app, verify its OSC-52 capabilities and ensure they are enabled in its settings.
2. **Verify Byobu Backend:** Make sure `byobu` is actually using `tmux` as its backend (this is the default in modern versions). You can check by running `byobu-info`.
3. **Nested Sessions:** If you have nested `tmux` or `byobu` sessions, you need to ensure the passthrough settings are applied to all layers, though it's generally best to avoid nesting.
