#!/usr/bin/env python3
# Function Name: performance_signal_scan, main
# Description: Scan source files for common performance-risk signals to guide manual performance review.

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from signal_scan import build_signal_report, print_signal_report  # noqa: E402
from skill_common import BROAD_TEXT_EXTENSIONS  # noqa: E402


PATTERNS = [
    ("possible unbounded query", re.compile(r"(?i)(\bselect\s+\*|\bfindAll\(|\ball\(\)|\bscan\(|\blimit\s*:\s*undefined\b)")),
    ("query or request in loop", re.compile(r"(?i)\b(for|while|foreach|map)\b.*\b(query|fetch|axios|requests\.|http\.|execute)\b")),
    ("synchronous io", re.compile(r"\b(readFileSync|writeFileSync|sleep\(|time\.sleep|Thread\.sleep)\b")),
    ("large in-memory operation", re.compile(r"(?i)\b(readlines\(|toArray\(|collect\(|JSON\.parse|json\.loads|sort\(|sorted\()\b")),
    ("cache signal", re.compile(r"(?i)\b(cache|memoize|lru|redis|ttl)\b")),
    ("pagination signal", re.compile(r"(?i)\b(offset|cursor|pageSize|limit|pagination)\b")),
]


def performance_signal_scan(target: Path) -> dict[str, object]:
    skill_root = Path(__file__).resolve().parents[1]
    return build_signal_report(target, PATTERNS, BROAD_TEXT_EXTENSIONS, __file__, {skill_root})


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan files for performance-review signals.")
    parser.add_argument("target", nargs="?", default=".", help="File or directory to scan.")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target not found: {target}", file=sys.stderr)
        return 1
    print_signal_report(
        "performance signal scan",
        performance_signal_scan(target),
        "note: signals are non-exhaustive line-based review prompts, not confirmed performance defects; source comments are skipped, but strings and docs may still match",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
