---
title: "Update Confluence pages from Markdown with the confluence CLI"
description: How to use the confluence CLI to push markdown files to Confluence, and the workaround for URLs not being clickable.
date: 2026-04-21
categories:
  - tools
  - confluence
---

I needed to export a couple of pages from Confluence, edit them as Markdown, and push them back. The [confluence CLI](https://github.com/Atlassian/confluence-cli) makes this straightforward.

## Install

```bash
npm install -g @ Atlassian/confluence-cli
```

## Configure

```bash
confluence init
```

This starts an interactive setup that asks for your Atlassian domain, API token, and email.

To create an API token, go to https://id.atlassian.com/manage-profile/security/api-tokens.

## Update a page

```bash
confluence update <PAGE_ID> -f page.md --format markdown
```

You can find the `PAGE_ID` from the page URL:
`https://simonsobs.atlassian.net/wiki/spaces/DM/pages/544505898/Data+Licensing+Proposal` → page ID is `544505898`.

## The URL workaround

The Confluence CLI's Markdown converter does not support markdown link syntax like `[text](url)`. Instead, put the URL on its own line with no other text around it:

```markdown
# Title

https://github.com/simonsobs/repo/blob/main/file.md
```

On its own line, Confluence will auto-convert it to a clickable hyperlink. If you add text before or after the URL on the same line, it won't be converted.

Also note that `--format markdown` works best. Other formats like `--format storage` or `--format html` will break the Markdown formatting entirely.