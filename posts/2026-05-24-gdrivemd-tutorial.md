---
title: "Synchronizing Google Docs and GitHub with gdrivemd"
date: 2026-05-24
categories: [tools, automation, github]
---

# Synchronizing Google Docs and GitHub with `gdrivemd`

Managing documentation often requires choosing between the collaborative ease of Google Docs and the version-controlled structure of GitHub. The **`gdrivemd`** scripts (usable as a skill for Gemini CLI or any other terminal-based AI agent) bridge this gap, providing a seamless two-way synchronization between a Google Doc and a local Markdown file.

## How it works

The skill leverages the Google Workspace CLI (`gog`) to convert and transfer documents:

1. **Pulling Changes:** When collaborators edit the Google Doc, you can pull the latest version directly into your local repository. The script utilizes `gog docs export --format md` to fetch the document. Images are intelligently handled and embedded natively as base64 data URIs.
2. **Pushing Changes:** When you make local edits to your Markdown file, you can push them back to Google Docs using `gog docs write --markdown`. You can choose to completely replace the document or append your changes.

## Usage

The `gdrivemd` repository provides two main scripts:

* `pull_from_gdoc.sh <doc_id> <output_file.md>`
* `push_to_gdoc.sh <input_file.md> <doc_id> [replace|append]`

This workflow allows developers to edit in their IDE, non-technical collaborators to edit in Google Docs, and both sides to stay perfectly synchronized through Git Pull Requests.

## Why is this useful? A Scenario

Imagine you are a software developer working on a project. You manage your project's documentation in Markdown files on GitHub so you can track changes and manage pull requests. However, you also have a project manager, a marketing lead, or external contributors who are not familiar with Git or Markdown. They prefer reviewing and suggesting edits using Google Docs, where they can use familiar commenting and suggesting tools.

Without `gdrivemd`, you would have to manually copy and paste text between Google Docs and GitHub, carefully formatting it each time and manually extracting and re-uploading images. 

With an AI agent equipped with the `gdrivemd` skill, this process becomes completely hands-off. 

### Example Interaction with an AI Agent

**You:** "The marketing team just finished reviewing our 'Getting Started' guide on Google Docs. Can you pull their changes and create a PR for me to review?"

**Agent:** "I'll take care of that right away."

*(The agent autonomously runs the `pull_from_gdoc.sh` script, which exports the Google Doc to Markdown, embedding any new images added by the marketing team. It then stages the changes, creates a new branch, commits the update, and opens a Pull Request on GitHub.)*

**Agent:** "I've pulled the latest updates from the Google Doc into a new branch and opened a Pull Request for you: `#42: Update Getting Started guide from Marketing`. Let me know if you want me to merge it!"

This allows everyone to work in the environment they are most comfortable in, while the AI agent seamlessly bridges the gap.

---

You can find the scripts and instructions in the [gdrivemd repository](https://github.com/zonca/gdrivemd), and see it in action in the [demo repository](https://github.com/zonca/gdrivemd-demo).
