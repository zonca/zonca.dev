# zonca.dev

Andrea Zonca's blog: notes on high-performance computing, Python, JupyterHub, Kubernetes
and AI for science. Markdown in `posts/` is rendered by an **Astro** static site and
deployed to **Cloudflare Workers Static Assets**.

## Stack

- **Astro** (static output, `build.format: file`) — minimal, mobile-first, zero client JS
  except the search page.
- **Content** — `posts/*.md` and `posts/*.qmd` are the source; notebooks (`posts/*.ipynb`)
  are converted at build time by `scripts/prepare_notebooks.py` **without executing them**
  (stored outputs are rendered).
- **Hosting** — static assets Worker deployed via `wrangler` (`wrangler.jsonc`), custom
  domain `www.zonca.dev` with automatic HTTPS; `zonca.dev` stays a 301 to `www`.

## Local development

```bash
npm install
npm run dev          # prepares notebooks/pages then starts the Astro dev server
```

Build and validate:

```bash
npm run build        # prepare_notebooks -> prepare_pages -> astro build
python scripts/validate_urls.py   # checks dist against the baseline manifest
npx astro check      # type check
```

## Authoring a blog post

1. Add `posts/YYYY-MM-DD-slug.md` with YAML front matter (`title` in quotes, `date`
   matching the filename, `layout: post`, existing `categories` only).
2. Optional `description` is used as the list summary; otherwise a short summary is
   generated from the first paragraph.
3. `draft: true` keeps a post off production (still visible in PR previews).
4. Execute: `npm run build` and check `dist` contains the new page.

Notebook posts get their front matter from the first raw/markdown cell of the `.ipynb`.

## Deploying (GitHub Actions)

Push to `main` (or merge a PR) → CI builds, runs `astro check` and the URL validation,
deploys the Worker, then **re-verifies the live site** (`www.zonca.dev`): every canonical
URL must return 200 and every historical alias must redirect to its canonical post. The
pipeline fails if any URL breaks.

Every PR gets a preview: the build is uploaded as a non-production Worker
**version** and the preview URL is commented on the PR. If the PR only modifies blog
posts, the comment links the modified post(s) directly.

## URL integrity

All current URLs are frozen. `/posts/<basename>.html` and `/posts/<basename>` both work,
and `public/_redirects` is generated from every historical alias (from the baseline
manifest in `tests/baseline/`). Never rename or remove a post file; if a slug must change,
add the old one as an alias.

## Rollback

The previous Quarto site is preserved at the `quarto-with-2026-10-01` release
(<https://github.com/zonca/zonca.dev/releases/tag/quarto-with-2026-10-01>). To roll back,
restore that commit and the former DNS setup (DreamHost nameservers were replaced by
Cloudflare on 2026-10-01).

## License

Site code: MIT. Content: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
