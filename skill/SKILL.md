---
name: zonca-dev
description: "Create a new blog post on zonca.dev: write the Markdown, add the images, open a pull request."
version: 2.0.0
author: Andrea Zonca
license: MIT
metadata:
  hermes:
    tags: [blog, zonca.dev, astro, markdown, pull-request]
---

# zonca.dev blog post skill

Create a blog post on the zonca.dev site (Astro, source in `posts/`) and open it as a pull
request. The post is **not** merged by this skill, Andrea reviews and merges it.

The Jules PR review workflow was removed from the repository (Jules is being decommissioned),
so a pull request now only needs the "Build and deploy Astro site" workflow to pass.

## Steps

1. Work in a clone of the repository:

   ```bash
   cd /tmp/opencode && git clone https://github.com/zonca/zonca.dev.git zonca.dev
   cd zonca.dev && git fetch origin && git checkout main && git pull --ff-only
   ```

2. Create a branch from `main`:

   ```bash
   git checkout -b blog/<slug>
   ```

3. Write the post as `posts/YYYY-MM-DD-<slug>.md`, following the conventions in the
   repository `AGENTS.md`: front matter with `title` (quoted, sentence case), `date`
   (matching the file name), `categories` (existing ones only) and `layout: post`;
   an optional one line `description`; `##` section headings; prose wrapped under 100
   characters; fenced code blocks with a language tag; internal links as
   `./YYYY-MM-DD-slug.md`.

4. Add the images to `posts/img/` and reference them relative to the post
   (`![caption](img/file.png)`), see `AGENTS.md`.

5. Check the post before committing: every link returns 200, no secrets, code blocks
   tagged.

6. Commit, push and open the pull request:

   ```bash
   git add posts/ && git commit -m "Add post: <title>"
   git push -u origin blog/<slug>
   gh pr create --base main --head blog/<slug> --title "Add post: <title>" --body "<summary>"
   ```

7. Report the pull request URL and the CI preview URL that the workflow comments on the
   pull request (the "Preview:" comment). The preview URL lets the post be checked in a
   browser before merging.

## Notes

- The site is deployed by GitHub Actions on every push to `main`, so the post goes live
  only after the pull request is merged.
- Post URLs are `/posts/<source-basename>`, derived from the file name. Never rename or
  move an existing post file.
- The Buffer social media step (see the site `AGENTS.md`) is optional and needs Andrea's
  approval for the drafts.
