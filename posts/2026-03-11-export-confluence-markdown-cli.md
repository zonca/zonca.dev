---
categories:
- documentation
date: '2026-03-11'
layout: post
title: Better way to export a Confluence page to Markdown
---

In a previous post, I wrote about [Export a Confluence page to Markdown](https://www.zonca.dev/posts/2024-08-04-export-confluence-markdown) by copying and pasting into Google Docs. I've since found a better and much more powerful way using the [confluence-cli](https://github.com/pchuri/confluence-cli) tool.

It is a command-line tool that interfaces directly with the Confluence API, allowing you to quickly export pages, including all of their formatting and attachments, directly to Markdown.

### Creating an API Token

To use the tool, you will need to create an API token for your Atlassian account.

1. Go to your [Atlassian Account Settings - API tokens](https://id.atlassian.com/manage-profile/security/api-tokens).
2. Click **Create API token**.
3. Give it a descriptive label like `confluence-cli` and copy the generated token.

Once you have your token, you can initialize the CLI (it supports interactive setup or setting environment variables, see their documentation for details).

### Exporting directly to Markdown

The CLI allows you to export a page and all its attachments straight into a local folder. Markdown is the default export format!

```bash
# Export page content and all attachments
confluence export 123456789 --dest ./exports
```

Replace `123456789` with the ID of your Confluence page. You can find the Page ID in the URL when editing the page, or by using `Page Information` from the Confluence menu.
