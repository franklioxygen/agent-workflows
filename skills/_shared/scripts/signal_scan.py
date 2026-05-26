#!/usr/bin/env python3
# Function Name: iter_text_files, is_source_comment_line, scan_file, build_signal_report, print_signal_report
# Description: Shared bounded text-file signal scanning helpers for agent-workflows review skills.

from __future__ import annotations

import re
from pathlib import Path

from skill_common import read_text_limited, should_skip_path


COMMENT_PREFIXES = ("#", "//", "/*", "*", "--", "<!--")


def iter_text_files(
    target: Path,
    text_extensions: set[str],
    script_file: str,
    extra_skip_roots: set[Path] | None = None,
) -> list[Path]:
    if target.is_file():
        return [target] if target.suffix in text_extensions else []
    return sorted(
        path
        for path in target.rglob("*")
        if path.is_file()
        and not should_skip_path(path, script_file=script_file, extra_skip_roots=extra_skip_roots)
        and path.suffix in text_extensions
    )


def is_source_comment_line(path: Path, line: str) -> bool:
    if path.suffix == ".md":
        return False
    return line.lstrip().startswith(COMMENT_PREFIXES)


def scan_file(path: Path, patterns: list[tuple[str, re.Pattern[str]]]) -> list[tuple[int, str, str]]:
    signals: list[tuple[int, str, str]] = []
    try:
        lines = read_text_limited(path).splitlines()
    except (UnicodeDecodeError, ValueError):
        return signals

    for line_number, line in enumerate(lines, 1):
        if is_source_comment_line(path, line):
            continue
        for label, pattern in patterns:
            if pattern.search(line):
                signals.append((line_number, label, line.strip()[:160]))
    return signals


def build_signal_report(
    target: Path,
    patterns: list[tuple[str, re.Pattern[str]]],
    text_extensions: set[str],
    script_file: str,
    extra_skip_roots: set[Path] | None = None,
) -> dict[str, object]:
    files = iter_text_files(target, text_extensions, script_file, extra_skip_roots)
    signals: list[dict[str, object]] = []
    for path in files:
        for line, label, snippet in scan_file(path, patterns):
            signals.append({"file": str(path), "line": line, "signal": label, "snippet": snippet})
    return {"files_scanned": len(files), "signals": signals}


def print_signal_report(title: str, report: dict[str, object], note: str) -> None:
    print(title)
    print(f"files scanned: {report['files_scanned']}")
    print(f"signals: {len(report['signals'])}")
    for signal in report["signals"]:
        print(f"{signal['file']}:{signal['line']} [{signal['signal']}] {signal['snippet']}")
    print(note)
