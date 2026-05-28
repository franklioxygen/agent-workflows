#!/usr/bin/env python3
# Function Name: summarize_results, EvaluationSummary
# Description: Aggregate single-prompt and workflow-guided JSONL run data into task-level and run-level comparison metrics.

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


REQUIRED_FIELDS = {
    "task_id",
    "condition",
    "run_id",
    "passed",
    "validation_passed",
    "human_accepted",
    "regression",
    "rework_required",
    "requirements_traceability",
    "cycle_time_seconds",
}


def load_results(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            missing = REQUIRED_FIELDS - row.keys()
            if missing:
                missing_fields = ", ".join(sorted(missing))
                raise ValueError(f"{path}:{line_number}: missing required fields: {missing_fields}")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no result rows found")
    return rows


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def median(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.median(values)


def summarize(rows: list[dict]) -> dict[str, dict[str, float | int | None]]:
    grouped_runs: dict[str, list[dict]] = defaultdict(list)
    grouped_tasks: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))

    for row in rows:
        condition = row["condition"]
        grouped_runs[condition].append(row)
        grouped_tasks[condition][row["task_id"]].append(row)

    summary: dict[str, dict[str, float | int | None]] = {}
    for condition, condition_runs in grouped_runs.items():
        task_groups = grouped_tasks[condition]
        first_runs = [run for run in condition_runs if int(run["run_id"]) == 1]

        pass_at_1_count = sum(1 for run in first_runs if bool(run["passed"]))
        strict_repeat_count = 0
        for task_runs in task_groups.values():
            ordered = sorted(task_runs, key=lambda item: int(item["run_id"]))
            if ordered and all(bool(run["passed"]) for run in ordered):
                strict_repeat_count += 1

        summary[condition] = {
            "task_count": len(task_groups),
            "run_count": len(condition_runs),
            "pass_at_1": rate(pass_at_1_count, len(first_runs)),
            "pass_hat_k": rate(strict_repeat_count, len(task_groups)),
            "validation_pass_rate": rate(
                sum(1 for run in condition_runs if bool(run["validation_passed"])),
                len(condition_runs),
            ),
            "human_acceptance_rate": rate(
                sum(1 for run in condition_runs if bool(run["human_accepted"])),
                len(condition_runs),
            ),
            "regression_rate": rate(
                sum(1 for run in condition_runs if bool(run["regression"])),
                len(condition_runs),
            ),
            "rework_rate": rate(
                sum(1 for run in condition_runs if bool(run["rework_required"])),
                len(condition_runs),
            ),
            "requirements_traceability_rate": rate(
                sum(1 for run in condition_runs if bool(run["requirements_traceability"])),
                len(condition_runs),
            ),
            "median_cycle_time_seconds": median(
                [float(run["cycle_time_seconds"]) for run in condition_runs]
            ),
        }

    return summary


def format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def format_seconds(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.0f}s"


def print_markdown(summary: dict[str, dict[str, float | int | None]]) -> None:
    headers = [
        "Condition",
        "Tasks",
        "Runs",
        "Pass@1",
        "Pass^k",
        "Validation",
        "Human Accept",
        "Regression",
        "Rework",
        "Traceability",
        "Median Time",
    ]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")
    for condition in sorted(summary):
        row = summary[condition]
        print(
            "| "
            + " | ".join(
                [
                    condition,
                    str(row["task_count"]),
                    str(row["run_count"]),
                    format_percent(row["pass_at_1"]),
                    format_percent(row["pass_hat_k"]),
                    format_percent(row["validation_pass_rate"]),
                    format_percent(row["human_acceptance_rate"]),
                    format_percent(row["regression_rate"]),
                    format_percent(row["rework_rate"]),
                    format_percent(row["requirements_traceability_rate"]),
                    format_seconds(row["median_cycle_time_seconds"]),
                ]
            )
            + " |"
        )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Summarize agent workflow evaluation runs.")
    parser.add_argument("results", help="Path to a JSONL results file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args(argv)

    try:
        rows = load_results(Path(args.results))
        summary = summarize(rows)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_markdown(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
