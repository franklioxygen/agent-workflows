#!/usr/bin/env python3
# Function Name: markdown_link_targets, check_required_files, check_markdown_links, skill_directories, check_skill_metadata, check_readme_inventory, run_audit, print_report, main
# Description: Audit an agent-workflows library for required files, broken Markdown links, stale README inventory entries, and bundled skill metadata drift.

from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from skill_common import (  # noqa: E402
    SHARED_FILES,
    WORKFLOW_FILES,
    collect_markdown_anchors,
    find_agent_workflows_root,
    is_support_skill_dir,
    parse_frontmatter,
    read_text_limited,
)

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def markdown_link_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("mailto:"):
            continue
        file_part = target.partition("#")[0]
        if not file_part:
            continue
        normalized = posixpath.normpath(file_part)
        if file_part.endswith("/") and not normalized.endswith("/"):
            normalized += "/"
        targets.add(normalized)
    return targets


def check_required_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel_path in [*SHARED_FILES.values(), *WORKFLOW_FILES.values()]:
        if not (root / rel_path).is_file():
            errors.append(f"Missing required file: {rel_path}")
    return errors


def check_markdown_links(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        try:
            text = read_text_limited(path)
        except ValueError as exc:
            errors.append(f"{rel} skipped oversized Markdown file: {exc}")
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for target in LINK_RE.findall(line):
                if "://" in target or target.startswith("mailto:"):
                    continue
                file_part, _, fragment = target.partition("#")
                target_path = path if not file_part else (path.parent / file_part).resolve()
                if file_part and not target_path.exists():
                    errors.append(f"{rel}:{line_number} missing link target: {target}")
                    continue
                if fragment and target_path.suffix == ".md":
                    try:
                        anchors = collect_markdown_anchors(target_path)
                    except ValueError as exc:
                        errors.append(f"{rel}:{line_number} skipped oversized link target {target}: {exc}")
                        continue
                    if fragment not in anchors:
                        errors.append(f"{rel}:{line_number} missing anchor in {target}: #{fragment}")
    return errors


def skill_directories(root: Path) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(path for path in skills_dir.iterdir() if path.is_dir() and not is_support_skill_dir(path))


def check_skill_metadata(root: Path) -> list[str]:
    errors: list[str] = []
    for skill_dir in skill_directories(root):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"Missing skill file: skills/{skill_dir.name}/SKILL.md")
            continue

        try:
            metadata = parse_frontmatter(skill_file)
        except ValueError as exc:
            errors.append(f"Skill metadata skipped for skills/{skill_dir.name}/SKILL.md: {exc}")
            continue
        if metadata.get("name") != skill_dir.name:
            errors.append(f"Skill name mismatch in skills/{skill_dir.name}/SKILL.md")
        description = metadata.get("description", "")
        if not description or "TODO" in description:
            errors.append(f"Missing usable skill description in skills/{skill_dir.name}/SKILL.md")

        interface_file = skill_dir / "agents" / "interface.yaml"
        if not interface_file.is_file():
            errors.append(f"Missing agent metadata: skills/{skill_dir.name}/agents/interface.yaml")
        else:
            try:
                interface_text = read_text_limited(interface_file)
            except ValueError as exc:
                errors.append(f"agents/interface.yaml for {skill_dir.name} skipped: {exc}")
                continue
            if f"${skill_dir.name}" not in interface_text:
                errors.append(f"agents/interface.yaml for {skill_dir.name} should mention ${skill_dir.name}")

        for legacy_name in ["openai.yaml", "claude.yaml"]:
            legacy_file = skill_dir / "agents" / legacy_name
            if legacy_file.exists():
                errors.append(f"Remove legacy agent metadata: skills/{skill_dir.name}/agents/{legacy_name}")
    return errors


def check_readme_inventory(root: Path) -> list[str]:
    errors: list[str] = []
    readme = root / "README.md"
    if not readme.is_file():
        return ["Missing README.md"]

    try:
        text = read_text_limited(readme)
    except ValueError as exc:
        return [f"README.md skipped: {exc}"]
    link_targets = markdown_link_targets(text)
    for rel_path in [*WORKFLOW_FILES.values(), *SHARED_FILES.values()]:
        if rel_path != "README.md" and rel_path not in link_targets:
            errors.append(f"README.md does not mention {rel_path}")

    for skill_dir in skill_directories(root):
        if f"skills/{skill_dir.name}/" not in link_targets:
            errors.append(f"README.md does not mention skills/{skill_dir.name}/")
    return errors


def run_audit(root: Path) -> dict[str, list[str]]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if root.name != "agent-workflows":
        warnings.append(f"Audit target is not named agent-workflows: {root}")
    if not root.is_dir():
        return {"errors": [f"Audit target is not a directory: {root}"], "warnings": warnings}

    errors.extend(check_required_files(root))
    errors.extend(check_markdown_links(root))
    errors.extend(check_skill_metadata(root))
    errors.extend(check_readme_inventory(root))
    return {"errors": errors, "warnings": warnings}


def print_report(report: dict[str, list[str]]) -> None:
    errors = report["errors"]
    warnings = report["warnings"]

    print("agent-workflows audit")
    print(f"errors: {len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")

    print(f"warnings: {len(warnings)}")
    for warning in warnings:
        print(f"WARNING: {warning}")

    if not errors:
        print("status: passed")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an agent-workflows library.")
    parser.add_argument(
        "root",
        nargs="?",
        default=None,
        help="Path to the agent-workflows library root. Defaults to auto-discovery.",
    )
    args = parser.parse_args()

    if args.root is None:
        root = find_agent_workflows_root(Path.cwd(), __file__)
        if root is None:
            print("agent-workflows library not found", file=sys.stderr)
            return 1
    else:
        root = Path(args.root)

    report = run_audit(root)
    print_report(report)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
