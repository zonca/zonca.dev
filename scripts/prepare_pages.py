#!/usr/bin/env python3
"""Scaffold the Astro static site build inputs.

- Copy the two QMD posts into .generated/posts/*.md (plain Markdown input).
- Copy GEMINI.md, AGENTS.md, skill/SKILL.md into .generated/pages/*.md.
- Generate public/_redirects from the baseline alias table plus fixed rules.
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
]


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
        ("GEMINI.md", os.path.join(gen_pages, "GEMINI.md")),
        ("AGENTS.md", os.path.join(gen_pages, "AGENTS.md")),
        ("skill/SKILL.md", os.path.join(gen_pages, "SKILL.md")),
    ]:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, src), dest)

    # _redirects
    aliases_path = os.path.join(ROOT, "tests", "baseline", "aliases.json")
    if os.path.exists(aliases_path):
        aliases = json.load(open(aliases_path, encoding="utf-8"))
        rules = []
        for source, target in sorted(aliases.items()):
            rules.append(f"{source} {target} 301")
        for source, target, status in FIXED_REDIRECTS:
            rules.append(f"{source} {target} {status}")
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
    print("public/ assets copied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
