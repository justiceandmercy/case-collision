#!/usr/bin/env python3
"""Detect file and directory names that collide on case-insensitive filesystems."""

from __future__ import annotations

import argparse
import json
import os
import sys
import unicodedata
from pathlib import Path

SKIP_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
}

NAME = "case-collision"


def normalize_key(path: str) -> str:
    """Normalize a path for case-insensitive, Unicode-aware comparison."""
    return unicodedata.normalize("NFC", path).casefold()


def collect_paths(root: Path) -> list[str]:
    collected: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        relative_dir = os.path.relpath(dirpath, root)
        names = list(filenames) + list(dirnames)
        for name in names:
            if relative_dir == ".":
                collected.append(name)
            else:
                collected.append(os.path.join(relative_dir, name))
    # Normalize separators for stable output.
    return [path.replace(os.sep, "/") for path in collected]


def find_collisions(root: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for path in collect_paths(root):
        groups.setdefault(normalize_key(path), []).append(path)
    return {key: sorted(paths) for key, paths in groups.items() if len(paths) > 1}


def render_text(collisions: dict[str, list[str]]) -> str:
    if not collisions:
        return "No case collisions found."
    lines = ["Case-insensitive path collisions:"]
    for key in sorted(collisions):
        lines.append("")
        lines.append(f"group: {key}")
        for path in collisions[key]:
            lines.append(f"  {path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=NAME,
        description="Find paths that differ only by case or Unicode normalization.",
    )
    parser.add_argument("path", nargs="?", default=".", help="directory to scan")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true",
                        help="exit with status 1 when collisions are found")
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    collisions = find_collisions(root)

    if args.format == "json":
        payload = {
            "collisions": [
                {"key": key, "paths": paths}
                for key, paths in sorted(collisions.items())
            ]
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(collisions))

    if args.strict and collisions:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
