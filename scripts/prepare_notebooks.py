#!/usr/bin/env python3
"""Preprocess every .ipynb in posts/ WITHOUT executing it.

Reads YAML front matter from the first raw/markdown cell when present, converts
markdown cells, code cells and STORED outputs into a generated Markdown post
under .generated/posts/<stem>.md. Binary image outputs are extracted to
public/posts/notebooks/<stem>/ with deterministic names. The normal site build
never executes notebooks; only notebook-conversion dependencies are needed.

Fails loudly on malformed notebooks, bad front matter, or missing assets.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
from typing import Any

import nbformat
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "posts")
OUT_POSTS = os.path.join(ROOT, ".generated", "posts")
OUT_IMAGES = os.path.join(ROOT, "public", "posts", "notebooks")

ERRORS: list[str] = []


def front_matter(text: str) -> tuple[dict, str]:
    """Return (yaml dict, remaining text) for a notebook cell string."""
    m = re.match(r"^\s*---\s*\n(.*?)\n\s*---\s*\n?", text, re.S)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
        if not isinstance(data, dict):
            raise ValueError("front matter is not a YAML mapping")
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid notebook front matter: {exc}") from exc
    return data, text[m.end():]


def save_image(data: bytes | str, mime: str, stem: str, key: str) -> str:
    ext = {"image/png": "png", "image/svg+xml": "svg", "image/jpeg": "jpg", "image/gif": "gif"}.get(mime)
    if not ext:
        raise ValueError(f"unsupported image mime {mime}")
    raw = base64.b64decode(data) if isinstance(data, str) else data
    digest = hashlib.sha1(raw).hexdigest()[:12]
    rel = os.path.join("notebooks", stem, f"{key}-{digest}.{ext}")
    out = os.path.join(OUT_IMAGES, stem, f"{key}-{digest}.{ext}")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(raw)
    return f"/posts/{rel.replace(os.sep, '/')}"


def cell_to_markdown(cell: dict, stem: str, counter: list[int]) -> str:
    chunks: list[str] = []
    if cell["cell_type"] == "markdown":
        text = "".join(cell.get("source", []))
        image_assets = cell.get("attachments") or {}
        for name, payload in image_assets.items():
            for mime, data in payload.items():
                url = save_image(data, mime, stem, f"att-{hashlib.sha1(name.encode()).hexdigest()[:8]}")
                # Rewrite both attachment:name and plain filename references
                text = re.sub(re.escape(name), url, text)
        if text.strip():
            chunks.append(text.rstrip() + "\n")
    elif cell["cell_type"] == "code":
        source = "".join(cell.get("source", []))
        lang = "python"
        chunks.append(f"```{lang}\n{source.rstrip()}\n```\n")
        for idx, output in enumerate(cell.get("outputs", [])):
            otype = output.get("output_type")
            data = output.get("data") or {}
            if otype == "stream":
                text = "".join(output.get("text", []))
                if text.strip():
                    chunks.append(f"```text\n{text.rstrip()}\n```\n")
                continue
            if "text/markdown" in data:
                chunks.append("".join(data["text/markdown"]).rstrip() + "\n")
                continue
            mime, payload = None, None
            for cand in ("text/html", "image/svg+xml", "image/png", "image/jpeg", "text/plain"):
                if cand in data:
                    mime, payload = cand, data[cand]
                    break
            if mime is None:
                continue
            if mime.startswith("image/"):
                counter[0] += 1
                url = save_image(payload, mime, stem, f"output-{counter[0]}")
                chunks.append(f"![output {counter[0]}]({url})\n")
            elif mime == "text/html":
                html = payload if isinstance(payload, str) else "".join(payload)
                if html.strip():
                    chunks.append(html.rstrip() + "\n")
            elif mime == "text/plain":
                text = payload if isinstance(payload, str) else "".join(payload)
                if text.strip():
                    chunks.append(f"```text\n{text.rstrip()}\n```\n")
    elif cell["cell_type"] == "raw":
        text = "".join(cell.get("source", []))
        if text.strip():
            chunks.append(text.rstrip() + "\n")
    return "\n".join(chunks) + "\n"


def convert_notebook(path: str) -> None:
    stem = os.path.splitext(os.path.basename(path))[0]
    try:
        nb = nbformat.read(path, as_version=4)
    except Exception as exc:
        ERRORS.append(f"{path}: cannot parse notebook: {exc}")
        return

    meta: dict[str, Any] = {}
    counter = [0]
    body_parts: list[str] = []

    for i, cell in enumerate(nb.cells):
        if i == 0 and cell["cell_type"] in ("raw", "markdown"):
            text = "".join(cell.get("source", []))
            if text.lstrip().startswith("---"):
                try:
                    meta, rest = front_matter(text)
                except ValueError as exc:
                    ERRORS.append(f"{path}: {exc}")
                    return
                # preserve any content after the front matter
                cell["source"] = rest.splitlines(keepends=True)
                if not rest.strip():
                    continue
        body_parts.append(cell_to_markdown(cell, stem, counter))

    meta.setdefault("title", stem)
    meta["date"] = meta.get("date") or os.path.basename(path)[:10]
    meta["source"] = f"posts/{os.path.basename(path)}"
    meta["notebook"] = True
    body = "\n".join(body_parts).strip() + "\n"

    fm_yaml = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    out = os.path.join(OUT_POSTS, f"{stem}.md")
    os.makedirs(OUT_POSTS, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"---\n{fm_yaml}\n---\n\n{body}")


def main() -> int:
    notebooks = sorted(f for f in os.listdir(POSTS) if f.endswith(".ipynb"))
    print(f"Preparing {len(notebooks)} notebooks...")
    for name in notebooks:
        convert_notebook(os.path.join(POSTS, name))
    if ERRORS:
        print("ERRORS:", file=sys.stderr)
        for e in ERRORS:
            print(f"  - {e}", file=sys.stderr)
        return 1
    # Fail loudly if any generated route collides (e.g. stem clash with .md)
    md_stems = {os.path.splitext(f)[0] for f in os.listdir(POSTS) if f.endswith(".md")}
    generated = {os.path.splitext(f)[0] for f in os.listdir(OUT_POSTS)} if os.path.isdir(OUT_POSTS) else set()
    clashes = generated & md_stems
    if clashes:
        print("Route collisions between notebooks and markdown posts:", clashes, file=sys.stderr)
        return 1
    print(f"OK: generated {len(generated)} notebook posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
