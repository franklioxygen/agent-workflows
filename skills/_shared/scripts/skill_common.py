#!/usr/bin/env python3
# Function Name: candidate_roots, find_agent_workflows_root, run_command, github_anchor, read_text_limited, parse_frontmatter, collect_markdown_anchors, should_skip_path, is_support_skill_dir
# Description: Shared filesystem, bounded text-reading, Markdown, Git, and discovery helpers reused by agent-workflows bundled skill scripts.

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


WORKFLOW_FILES = {
    "project-initialization": "project-initialization-agent-workflow.md",
    "feature": "feature-development-agent-workflow.md",
    "bug-fix": "bug-fix-agent-workflow.md",
    "code-review": "code-review-agent-workflow.md",
    "incident": "incident-debugging-agent-workflow.md",
    "refactoring": "refactoring-agent-workflow.md",
    "tech-debt": "tech-debt-cleanup-agent-workflow.md",
}

SHARED_FILES = {
    "readme": "README.md",
    "preflight": "shared/repository-preflight.md",
    "safety_rules": "shared/safety-rules.md",
    "workflow_conventions": "shared/workflow-conventions.md",
}

DEFAULT_SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}

BROAD_TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cfg",
    ".conf",
    ".cpp",
    ".cs",
    ".css",
    ".env",
    ".go",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".kt",
    ".md",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".sql",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

MAX_TEXT_FILE_BYTES = 2 * 1024 * 1024
HEADING_RE = re.compile(r"^(#+)\s+(.+?)\s*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def candidate_roots(start: Path, script_file: str | None = None) -> list[Path]:
    candidates: list[Path] = []
    env_root = os.environ.get("AGENT_WORKFLOWS_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser())

    if script_file:
        script_path = Path(script_file).resolve()
        candidates.extend(parent for parent in script_path.parents if parent.name == "agent-workflows")

    current = start.resolve()
    if current.is_file():
        current = current.parent
    for path in [current, *current.parents]:
        if path.name == "agent-workflows":
            candidates.append(path)
        candidates.append(path / "agent-workflows")
    return candidates


def find_agent_workflows_root(start: Path, script_file: str | None = None) -> Path | None:
    seen: set[Path] = set()
    for candidate in candidate_roots(start, script_file):
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / "README.md").is_file() and all(
            (resolved / rel_path).is_file() for rel_path in WORKFLOW_FILES.values()
        ):
            return resolved
    return None


def run_command(args: list[str], cwd: Path) -> tuple[int, str, str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def github_anchor(heading: str) -> str:
    anchor = re.sub(r"[^a-z0-9\s-]", "", heading.lower())
    return re.sub(r"\s+", "-", anchor).strip("-")


def read_text_limited(path: Path, max_bytes: int = MAX_TEXT_FILE_BYTES) -> str:
    size = path.stat().st_size
    if size > max_bytes:
        raise ValueError(f"{path} is {size} bytes; limit is {max_bytes} bytes")
    return path.read_text(encoding="utf-8")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = read_text_limited(path)
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    result: dict[str, str] = {}
    block_key: str | None = None
    block_lines: list[str] = []
    for line in match.group(1).splitlines():
        if block_key is not None and (line.startswith(" ") or line.startswith("\t")):
            block_lines.append(line.strip())
            continue
        if block_key is not None:
            result[block_key] = "\n".join(block_lines).strip()
            block_key = None
            block_lines = []
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        clean_key = key.strip()
        clean_value = value.strip()
        if clean_value in {"|", ">"}:
            block_key = clean_key
            block_lines = []
            continue
        result[clean_key] = clean_value.strip('"').strip("'")
    if block_key is not None:
        result[block_key] = "\n".join(block_lines).strip()
    return result


def collect_markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    for line in read_text_limited(path).splitlines():
        match = HEADING_RE.match(line)
        if match:
            anchors.add(github_anchor(match.group(2).strip()))
    return anchors


def should_skip_path(path: Path, script_file: str | None = None, extra_skip_roots: set[Path] | None = None) -> bool:
    resolved = path.resolve()
    if script_file and resolved == Path(script_file).resolve():
        return True
    if extra_skip_roots and any(resolved == root.resolve() or resolved.is_relative_to(root.resolve()) for root in extra_skip_roots):
        return True
    return any(part in DEFAULT_SKIP_DIRS for part in path.parts)


def is_support_skill_dir(path: Path) -> bool:
    return path.name.startswith("_") or path.name.startswith(".")
