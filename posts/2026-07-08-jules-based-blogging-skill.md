---
title: "Creating Blog Posts with a Jules-Based Blogging Skill"
date: '2026-07-08'
categories: [tools, automation]
description: "A new minimal AI skill for my blog that lets Jules, an asynchronous coding agent, handle all the heavy lifting of post creation."
aliases:
  - /posts/2026-07-08-zonca-dev-jules-skill
---

I've recently added a new Jules-based blogging skill to my repository that significantly streamlines the process of writing new posts. The skill acts as a bridge between my AI assistant and Jules, an asynchronous coding agent from Google, automating the entire workflow from drafting to formatting.

## What the Skill Does

The skill is incredibly minimal. Its sole purpose is to capture the raw content, notes, links, and context I want to write about and send them to Jules. The skill itself contains only a few lines of instruction. All the complex rules regarding how the blog is structured—formatting, categories, YAML front matter—live entirely in `AGENTS.md`.

## Why Use Jules?

Jules is a powerful asynchronous coding agent. Instead of me manually writing the post, structuring the YAML front matter, deciding on existing categories, and uploading code snippets to GitHub Gists, I just dump all my raw thoughts into a single command:

```bash
jules new --repo zonca/zonca.dev "<paste all the useful content, notes, links, and context for the post here>"
```

Jules takes this chaotic input, reads `AGENTS.md` to understand my blog's strict conventions, and autonomously generates a complete, perfectly formatted post file.

## Why a Skill?

The skill acts purely as an entry point. When I tell my AI assistant (like opencode), "create a blog post about X", it loads this blogging skill. This skill simply instructs the assistant to pass the content along to Jules.

The beauty of this approach is the clean separation of concerns: the skill is just a pointer, while `AGENTS.md` holds the actual, detailed instruction set for the blog. This keeps the skill file tiny and allows the agent to focus on executing standard repository conventions.

## How to Generalize This to Other Blogs

This pattern is highly reusable and can be applied to any blog (Quarto, Hugo, Jekyll, or any static site generator). Here is the recipe:

1. Put a `SKILL.md` in your repository that instructs your AI assistant to send content to Jules.
2. Put your detailed blog post creation instructions in `AGENTS.md`. Include details on file naming, YAML front matter, categories, body style, and script handling.
3. The AI will read `AGENTS.md` automatically, as it is a standard convention.
4. Symlink the skill folder into `~/.agents/skills/` so your AI assistant can discover it.

By keeping the blog conventions in `AGENTS.md`, you centralize your workflow documentation while letting the AI handle the mechanical execution.

## The Skill File Format

The skill file itself uses YAML front matter to define its name and description. The description field is crucial because it helps the AI decide when to load this specific skill. After the front matter, a short markdown body provides the actual usage command.

## Examples

Here is the actual `SKILL.md` content:

````yaml
---
name: zonca.dev
description: Create a new blog post on zonca.dev using Jules.
---

# zonca.dev blog post skill

Send the entire content you want to post about into Jules, then let Jules handle it from there.

## Usage

```bash
jules new --repo zonca/zonca.dev "<paste all the useful content, notes, links, and context for the post here>"
```

Jules will read the project's `AGENTS.md` for instructions on how to format and create the post.
````

And here is a snippet from the `AGENTS.md` that Jules reads to format the post correctly:

````markdown
### YAML front matter (header)

Every post starts with a YAML front matter block. Required and common fields:

```yaml
---
title: "Your Post Title"
date: YYYY-MM-DD
categories: [category1, category2]
---
```

- **title**: Always use quotes. Keep it concise and descriptive.
- **date**: Must match the date in the filename.
- **categories**: Use **existing categories only** — do not invent new ones. Common categories: `python`, `kubernetes`, `jupyterhub`, `jetstream`, `linux`, `hpc`, `github`, `git`, `openscience`, `dask`, `singularity`, `nersc`, `sdsc`, `ai`, `llm`, `automation`, `tools`, `documentation`, `events`, `education`, `nbgrader`, `healpy`, `pysm`, `cosmology`, `cloudcomputing`, `openstack`, `jetstream2`, `italian`.
````

With this setup, creating a new blog post has shifted from a manual formatting chore to simply sharing my raw notes with an AI agent.
