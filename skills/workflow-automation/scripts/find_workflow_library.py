#!/usr/bin/env python3
# Function Name: is_library_root, find_workflow_library, build_manifest, main
# Description: Locate the agent-workflows library using environment-aware and script-relative discovery, then print the workflow file manifest.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from skill_common import SHARED_FILES, WORKFLOW_FILES, candidate_roots  # noqa: E402


def is_library_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    return all((path / rel_path).is_file() for rel_path in SHARED_FILES.values()) and all(
        (path / rel_path).is_file() for rel_path in WORKFLOW_FILES.values()
    )


def find_workflow_library(start: Path) -> Path | None:
    seen: set[Path] = set()

    for candidate in candidate_roots(start, __file__):
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if is_library_root(resolved):
            return resolved

    return None


def build_manifest(root: Path) -> dict[str, object]:
    return {
        "root": str(root),
        "shared": {name: str(root / rel_path) for name, rel_path in SHARED_FILES.items()},
        "workflows": {
            name: str(root / rel_path) for name, rel_path in WORKFLOW_FILES.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Locate an agent-workflows library and print its file manifest."
    )
    parser.add_argument(
        "--start",
        default=".",
        help="Start path for the search. Defaults to the current directory.",
    )
    parser.add_argument(
        "--workflow",
        choices=sorted(WORKFLOW_FILES),
        help="Print only the selected workflow file path.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the result as JSON.",
    )
    args = parser.parse_args()

    root = find_workflow_library(Path(args.start))
    if root is None:
        print("agent-workflows library not found", file=sys.stderr)
        return 1

    manifest = build_manifest(root)
    if args.workflow:
        result: object = manifest["workflows"][args.workflow]
    else:
        result = manifest

    if args.json or isinstance(result, dict):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
