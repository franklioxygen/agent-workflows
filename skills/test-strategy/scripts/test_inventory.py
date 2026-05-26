#!/usr/bin/env python3
# Function Name: discover_test_files, script_name_tokens, is_validation_script, pyproject_configures_pytest, discover_package_commands, discover_config_files, build_inventory, print_inventory, main
# Description: Inventory test files, likely test commands, and validation config files for test-strategy planning.

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - kept for older Python runtimes.
    tomllib = None  # type: ignore[assignment]

SHARED_SCRIPTS = Path(__file__).resolve().parents[2] / "_shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from skill_common import read_text_limited, should_skip_path  # noqa: E402

CONFIG_NAMES = {
    "package.json",
    "pyproject.toml",
    "pytest.ini",
    "tox.ini",
    "vitest.config.ts",
    "vitest.config.js",
    "jest.config.js",
    "jest.config.ts",
    "playwright.config.ts",
    "go.mod",
    "Cargo.toml",
}

VALIDATION_SCRIPT_WORDS = {
    "build",
    "check",
    "ci",
    "e2e",
    "format",
    "integration",
    "lint",
    "spec",
    "test",
    "type",
    "unit",
    "validate",
    "verify",
}
VALIDATION_SCRIPT_COMPACT_NAMES = {"typecheck"}
VALIDATION_COMMAND_PREFIXES = (
    "cargo test",
    "eslint",
    "go test",
    "jest",
    "mypy",
    "playwright test",
    "prettier --check",
    "pytest",
    "ruff",
    "tsc",
    "vitest",
)


def discover_test_files(root: Path) -> list[str]:
    files: list[str] = []
    for path in root.rglob("*"):
        if should_skip_path(path, script_file=__file__) or not path.is_file():
            continue
        rel = path.relative_to(root)
        parts = [part.lower() for part in rel.parts]
        name = path.name.lower()
        stem = path.stem.lower()
        in_test_dir = any(part in {"test", "tests", "__tests__", "spec", "specs"} for part in parts[:-1])
        test_file_name = (
            name.startswith("test_")
            or stem.endswith("_test")
            or ".test." in name
            or ".spec." in name
        )
        if in_test_dir or test_file_name:
            files.append(str(path.relative_to(root)))
    return sorted(files)


def script_name_tokens(name: str) -> set[str]:
    camel_split = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    return {token for token in re.split(r"[^A-Za-z0-9]+", camel_split.lower()) if token}


def is_validation_script(name: str, command: object) -> bool:
    compact_name = re.sub(r"[^a-z0-9]", "", name.lower())
    if script_name_tokens(name) & VALIDATION_SCRIPT_WORDS:
        return True
    if compact_name in VALIDATION_SCRIPT_COMPACT_NAMES:
        return True
    if isinstance(command, str):
        normalized_command = command.strip().lower()
        return any(normalized_command.startswith(prefix) for prefix in VALIDATION_COMMAND_PREFIXES)
    return False


def pyproject_configures_pytest(path: Path) -> bool:
    if not path.is_file():
        return False
    if tomllib is None:
        try:
            return "[tool.pytest" in read_text_limited(path)
        except (OSError, ValueError):
            return False
    try:
        data = tomllib.loads(read_text_limited(path))
    except (OSError, ValueError, tomllib.TOMLDecodeError):
        return False
    tool = data.get("tool", {})
    return isinstance(tool, dict) and "pytest" in tool


def discover_package_commands(root: Path) -> dict[str, list[str]]:
    commands: dict[str, list[str]] = {}
    package_json = root / "package.json"
    if package_json.is_file():
        try:
            data = json.loads(read_text_limited(package_json))
            scripts = data.get("scripts", {})
            if isinstance(scripts, dict):
                commands["npm"] = [
                    f"npm run {name}"
                    for name, command in scripts.items()
                    if is_validation_script(name, command)
                ]
        except json.JSONDecodeError:
            commands["npm"] = ["package.json exists but could not be parsed"]
        except ValueError as exc:
            commands["npm"] = [f"package.json skipped: {exc}"]

    if (root / "pytest.ini").is_file() or pyproject_configures_pytest(root / "pyproject.toml"):
        commands.setdefault("python", []).append("pytest")
    if (root / "tox.ini").is_file():
        commands.setdefault("python", []).append("tox")
    if (root / "go.mod").is_file():
        commands.setdefault("go", []).append("go test ./...")
    if (root / "Cargo.toml").is_file():
        commands.setdefault("rust", []).append("cargo test")
    return commands


def discover_config_files(root: Path) -> list[str]:
    return sorted(str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and path.name in CONFIG_NAMES)


def build_inventory(root: Path) -> dict[str, object]:
    return {
        "root": str(root),
        "test_files": discover_test_files(root),
        "config_files": discover_config_files(root),
        "suggested_commands": discover_package_commands(root),
    }


def print_inventory(inventory: dict[str, object]) -> None:
    print("test strategy inventory")
    print(f"root: {inventory['root']}")
    test_files = inventory["test_files"]
    print(f"test files: {len(test_files)}")
    for path in test_files:
        print(f"  {path}")
    print("config files:")
    for path in inventory["config_files"]:
        print(f"  {path}")
    print("suggested commands:")
    for group, commands in inventory["suggested_commands"].items():
        for command in commands:
            print(f"  {group}: {command}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory test files and likely validation commands.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to inspect.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"root not found: {root}", file=sys.stderr)
        return 1
    print_inventory(build_inventory(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
