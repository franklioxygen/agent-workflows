#!/usr/bin/env python3
# Function Name: main, run_one_plan_item, load_task_manifest, build_run_plan, build_prompt, prepare_run_repo, run_validation_commands, run_claude_code, extract_claude_result_text, sanitize_agent_report, directory_diff, directory_status, write_blinded_artifact
# Description: Run real single-prompt and workflow-guided Claude Code evaluation tasks, capturing artifacts, sanitized agent reports, public validation, and locked evaluator checks for later blinded scoring.

from __future__ import annotations

import argparse
import difflib
import json
import random
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


HARNESS_VERSION = "claude-code-runner-0.2.0"
DEFAULT_CONDITIONS = ("single_prompt", "workflow_guided")
DEFAULT_ALLOWED_TOOLS = "Read,Edit,Write,Bash"
PROMPT_MODES = ("controlled", "workflow-lift")

WORKFLOW_BY_CATEGORY = {
    "bug-fix": "bug-fix-agent-workflow.md",
    "feature": "feature-development-agent-workflow.md",
    "refactor": "refactoring-agent-workflow.md",
    "incident": "incident-debugging-agent-workflow.md",
    "migration": "skills/migration-planning/SKILL.md",
}


def _run(
    command: list[str],
    *,
    cwd: Path,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(["git", "-C", str(repo), *args], cwd=repo)


def is_git_repo(repo: Path) -> bool:
    result = _git(repo, "rev-parse", "--is-inside-work-tree")
    if result.returncode != 0 or result.stdout.strip() != "true":
        return False
    top_level = _git(repo, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0:
        return False
    return Path(top_level.stdout.strip()).resolve() == repo.resolve()


def repo_sha(repo: Path) -> str:
    if not is_git_repo(repo):
        return "non-git"
    result = _git(repo, "rev-parse", "HEAD")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to read repo SHA")
    return result.stdout.strip()


def repo_is_dirty(repo: Path) -> bool:
    if not is_git_repo(repo):
        return False
    result = _git(repo, "status", "--porcelain")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to read git status")
    return bool(result.stdout.strip())


def command_to_text(command: str | list[str]) -> str:
    if isinstance(command, str):
        return command
    return shlex.join(str(part) for part in command)


def load_task_manifest(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list) or not tasks:
        raise ValueError(f"{path}: expected a non-empty tasks list")
    required = {"task_id", "category", "prompt", "acceptance_criteria", "validation_commands"}
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError(f"{path}: task {index} must be an object")
        missing = required - task.keys()
        if missing:
            raise ValueError(
                f"{path}: task {index} missing fields: {', '.join(sorted(missing))}"
            )
        if not isinstance(task["acceptance_criteria"], list) or not task["acceptance_criteria"]:
            raise ValueError(f"{path}: task {task['task_id']} has no acceptance criteria")
        if not isinstance(task["validation_commands"], list):
            raise ValueError(f"{path}: task {task['task_id']} validation_commands must be a list")
        if "hidden_validation_commands" in task and not isinstance(
            task["hidden_validation_commands"], list
        ):
            raise ValueError(
                f"{path}: task {task['task_id']} hidden_validation_commands must be a list"
            )
    return tasks


def build_run_plan(
    tasks: list[dict[str, Any]],
    *,
    runs_per_condition: int,
    conditions: tuple[str, ...],
    seed: int,
) -> list[dict[str, Any]]:
    plan = [
        {"task": task, "condition": condition, "run_id": run_id}
        for task in tasks
        for condition in conditions
        for run_id in range(1, runs_per_condition + 1)
    ]
    rng = random.Random(seed)
    rng.shuffle(plan)
    for index, item in enumerate(plan, start=1):
        item["run_order"] = index
    return plan


def workflow_path_for_task(task: dict[str, Any], workflow_root: Path) -> Path:
    rel_path = WORKFLOW_BY_CATEGORY.get(str(task["category"]))
    if rel_path is None:
        raise ValueError(
            f"no workflow mapping for category {task['category']!r}; "
            f"known categories: {', '.join(sorted(WORKFLOW_BY_CATEGORY))}"
        )
    return workflow_root / rel_path


def _criteria_text(task: dict[str, Any]) -> str:
    return "\n".join(
        f"{index}. {criterion}"
        for index, criterion in enumerate(task["acceptance_criteria"], start=1)
    )


def _validation_text(task: dict[str, Any]) -> str:
    return "\n".join(
        f"- {command_to_text(command)}" for command in task["validation_commands"]
    )


def build_prompt(
    task: dict[str, Any],
    *,
    condition: str,
    workflow_root: Path,
    prompt_mode: str = "controlled",
) -> str:
    if prompt_mode not in PROMPT_MODES:
        raise ValueError(f"unknown prompt mode: {prompt_mode}")
    shared = (
        f"Task id: {task['task_id']}\n"
        f"Category: {task['category']}\n"
        f"Difficulty: {task.get('difficulty', 'unspecified')}\n\n"
        f"Task:\n{task['prompt']}\n\n"
        f"Acceptance criteria:\n{_criteria_text(task)}\n\n"
        f"Validation commands to run before finishing:\n{_validation_text(task)}\n\n"
        "Work only in the current repository checkout. Make the smallest change that "
        "satisfies the acceptance criteria. Do not commit. At the end, summarize the "
        "files changed and validation evidence."
    )
    if prompt_mode == "workflow-lift":
        issue_prompt = str(task.get("single_prompt", task.get("brief_prompt", task["prompt"])))
        single_shared = (
            f"Task id: {task['task_id']}\n"
            f"Category: {task['category']}\n"
            f"Difficulty: {task.get('difficulty', 'unspecified')}\n\n"
            f"Issue report:\n{issue_prompt}\n\n"
            f"Validation commands to run before finishing:\n{_validation_text(task)}\n\n"
            "Work only in the current repository checkout. Make the smallest scoped "
            "change that addresses the issue report. Do not read or use workflow "
            "documents. Do not commit. At the end, summarize the files changed and "
            "validation evidence."
        )
        workflow_shared = (
            f"Task id: {task['task_id']}\n"
            f"Category: {task['category']}\n"
            f"Difficulty: {task.get('difficulty', 'unspecified')}\n\n"
            f"Issue report:\n{issue_prompt}\n\n"
            f"Acceptance criteria:\n{_criteria_text(task)}\n\n"
            f"Validation commands to run before finishing:\n{_validation_text(task)}\n\n"
            "Work only in the current repository checkout. Follow the workflow's "
            "diagnosis, implementation, validation, and final-report expectations. "
            "Do not commit. At the end, include a Requirements Traceability section "
            "mapping every acceptance criterion to the file/function changed and the "
            "test or command that validates it."
        )
        if condition == "single_prompt":
            return (
                "You are running the single_prompt evaluation condition.\n\n"
                f"{single_shared}"
            )
        if condition == "workflow_guided":
            workflow_path = workflow_path_for_task(task, workflow_root)
            return (
                "You are running the workflow_guided evaluation condition. Read and follow "
                f"this workflow before editing: {workflow_path}\n\n"
                f"{workflow_shared}"
            )
        raise ValueError(f"unknown condition: {condition}")
    if condition == "single_prompt":
        return (
            "You are running the single_prompt evaluation condition. Do not read or "
            "use the agent-workflows workflow documents for this run.\n\n"
            f"{shared}"
        )
    if condition == "workflow_guided":
        workflow_path = workflow_path_for_task(task, workflow_root)
        return (
            "You are running the workflow_guided evaluation condition. Read and follow "
            f"this workflow before editing: {workflow_path}\n\n"
            f"{shared}"
        )
    raise ValueError(f"unknown condition: {condition}")


def prepare_run_repo(
    source_repo: Path,
    destination: Path,
    *,
    allow_dirty_source: bool,
) -> str:
    if destination.exists():
        raise FileExistsError(f"run repository already exists: {destination}")
    if is_git_repo(source_repo):
        if repo_is_dirty(source_repo) and not allow_dirty_source:
            raise RuntimeError(
                f"{source_repo} has uncommitted changes; pass --allow-dirty-source "
                "only for exploratory runs"
            )
        sha = repo_sha(source_repo)
        result = _run(
            ["git", "clone", "--quiet", "--no-hardlinks", str(source_repo), str(destination)],
            cwd=source_repo,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "git clone failed")
        checkout = _git(destination, "checkout", "--quiet", sha)
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr.strip() or "git checkout failed")
        return sha
    shutil.copytree(source_repo, destination)
    return "non-git"


def claude_version(claude_bin: str) -> str:
    result = _run([claude_bin, "--version"], cwd=Path.cwd())
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def run_claude_code(
    *,
    claude_bin: str,
    prompt: str,
    repo_dir: Path,
    workflow_root: Path,
    condition: str,
    model: str,
    allowed_tools: str,
    permission_mode: str,
    max_budget_usd: str | None,
    timeout_seconds: int,
) -> tuple[subprocess.CompletedProcess[str] | None, float, bool]:
    command = [
        claude_bin,
        "-p",
        prompt,
        "--output-format",
        "json",
        "--model",
        model,
        "--permission-mode",
        permission_mode,
        "--allowedTools",
        allowed_tools,
        "--no-session-persistence",
    ]
    if condition == "workflow_guided":
        command.extend(["--add-dir", str(workflow_root)])
    if max_budget_usd:
        command.extend(["--max-budget-usd", max_budget_usd])
    started = time.monotonic()
    try:
        result = _run(command, cwd=repo_dir, timeout=timeout_seconds)
        return result, time.monotonic() - started, False
    except subprocess.TimeoutExpired as exc:
        timed_out = subprocess.CompletedProcess(
            command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "Claude Code timed out",
        )
        return timed_out, time.monotonic() - started, True


def run_validation_commands(
    repo_dir: Path,
    commands: list[str | list[str]],
    *,
    timeout_seconds: int,
) -> tuple[bool, str, list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    log_parts: list[str] = []
    all_passed = True
    for command in commands:
        command_text = command_to_text(command)
        started = time.monotonic()
        try:
            result = subprocess.run(
                command_text,
                cwd=repo_dir,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            result = subprocess.CompletedProcess(
                command_text,
                returncode=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "validation command timed out",
            )
            timed_out = True
        duration = time.monotonic() - started
        passed = result.returncode == 0
        all_passed = all_passed and passed
        records.append(
            {
                "command": command_text,
                "exit_code": result.returncode,
                "duration_seconds": duration,
                "timed_out": timed_out,
            }
        )
        log_parts.extend(
            [
                f"$ {command_text}",
                f"exit_code={result.returncode} duration_seconds={duration:.3f}",
                "--- stdout ---",
                result.stdout or "",
                "--- stderr ---",
                result.stderr or "",
                "",
            ]
        )
    return all_passed, "\n".join(log_parts), records


def extract_claude_result_text(stdout_text: str) -> str:
    if not stdout_text.strip():
        return ""
    try:
        payload = json.loads(stdout_text)
    except json.JSONDecodeError:
        return stdout_text.strip()
    result = payload.get("result")
    if isinstance(result, str):
        return result.strip()
    return stdout_text.strip()


def sanitize_agent_report(report: str, *, workflow_root: Path) -> str:
    replacements = {
        str(workflow_root): "[workflow-root]",
        "workflow_guided": "[condition]",
        "single_prompt": "[condition]",
        "bug-fix-agent-workflow.md": "[process-document]",
        "feature-development-agent-workflow.md": "[process-document]",
        "refactoring-agent-workflow.md": "[process-document]",
        "incident-debugging-agent-workflow.md": "[process-document]",
        "skills/migration-planning/SKILL.md": "[process-document]",
    }
    sanitized = report
    for needle, replacement in replacements.items():
        sanitized = sanitized.replace(needle, replacement)
    return sanitized.strip()


def _relative_files(root: Path) -> set[Path]:
    ignored_parts = {".git", "__pycache__", ".pytest_cache"}
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in ignored_parts for part in path.relative_to(root).parts)
        and path.suffix != ".pyc"
    }


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def directory_diff(before_dir: Path, after_dir: Path) -> str:
    lines: list[str] = []
    all_files = sorted(_relative_files(before_dir) | _relative_files(after_dir))
    for rel_path in all_files:
        before_path = before_dir / rel_path
        after_path = after_dir / rel_path
        before_exists = before_path.exists()
        after_exists = after_path.exists()
        before_text = _read_text(before_path) if before_exists else ""
        after_text = _read_text(after_path) if after_exists else ""
        if before_text is None or after_text is None:
            if before_exists != after_exists or before_path.read_bytes() != after_path.read_bytes():
                lines.append(f"Binary files differ: {rel_path}")
            continue
        if before_text == after_text:
            continue
        before_lines = before_text.splitlines(keepends=True)
        after_lines = after_text.splitlines(keepends=True)
        lines.extend(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"a/{rel_path}",
                tofile=f"b/{rel_path}",
            )
        )
    return "".join(lines) if lines else "No file changes.\n"


def directory_status(before_dir: Path, after_dir: Path) -> str:
    lines: list[str] = []
    before_files = _relative_files(before_dir)
    after_files = _relative_files(after_dir)
    for rel_path in sorted(after_files - before_files):
        lines.append(f"A  {rel_path}")
    for rel_path in sorted(before_files - after_files):
        lines.append(f"D  {rel_path}")
    for rel_path in sorted(before_files & after_files):
        if (before_dir / rel_path).read_bytes() != (after_dir / rel_path).read_bytes():
            lines.append(f"M  {rel_path}")
    return "\n".join(lines) + ("\n" if lines else "")


def git_diff(repo_dir: Path, *, baseline_dir: Path | None = None) -> str:
    if not is_git_repo(repo_dir):
        if baseline_dir is None:
            return "diff unavailable: run repository is not a git repository\n"
        return directory_diff(baseline_dir, repo_dir)
    result = _git(repo_dir, "diff", "--binary")
    return result.stdout if result.returncode == 0 else result.stderr


def git_status(repo_dir: Path, *, baseline_dir: Path | None = None) -> str:
    if not is_git_repo(repo_dir):
        if baseline_dir is None:
            return "status unavailable: run repository is not a git repository\n"
        return directory_status(baseline_dir, repo_dir)
    result = _git(repo_dir, "status", "--short")
    return result.stdout if result.returncode == 0 else result.stderr


def write_blinded_artifact(
    *,
    task: dict[str, Any],
    blinded_path: Path,
    diff_text: str,
    validation_log: str,
    agent_report: str,
) -> None:
    text = (
        f"# Blinded Artifact: {task['task_id']}\n\n"
        f"## Task\n\n{task['prompt']}\n\n"
        f"## Acceptance Criteria\n\n{_criteria_text(task)}\n\n"
        f"## Validation Commands\n\n{_validation_text(task)}\n\n"
        "## Diff\n\n"
        "```diff\n"
        f"{diff_text}\n"
        "```\n\n"
        "## Validation Log\n\n"
        "```text\n"
        f"{validation_log}\n"
        "```\n"
        "\n## Agent Report\n\n"
        "```text\n"
        f"{agent_report or 'No final report captured.'}\n"
        "```\n"
    )
    blinded_path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def run_one_plan_item(
    item: dict[str, Any],
    *,
    args: argparse.Namespace,
    source_repo: Path,
    workflow_root: Path,
    output_dir: Path,
    env: dict[str, Any],
) -> dict[str, Any]:
    task = item["task"]
    condition = item["condition"]
    run_id = int(item["run_id"])
    run_order = int(item["run_order"])
    safe_task_id = str(task["task_id"]).replace("/", "_")
    run_dir = output_dir / "runs" / f"{run_order:04d}_{safe_task_id}_{condition}_run{run_id}"
    repo_dir = run_dir / "repo"
    artifact_dir = run_dir / "artifact"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    locked_sha = prepare_run_repo(
        source_repo, repo_dir, allow_dirty_source=args.allow_dirty_source
    )
    baseline_dir: Path | None = None
    if not is_git_repo(repo_dir):
        baseline_dir = run_dir / "baseline"
        shutil.copytree(repo_dir, baseline_dir)
    prompt = build_prompt(
        task,
        condition=condition,
        workflow_root=workflow_root,
        prompt_mode=args.prompt_mode,
    )
    (artifact_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    if args.dry_run:
        claude_result = subprocess.CompletedProcess([], 0, "", "dry run\n")
        claude_seconds = 0.0
        claude_timed_out = False
    else:
        claude_result, claude_seconds, claude_timed_out = run_claude_code(
            claude_bin=args.claude_bin,
            prompt=prompt,
            repo_dir=repo_dir,
            workflow_root=workflow_root,
            condition=condition,
            model=args.model,
            allowed_tools=args.allowed_tools,
            permission_mode=args.permission_mode,
            max_budget_usd=args.max_budget_usd,
            timeout_seconds=args.time_budget_seconds,
        )

    (artifact_dir / "claude.stdout.json").write_text(
        claude_result.stdout or "", encoding="utf-8"
    )
    (artifact_dir / "claude.stderr.txt").write_text(
        claude_result.stderr or "", encoding="utf-8"
    )
    agent_report = sanitize_agent_report(
        extract_claude_result_text(claude_result.stdout or ""),
        workflow_root=workflow_root,
    )
    (artifact_dir / "agent_report.txt").write_text(agent_report, encoding="utf-8")

    public_validation_passed, public_validation_log, public_validation_records = run_validation_commands(
        repo_dir,
        task["validation_commands"],
        timeout_seconds=args.validation_timeout_seconds,
    )
    hidden_commands = task.get("hidden_validation_commands", [])
    if hidden_commands:
        hidden_validation_passed, hidden_validation_log, hidden_validation_records = (
            run_validation_commands(
                repo_dir,
                hidden_commands,
                timeout_seconds=args.validation_timeout_seconds,
            )
        )
    else:
        hidden_validation_passed = True
        hidden_validation_log = "No locked evaluator checks declared.\n"
        hidden_validation_records = []
    validation_passed = public_validation_passed and hidden_validation_passed
    validation_records = [
        {**record, "visibility": "public"} for record in public_validation_records
    ] + [{**record, "visibility": "locked_evaluator"} for record in hidden_validation_records]
    validation_log = (
        "## Public validation commands\n\n"
        f"{public_validation_log}\n"
        "## Locked evaluator checks\n\n"
        f"{hidden_validation_log}"
    )
    diff_text = git_diff(repo_dir, baseline_dir=baseline_dir)
    status_text = git_status(repo_dir, baseline_dir=baseline_dir)
    (artifact_dir / "validation.log").write_text(validation_log, encoding="utf-8")
    (artifact_dir / "diff.patch").write_text(diff_text, encoding="utf-8")
    (artifact_dir / "status.txt").write_text(status_text, encoding="utf-8")

    blinded_path = output_dir / "blinded" / f"run-{run_order:04d}.md"
    blinded_path.parent.mkdir(parents=True, exist_ok=True)
    write_blinded_artifact(
        task=task,
        blinded_path=blinded_path,
        diff_text=diff_text,
        validation_log=validation_log,
        agent_report=agent_report,
    )

    metadata = {
        "task_id": task["task_id"],
        "condition": condition,
        "workflow": (
            WORKFLOW_BY_CATEGORY.get(str(task["category"]))
            if condition == "workflow_guided"
            else None
        ),
        "run_id": run_id,
        "run_order": run_order,
        "source_repo_sha": locked_sha,
        "claude_exit_code": claude_result.returncode,
        "claude_timed_out": claude_timed_out,
        "claude_duration_seconds": claude_seconds,
        "validation_passed": validation_passed,
        "public_validation_passed": public_validation_passed,
        "hidden_validation_passed": hidden_validation_passed,
        "validation": validation_records,
        "artifact_path": str(artifact_dir),
        "blinded_artifact_path": str(blinded_path),
    }
    (artifact_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )

    row = {
        "task_id": task["task_id"],
        "condition": condition,
        "workflow": metadata["workflow"],
        "run_id": run_id,
        "run_order": run_order,
        "env": {**env, "repo_sha": locked_sha},
        "artifact_path": str(artifact_dir),
        "blinded_artifact_path": str(blinded_path),
        "validation_passed": validation_passed,
        "public_validation_passed": public_validation_passed,
        "hidden_validation_passed": hidden_validation_passed,
        "cycle_time_seconds": claude_seconds,
        "claude_exit_code": claude_result.returncode,
        "claude_timed_out": claude_timed_out,
        "needs_blinded_scoring": True,
    }
    append_jsonl(output_dir / "runs.jsonl", row)
    return row


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run real Claude Code evaluation tasks and capture artifacts for blinded scoring."
    )
    parser.add_argument("tasks", help="Task manifest JSON file.")
    parser.add_argument("--repo", required=True, help="Target repository to evaluate.")
    parser.add_argument(
        "--workflow-root",
        default=str(Path(__file__).resolve().parents[2]),
        help="agent-workflows repository root used for workflow_guided runs.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where run artifacts and runs.jsonl will be written.",
    )
    parser.add_argument("--runs-per-condition", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260528)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--claude-bin", default="claude")
    parser.add_argument("--allowed-tools", default=DEFAULT_ALLOWED_TOOLS)
    parser.add_argument("--permission-mode", default="bypassPermissions")
    parser.add_argument("--max-budget-usd", default=None)
    parser.add_argument("--time-budget-seconds", type=int, default=1800)
    parser.add_argument("--validation-timeout-seconds", type=int, default=600)
    parser.add_argument("--prompt-template-version", default="claude-code-runner-v1")
    parser.add_argument(
        "--prompt-mode",
        choices=PROMPT_MODES,
        default="controlled",
        help=(
            "controlled keeps both conditions on the same task and acceptance criteria; "
            "workflow-lift compares a terse single prompt against workflow-guided execution "
            "with the full criteria and final-report expectations."
        ),
    )
    parser.add_argument(
        "--conditions",
        default=",".join(DEFAULT_CONDITIONS),
        help="Comma-separated conditions to run.",
    )
    parser.add_argument(
        "--allow-dirty-source",
        action="store_true",
        help="Allow cloning a source repository with uncommitted changes. Exploratory only.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create run repositories and artifacts without invoking Claude Code.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    tasks_path = Path(args.tasks).resolve()
    source_repo = Path(args.repo).resolve()
    workflow_root = Path(args.workflow_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    conditions = tuple(
        condition.strip() for condition in args.conditions.split(",") if condition.strip()
    )
    unknown = sorted(set(conditions) - set(DEFAULT_CONDITIONS))
    if unknown:
        print(f"unknown condition(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    if args.runs_per_condition < 1:
        print("--runs-per-condition must be >= 1", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)

    tasks = load_task_manifest(tasks_path)
    plan = build_run_plan(
        tasks,
        runs_per_condition=args.runs_per_condition,
        conditions=conditions,
        seed=args.seed,
    )
    env = {
        "model_provider": "anthropic",
        "model_id": args.model,
        "model_parameters": {
            "permission_mode": args.permission_mode,
            "allowed_tools": args.allowed_tools,
            "max_budget_usd": args.max_budget_usd,
            "claude_code_version": claude_version(args.claude_bin),
            "prompt_mode": args.prompt_mode,
        },
        "repo_sha": repo_sha(source_repo),
        "tool_access": [tool.strip() for tool in args.allowed_tools.split(",")],
        "time_budget_seconds": args.time_budget_seconds,
        "prompt_template_version": args.prompt_template_version,
        "agent_harness_version": HARNESS_VERSION,
        "kit_version": "2.1.0",
    }
    (output_dir / "run_plan.json").write_text(
        json.dumps(
            [
                {
                    "task_id": item["task"]["task_id"],
                    "condition": item["condition"],
                    "run_id": item["run_id"],
                    "run_order": item["run_order"],
                }
                for item in plan
            ],
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    for item in plan:
        row = run_one_plan_item(
            item,
            args=args,
            source_repo=source_repo,
            workflow_root=workflow_root,
            output_dir=output_dir,
            env=env,
        )
        print(
            f"run_order={row['run_order']} task={row['task_id']} "
            f"condition={row['condition']} validation_passed={row['validation_passed']}"
        )

    print(f"\nWrote run artifacts to: {output_dir}")
    print("Next: have blinded raters score output_dir/blinded/*.md using evaluation/RUBRIC.md.")
    print("Do not feed runs.jsonl directly to summarize_results.py; it is not adjudicated results.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
