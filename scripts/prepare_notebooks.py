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
import shutil
import sys
from typing import Any

import nbformat
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "posts")
OUT_POSTS = os.path.join(ROOT, ".generated", "posts")
OUT_IMAGES = os.path.join(ROOT, "public", "posts", "notebooks")

ERRORS: list[str] = []

FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def section_headings(text: str) -> list[str]:
    """Return level-2+ ATX headings in a markdown string, ignoring fenced blocks.

    Astro turns each of these into `<h2 id="...">`, which is the only way a reader
    can link straight at one part of a long notebook post, so a notebook without
    any of them cannot be cited section by section.
    """
    found: list[str] = []
    fenced = False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) >= 2:
            found.append(m.group(2).strip())
    return found


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


def image_size(raw: bytes, mime: str) -> tuple[int, int] | None:
    """Return (width, height) for PNG/JPEG/SVG image data."""
    try:
        if mime == "image/png" and raw[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")
            return w, h
        if mime == "image/jpeg" and raw[:2] == b"\xff\xd8":
            i = 2
            while i < len(raw):
                if raw[i] != 0xFF:
                    i += 1
                    continue
                marker = raw[i + 1]
                if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h = int.from_bytes(raw[i + 5 : i + 7], "big")
                    w = int.from_bytes(raw[i + 7 : i + 9], "big")
                    return w, h
                if marker in (0xD8, 0xD9):
                    return None
                seg_len = int.from_bytes(raw[i + 2 : i + 4], "big")
                i += 2 + seg_len
        if mime == "image/svg+xml":
            text = raw.decode("utf-8", errors="replace")
            m = re.search(r"width=\"?(\d+)", text)
            h = re.search(r"height=\"?(\d+)", text)
            if m and h:
                return int(m.group(1)), int(h.group(1))
            vb = re.search(r"viewBox=\"[\d.\- ]+\s+[\d.\- ]+\s+([\d.]+)\s+([\d.]+)\"", text)
            if vb:
                return int(float(vb.group(1))), int(float(vb.group(2)))
    except Exception:
        pass
    return None


def save_image(data: bytes | str, mime: str, stem: str, key: str) -> tuple[str, tuple[int, int] | None]:
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
    return f"/posts/{rel.replace(os.sep, '/')}", image_size(raw, mime)


def img_html(url: str, size: tuple[int, int] | None, alt: str) -> str:
    dims = f' width="{size[0]}" height="{size[1]}"' if size else ""
    return f'<img src="{url}"{dims} loading="lazy" decoding="async" alt="{alt}">'


def cell_to_markdown(cell: dict, stem: str, counter: list[int]) -> str:
    chunks: list[str] = []
    if cell["cell_type"] == "markdown":
        text = "".join(cell.get("source", []))
        image_assets = cell.get("attachments") or {}
        for name, payload in image_assets.items():
            for mime, data in payload.items():
                url, _size = save_image(data, mime, stem, f"att-{hashlib.sha1(name.encode()).hexdigest()[:8]}")
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
                url, size = save_image(payload, mime, stem, f"output-{counter[0]}")
                chunks.append(img_html(url, size, f"output {counter[0]}") + "\n")
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
    sections: list[str] = []

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
        if cell["cell_type"] == "markdown":
            sections.extend(section_headings("".join(cell.get("source", []))))
        body_parts.append(cell_to_markdown(cell, stem, counter))

    if not sections:
        ERRORS.append(
            f"{path}: no `##` section headings, so the published post has no anchors "
            "to link to; give each part of the notebook a `##` heading"
        )

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


def prune_stale(stems: set[str]) -> list[str]:
    """Delete generated output whose notebook no longer exists (renamed or removed).

    Only posts carrying the `notebook: true` marker are eligible. `prepare_pages.py`
    writes the QMD posts into this same directory, and those must survive.
    """
    removed: list[str] = []
    if os.path.isdir(OUT_POSTS):
        for name in sorted(os.listdir(OUT_POSTS)):
            if not name.endswith(".md"):
                continue
            stem = os.path.splitext(name)[0]
            if stem in stems:
                continue
            path = os.path.join(OUT_POSTS, name)
            try:
                with open(path, encoding="utf-8") as fh:
                    head = fh.read(4096)
            except OSError:
                continue
            if re.search(r"^notebook: true$", head, re.M):
                os.remove(path)
                removed.append(f"post for {stem}")
    if os.path.isdir(OUT_IMAGES):
        for name in sorted(os.listdir(OUT_IMAGES)):
            path = os.path.join(OUT_IMAGES, name)
            if os.path.isdir(path) and name not in stems:
                shutil.rmtree(path)
                removed.append(f"image dir for {name}")
    return removed


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
    # Prune only after every notebook converted, so a parse failure cannot
    # delete the output of the notebook that caused it.
    for what in prune_stale({os.path.splitext(n)[0] for n in notebooks}):
        print(f"pruned stale {what}")
    # Fail loudly if any generated route collides (e.g. stem clash with .md)
    md_stems = {os.path.splitext(f)[0] for f in os.listdir(POSTS) if f.endswith(".md")}
    generated = {os.path.splitext(f)[0] for f in os.listdir(OUT_POSTS)} if os.path.isdir(OUT_POSTS) else set()
    clashes = generated & md_stems
    if clashes:
        print("Route collisions between notebooks and markdown posts:", clashes, file=sys.stderr)
        return 1
    print(f"OK: generated {len(notebooks)} notebook posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
