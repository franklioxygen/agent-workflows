#!/usr/bin/env python3
# Function Name: git_state, discover_skills, discover_workflows, suggested_validation_commands, missing_validation_commands, release_report, main
# Description: Collect release-prep facts for an agent-workflows library, including Git state when available, workflow files, bundled skills, and suggested validation commands.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from skill_common import WORKFLOW_FILES, find_agent_workflows_root, run_command  # noqa: E402


VALIDATION_COMMANDS = [
    (
        "skills/workflow-maintainer/scripts/audit_workflow_library.py",
        "python3 skills/workflow-maintainer/scripts/audit_workflow_library.py",
    ),
    (
        "skills/workflow-automation/scripts/find_workflow_library.py",
        "python3 skills/workflow-automation/scripts/find_workflow_library.py --json",
    ),
]


def git_state(root: Path) -> dict[str, object]:
    code, stdout, stderr = run_command(["git", "rev-parse", "--is-inside-work-tree"], root)
    if code != 0 or stdout != "true":
        return {
            "available": False,
            "reason": stderr or "not a git repository",
        }

    branch_code, branch, branch_err = run_command(["git", "branch", "--show-current"], root)
    status_code, status, status_err = run_command(["git", "status", "--short"], root)
    diff_code, diff, diff_err = run_command(["git", "diff", "--name-only"], root)
    staged_code, staged, staged_err = run_command(["git", "diff", "--cached", "--name-only"], root)

    return {
        "available": True,
        "branch": branch if branch_code == 0 else f"unknown: {branch_err}",
        "status": status.splitlines() if status_code == 0 and status else [],
        "unstaged_files": diff.splitlines() if diff_code == 0 and diff else [],
        "staged_files": staged.splitlines() if staged_code == 0 and staged else [],
        "errors": [err for err in [status_err, diff_err, staged_err] if err],
    }


def discover_skills(root: Path) -> list[str]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(path.name for path in skills_dir.iterdir() if (path / "SKILL.md").is_file())


def discover_workflows(root: Path) -> list[str]:
    return [rel_path for rel_path in WORKFLOW_FILES.values() if (root / rel_path).is_file()]


def suggested_validation_commands(root: Path) -> list[str]:
    return [command for rel_path, command in VALIDATION_COMMANDS if (root / rel_path).is_file()]


def missing_validation_commands(root: Path) -> list[str]:
    return [command for rel_path, command in VALIDATION_COMMANDS if not (root / rel_path).is_file()]


def release_report(root: Path) -> dict[str, object]:
    return {
        "root": str(root),
        "git": git_state(root),
        "workflows": discover_workflows(root),
        "skills": discover_skills(root),
        "suggested_validation": suggested_validation_commands(root),
        "missing_validation": missing_validation_commands(root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect release-prep facts for agent-workflows.")
    parser.add_argument(
        "root",
        nargs="?",
        default=None,
        help="Path to agent-workflows root. Defaults to auto-discovery.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else find_agent_workflows_root(Path.cwd(), __file__)
    if root is None:
        print("agent-workflows library not found", file=sys.stderr)
        return 1

    report = release_report(root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    print("agent-workflows release prep")
    print(f"root: {report['root']}")
    git = report["git"]
    if isinstance(git, dict) and git.get("available"):
        print(f"git branch: {git.get('branch')}")
        status = git.get("status") or []
        print(f"git changed entries: {len(status)}")
        for entry in status:
            print(f"  {entry}")
    else:
        reason = git.get("reason") if isinstance(git, dict) else "unknown"
        print(f"git unavailable: {reason}")

    print("workflows:")
    for workflow in report["workflows"]:
        print(f"  {workflow}")

    print("skills:")
    for skill in report["skills"]:
        print(f"  {skill}")

    print("suggested validation:")
    for command in report["suggested_validation"]:
        print(f"  {command}")
    missing_validation = report.get("missing_validation") or []
    if missing_validation:
        print("missing validation:")
        for command in missing_validation:
            print(f"  {command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
