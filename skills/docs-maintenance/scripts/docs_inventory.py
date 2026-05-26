#!/usr/bin/env python3
# Function Name: markdown_files, inspect_markdown, docs_inventory, print_inventory, main
# Description: Inventory Markdown documentation files, headings, links, and maintenance markers for docs-maintenance work.

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from skill_common import read_text_limited, should_skip_path  # noqa: E402

HEADING_RE = re.compile(r"^#+\s+")
LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
MARKER_RE = re.compile(r"\b(TODO|FIXME|TBD|XXX)\b")


def markdown_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".md" else []
    return sorted(path for path in root.rglob("*.md") if path.is_file() and not should_skip_path(path, script_file=__file__))


def inspect_markdown(path: Path, root: Path) -> dict[str, object]:
    try:
        text = read_text_limited(path)
    except ValueError as exc:
        return {
            "path": str(path.relative_to(root) if path.is_relative_to(root) else path),
            "lines": 0,
            "headings": 0,
            "links": 0,
            "markers": 0,
            "has_function_header": False,
            "skipped": str(exc),
        }
    lines = text.splitlines()
    return {
        "path": str(path.relative_to(root) if path.is_relative_to(root) else path),
        "lines": len(lines),
        "headings": sum(1 for line in lines if HEADING_RE.match(line)),
        "links": sum(len(LINK_RE.findall(line)) for line in lines),
        "markers": sum(len(MARKER_RE.findall(line)) for line in lines),
        "has_function_header": "Function Name:" in text and "Description:" in text,
        "skipped": "",
    }


def docs_inventory(root: Path) -> list[dict[str, object]]:
    base = root if root.is_dir() else root.parent
    return [inspect_markdown(path, base) for path in markdown_files(root)]


def print_inventory(items: list[dict[str, object]]) -> None:
    print("docs inventory")
    print(f"markdown files: {len(items)}")
    for item in items:
        if item.get("skipped"):
            print(f"{item['path']}: skipped, {item['skipped']}")
            continue
        header = "header" if item["has_function_header"] else "no-header"
        print(
            f"{item['path']}: {item['lines']} lines, "
            f"{item['headings']} headings, {item['links']} links, "
            f"{item['markers']} markers, {header}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory Markdown documentation files.")
    parser.add_argument("root", nargs="?", default=".", help="Documentation root to inspect.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"root not found: {root}", file=sys.stderr)
        return 1
    print_inventory(docs_inventory(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
