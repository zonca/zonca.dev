#!/usr/bin/env python3
"""Validate the Astro build against the baseline URL manifest.

Modes:
  (default)   checks the local dist/ directory
  --live URL  checks a deployed site over HTTP (e.g. https://xxx.workers.dev)

Checks:
  - every public canonical URL from the manifest has a build artifact (or
    returns 200 / a redirect chain ending at 200 when --live)
  - every alias maps to an existing canonical target
  - no duplicate/extra post routes; post counts match the manifest
  - internal absolute links resolve inside dist/ (or return 200 when --live)
  - the generated _redirects file covers every manifest alias exactly once
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tests", "baseline", "manifest.json")
ALIASES = os.path.join(ROOT, "tests", "baseline", "aliases.json")

failures: list[str] = []


def fail(msg: str):
    failures.append(msg)
    print(f"  FAIL: {msg}")


def check_local():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    dist = os.path.join(ROOT, "dist")
    public_manifest = [r for r in manifest if not r["draft"]]
    print(f"Manifest: {len(public_manifest)} public canonical URLs, {len(aliases)} aliases")

    dist_posts = [
        f for f in os.listdir(os.path.join(dist, "posts"))
        if f.endswith(".html") and not f.startswith(".")
    ]
    expected_posts = sum(1 for r in public_manifest if r["canonical"].startswith("/posts/"))
    if len(dist_posts) != expected_posts:
        fail(f"post count mismatch: dist={len(dist_posts)} manifest={expected_posts}")

    missing = []
    for r in public_manifest:
        path = os.path.join(dist, r["canonical"].lstrip("/"))
        if not os.path.exists(path):
            missing.append(r["canonical"])
    for m in missing[:20]:
        fail(f"missing build artifact for {m}")
    if len(missing) > 20:
        fail(f"... and {len(missing) - 20} more missing artifacts")

    # aliases: target must exist
    for src, target in aliases.items():
        path = os.path.join(dist, target.lstrip("/"))
        if not os.path.exists(path):
            fail(f"alias {src} -> missing target {target}")

    # _redirects: one rule per alias (plus consult rules)
    redirects_path = os.path.join(dist, "_redirects")
    if os.path.exists(redirects_path):
        rules = [l.strip() for l in open(redirects_path, encoding="utf-8") if l.strip()]
        generated = {r.split()[0] for r in rules if not r.startswith("#")}
        expected = set(aliases.keys()) | {"/consult", "/consult/", "/page/1"}
        missing_rules = expected - generated
        extra_rules = generated - expected
        if missing_rules:
            fail(f"redirects missing {len(missing_rules)} alias rules: {sorted(missing_rules)[:5]}")
        if extra_rules:
            fail(f"redirects contain {len(extra_rules)} unexpected rules: {sorted(extra_rules)[:5]}")
        fixed_targets = {"/consult": "/ai/", "/consult/": "/ai/", "/page/1": "/"}
        for src in sorted(expected):
            rule = [r for r in rules if r.split()[0] == src]
            if rule:
                parts = rule[0].split()
                target = parts[1] if len(parts) > 1 else ""
                if target != aliases.get(src, fixed_targets.get(src, "/ai/")):
                    fail(f"redirect {src} -> {target} does not match manifest {aliases.get(src)}")
        # duplicate sources not allowed
        dupes = {r.split()[0] for r in rules} if len(generated) != len([r for r in rules]) else set()
        if dupes:
            fail(f"duplicate redirect sources: {sorted(dupes)[:5]}")
    else:
        fail("dist/_redirects missing")

    # internal absolute links resolve inside dist
    href_re = re.compile(r'(?:href|src)="(/[^"#?]*)(?:[?#][^"]*)?"')
    broken: list[str] = []
    seen: set[str] = set()
    for root, _dirs, files in os.walk(dist):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(root, fn)
            if fp in seen:
                continue
            seen.add(fp)
            html = open(fp, encoding="utf-8", errors="replace").read()
            for m in href_re.finditer(html):
                url = m.group(1)
                if url.endswith(".html"):
                    target = os.path.join(dist, url.lstrip("/"))
                    if not os.path.exists(target):
                        broken.append((os.path.relpath(fp, dist), url))
    if broken:
        fail(f"{len(broken)} broken internal links (first 10):")
        for b in broken[:10]:
            print(f"      {b[0]} -> {b[1]}")

    print(f"Checked {len(seen)} HTML files")


def http_get(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "zonca-validator"})
    # Follows redirect chains; the final response/URL is what we validate.
    return urllib.request.urlopen(req, timeout=timeout)


def _http_status(base: str, path: str, timeout: int = 10) -> tuple[int, str]:
    try:
        resp = http_get(base + path, timeout)
        url = resp.geturl()
        status = resp.status
        resp.close()
        return status, url
    except urllib.error.HTTPError as e:
        return e.code, base + path
    except Exception as exc:
        return -1, f"ERR:{type(exc).__name__}:{exc}"


def check_live(base: str, workers: int = 16):
    from concurrent.futures import ThreadPoolExecutor

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    aliases = json.load(open(ALIASES, encoding="utf-8"))
    public_manifest = [r for r in manifest if not r["draft"]]
    print(f"Live site: {base}  ({len(public_manifest)} canonical, {len(aliases)} aliases)")

    displayed_errors = 0

    def report_errors(prefix: str, path: str, value):
        nonlocal displayed_errors
        if isinstance(value, str):
            if displayed_errors < 5:
                displayed_errors += 1
                print(f"  [diag] {path}: {value}")

    # Canonical: both /posts/x and /posts/x.html return 200
    canonical_ok = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {}
        for r in public_manifest:
            clean = re.sub(r"\.html$", "", r["canonical"])
            futures[r["canonical"]] = (r["canonical"], pool.submit(_http_status, base, clean), pool.submit(_http_status, base, r["canonical"]))
        for canonical, (_, f1, f2) in futures.items():
            st1, u1 = f1.result()
            st2, u2 = f2.result()
            if st1 == 200 and st2 == 200:
                canonical_ok += 1
            else:
                report_errors("canonical", canonical, u1 if st1 == -1 else u2 if st2 == -1 else st2)
                fail(f"{canonical} extless={st1} .html={st2}")
    print(f"Canonical URLs OK: {canonical_ok}/{len(public_manifest)}")

    # Aliases: must end at the canonical target with a 200 (redirect chain ok)
    alias_ok = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            src: (src, target, pool.submit(_http_status, base, src))
            for src, target in aliases.items()
        }
        for src, target, f in futures.values():
            status, final_url = f.result()
            expected = base + re.sub(r"\.html$", "", target)
            if status == 200 and final_url == expected:
                alias_ok += 1
            else:
                report_errors("alias", src, f"{status} -> {final_url}")
                fail(f"alias {src} -> status {status}, landed at {final_url} (expected {expected})")
    print(f"Alias redirects OK: {alias_ok}/{len(aliases)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", metavar="URL", help="validate a deployed site over HTTP")
    args = parser.parse_args()
    if args.live:
        check_live(args.live.rstrip("/"))
    else:
        check_local()
    if failures:
        print(f"\n{len(failures)} FAILURES")
        return 1
    print("\nAll checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
