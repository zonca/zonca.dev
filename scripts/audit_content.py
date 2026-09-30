#!/usr/bin/env python3
"""Audit posts for rendering features that must survive the Astro migration.

Produces tests/baseline/content_features.json with per-file feature flags and
prints a summary plus the representative regression set.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tests", "baseline", "content_features.json")

FEATURES = {
    "raw_html": r"<(div|span|iframe|video|img|script|style|br|hr)\b",
    "script_embed": r"<script\b",
    "math_inline": r"\$\$?[^$]+\$\$?",
    "table": r"^\s*\|.*\|\s*$",
    "fence": r"^```",
    "code_indent": r"^    ",
    "internal_link_md": r"\]\(\./[^)]+\.md",
    "internal_link_html": r"\]\(\./[^)]+\.html",
    "image_rel": r"!\[[^\]]*\]\((?!http)([^)]+)\)",
    "link_abs_post": r"\]\(/posts/",
    "download_file": r"\]\([^)]+\.(ipynb|py|sh|jpeg|jpg|png|gif|pdf|txt)" + r"\)",
    "custom_metadata": r"^(output-file|title-block-banner|toc|code-fold|bibliography|fig-|chunk-|knitr|jupyter)",
    "gist": r"gist\.github\.com",
    "youTube": r"youtube\.com|youtu\.be",
    "spoiler": r"<details>",
}


def main() -> int:
    files = sorted(
        glob.glob(os.path.join(ROOT, "posts", "*.md"))
        + glob.glob(os.path.join(ROOT, "posts", "*.qmd"))
        + glob.glob(os.path.join(ROOT, "posts", "*.ipynb"))
    )
    report: dict[str, dict] = {}
    for path in files:
        rel = os.path.relpath(path, ROOT)
        base = os.path.basename(path)
        if base == "README.md":
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        flags = {}
        for name, pat in FEATURES.items():
            flags[name] = bool(re.search(pat, text, re.M))
        report[rel] = flags

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    counts = {name: sum(1 for f in report.values() if f[name]) for name in FEATURES}
    print("Feature counts (files with feature):")
    for name, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {name}: {count}")

    # Representative regression set: one file per feature category plus
    # archetypes per source type, drawn from existing posts.
    picks = {
        "old_markdown": "posts/2006-09-20-pillole-di-astrofisica.md",
        "recent_markdown": "posts/2026-09-28-software-citation-primer.md",
        "qmd_post": "posts/2026-09-01-python-for-hpc.qmd",
        "notebook_png": None,
        "notebook_markdown_output": None,
        "post_aliases": None,
        "post_raw_html": None,
        "post_local_images": None,
    }
    for path, flags in report.items():
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4000)
        has_alias = re.search(r"^aliases:", head, re.M)
        if picks["post_aliases"] is None and has_alias:
            picks["post_aliases"] = path
        if picks["post_raw_html"] is None and flags["raw_html"]:
            picks["post_raw_html"] = path
        if picks["post_local_images"] is None and (
            flags["image_rel"] and re.search(r"!\[[^\]]*\]\((?!(http))", head)
        ):
            picks["post_local_images"] = path
    # Notebooks selected separately (need to inspect outputs)
    notebooks = [p for p in report if p.endswith(".ipynb")]
    for nb in notebooks:
        import json as _json

        cell_types = [c["cell_type"] for c in _json.load(open(nb, encoding="utf-8"))["cells"]]
        out_mimes: set[str] = set()
        try:
            nb_data = _json.load(open(nb, encoding="utf-8"))
            for c in nb_data["cells"]:
                for o in c.get("outputs", []):
                    out_mimes.update(o.get("data", {}).keys())
        except Exception:
            pass
        if picks["notebook_png"] is None and "image/png" in out_mimes:
            picks["notebook_png"] = nb
        if picks["notebook_markdown_output"] is None and "text/markdown" in out_mimes:
            picks["notebook_markdown_output"] = nb
    print("\nRepresentative regression set:")
    for key, val in picks.items():
        if val is None:
            print(f"  {key}: MISSING")
        else:
            print(f"  {key}: {val}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
