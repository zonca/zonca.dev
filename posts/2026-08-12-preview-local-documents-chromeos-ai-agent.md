---
title: "Preview local documents from a Linux AI agent in ChromeOS Chrome"
date: 2026-08-12
categories: [ai, automation, linux, tools]
layout: post
description: "A small agent skill bridges Crostini and ChromeOS so coding agents can open generated PDFs, images, and HTML in the Chromebook's normal Chrome browser."
---

AI coding agents work very well inside a Chromebook's Crostini Linux container, but showing a
generated PDF, image, or HTML page in the normal ChromeOS browser is surprisingly awkward. I
created [AI Document Preview for ChromeOS](https://github.com/zonca/ai-document-preview-chromeos-skill)
to make that handoff a one-command operation that any terminal-based agent can use.

## The ChromeOS and Linux boundary

When Linux is enabled on a Chromebook, the coding environment and the main browser do not run in
the same filesystem namespace.

The AI agent sees a path like:

```text
/home/user/project/output/report.pdf
```

ChromeOS Chrome does not see that as a normal local path. Passing
`file:///home/user/project/output/report.pdf` to the host browser is not the same as opening a file
that lives in ChromeOS Downloads.

The usual alternatives are all imperfect:

- `xdg-open` can launch a Linux application instead of the ChromeOS browser.
- Installing Chrome or another browser inside Linux creates a second browser profile without the
  user's normal ChromeOS tabs, extensions, and settings.
- Copying every generated artifact into Downloads is repetitive and leaves extra files behind.
- Copying an HTML file alone can break its relative CSS, JavaScript, fonts, and images.
- A browser-automation bridge is unnecessary when the agent only needs to display a file.

This is not really a document-rendering problem. Chrome already renders PDFs, images, SVG, and
HTML well. It is a boundary-crossing problem between Crostini and ChromeOS.

## A small HTTP bridge

The skill solves the problem with components already present on a normal Chromebook Linux setup:

1. Start Python's static HTTP server in the file's containing directory.
2. Expose it on an available local port.
3. Verify that the requested file returns successfully.
4. Build a URL using `penguin.linux.test`, the ChromeOS hostname for the Crostini container.
5. Give that URL to `garcon-url-handler`, which opens it through ChromeOS's URL handling.

The path becomes a browser URL:

```text
/home/user/project/output/report.pdf
                  |
                  | Python HTTP server inside Crostini
                  v
http://penguin.linux.test:43913/report.pdf
                  |
                  | garcon-url-handler
                  v
          ChromeOS Chrome tab
```

The agent does not need a Linux GUI browser, a Chrome extension, or access to the user's browsing
session. It only asks ChromeOS to open a local HTTP URL.

## Install the skill globally

Clone the public repository into the directory shared by compatible agent runtimes:

```bash
git clone https://github.com/zonca/ai-document-preview-chromeos-skill.git ~/.agents/skills/ai-document-preview-chromeos-skill
```

Start a new agent session if your runtime discovers skills only at startup.

The skill is designed for prompts such as:

```text
Open this PDF in my ChromeOS browser.
```

```text
Preview the generated HTML in Chromebook Chrome, not in Linux.
```

```text
Show me the two PNG files you just generated in ChromeOS.
```

It can also be invoked explicitly:

```text
Use $ai-document-preview-chromeos-skill to open build/report.pdf.
```

The agent reads `SKILL.md`, resolves the absolute path, and runs the bundled helper. The user does
not need to translate a Linux path into a browser URL or manage the server manually.

## Use it directly from the terminal

The same helper works without an agent. Define its path once:

```bash
PREVIEW_SCRIPT="$HOME/.agents/skills/ai-document-preview-chromeos-skill/scripts/preview.py"
```

Open a PDF:

```bash
python3 "$PREVIEW_SCRIPT" open /home/user/project/output/report.pdf
```

Open an image:

```bash
python3 "$PREVIEW_SCRIPT" open /home/user/project/output/figure.png
```

Open an HTML page:

```bash
python3 "$PREVIEW_SCRIPT" open /home/user/project/site/index.html
```

Filenames containing spaces and other URL-sensitive characters are encoded automatically.

## Open several generated files

Call `open` once for each file:

```bash
python3 "$PREVIEW_SCRIPT" open /home/user/project/output/contract.pdf
python3 "$PREVIEW_SCRIPT" open /home/user/project/output/notice.pdf
```

If the files are in the same directory, the helper reuses the running server and opens each one
in ChromeOS. If the next file is elsewhere, it replaces the previous server with one rooted at
the new directory.

The supported formats are PDF, PNG, JPEG, GIF, WebP, SVG, BMP, AVIF, HTML, and HTM. The helper
does not convert them; it lets Chrome use its native renderers.

## Keep HTML assets working

The server uses the requested file's parent directory as its root. Suppose an agent generates:

```text
site/
├── index.html
├── styles.css
├── app.js
└── images/
    └── diagram.svg
```

Opening `site/index.html` also makes `styles.css`, `app.js`, and `images/diagram.svg` available at
relative URLs. This is the main advantage over copying only `index.html` to another folder.

The helper is for static output. A React, Vite, or other development application should use its
own development server; the agent can then open that server's URL with `garcon-url-handler`.

## Check and stop the server

The server remains running after a document opens so the user can refresh the tab and the agent
can preview more files from the same directory.

Check its status:

```bash
python3 "$PREVIEW_SCRIPT" status
```

Stop it when review is complete:

```bash
python3 "$PREVIEW_SCRIPT" stop
```

The helper tracks one server per Linux user in
`~/.local/state/ai-document-preview-chromeos-skill`. This prevents agents from accumulating many
abandoned preview servers across separate terminal calls.

## Security considerations

The bridge is local and does not upload the document to a third-party service, but it is still an
HTTP server.

- The server exposes the file's containing directory, not only the selected file. That scope is
  required for HTML-relative assets.
- It binds so ChromeOS can reach Crostini. Network configuration determines whether the port is
  reachable beyond the Chromebook host.
- It uses an ephemeral port rather than a fixed one.
- It has no authentication or TLS and is not intended as a permanent server.
- Sensitive previews should be stopped immediately after review.

The skill validates the extension, confirms the file exists, checks that
`garcon-url-handler` is available, waits for the HTTP server, and verifies the specific file before
opening ChromeOS.

## Preview versus browser control

I also maintain a separate workflow for [controlling an existing ChromeOS browser with an AI
coding agent](https://www.zonca.dev/posts/2026-07-28-control-existing-chromeos-browser-ai-agent.html).
That tool attaches through the Playwright extension and is appropriate when an agent must inspect
pages, click controls, continue after login, or use an authenticated browser session.

Document preview has a deliberately smaller scope:

| Task | Document preview | Browser control |
|---|---:|---:|
| Open a generated PDF, image, or HTML file | Yes | Possible but unnecessary |
| Preserve the user's ChromeOS browser choice | Yes | Yes |
| Read or click the resulting page | No | Yes |
| Use existing cookies and authenticated sessions | No | Yes |
| Require a Chrome extension handoff | No | Yes |
| Run a local static HTTP server | Yes | No |

For a generated contract, chart, screenshot, report, or static web mockup, document preview is the
simpler and safer abstraction. Use browser control only when the task truly needs interaction.

## Why package this as an agent skill

The underlying commands are short, but the reliable workflow has several details that an agent
would otherwise rediscover each time:

- choose ChromeOS Chrome rather than a Linux opener;
- avoid unusable `file://` paths;
- select and remember a free port;
- preserve HTML-relative assets;
- verify the server before reporting success;
- reuse one server for neighboring files;
- replace it when the root changes; and
- know when to stop it.

Packaging those decisions as a skill makes natural-language requests consistent across coding
agents. The deterministic Python helper handles process state; `SKILL.md` tells the agent when and
how to invoke it.

The source, installation instructions, supported formats, lifecycle commands, and troubleshooting
guide are available in the public
[zonca/ai-document-preview-chromeos-skill repository](https://github.com/zonca/ai-document-preview-chromeos-skill).
