#!/usr/bin/env python3
# Function Name: migration_signal_scan, main
# Description: Scan files for migration-related signals that require migration-planning review.

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
    ("destructive schema change", re.compile(r"(?i)\b(drop|truncate|delete\s+from|alter\s+table.*drop|drop\s+column)\b")),
    ("schema migration", re.compile(r"(?i)\b(create\s+table|alter\s+table|add\s+column|create\s+index|migration|migrate)\b")),
    ("data backfill", re.compile(r"(?i)\b(backfill|data migration|batch update|reindex|recompute)\b")),
    ("contract versioning", re.compile(r"(?i)\b(api[_-]?version|v[0-9]+/|deprecated|deprecation|compatibility)\b")),
    ("api breaking change", re.compile(r"(?i)\b(remove|rename|delete|required)\b.*\b(endpoint|route|api|field|parameter|param|property)\b")),
    ("configuration contract", re.compile(r"(?i)\b(env var|environment variable|config|setting|settings|helm|terraform|cloudformation)\b")),
    ("queue or event schema", re.compile(r"(?i)\b(queue|topic|event|message|schema|consumer|producer|kafka|sqs|pubsub|rabbitmq)\b")),
    ("feature flag", re.compile(r"(?i)\b(feature[_-]?flag|flagged|rollout|kill switch)\b")),
]


def migration_signal_scan(target: Path) -> dict[str, object]:
    skill_root = Path(__file__).resolve().parents[1]
    return build_signal_report(target, PATTERNS, BROAD_TEXT_EXTENSIONS, __file__, {skill_root})


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan files for migration-planning signals.")
    parser.add_argument("target", nargs="?", default=".", help="File or directory to scan.")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target not found: {target}", file=sys.stderr)
        return 1
    print_signal_report(
        "migration signal scan",
        migration_signal_scan(target),
        "note: signals are non-exhaustive line-based migration-planning prompts, not confirmed risks; source comments are skipped, but strings and docs may still match",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
