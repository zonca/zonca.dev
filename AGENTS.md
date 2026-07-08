# Agent notes

- Review GEMINI.md before working—contains project-specific guidance and expectations.

## Creating a new blog post

Blog posts live in the `posts/` directory as Markdown files.

### File naming

```
posts/YYYY-MM-DD-slug.md
```

The slug should be lowercase, hyphenated, and descriptive (e.g., `2026-04-22-deploy-jupyterhub-openstack-magnum-tofu.md`).

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
- **description** (optional): A one-sentence summary used for SEO and social previews.
- **author** (optional): Defaults to "Andrea Zonca" via `posts/_metadata.yml`.
- **layout**: Set to `post` for blog posts (some older posts omit this).
- **slug** (optional): Override the URL slug if it differs from the filename.
- **aliases** (optional): Old URLs that should redirect to this post.

### Body content and style

- Write in Markdown. The site is built with **Quarto** using the `litera` theme.
- Use `##` for section headings (the title is rendered separately from the banner block).
- Keep an introductory paragraph right after the front matter that summarizes what the post is about.
- Use bullet points and numbered lists for step-by-step instructions.
- Link to relevant resources (GitHub repos, documentation, gists) inline.
- For images, use paths relative to the post's directory (e.g., `img/screenshot.png`). Avoid absolute paths like `/img/...`.
- Use `---` horizontal rules to separate major sections.

### Scripts and code

- **Multi-line scripts**: Upload to a [GitHub Gist](https://gist.github.com/) and embed it in the post:
  ```html
  <script src="https://gist.github.com/zonca/GIST_ID.js"></script>
  ```
  Also provide a plain-text link to the gist for accessibility.
- **One-liners**: Can stay inline in the post body, for example:
  ```bash
  curl -o ~/.up.sh https://raw.githubusercontent.com/zonca/up/main/up.sh
  ```
- **Code blocks**: Use fenced code blocks with language tags (```` ```bash ````, ```` ```python ````).

### Categories reference

Only use categories that already exist in the blog. To check existing categories, search the `categories:` field across files in `posts/`. Never create new categories unless explicitly instructed.

### Publishing workflow

1. Create the new post file in `posts/`.
2. Commit and push to the `main` branch (or open a PR for significant posts).
3. GitHub Actions renders the Quarto project and publishes to GitHub Pages automatically.
4. The Netlify build also triggers on pushes to `main`.

## Buffer Social Media

### Setup
- Buffer skill located at: `/home/zonca/.agents/skills/buffer/SKILL.md`
- Uses GraphQL API at `https://api.buffer.com`
- Environment variable `BUFFER_KEY` must be set

### Channel IDs (organization: 655270181efd918df3d33eff)
| Platform | Channel ID |
|----------|------------|
| Twitter/X | `6552702d7a6cf4d23f916d5c` |
| LinkedIn | `67c6746b3b85969eafee1ee4` |
| Bluesky | `67c6738e3b85969eafe22a07` |

### Quick post creation
```bash
buffer_query() {
  curl -s -X POST "https://api.buffer.com" \
    -H "Authorization: Bearer $BUFFER_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$1\"}"
}

buffer_query "mutation { createPost(input: { text: \"POST TEXT\", channelId: \"CHANNEL_ID\", schedulingType: automatic, mode: addToQueue }) { ... on PostActionSuccess { post { id text dueAt } } ... on MutationError { message } } }"
```

### Workflow for new blog posts
1. Read the post content
2. Draft 1 announcement post adapted for each platform (Twitter: short + hashtags, LinkedIn: professional with bullet points, Mastodon/Bluesky: similar to Twitter)
3. Show drafts to user for approval
4. Once approved, queue to all 3 channels using Buffer API
