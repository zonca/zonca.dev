---
title: "Copy a Single Codex Session to Another Machine"
date: "2025-12-16"
categories: [ai]
---

You might want to copy a Codex session to another machine to continue a conversation started on one device, such as moving from a laptop to a desktop or server.

Each Codex chat is stored as a single `.jsonl` file under `~/.codex/sessions/`.

## 1. Locate the session file

Sessions are organized by date:

```
~/.codex/sessions/YYYY/MM/DD/
```

Example:

```
rollout-2025-12-16T08-52-19-019b2813-b881-7813-afe8-bf072950e53b.jsonl
```

The long ID at the end uniquely identifies the chat.

## 2. Copy the session to the other machine

First, create the directory structure on the remote machine:

```bash
ssh sshhost "mkdir -p ~/.codex/sessions/2025/12/16"
```

Then copy the session file using `scp`:

```bash
scp ~/.codex/sessions/2025/12/16/rollout-2025-12-16T08-52-19-019b2813-b881-7813-afe8-bf072950e53b.jsonl \
    sshhost:~/.codex/sessions/2025/12/16/
```

## 3. Resume the Codex chat after transfer

Once Codex is running on the destination machine:

1. Open Codex CLI.
2. Run:

   ```
   /resume
   ```
3. Select the transferred session from the list.
4. Continue the conversation from the last message.

Codex restores the full conversation state directly from the `.jsonl` session file.

## Notes

* Do **not** copy `history.jsonl` or other files.
* Keep the original filename and directory structure.
* One `.jsonl` file always corresponds to one chat.
