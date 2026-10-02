#!/usr/bin/env python3
"""Build the 3MF viewer and trim dist/ in place to the minimal embedded set.

Runs `npm run build`, then strips dist/ down to only what the embedded viewer
needs at runtime - index.html, embed.js, and assets/ - deleting the demo pages,
sample models, logos, and the favicon (plus its <link> in index.html).

After it finishes, copy the contents of dist/ straight into parts/vendor/.
Run from anywhere:  python3 build.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent     # the 3mfViewer source dir
DIST = HERE / "dist"

# The only entries the embedded viewer actually needs. Everything else the build
# drops into dist/ (data/, *-demo.html, *.png, ...) gets removed. Keeping this as
# an allow-list means new demo/sample files can't sneak into the vendored copy.
KEEP = {"index.html", "embed.js", "assets"}


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
    print("\nDone. Copy the contents of dist/ into parts/vendor/.")


if __name__ == "__main__":
    build()
    trim()
    summary()
