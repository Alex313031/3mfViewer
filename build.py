#!/usr/bin/env python3
"""Build the 3MF viewer and trim dist/ in place to the minimal embedded set.

Runs `npm run build`, then strips dist/ down to only what the embedded viewer
needs at runtime - index.html, embed.js, and assets/ - deleting the demo pages,
sample models, logos, and the favicon (plus its <link> in index.html).

By default it leaves the trimmed output in dist/; pass -d/--dist to also copy it
into the directory above this script (the vendored viewer location, e.g.
parts/vendor/) - build, minify, and deploy in one swoop.
Run from anywhere:  python3 build.py [-d|--dist]
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent     # the 3mfViewer source dir
DIST = HERE / "dist"

# The only entries the embedded viewer actually needs: the app, the embed loader,
# the hashed asset bundle, and 3mf_logo.png (the viewer UI / preview-bar logo,
# referenced relatively so it resolves under the vendored subpath). Everything
# else the build drops into dist/ (data/, *-demo.html, the favicon, demo images)
# is removed. Allow-list so new demo/sample files can't sneak in.
KEEP = {"index.html", "embed.js", "assets", "3mf_logo.png"}


def build() -> None:
    print("==> npm run build")
    subprocess.run(["npm", "run", "build"], cwd=HERE, check=True)


def trim() -> None:
    if not DIST.is_dir():
        sys.exit(f"!! no dist/ at {DIST} - did the build fail?")
    print(f"==> trimming {DIST.name}/ to {sorted(KEEP)}")
    for entry in sorted(DIST.iterdir()):
        if entry.name in KEEP:
            continue
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
        print(f"    removed {entry.name}")
    strip_favicon(DIST / "index.html")


def strip_favicon(index_html: Path) -> None:
    """Drop the <link rel="icon" ...> line (its target png is being removed)."""
    html = index_html.read_text(encoding="utf-8")
    # anchor to the line and only eat its own trailing newline (not the next
    # line's indentation), so the surrounding markup keeps its formatting.
    trimmed = re.sub(
        r'^[ \t]*<link\b[^>]*\brel=["\']icon["\'][^>]*>[ \t]*\r?\n?',
        "", html, flags=re.MULTILINE,
    )
    if trimmed != html:
        index_html.write_text(trimmed, encoding="utf-8")
        print("    removed <link rel=icon> from index.html")
    else:
        print("    (no <link rel=icon> in index.html - nothing to strip)")


def summary() -> None:
    files = sorted(p for p in DIST.rglob("*") if p.is_file())
    total = sum(p.stat().st_size for p in files)
    print(f"==> dist/ now holds {len(files)} files, {total / 1_048_576:.1f} MB:")
    for p in files:
        print(f"    {p.relative_to(DIST)}")


def deploy() -> None:
    """Copy the trimmed dist/ into the directory above this script (the vendored
    viewer location, e.g. parts/vendor/), replacing the previous copy. Only the
    dist entries are touched, so sibling dirs (like this source tree) are left alone."""
    dest = HERE.parent
    print(f"==> deploying dist/ -> {dest}")
    for item in sorted(DIST.iterdir()):
        target = dest / item.name
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif target.exists() or target.is_symlink():
            target.unlink()
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
        print(f"    {item.name} -> {target}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Build the 3MF viewer and trim dist/ to the minimal embedded set."
    )
    parser.add_argument(
        "-d", "--dist", action="store_true",
        help="after building + trimming, also copy dist/ into the directory above "
             "this script (the vendored viewer location) - build, minify, deploy in one go",
    )
    args = parser.parse_args()

    build()
    trim()
    summary()
    if args.dist:
        deploy()
        print(f"\nDone. Built, trimmed, and deployed to {HERE.parent}.")
    else:
        print(f"\nDone. Run with -d/--dist to also copy dist/ into {HERE.parent}.")
