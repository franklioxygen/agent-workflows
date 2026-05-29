#!/usr/bin/env python3
# Function Name: main, load_jsonl, merge_run_and_rater_rows, outcome_from_raters
# Description: Combine real Claude Code run metadata, objective locked-check results, blinded rater scores, and adjudications into the adjudicated results.jsonl consumed by evaluation summaries and charts.

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


BINARY_OUTCOMES = (
    "passed",
    "validation_passed",
    "human_accepted",
    "regression",
    "rework_required",
    "requirements_traceability",
)

OPTIONAL_RUN_METADATA_FIELDS = (
    "public_validation_passed",
    "hidden_validation_passed",
)


def run_key(row: dict[str, Any]) -> tuple[str, str, int]:
    return (str(row["task_id"]), str(row["condition"]), int(row["run_id"]))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def _validate_rater_rows(rater_rows: list[dict[str, Any]]) -> None:
    for row in rater_rows:
        missing = {"task_id", "condition", "run_id", "rater_id"} - row.keys()
        missing.update(field for field in BINARY_OUTCOMES if field not in row)
        if missing:
            raise ValueError(
                f"rater row {run_key(row) if {'task_id', 'condition', 'run_id'} <= row.keys() else row} "
                f"missing fields: {', '.join(sorted(missing))}"
            )
        for field in BINARY_OUTCOMES:
            if not isinstance(row[field], bool):
                raise ValueError(f"rater row {run_key(row)} field {field} must be boolean")


def _validate_adjudications(adjudications: dict[tuple[str, str, int], dict[str, Any]]) -> None:
    for key, row in adjudications.items():
        for field in BINARY_OUTCOMES:
            if field in row and not isinstance(row[field], bool):
                raise ValueError(f"adjudication row {key} field {field} must be boolean")


def outcome_from_raters(
    *,
    key: tuple[str, str, int],
    outcome: str,
    rater_rows: list[dict[str, Any]],
    adjudication: dict[str, Any] | None,
) -> tuple[bool, bool]:
    values = [row[outcome] for row in rater_rows]
    if not values:
        raise ValueError(f"{key}: no rater scores found for {outcome}")
    if all(value == values[0] for value in values):
        return bool(values[0]), False
    if adjudication is None or outcome not in adjudication:
        raise ValueError(
            f"{key}: rater disagreement on {outcome}; provide an adjudication row"
        )
    return bool(adjudication[outcome]), True


def merge_run_and_rater_rows(
    run_rows: list[dict[str, Any]],
    rater_rows: list[dict[str, Any]],
    adjudication_rows: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    _validate_rater_rows(rater_rows)
    by_run: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rater_rows:
        by_run[run_key(row)].append(row)
    adjudications = {
        run_key(row): row for row in (adjudication_rows or [])
    }
    _validate_adjudications(adjudications)

    results: list[dict[str, Any]] = []
    for run in sorted(run_rows, key=lambda row: int(row["run_order"])):
        key = run_key(run)
        raters = by_run.get(key, [])
        rater_ids = sorted({str(row["rater_id"]) for row in raters})
        if len(rater_ids) < 2:
            raise ValueError(f"{key}: fewer than two distinct rater rows")
        adjudication = adjudications.get(key)
        final_outcomes: dict[str, bool] = {}
        adjudicated = False
        for outcome in BINARY_OUTCOMES:
            final_value, used_adjudication = outcome_from_raters(
                key=key,
                outcome=outcome,
                rater_rows=raters,
                adjudication=adjudication,
            )
            final_outcomes[outcome] = final_value
            adjudicated = adjudicated or used_adjudication
        result = {
            "task_id": run["task_id"],
            "condition": run["condition"],
            "workflow": run.get("workflow"),
            "run_id": run["run_id"],
            "run_order": run["run_order"],
            "env": run["env"],
            "artifact_path": run["artifact_path"],
            "blinded_artifact_path": run["blinded_artifact_path"],
            **final_outcomes,
            "cycle_time_seconds": run["cycle_time_seconds"],
            "adjudicated": adjudicated,
            "rater_ids": rater_ids,
            "notes": (
                adjudication.get("adjudication_notes")
                if adjudication and adjudication.get("adjudication_notes")
                else run.get("notes")
            ),
        }
        for field in OPTIONAL_RUN_METADATA_FIELDS:
            if field in run:
                if not isinstance(run[field], bool):
                    raise ValueError(f"{key}: run field {field} must be boolean")
                result[field] = run[field]
        results.append(result)
    return results


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Build adjudicated results.jsonl from real run metadata and blinded rater scores."
    )
    parser.add_argument("--runs", required=True, help="runs.jsonl from run_claude_code_study.py")
    parser.add_argument("--raters", required=True, help="Blinded rater scores JSONL")
    parser.add_argument(
        "--adjudications",
        default=None,
        help="Optional adjudication JSONL for rater disagreements",
    )
    parser.add_argument("--output", required=True, help="Output adjudicated results.jsonl")
    args = parser.parse_args(argv)
    try:
        run_rows = load_jsonl(Path(args.runs))
        rater_rows = load_jsonl(Path(args.raters))
        adjudication_rows = (
            load_jsonl(Path(args.adjudications)) if args.adjudications else []
        )
        results = merge_run_and_rater_rows(run_rows, rater_rows, adjudication_rows)
        write_jsonl(Path(args.output), results)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
