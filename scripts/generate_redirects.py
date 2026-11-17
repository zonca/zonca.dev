#!/usr/bin/env python3
"""Add the permanent 301 rules for the `.html` URLs that Cloudflare only 307s.

`astro build` writes one HTML file per route and Cloudflare Workers Static
Assets rewrites `/about.html` to `/about` on its own. For a route that Astro
emits directly (`about.html`, `posts/<slug>.html`, `ai/research.html`) that
rewrite is a **301**. For a route emitted inside a subdirectory
(`categories/<category>.html`, `page/<n>.html`, `search.html`) the same rewrite
is a **307**. A temporary redirect consolidates nothing, so Google keeps the
`.html` URL in the index as a duplicate. That is exactly what the Search
Console duplicate reports for zonca.dev are made of.

`prepare_pages.py` already emits 301 rules for every page of the baseline
manifest (all posts and root pages), so this script closes only the remaining
gap, and it derives it from the real build output instead of re-deriving the
route list in Python. That way `/search`, category pages, archive pagination
and any route added later are covered automatically.

Cloudflare applies `_redirects` before serving a static asset ("Redirects are
always followed, regardless of whether or not an asset matches the incoming
request"), so these rules win over the asset layer's 307.

Trailing-slash forms are deliberately NOT handled here. Cloudflare answers
`/about/` with a 307 as well, but Google has never indexed a single one of
them (URL Inspection API, 2026-11-16: `/about/`, `/posts/<slug>/`,
`/categories/<category>/` all report "URL is unknown to Google"), so rules for
them would spend half of the remaining `_redirects` budget for no measurable
gain. See notes/zonca-dev-search-console.md in project_work for the audit.

Usage (run after `astro build`):
    python3 scripts/generate_redirects.py [--check]
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from prepare_pages import clean_url  # noqa: E402  (same normalization as the aliases)

DIST = os.path.join(ROOT, "dist")
# Cloudflare Workers Static Assets allows 2000 static rules in `_redirects`;
# leave headroom so a content milestone fails the build loudly here instead of
# silently shipping a file Cloudflare truncates.
MAX_RULES = 1900


def built_routes(dist_dir: str = DIST) -> list[str]:
    """Every HTML route of the build, normalized the way the live site serves it."""
    routes = []
    for root, _dirs, files in os.walk(dist_dir):
        for name in files:
            if not name.endswith(".html"):
                continue
            rel = os.path.relpath(os.path.join(root, name), dist_dir).replace(os.sep, "/")
            if rel == "index.html" or rel.endswith("/404.html") or rel == "404.html":
                continue
            routes.append(clean_url("/" + rel))
    return sorted(routes)


def variant_rules(dist_dir: str = DIST, existing_sources: set[str] | None = None) -> list[tuple[str, str]]:
    """(source, target) 301 rules for built routes whose `.html` form is not covered yet."""
    existing_sources = set(existing_sources or ())
    # A target that is itself a redirect source would make a two hop chain.
    redirecting = {s.rstrip("/") for s in existing_sources} | {s[:-5] for s in existing_sources if s.endswith(".html")}
    rules: list[tuple[str, str]] = []
    for target in built_routes(dist_dir):
        if target == "/":
            continue
        source = target.rstrip("/") + ".html"
        if source == target or source in existing_sources:
            continue
        if target.rstrip("/") in redirecting:
            continue
        rules.append((source, target))
    return rules


def read_rules(path: str) -> list[str]:
    if not os.path.exists(path):
        return []
    return [line.strip() for line in open(path, encoding="utf-8") if line.strip() and not line.startswith("#")]


def apply(dist_dir: str = DIST) -> int:
    redirects = os.path.join(dist_dir, "_redirects")
    rules = read_rules(redirects)
    if not rules:
        print(f"ERROR: {redirects} missing; run scripts/prepare_pages.py first", file=sys.stderr)
        return 1
    sources = {line.split()[0] for line in rules}
    added = variant_rules(dist_dir, sources)
    total = len(rules) + len(added)
    if total > MAX_RULES:
        print(
            f"ERROR: _redirects would hold {total} rules, over the {MAX_RULES} safety limit "
            f"(Cloudflare allows 2000 static rules). Move the legacy alias rules to Cloudflare "
            f"Bulk Redirects before adding more content.",
            file=sys.stderr,
        )
        return 1
    with open(redirects, "w", encoding="utf-8") as fh:
        fh.write("\n".join(rules + [f"{source} {target} 301" for source, target in added]) + "\n")
    print(f"added {len(added)} .html 301 rules, {total} rules total")
    return 0


def main() -> int:
    if "--check" in sys.argv:
        redirects = os.path.join(DIST, "_redirects")
        rules = read_rules(redirects)
        sources = {line.split()[0] for line in rules}
        missing = variant_rules(DIST, sources)
        if missing:
            print(f"{len(missing)} .html 301 rules missing, first: {missing[:5]}", file=sys.stderr)
            return 1
        print("all .html 301 rules present")
        return 0
    return apply(DIST)


if __name__ == "__main__":
    sys.exit(main())
