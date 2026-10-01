# Agent notes

Review GEMINI.md before working—contains project-specific guidance and expectations.

## Pre-commit checklist

Before committing any blog post, **always** run these checks:

1. **Validate front matter**: Ensure `title`, `date`, `categories`, and `layout` are present and correct.
2. **Check all links**: Extract every URL from the post and verify each returns HTTP 200 (or 401 for API endpoints requiring auth). Fix any broken links before committing.
3. **Verify code blocks**: Ensure all fenced code blocks have a language tag and that commands are syntactically valid.
4. **Check for secrets**: Scan the post for API keys, tokens, or passwords. Never commit secrets to version control.

## Commit and push workflow

- **Commit and push** every change to `main` after completing the checks; pushing to `main`
  automatically builds, deploys and live-verifies the site (GitHub Actions). `main` is the
  production branch.
- **Commit message format**: Use a concise, descriptive message that explains what changed and why.
- **Never force-push** to `main`.
- For significant, experimental or multi-step work: push a topic branch and open a PR
  (PRs get a version preview + URL comment, and never touch production).

## Visual and navigation changes

- For any navigation, layout, or CSS change, inspect the rendered page at desktop and mobile widths
  before publishing, then inspect the live page again after publishing. Build success and HTTP checks
  do not replace visual verification. Use the PR preview URL for review.
- Navigation markup must be semantic and structurally match its CSS. Links intended as flex or grid
  items must be direct children of the navigation container, not hidden inside an automatically
  generated paragraph wrapper.
- Verify the global header, page-level navigation, overflow, wrapping, active states, and mobile menu
  behavior on every page type affected by the change.
- If the connected visual browser is unavailable, do not report visual verification as complete. Make
  the source-level fix, publish a preview, and ask Andrea to confirm the rendering before closing the
  visual issue.

## URL integrity

All existing URLs are frozen and verified in CI:

- Post URLs are `/posts/<source-basename>` (with and without `.html`). They are derived from
  the source basename, **never** from a legacy `slug:` field.
- Never rename, move or delete a post file. If a slug must change, add the old path as an
  `aliases:` entry in the new front matter — `public/_redirects` is generated from the
  baseline manifest (`tests/baseline/aliases.json`), and `scripts/baseline_manifest.py`
  regenerates it from source front matter.
- `draft: true` posts stay off production but appear in PR previews.
- Commit the regenerated `tests/baseline/` fixture when aliases/categories change.

## Site build (Astro + Cloudflare)

- The site is Astro static output served by Cloudflare Workers Static Assets
  (`wrangler.jsonc`, custom domain `www.zonca.dev`, apex 301 → `www`).
- Build pipeline (`npm run build`): `scripts/prepare_notebooks.py` (converts `.ipynb`
  without executing; front matter read from first raw/markdown cell) →
  `scripts/prepare_pages.py` (copies QMD posts, root pages, assets, generates
  `public/_redirects` and `llms.txt`/`.well-known`) → `astro build`.
- Validation: `python3 scripts/validate_urls.py` (dist) and `--live https://www.zonca.dev`
  (production; run by CI after every deploy: 411 canonical URLs + 247 aliases).
- Notebooks: never execute them during builds; stored outputs (text/markdown/HTML/PNG/SVG)
  render as static content. Fix broken notebook output by editing the stored output.
- The previous Quarto site is preserved in the `quarto-with-2026-10-01` release for rollback.

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
title: "Your concise post title"
date: YYYY-MM-DD
categories: [category1, category2]
layout: post
---
```

- **title**: Always use quotes. Use sentence case, never title case. Capitalize
  only the first word and proper nouns or acronyms such as ChromeOS and AI.
  Prefer literal, concrete wording that says what the post helps the reader do.
  Avoid vague metaphors such as "giving an agent my browser."
- **date**: Must match the date in the filename.
- **categories**: Use **existing categories only** — do not invent new ones. Common categories: `python`, `kubernetes`, `jupyterhub`, `jetstream`, `linux`, `hpc`, `github`, `git`, `openscience`, `dask`, `singularity`, `nersc`, `sdsc`, `ai`, `llm`, `automation`, `tools`, `documentation`, `events`, `education`, `nbgrader`, `healpy`, `pysm`, `cosmology`, `cloudcomputing`, `openstack`, `jetstream2`, `italian`.
- **description** (optional): One-sentence summary used for SEO, social previews and the post-list summary.
- **author** (optional): Defaults to "Andrea Zonca" via `posts/_metadata.yml`.
- **layout**: Set to `post` for blog posts.
- **slug** (optional): Only used by the legacy site; new sites derive URLs from the filename. Use `aliases` instead for old URLs.
- **aliases** (optional): Old URLs that should redirect to this post (used to generate `_redirects`).
- **draft**: `true` hides the post from production while keeping it in PR previews.

### Body content and style

- Write in Markdown. The site is built with **Astro** (`litera`-inspired clean theme).
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
- Math (`$...$`, `$$...$$`) is supported and rendered with KaTeX.

### Categories reference

Only use categories that already exist in the blog. To check existing categories, search the `categories:` field across files in `posts/`. Never create new categories unless explicitly instructed.

### Publishing workflow

1. Create the new post file in `posts/` and commit to `main` (or a PR branch).
2. Push to `main` → GitHub Actions builds, deploys to Cloudflare and live-verifies every URL.
3. Push a PR branch → CI builds and comments a version preview URL; `draft: true` posts are visible in the preview.

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

Note: If running with Jules, you do not need to do the Buffer social media posting step.
