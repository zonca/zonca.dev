#!/usr/bin/env python3
"""Fail if a URL that was reachable before is no longer reachable.

The baseline manifest is regenerated from the post front matter before every
build, so validating a build against it cannot see a URL that was dropped: the
manifest silently follows the sources. This check compares the manifest as it
was at the base revision with the manifest rebuilt from the current sources,
and requires every URL that was reachable before to still be reachable now,
either as a page or as an alias (redirect) declared in the front matter.

It catches renames, deletions, unpublishing a post with ``draft: true`` and
dropping an ``aliases:`` entry, all of which silently break a published URL.

Usage:
    python3 scripts/check_url_history.py [--base REV]

REV is the revision the change is compared against: the base branch tip for a
pull request, the previous tip of the branch for a push. It defaults to
``BASE_SHA`` from the environment and then to the merge base of HEAD with the
default branch, so the check also runs on a local topic branch.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import baseline_manifest  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = "tests/baseline/manifest.json"
ALIASES_PATH = "tests/baseline/aliases.json"
DEFAULT_BRANCHES = ("origin/main", "main")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", ROOT, *args], capture_output=True, text=True, check=False
    )


def normalize(url: str) -> str:
    """The URL as the site serves it: the manifest tracks the .html form."""
    url = url.strip()
    if url.endswith("/") and len(url) > 1:
        url = url[:-1]
    if url.endswith(".html"):
        url = url[: -len(".html")]
    return url


def reachable(rows: list[dict], aliases: dict[str, str]) -> set[str]:
    """Every URL a reader can reach: the public pages plus the redirects."""
    urls = {normalize(r["canonical"]) for r in rows if not r.get("draft")}
    urls |= {normalize(a) for a in aliases}
    return urls


def published_by(rows: list[dict]) -> dict[str, str]:
    return {normalize(r["canonical"]): r.get("source", "?") for r in rows}


def default_base() -> str | None:
    for ref in DEFAULT_BRANCHES:
        proc = git("merge-base", "HEAD", ref)
        sha = proc.stdout.strip()
        if proc.returncode == 0 and sha:
            return sha
    return None


def read_at(rev: str, path: str) -> str | None:
    """The content of a file at a revision, or None if it does not exist."""
    proc = git("show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default=os.environ.get("BASE_SHA") or "",
        help="revision to compare against (default: $BASE_SHA, then the merge base with the default branch)",
    )
    args = parser.parse_args()

    base = args.base or default_base()
    if not base:
        print("No base revision found, nothing to compare against.")
        return 0

    base_manifest_text = read_at(base, MANIFEST_PATH)
    if base_manifest_text is None:
        print(f"No baseline manifest at {base}, nothing to compare against.")
        return 0
    base_aliases_text = read_at(base, ALIASES_PATH) or "{}"

    try:
        base_rows = json.loads(base_manifest_text)
        base_aliases = json.loads(base_aliases_text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: cannot parse the baseline manifest at {base}: {exc}", file=sys.stderr)
        return 2

    rows = baseline_manifest.build_rows()
    aliases = baseline_manifest.build_aliases(rows)

    before = reachable(base_rows, base_aliases)
    after = reachable(rows, aliases)
    missing = sorted(before - after)
    added = sorted(after - before)
    sources = published_by(base_rows)

    subject = git("log", "-1", "--format=%h %s", base).stdout.strip() or base
    print(f"URL history check against {subject}")
    print(f"  reachable before: {len(before)}    reachable now: {len(after)}")
    print(f"  new URLs: {len(added)}")

    if not missing:
        print("  every URL that was reachable before is still reachable")
        return 0

    print(f"  FAIL: {len(missing)} URL(s) that were reachable before are no longer reachable:")
    for url in missing:
        source = sources.get(url)
        if source:
            print(f"\n    {url}")
            print(f"      was a page, published by {source}")
        else:
            print(f"\n    {url}")
            print("      was a redirect")
        print("      now neither a page nor a redirect")
        print(
            f"\n    Fix: add 'aliases: [{url}]' to the front matter of the post that "
            "replaces it,"
        )
        print("    or restore the deleted file, so the old URL keeps redirecting.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
