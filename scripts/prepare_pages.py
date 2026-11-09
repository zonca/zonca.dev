#!/usr/bin/env python3
"""Scaffold the Astro static site build inputs.

- Copy the two QMD posts into .generated/posts/*.md (plain Markdown input).
- Copy AGENTS.md, skill/SKILL.md into .generated/pages/*.md.
- Generate public/_redirects from the baseline alias table (every spelling of
  each alias, plus .ipynb notebook URLs) and the fixed rules.
- Copy co-located post assets (images, fonts, scripts, docs/, profile.jpg)
  into public/ so relative URLs keep resolving exactly like production.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED = os.path.join(ROOT, ".generated")
PUBLIC = os.path.join(ROOT, "public")

FIXED_REDIRECTS = [
    ("/consult", "/ai/", 301),
    ("/consult/", "/ai/", 301),
    ("/page/1", "/", 301),
    ("/GEMINI", "/AGENTS", 301),
]


def alias_variants(source: str) -> list[str]:
    """The spellings of one legacy URL that crawlers and old links request.

    Cloudflare `_redirects` matches paths exactly, so `/2020/09/post`,
    `/2020/09/post/` and `/2020/09/post.html` each need their own rule.
    """
    base = source[:-5] if source.endswith(".html") else source.rstrip("/")
    return [base, base + "/", base + ".html"]


def clean_url(path: str) -> str:
    """The final public URL of a page: no `.html`, and `/dir/index.html` -> `/dir/`."""
    if path.endswith("/index.html"):
        return path[: -len("index.html")]
    if path.endswith(".html"):
        return path[:-5]
    return path


def redirect_rules(aliases: dict[str, str], manifest: list[dict]) -> list[tuple[str, str, int]]:
    """Every (source, target, status) rule of public/_redirects, deduplicated.

    - each alias plus its trailing-slash and `.html` spellings
    - `/posts/<name>.ipynb` for notebook posts, which Google picks up from the
      GitHub source links
    - `<page>.html` -> `<page>` for every public page, so the `.html` form
      answers with a permanent 301 instead of the temporary 307 that
      Cloudflare `html_handling` sends
    - the fixed rules
    Every target is the final extensionless URL, so a redirect is one hop.
    Spellings that collide with a real page or an earlier rule are skipped.
    """
    pages = set()
    for r in manifest:
        c = r["canonical"]
        pages |= {c, c[:-5] if c.endswith(".html") else c}
    rules: dict[str, tuple[str, int]] = {}
    for source, target in sorted(aliases.items()):
        rules[source] = (clean_url(target), 301)
    for source, target in sorted(aliases.items()):
        for variant in alias_variants(source):
            if variant not in rules and variant not in pages:
                rules[variant] = (clean_url(target), 301)
    for r in manifest:
        if r.get("source_type") == "ipynb" and not r.get("draft"):
            stem = os.path.splitext(os.path.basename(r["source"]))[0]
            rules.setdefault(f"/posts/{stem}.ipynb", (clean_url(r["canonical"]), 301))
    for r in manifest:
        c = r["canonical"]
        if not r.get("draft") and c.endswith(".html") and c not in rules:
            rules[c] = (clean_url(c), 301)
    for source, target, status in FIXED_REDIRECTS:
        rules[source] = (target, status)
    return [(src, tgt, st) for src, (tgt, st) in rules.items()]


def main() -> int:
    gen_posts = os.path.join(GENERATED, "posts")
    gen_pages = os.path.join(GENERATED, "pages")
    os.makedirs(gen_posts, exist_ok=True)
    os.makedirs(gen_pages, exist_ok=True)

    # QMD posts -> Markdown (inject source so GitHub buttons point at the QMD)
    for name in os.listdir(os.path.join(ROOT, "posts")):
        if name.endswith(".qmd"):
            text = open(os.path.join(ROOT, "posts", name), encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
            if m:
                fm = yaml.safe_load(m.group(1)) or {}
                fm["source"] = f"posts/{name}"
                rebuilt = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip() + "\n---\n"
                text = rebuilt + text[m.end():]
            dst = os.path.join(gen_posts, os.path.splitext(name)[0] + ".md")
            with open(dst, "w", encoding="utf-8") as fh:
                fh.write(text)
            print(f"copied qmd -> {dst}")

    # Root markdown pages
    for src, dest in [
        ("AGENTS.md", os.path.join(gen_pages, "AGENTS.md")),
        ("skill/SKILL.md", os.path.join(gen_pages, "SKILL.md")),
    ]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, src), dest)

    # _redirects
    aliases_path = os.path.join(ROOT, "tests", "baseline", "aliases.json")
    if os.path.exists(aliases_path):
        aliases = json.load(open(aliases_path, encoding="utf-8"))
        manifest = json.load(open(os.path.join(ROOT, "tests", "baseline", "manifest.json"), encoding="utf-8"))
        rules = [f"{s} {t} {st}" for s, t, st in redirect_rules(aliases, manifest)]
        os.makedirs(PUBLIC, exist_ok=True)
        with open(os.path.join(PUBLIC, "_redirects"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(rules) + "\n")
        print(f"wrote {len(rules)} redirect rules")
    else:
        print("WARNING: tests/baseline/aliases.json missing; run baseline_manifest.py first",
              file=sys.stderr)
        return 1

    # Co-located post assets: everything tracked in posts/ that is not source
    tracked = subprocess.run(
        ["git", "ls-files", "posts/", "docs/", "skill/"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.splitlines()
    for rel in tracked:
        base = os.path.basename(rel)
        if base.endswith((".md", ".qmd", ".ipynb")) or base == "README.md" or base == "_metadata.yml":
            continue
        src = os.path.join(ROOT, rel)
        dst = os.path.join(PUBLIC, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # Root profile image used by about page
    for name in ("profile.jpg",):
        src = os.path.join(ROOT, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(PUBLIC, name))

    # robots.txt
    with open(os.path.join(PUBLIC, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("Sitemap: https://www.zonca.dev/sitemap.xml\n")

    # favicon
    favicon = os.path.join(ROOT, "posts", "favicon.ico")
    if os.path.exists(favicon):
        shutil.copy2(favicon, os.path.join(PUBLIC, "favicon.ico"))

    # llms.txt (AI-agent oriented site overview)
    os.makedirs(PUBLIC, exist_ok=True)
    with open(os.path.join(PUBLIC, "llms.txt"), "w", encoding="utf-8") as fh:
        fh.write(
            "# zonca.dev\n\n"
            "Andrea Zonca - computational scientist at the San Diego Supercomputer Center.\n"
            "Notes on Python, JupyterHub, Kubernetes and AI for science.\n\n"
            "Key pages:\n"
            "- [About](https://www.zonca.dev/about)\n"
            "- [AI consulting](https://www.zonca.dev/ai)\n"
            "- [All posts](https://www.zonca.dev/)\n"
        )

    # .well-known/ard.json + ai-catalog.json (ARD spec-compliant manifest)
    ard_manifest = {
        "specVersion": "1.0",
        "entries": [
            {
                "@context": "https://agenticresourcediscovery.org/context/v1",
                "identifier": "urn:air:www.zonca.dev:site:zonca-dev",
                "displayName": "zonca.dev",
                "type": "application/ai-catalog+json",
                "url": "https://www.zonca.dev/.well-known/ai-catalog.json",
                "description": "Andrea Zonca: notes on Python, JupyterHub, Kubernetes and AI for science.",
                "representativeQueries": [
                    "Andrea Zonca high performance computing and AI blog",
                    "JupyterHub Kubernetes tutorial",
                ],
            }
        ],
    }
    well_known = os.path.join(PUBLIC, ".well-known")
    os.makedirs(well_known, exist_ok=True)
    for name in ("ard.json", "ai-catalog.json"):
        with open(os.path.join(well_known, name), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(ard_manifest, indent=2) + "\n")
    print("public/ assets copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
