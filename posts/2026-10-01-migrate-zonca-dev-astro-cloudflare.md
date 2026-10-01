---
title: "Migrating zonca.dev from Quarto to Astro on Cloudflare Workers"
date: 2026-10-01
categories: [tools, github, cloudcomputing]
layout: post
draft: true
description: "How zonca.dev moved from Quarto served by Netlify to a minimal Astro static site on Cloudflare Workers, keeping every URL and redirect intact."
---

I migrated zonca.dev from Quarto (rendered by GitHub Actions and served by Netlify) to a
minimal, mobile-first Astro static site deployed on Cloudflare Workers Static Assets. This
post explains why, how the migration preserved every URL, and how the site is built and
deployed now.

---

## Why move

The Quarto setup worked for years, but I wanted a lighter build and a single platform for
both the site and its deploys. The main constraints were that nothing could break:

- Preserve every current canonical URL exactly, especially `/posts/YYYY-MM-DD-slug`.
- Preserve all historical aliases and redirects (over 200), mostly old Jekyll-style URLs.
- Keep Markdown as the authoring format and support Jupyter notebooks as first-class
  posts, rendering stored outputs without executing them during builds.
- Keep the "Download source" and "Contribute" links on every post.

## The migration plan

I started from a machine-readable baseline: a manifest of all 411 public URLs and 247
aliases derived from the existing site's front matter, cross-checked against the production
sitemap. Every acceptance check compares the new site against this manifest.

The new build:

- **Astro static output** in `src/`, with content collections reading `posts/*.md` plus
  generated notebook posts under `.generated/`.
- **Notebooks** are converted by `scripts/prepare_notebooks.py` without execution: front
  matter is read from the first cell, stored outputs (text, HTML, Markdown, PNG, SVG) are
  converted to static content and extracted images.
- **Redirects**: `public/_redirects` is generated from every historical alias, pointing to
  the canonical posts with 301s.

## URLs: verified, not assumed

After the cutover, a validator walks the live site and confirms every expected canonical
URL returns 200 and every alias ends at its intended canonical post. This runs automatically
in CI after every deploy — the pipeline fails if any URL breaks:

```
Canonical URLs OK: 411/411
Alias redirects OK: 247/247
```

## Deploying on Cloudflare Workers

The site is a static assets-only Worker: `wrangler.jsonc` serves `dist/` with Cloudflare's
automatic trailing-slash handling, so both `/posts/name` and `/posts/name.html` work and
trailing-slash URLs redirect cleanly. `www.zonca.dev` is attached as a custom domain with
automatic HTTPS; the apex `zonca.dev` keeps redirecting to `www`.

Moving DNS from DreamHost to Cloudflare required replicating the mail records exactly (MX
to Mailchannels, SPF, DMARC) before switching nameservers, so email was not disrupted.

## CI/CD

GitHub Actions now builds and validates on every push and pull request:

- Push: build → `astro check` → URL validation → deploy to the production Worker → re-run
  the full live URL verification.
- Pull requests: Netlify-style previews. The PR build is uploaded as a Worker **version**
  (never touching production) and the version preview URL is commented on the PR.

## Results

The final Lighthouse run on the homepage is 100/100/100/100 (performance, accessibility,
best practices, SEO), up from 95/91/96 with the previous design, and zero client-side
JavaScript except the small search page. Mobile is the primary target: a single-column
layout, no sidebars, and 720px readable content.

---

If you want the same setup for your own blog, the key insight is to build the URL manifest
first — everything else is much easier once you can verify nothing breaks.
