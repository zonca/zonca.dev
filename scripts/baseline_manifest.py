#!/usr/bin/env python3
"""Build the machine-readable baseline URL manifest for a spot-checked production site.

Canonical URL conventions (verified against production, www.zonca.dev):
  - Posts (Markdown/QMD/notebook): /posts/<source-basename>.html
    The .html form is the URL in the production sitemap.
  - Pages: index.qmd -> /index.html, about.qmd -> /about.html,
    ai/*.qmd -> /ai/<stem>.html, AGENTS.md -> /AGENTS.html,
    GEMINI.md -> /GEMINI.html, skill/SKILL.md -> /skill/SKILL.html
  - Alias URLs (from front matter) are known redirect sources; their target is
    the canonical URL of the source file that declares them.

Outputs:
  tests/baseline/manifest.json   manifest rows for every public page
  tests/baseline/aliases.json    alias source -> canonical target
  tests/baseline/summary.txt     human-readable summary

Draft posts (draft: true) are flagged and excluded from the canonical set:
production currently serves them as an empty HTML shell and omits them from
the sitemap.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import datetime

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "posts")
OUT_DIR = os.path.join(ROOT, "tests", "baseline")


def read_yaml(text: str) -> dict:
    m = re.match(r"^\s*---\s*\n(.*?)\n\s*---\s*\n?", text, re.S)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {"_yaml_error": True}


def notebook_front_matter(path: str) -> dict:
    """Read YAML front matter from the first raw cell of an .ipynb."""
    try:
        import json as _json

        nb = _json.load(open(path, encoding="utf-8"))
        for cell in nb.get("cells", []):
            if cell.get("cell_type") in ("raw", "markdown"):
                src = "".join(cell.get("source", []))
                if src.lstrip().startswith("---"):
                    fm = read_yaml(src)
                    if fm:
                        return fm
            break
    except Exception as exc:  # malformed JSON etc.
        return {"_parse_error": str(exc)}
    return {}


def collect_posts() -> list[dict]:
    rows = []
    patterns = ["*.md", "*.qmd", "*.ipynb"]
    files = []
    for pat in patterns:
        files.extend(sorted(glob.glob(os.path.join(POSTS, pat))))
    for path in files:
        base = os.path.basename(path)
        if base == "README.md":
            continue
        stem = os.path.splitext(base)[0]
        ext = os.path.splitext(base)[1].lstrip(".")
        if ext == "ipynb":
            fm = notebook_front_matter(path)
        else:
            fm = read_yaml(open(path, encoding="utf-8", errors="replace").read())
        if fm.get("_yaml_error"):
            fm = {}
        title = fm.get("title") or stem
        date = fm.get("date") or ""
        if date:
            date = str(date)[:10]
        rows.append(
            {
                "source": f"posts/{base}",
                "source_type": ext,
                "canonical": f"/posts/{stem}.html",
                "title": title,
                "date": date,
                "categories": fm.get("categories") or [],
                "aliases": list(fm.get("aliases") or []),
                "draft": bool(fm.get("draft")),
                **({"front_matter_error": True} if fm.get("_yaml_error") else {}),
                **({"parse_error": True} if fm.get("_parse_error") else {}),
            }
        )
    return rows


def collect_pages() -> list[dict]:
    pages = [
        ("index.qmd", "/index.html"),
        ("about.qmd", "/about.html"),
        ("AGENTS.md", "/AGENTS.html"),
        ("GEMINI.md", "/GEMINI.html"),
        ("skill/SKILL.md", "/skill/SKILL.html"),
    ]
    ai_files = sorted(glob.glob(os.path.join(ROOT, "ai", "*.qmd")))
    for af in ai_files:
        pages.append((f"ai/{os.path.basename(af)}", f"/ai/{os.path.splitext(os.path.basename(af))[0]}.html"))
    rows = []
    for source, canonical in pages:
        fm = read_yaml(open(os.path.join(ROOT, source), encoding="utf-8", errors="replace").read())
        rows.append(
            {
                "source": source,
                "source_type": os.path.splitext(source)[1].lstrip("."),
                "canonical": canonical,
                "title": fm.get("title") or canonical,
                "date": "",
                "categories": [],
                "aliases": [],
                "draft": False,
            }
        )
    return rows


def main() -> int:
    posts = collect_posts()
    pages = collect_pages()
    all_rows = posts + pages

    canonical_urls = [r["canonical"] for r in all_rows]
    duplicates = sorted({u for u in canonical_urls if canonical_urls.count(u) > 1})

    aliases: dict[str, str] = {}
    for r in all_rows:
        for a in r["aliases"]:
            a = str(a).strip()
            if a and not a.startswith("/"):
                a = "/" + a
            norm = a.rstrip("/")
            if not norm:
                continue
            if norm in aliases and aliases[norm] != r["canonical"]:
                print(f"WARNING: conflicting alias {norm} -> {aliases[norm]} vs {r['canonical']}", file=sys.stderr)
            aliases[norm] = r["canonical"]

    draft_rows = [r for r in all_rows if r["draft"]]
    public_rows = [r for r in all_rows if not r["draft"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(all_rows, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "aliases.json"), "w", encoding="utf-8") as fh:
        json.dump(aliases, fh, indent=2, ensure_ascii=False, sort_keys=True)

    summary = [
        f"Generated: {datetime.utcnow().isoformat()}Z",
        f"Post sources: {len(posts)}  Pages: {len(pages)}",
        f"Public canonical URLs: {len(public_rows)}  Draft (excluded): {len(draft_rows)}",
        f"Aliases: {len(aliases)}",
        f"Duplicate canonical URLs: {len(duplicates)}",
    ]
    for d in duplicates:
        summary.append(f"  DUPLICATE: {d}")
    missing_meta = [r for r in posts if not r["date"]]
    if missing_meta:
        summary.append(f"Posts without a date: {len(missing_meta)}")
        for r in missing_meta:
            summary.append(f"  {r['source']}")
    for r in posts:
        if r.get("front_matter_error") or r.get("parse_error"):
            summary.append(f"PARSE ISSUE: {r['source']}")
    with open(os.path.join(OUT_DIR, "summary.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(summary) + "\n")
    print("\n".join(summary))
    return 1 if duplicates or missing_meta else 0


if __name__ == "__main__":
    sys.exit(main())
