---
title: "Connect Gmail (and More) to Codex CLI and Gemini CLI with Smithery (MCP)"
description: "Use Smithery to connect Gmail, Google Sheets, and Calendar to terminal AI assistants via MCP, with OAuth handled in the browser."
date: "2026-02-06"
categories: [ai]
---

Terminal AI assistants become much more useful once they can *act* on the systems you already use, not just talk about them.
Model Context Protocol (MCP) is a standard way to plug tools (Gmail, Google Sheets, Calendar, etc.) into an AI client. Smithery hosts MCP servers and provides the authentication UI, so you can connect services with an OAuth flow in your browser and then use them from a CLI ([Smithery docs](https://smithery.mintlify.dev/docs/getting_started/quickstart_connect)).

In this post I’ll show how to connect a Smithery-hosted Gmail tool to:

* **Codex CLI** (OpenAI)
* **Gemini CLI** (Google)

I’ll mention Sheets/Calendar too, but the examples focus on Gmail drafts, because that is the most immediately useful and the lowest-risk mode (draft first, review in the Gmail web UI, then send manually).

## What You Get (Why CLI Is Better Than A Web Chat)

Using Gmail from a terminal assistant is interesting because the CLI is also your *working directory*:

* The assistant can read and write **local files** (notes, CSVs, PDFs, plots) and then attach them to a draft email.
* The workflow is **reproducible**: prompts, scripts, and outputs can live in a folder (and in git).
* You avoid copy/paste between browser tabs: “generate report -> save file -> draft email with attachment” becomes one flow.

## Prerequisites

* A Smithery account.
* A Google account with Gmail (and optionally Sheets/Calendar).
* Codex CLI installed and logged in.
* Gemini CLI installed and logged in.

## Step 1: Pick A Smithery MCP Server

On Smithery, find the MCP server you want (for example a Gmail server, or a Google Workspace server that includes Gmail + Calendar + Sheets).

Every Smithery server has a URL in this format:

```text
https://server.smithery.ai/{serverName}
```

Copy that URL. You’ll use the exact same URL in both Codex CLI and Gemini CLI.

## Step 2A: Connect From Codex CLI (MCP)

Codex can connect to a remote MCP server URL and then run an OAuth login flow ([Codex MCP docs](https://developers.openai.com/codex/mcp/)).

1. Add the Smithery server:

```bash
codex mcp add gmail --url "https://server.smithery.ai/<serverName>"
```

2. Verify it is configured:

```bash
codex mcp list
```

3. Run the OAuth login (this opens a browser window):

```bash
codex --enable rmcp_client mcp login gmail
```

If you prefer not to pass `--enable rmcp_client` every time, you can enable it in your Codex config (see the [Codex CLI reference](https://github.com/openai/codex/blob/main/docs/codex-cli-reference.md)).

## Step 2B: Connect From Gemini CLI (MCP)

Gemini CLI reads MCP server configuration from:

* project: `.gemini/settings.json`
* global: `~/.gemini/settings.json`

Add an entry for the Smithery server (HTTP streaming transport) like:

```json
{
  "mcpServers": {
    "gmail": {
      "httpUrl": "https://server.smithery.ai/<serverName>"
    }
  }
}
```

Then start Gemini CLI:

```bash
gemini
```

When the server requires OAuth, Gemini CLI will open a browser window and store tokens locally (so you usually only need to authenticate once per server).
See the Gemini CLI documentation on [MCP servers](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html).

## Example: Draft A Gmail Message With A Local Attachment

This is the part that is hard to replicate in a web chat: your assistant can *use files from the folder you are already working in*.

Create a couple of local files:

```bash
mkdir -p out
cat > out/notes.md <<'EOF'
Hi all,

Here is a quick update:
- Item A is done
- Item B needs review

Andrea
EOF

printf "task,status\nItem A,done\nItem B,needs review\n" > out/status.csv
```

Now, in **Codex CLI** or **Gemini CLI**, ask something like:

> Create a *Gmail draft* to my group.
> Subject: "Weekly update"
> Use `out/notes.md` as the body.
> Attach `out/status.csv`.
> Do not send.

At the end you should have a **draft** in Gmail that you can review in the Gmail web UI.

## Adding Sheets And Calendar (Same Pattern)

Once Gmail works, Sheets and Calendar are the same idea:

* Add another Smithery server URL for Sheets and/or Calendar.
* Authenticate once in the browser.
* Ask the assistant to read a spreadsheet, compute something locally, then draft an email and optionally create a calendar event.

The important shift is that the CLI assistant can use your filesystem as the “source of truth” for intermediate artifacts (CSVs, PDFs, plots, Markdown notes), not just whatever happens to be in a chat transcript.
