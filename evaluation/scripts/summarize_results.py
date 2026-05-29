#!/usr/bin/env python3
# Function Name: summarize, main, validate_result_row, validate_rater_row, locked_checks_passed, locked_check_coverage_warnings, reliability_items_for_outcome, fleiss_kappa_binary, raw_agreement_binary, reliability_with_ci, rater_coverage_warnings
# Description: Aggregate adjudicated results and per-rater scores into per-condition metrics with bootstrap CIs, paired permutation tests, task-weighted pass rates, objective locked-check regression protection, chance-corrected reliability estimates, Holm-Bonferroni correction, and power warnings.

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable


REQUIRED_FIELDS = {
    "task_id",
    "condition",
    "run_id",
    "run_order",
    "env",
    "artifact_path",
    "blinded_artifact_path",
    "passed",
    "validation_passed",
    "human_accepted",
    "regression",
    "rework_required",
    "requirements_traceability",
    "cycle_time_seconds",
    "adjudicated",
    "rater_ids",
}

REQUIRED_ENV_FIELDS = {
    "model_provider",
    "model_id",
    "model_parameters",
    "repo_sha",
    "tool_access",
    "time_budget_seconds",
    "prompt_template_version",
    "agent_harness_version",
    "kit_version",
}

REQUIRED_RATER_FIELDS = {
    "task_id",
    "condition",
    "run_id",
    "rater_id",
    "passed",
    "validation_passed",
    "human_accepted",
    "regression",
    "rework_required",
    "requirements_traceability",
}

BINARY_OUTCOMES = (
    "passed",
    "validation_passed",
    "human_accepted",
    "regression",
    "rework_required",
    "requirements_traceability",
)

PROPORTION_METRICS = (
    "task_pass_rate",
    "reliable_pass_at_k",
    "clean_pass_rate",
    "regression_free_rate",
    "no_rework_rate",
)

ALL_METRICS = PROPORTION_METRICS

PRIMARY_HYPOTHESES = (
    "task_pass_rate",
    "reliable_pass_at_k",
    "regression_free_rate",
)

RELIABILITY_PRIMARY_OUTCOMES = {
    "passed",
    "regression",
}

BOOTSTRAP_RESAMPLES = 10000
PERMUTATION_RESAMPLES = 10000
DEFAULT_SEED = 20260528
ALPHA = 0.05
CI_LEVEL = 0.95
MIN_TASKS = 30
MIN_K = 3
PRIMARY_CI_HALF_WIDTH = 0.15
KAPPA_THRESHOLD = 0.6
RFR_DEFINITION = (
    "no human-scored unrelated regression and, when present, hidden locked evaluator "
    "checks passed"
)


def _run_key(row: dict) -> tuple[str, str, int]:
    return (str(row["task_id"]), str(row["condition"]), int(row["run_id"]))


def validate_result_row(row: dict, path: Path, line_number: int) -> None:
    env = row.get("env")
    if not isinstance(env, dict):
        raise ValueError(f"{path}:{line_number}: env must be a JSON object")
    env_missing = REQUIRED_ENV_FIELDS - env.keys()
    if env_missing:
        raise ValueError(
            f"{path}:{line_number}: env missing fields: {', '.join(sorted(env_missing))}"
        )
    for field in BINARY_OUTCOMES + ("adjudicated",):
        if not isinstance(row.get(field), bool):
            raise ValueError(f"{path}:{line_number}: {field} must be boolean")
    for field in ("public_validation_passed", "hidden_validation_passed"):
        if field in row and not isinstance(row[field], bool):
            raise ValueError(f"{path}:{line_number}: {field} must be boolean")
    for field in ("run_id", "run_order"):
        if type(row.get(field)) is not int or row[field] < 1:
            raise ValueError(f"{path}:{line_number}: {field} must be a positive integer")
    cycle_time = row.get("cycle_time_seconds")
    if not isinstance(cycle_time, (int, float)) or cycle_time <= 0:
        raise ValueError(
            f"{path}:{line_number}: cycle_time_seconds must be a positive number"
        )
    rater_ids = row.get("rater_ids")
    if (
        not isinstance(rater_ids, list)
        or not all(isinstance(rater_id, str) and rater_id for rater_id in rater_ids)
        or len(set(rater_ids)) < 2
    ):
        raise ValueError(
            f"{path}:{line_number}: rater_ids must list at least two distinct rater ids"
        )


def validate_rater_row(row: dict, path: Path, line_number: int) -> None:
    for field in BINARY_OUTCOMES:
        if not isinstance(row.get(field), bool):
            raise ValueError(f"{path}:{line_number}: {field} must be boolean")
    if type(row.get("run_id")) is not int or row["run_id"] < 1:
        raise ValueError(f"{path}:{line_number}: run_id must be a positive integer")
    if not isinstance(row.get("rater_id"), str) or not row["rater_id"]:
        raise ValueError(f"{path}:{line_number}: rater_id must be a non-empty string")


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
                raise ValueError(
                    f"{path}:{line_number}: missing required fields: {', '.join(sorted(missing))}"
                )
            validate_result_row(row, path, line_number)
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no result rows found")
    return rows


def load_raters(path: Path) -> list[dict]:
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
            missing = REQUIRED_RATER_FIELDS - row.keys()
            if missing:
                raise ValueError(
                    f"{path}:{line_number}: missing required fields: {', '.join(sorted(missing))}"
                )
            validate_rater_row(row, path, line_number)
            rows.append(row)
    return rows


def check_env_consistency(rows: list[dict]) -> list[str]:
    warnings: list[str] = []
    fields = (
        "model_provider",
        "model_id",
        "model_parameters",
        "repo_sha",
        "tool_access",
        "time_budget_seconds",
        "prompt_template_version",
        "agent_harness_version",
        "kit_version",
    )
    for field in fields:
        seen = {json.dumps(row["env"].get(field), sort_keys=True) for row in rows}
        if len(seen) > 1:
            warnings.append(
                f"env.{field} differs across rows; cross-row comparison may be invalid"
            )
    return warnings


def locked_checks_passed(row: dict) -> int:
    if "hidden_validation_passed" not in row:
        return 1
    return _bool(row["hidden_validation_passed"])


def locked_check_coverage_warnings(rows: list[dict]) -> list[str]:
    warnings: list[str] = []
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_condition[str(row["condition"])].append(row)

    conditions_with_locked = []
    conditions_without_locked = []
    for condition, condition_rows in sorted(by_condition.items()):
        locked_count = sum(1 for row in condition_rows if "hidden_validation_passed" in row)
        if locked_count == len(condition_rows):
            conditions_with_locked.append(condition)
        elif locked_count == 0:
            conditions_without_locked.append(condition)
        else:
            warnings.append(
                f"{condition}: hidden_validation_passed present on {locked_count}/"
                f"{len(condition_rows)} rows; RFR comparability is mixed"
            )

    if conditions_with_locked and conditions_without_locked:
        warnings.append(
            "hidden_validation_passed is absent for "
            f"{', '.join(conditions_without_locked)} but present for "
            f"{', '.join(conditions_with_locked)}; RFR falls back to human regression "
            "where locked checks are absent"
        )
    return warnings


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _bool(value: Any) -> int:
    return 1 if bool(value) else 0


def compute_task_metric(metric: str, runs: list[dict]) -> float | None:
    if not runs:
        return None
    runs_sorted = sorted(runs, key=lambda r: int(r["run_id"]))
    if metric == "task_pass_rate":
        return _mean([_bool(r["passed"]) for r in runs_sorted])
    if metric in {"reliable_pass_at_k", "repeated_run_consistency"}:
        return 1.0 if all(_bool(r["passed"]) for r in runs_sorted) else 0.0
    if metric == "clean_pass_rate":
        return _mean(
            [
                _bool(r["passed"])
                and _bool(r["validation_passed"])
                and not _bool(r["regression"])
                and not _bool(r["rework_required"])
                for r in runs_sorted
            ]
        )
    if metric == "regression_free_rate":
        return _mean(
            [
                1
                if not _bool(r["regression"]) and locked_checks_passed(r)
                else 0
                for r in runs_sorted
            ]
        )
    if metric == "no_rework_rate":
        return _mean([1 - _bool(r["rework_required"]) for r in runs_sorted])
    raise ValueError(f"unknown metric: {metric}")


def per_task_values(rows: list[dict], metric: str) -> dict[str, dict[str, float]]:
    grouped: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["condition"]][row["task_id"]].append(row)
    output: dict[str, dict[str, float]] = {}
    for condition, task_runs in grouped.items():
        per_task: dict[str, float] = {}
        for task_id, runs in task_runs.items():
            value = compute_task_metric(metric, runs)
            if value is not None:
                per_task[task_id] = value
        output[condition] = per_task
    return output


def bootstrap_ci(
    values: list[float],
    *,
    aggregate: Callable[[list[float]], float],
    resamples: int,
    rng: random.Random,
) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    point = aggregate(values)
    if len(values) == 1:
        return point, point, point
    n = len(values)
    boots: list[float] = []
    for _ in range(resamples):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        boots.append(aggregate(sample))
    boots.sort()
    lo_index = int(0.025 * resamples)
    hi_index = max(0, int(0.975 * resamples) - 1)
    return point, boots[lo_index], boots[hi_index]


def paired_delta_ci(
    single: dict[str, float],
    workflow: dict[str, float],
    *,
    resamples: int,
    rng: random.Random,
) -> tuple[list[str], float | None, float | None, float | None]:
    shared_tasks = sorted(set(single) & set(workflow))
    if not shared_tasks:
        return [], None, None, None
    diffs = [workflow[t] - single[t] for t in shared_tasks]
    point, lo, hi = bootstrap_ci(
        diffs, aggregate=_mean, resamples=resamples, rng=rng
    )
    return shared_tasks, point, lo, hi


def paired_permutation_pvalue(
    single: dict[str, float],
    workflow: dict[str, float],
    *,
    resamples: int,
    rng: random.Random,
) -> float | None:
    shared_tasks = sorted(set(single) & set(workflow))
    if not shared_tasks:
        return None
    diffs = [workflow[t] - single[t] for t in shared_tasks]
    observed = abs(_mean(diffs))
    if 2 ** len(diffs) <= resamples:
        extreme = 0
        total = 2 ** len(diffs)
        for mask in range(total):
            permuted = [
                diff if (mask >> index) & 1 else -diff
                for index, diff in enumerate(diffs)
            ]
            if abs(_mean(permuted)) >= observed:
                extreme += 1
        return extreme / total
    extreme = 0
    for _ in range(resamples):
        permuted = [d if rng.random() < 0.5 else -d for d in diffs]
        if abs(_mean(permuted)) >= observed:
            extreme += 1
    return (extreme + 1) / (resamples + 1)


def holm_bonferroni(
    pvalues: dict[str, float], alpha: float
) -> dict[str, dict[str, Any]]:
    if not pvalues:
        return {}
    ranked = sorted(pvalues.items(), key=lambda kv: kv[1])
    m = len(ranked)
    result: dict[str, dict[str, Any]] = {}
    still_rejecting = True
    for index, (metric, p) in enumerate(ranked):
        threshold = alpha / (m - index)
        rejected = bool(still_rejecting and p <= threshold)
        if not rejected:
            still_rejecting = False
        result[metric] = {"p": p, "threshold": threshold, "rejected": rejected}
    return result


def cohens_kappa(pairs: list[tuple[int, int]]) -> float | None:
    if not pairs:
        return None
    n = len(pairs)
    p_observed = sum(1 for a, b in pairs if a == b) / n
    p_a1 = sum(1 for a, _ in pairs if a == 1) / n
    p_b1 = sum(1 for _, b in pairs if b == 1) / n
    p_expected = p_a1 * p_b1 + (1 - p_a1) * (1 - p_b1)
    if p_expected >= 1.0:
        return 1.0 if p_observed >= 1.0 else 0.0
    return (p_observed - p_expected) / (1 - p_expected)


def reliability_items_for_outcome(
    rater_rows: list[dict], outcome: str, condition: str | None = None
) -> list[dict[str, Any]]:
    by_run: dict[tuple[str, str, int], dict[str, int]] = defaultdict(dict)
    for row in rater_rows:
        if condition is not None and row["condition"] != condition:
            continue
        by_run[_run_key(row)][str(row["rater_id"])] = _bool(row[outcome])
    return [
        {"key": key, "ratings": ratings}
        for key, ratings in sorted(by_run.items())
        if len(ratings) >= 2
    ]


def fleiss_kappa_binary(items: list[tuple[int, int]]) -> float | None:
    usable = [counts for counts in items if sum(counts) >= 2]
    if not usable:
        return None
    observed_agreement: list[float] = []
    total_zeros = 0
    total_ones = 0
    for zero_count, one_count in usable:
        n = zero_count + one_count
        observed_agreement.append(
            (zero_count * (zero_count - 1) + one_count * (one_count - 1))
            / (n * (n - 1))
        )
        total_zeros += zero_count
        total_ones += one_count
    total_ratings = total_zeros + total_ones
    p_zero = total_zeros / total_ratings
    p_one = total_ones / total_ratings
    expected = p_zero * p_zero + p_one * p_one
    observed = _mean(observed_agreement)
    if expected >= 1.0:
        return 1.0 if observed >= 1.0 else 0.0
    return (observed - expected) / (1 - expected)


def raw_agreement_binary(items: list[dict[str, Any]]) -> float | None:
    agreements: list[float] = []
    for item in items:
        values = list(item["ratings"].values())
        if len(values) < 2:
            continue
        matching_pairs = 0
        total_pairs = 0
        for left_index, left in enumerate(values):
            for right in values[left_index + 1 :]:
                total_pairs += 1
                if left == right:
                    matching_pairs += 1
        if total_pairs:
            agreements.append(matching_pairs / total_pairs)
    return _mean(agreements) if agreements else None


def reliability_value(
    items: list[dict[str, Any]], method: str | None = None
) -> tuple[str | None, float | None]:
    if not items:
        return None, None
    rater_sets = {tuple(sorted(item["ratings"])) for item in items}
    if method is None:
        method = (
            "cohens_kappa"
            if len(rater_sets) == 1 and len(next(iter(rater_sets))) == 2
            else "fleiss_kappa"
        )
    if method == "cohens_kappa":
        rater_a, rater_b = next(iter(rater_sets))
        pairs = [
            (item["ratings"][rater_a], item["ratings"][rater_b])
            for item in items
        ]
        return method, cohens_kappa(pairs)
    if method == "fleiss_kappa":
        counts = []
        for item in items:
            values = list(item["ratings"].values())
            counts.append((values.count(0), values.count(1)))
        return method, fleiss_kappa_binary(counts)
    raise ValueError(f"unknown reliability method: {method}")


def reliability_with_ci(
    items: list[dict[str, Any]],
    *,
    resamples: int,
    rng: random.Random,
) -> dict[str, Any] | None:
    method, point = reliability_value(items)
    if method is None:
        return None
    agreement = raw_agreement_binary(items)
    values = [
        value
        for item in items
        for value in item["ratings"].values()
    ]
    positive_rate = _mean(values) if values else None
    n = len(items)
    if n == 1:
        return {
            "method": method,
            "kappa": point,
            "agreement_rate": agreement,
            "positive_rate": positive_rate,
            "ci_lo": point,
            "ci_hi": point,
            "n_items": n,
        }
    boots: list[float] = []
    for _ in range(resamples):
        sample = [items[rng.randrange(n)] for _ in range(n)]
        _, kappa = reliability_value(sample, method)
        if kappa is not None:
            boots.append(kappa)
    if not boots:
        return {
            "method": method,
            "kappa": point,
            "agreement_rate": agreement,
            "positive_rate": positive_rate,
            "ci_lo": None,
            "ci_hi": None,
            "n_items": n,
        }
    boots.sort()
    lo_index = int(0.025 * len(boots))
    hi_index = max(0, int(0.975 * len(boots)) - 1)
    return {
        "method": method,
        "kappa": point,
        "agreement_rate": agreement,
        "positive_rate": positive_rate,
        "ci_lo": boots[lo_index],
        "ci_hi": boots[hi_index],
        "n_items": n,
    }


def rater_coverage_warnings(rows: list[dict], rater_rows: list[dict]) -> list[str]:
    warnings: list[str] = []
    result_keys = {_run_key(row) for row in rows}
    by_run: dict[tuple[str, str, int], list[str]] = defaultdict(list)
    for row in rater_rows:
        by_run[_run_key(row)].append(str(row["rater_id"]))
    for row in rows:
        key = _run_key(row)
        expected = set(row["rater_ids"])
        actual = set(by_run.get(key, []))
        if len(actual) < 2:
            warnings.append(
                f"{key}: fewer than two rater rows found; reliability is incomplete"
            )
        if actual and actual != expected:
            warnings.append(
                f"{key}: rater_ids in results do not match raters file"
            )
        if len(by_run.get(key, [])) != len(actual):
            warnings.append(f"{key}: duplicate rater_id rows found")
    extra = sorted(set(by_run) - result_keys)
    if extra:
        warnings.append(
            f"{len(extra)} rater-scored run(s) are absent from the adjudicated results"
        )
    return warnings


def summarize(
    rows: list[dict],
    rater_rows: list[dict] | None = None,
    *,
    seed: int = DEFAULT_SEED,
    bootstrap_resamples: int = BOOTSTRAP_RESAMPLES,
    permutation_resamples: int = PERMUTATION_RESAMPLES,
) -> dict[str, Any]:
    rng = random.Random(seed)
    rater_rows = rater_rows or []

    conditions = sorted({row["condition"] for row in rows})

    summary: dict[str, Any] = {
        "config": {
            "seed": seed,
            "bootstrap_resamples": bootstrap_resamples,
            "permutation_resamples": permutation_resamples,
            "alpha": ALPHA,
            "ci_level": CI_LEVEL,
            "primary_hypotheses": list(PRIMARY_HYPOTHESES),
            "min_tasks": MIN_TASKS,
            "min_k": MIN_K,
            "primary_ci_half_width": PRIMARY_CI_HALF_WIDTH,
            "kappa_threshold": KAPPA_THRESHOLD,
            "regression_free_rate_definition": RFR_DEFINITION,
        },
        "env": rows[0]["env"] if rows else None,
        "conditions": {},
        "comparisons": {},
        "reliability": {},
        "warnings": [],
    }

    summary["warnings"].extend(check_env_consistency(rows))
    summary["warnings"].extend(locked_check_coverage_warnings(rows))
    if rater_rows:
        summary["warnings"].extend(rater_coverage_warnings(rows, rater_rows))

    per_metric_per_task: dict[str, dict[str, dict[str, float]]] = {
        metric: per_task_values(rows, metric) for metric in ALL_METRICS
    }

    for condition in conditions:
        condition_block: dict[str, Any] = {}
        condition_runs = [row for row in rows if row["condition"] == condition]
        condition_tasks: dict[str, list[dict]] = defaultdict(list)
        for row in condition_runs:
            condition_tasks[row["task_id"]].append(row)
        condition_block["task_count"] = len(condition_tasks)
        condition_block["run_count"] = len(condition_runs)
        condition_block["mean_runs_per_task"] = (
            len(condition_runs) / len(condition_tasks) if condition_tasks else 0.0
        )
        condition_block["min_runs_per_task"] = (
            min(len(runs) for runs in condition_tasks.values())
            if condition_tasks
            else 0
        )

        for metric in PROPORTION_METRICS:
            values = list(per_metric_per_task[metric].get(condition, {}).values())
            point, lo, hi = bootstrap_ci(
                values,
                aggregate=_mean,
                resamples=bootstrap_resamples,
                rng=rng,
            )
            condition_block[metric] = (
                {"point": point, "ci_lo": lo, "ci_hi": hi, "n_tasks": len(values)}
                if point is not None
                else None
            )

        summary["conditions"][condition] = condition_block

    if "single_prompt" in conditions and "workflow_guided" in conditions:
        comparisons: dict[str, dict[str, Any]] = {}
        primary_pvalues: dict[str, float] = {}
        for metric in ALL_METRICS:
            single_dict = per_metric_per_task[metric].get("single_prompt", {})
            workflow_dict = per_metric_per_task[metric].get("workflow_guided", {})
            shared, point, lo, hi = paired_delta_ci(
                single_dict,
                workflow_dict,
                resamples=bootstrap_resamples,
                rng=rng,
            )
            if not shared:
                continue
            p_value = paired_permutation_pvalue(
                single_dict,
                workflow_dict,
                resamples=permutation_resamples,
                rng=rng,
            )
            block: dict[str, Any] = {
                "delta": point,
                "ci_lo": lo,
                "ci_hi": hi,
                "n_paired_tasks": len(shared),
                "p_two_sided": p_value,
            }
            comparisons[metric] = block
            if metric in PRIMARY_HYPOTHESES and p_value is not None:
                primary_pvalues[metric] = p_value
        holm = holm_bonferroni(primary_pvalues, ALPHA)
        for metric, holm_block in holm.items():
            comparisons[metric]["holm_threshold"] = holm_block["threshold"]
            comparisons[metric]["holm_rejected"] = holm_block["rejected"]
        summary["comparisons"] = comparisons

    if rater_rows:
        reliability: dict[str, dict[str, dict[str, Any]]] = {}
        for outcome in BINARY_OUTCOMES:
            outcome_block: dict[str, dict[str, Any]] = {}
            for condition in conditions:
                items = reliability_items_for_outcome(rater_rows, outcome, condition)
                if not items:
                    continue
                reliability_entry = reliability_with_ci(
                    items, resamples=bootstrap_resamples, rng=rng
                )
                if reliability_entry is not None:
                    outcome_block[condition] = reliability_entry
            if outcome_block:
                reliability[outcome] = outcome_block
        summary["reliability"] = reliability
    else:
        summary["warnings"].append(
            "no raters file provided; inter-rater reliability cannot be claimed"
        )

    power_warnings = _power_warnings(summary)
    summary["warnings"].extend(power_warnings)
    summary["power_warning"] = bool(power_warnings)
    summary["low_reliability"] = _is_low_reliability(summary.get("reliability", {}))

    return summary


def _power_warnings(summary: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    for condition, block in summary["conditions"].items():
        tasks = block.get("task_count", 0)
        mean_k = block.get("mean_runs_per_task", 0.0)
        min_k = block.get("min_runs_per_task", 0)
        if tasks < MIN_TASKS:
            warnings.append(
                f"{condition}: {tasks} tasks < required {MIN_TASKS}; underpowered for primary hypotheses"
            )
        if min_k < MIN_K:
            warnings.append(
                f"{condition}: min k = {min_k} runs/task < required {MIN_K}; repeated-run metrics unreliable"
            )
        for metric in PRIMARY_HYPOTHESES:
            entry = block.get(metric)
            if (
                isinstance(entry, dict)
                and entry.get("ci_lo") is not None
                and entry.get("ci_hi") is not None
            ):
                half = (entry["ci_hi"] - entry["ci_lo"]) / 2.0
                if half > PRIMARY_CI_HALF_WIDTH:
                    warnings.append(
                        f"{condition}.{metric}: 95% CI half-width {half:.3f} > {PRIMARY_CI_HALF_WIDTH}; inadequate precision"
                    )
    return warnings


def _is_low_reliability(reliability: dict[str, Any]) -> bool:
    for outcome in RELIABILITY_PRIMARY_OUTCOMES:
        block = reliability.get(outcome, {})
        for entry in block.values():
            kappa = entry.get("kappa")
            if kappa is not None and kappa < KAPPA_THRESHOLD:
                return True
    return False


METRIC_LABELS = {
    "task_pass_rate": "TPR",
    "reliable_pass_at_k": "RP@k",
    "clean_pass_rate": "CPR",
    "regression_free_rate": "RFR",
    "no_rework_rate": "NRR",
}


def _format_proportion(block: Any) -> str:
    if not isinstance(block, dict) or block.get("point") is None:
        return "n/a"
    return (
        f"{block['point'] * 100:.1f}% "
        f"[{block['ci_lo'] * 100:.1f}, {block['ci_hi'] * 100:.1f}]"
    )


def _format_delta(metric: str, block: dict[str, Any]) -> str:
    if not block or block.get("delta") is None:
        return "n/a"
    return (
        f"{block['delta'] * 100:+.1f}pp "
        f"[{block['ci_lo'] * 100:+.1f}, {block['ci_hi'] * 100:+.1f}]"
    )


def _format_pvalue(value: float | None) -> str:
    if value is None:
        return "n/a"
    if value < 0.0001:
        return "<0.0001"
    return f"{value:.4f}"


def _format_holm(comparison: dict[str, Any]) -> str:
    if "holm_rejected" not in comparison:
        return "—"
    return "yes" if comparison["holm_rejected"] else "no"


def _format_kappa(entry: Any) -> str:
    if not isinstance(entry, dict) or entry.get("kappa") is None:
        return "n/a"
    method = {
        "cohens_kappa": "Cohen",
        "fleiss_kappa": "Fleiss",
    }.get(entry.get("method"), "Kappa")
    ci_lo = entry.get("ci_lo")
    ci_hi = entry.get("ci_hi")
    ci_text = (
        f"[{ci_lo:.2f}, {ci_hi:.2f}]"
        if ci_lo is not None and ci_hi is not None
        else "[n/a]"
    )
    agreement = entry.get("agreement_rate")
    agreement_text = (
        f", raw={agreement * 100:.1f}%"
        if isinstance(agreement, (int, float))
        else ""
    )
    positive_rate = entry.get("positive_rate")
    positive_text = (
        f", pos={positive_rate * 100:.1f}%"
        if isinstance(positive_rate, (int, float))
        else ""
    )
    return (
        f"{method} κ={entry['kappa']:.2f} "
        f"{ci_text} "
        f"(n={entry['n_items']}{agreement_text}{positive_text})"
    )


def print_markdown(summary: dict[str, Any]) -> None:
    print("## Outcomes (with 95% bootstrap CIs and paired permutation tests)")
    rfr_definition = summary.get("config", {}).get("regression_free_rate_definition")
    if rfr_definition:
        print()
        print(f"_RFR definition: {rfr_definition}._")
    print()
    print(
        "| Metric | single_prompt | workflow_guided | Δ (95% CI) | p (paired) | Holm-rejected |"
    )
    print("| --- | --- | --- | --- | --- | --- |")
    for metric, label in METRIC_LABELS.items():
        sp_block = summary["conditions"].get("single_prompt", {}).get(metric)
        wg_block = summary["conditions"].get("workflow_guided", {}).get(metric)
        cmp_block = summary["comparisons"].get(metric, {})
        print(
            f"| {label} "
            f"| {_format_proportion(sp_block)} "
            f"| {_format_proportion(wg_block)} "
            f"| {_format_delta(metric, cmp_block)} "
            f"| {_format_pvalue(cmp_block.get('p_two_sided'))} "
            f"| {_format_holm(cmp_block)} |"
        )

    if summary.get("reliability"):
        print()
        print("## Inter-Rater Reliability (κ)")
        print()
        print("| Outcome | single_prompt | workflow_guided |")
        print("| --- | --- | --- |")
        for outcome in BINARY_OUTCOMES:
            block = summary["reliability"].get(outcome, {})
            sp_entry = block.get("single_prompt")
            wg_entry = block.get("workflow_guided")
            print(
                f"| {outcome} "
                f"| {_format_kappa(sp_entry)} "
                f"| {_format_kappa(wg_entry)} |"
            )

    if summary.get("warnings"):
        print()
        print("## Warnings")
        for warning in summary["warnings"]:
            print(f"- {warning}")

    flags = []
    if summary.get("power_warning"):
        flags.append(
            "**Power warning**: study is underpowered for primary hypotheses; results are exploratory only."
        )
    if summary.get("low_reliability"):
        flags.append(
            f"**Low reliability**: κ below {KAPPA_THRESHOLD} on a primary outcome; confirmatory claims are not supported without a new pre-registered scoring round."
        )
    if flags:
        print()
        for flag in flags:
            print(flag)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize agent workflow evaluation runs with CIs, paired tests, and inter-rater reliability."
    )
    parser.add_argument("results", help="Path to a JSONL results file.")
    parser.add_argument(
        "--raters",
        default=None,
        help="Path to a JSONL per-rater scores file (for inter-rater reliability).",
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED, help="Random seed for bootstrap and permutation tests."
    )
    parser.add_argument(
        "--bootstrap-resamples",
        type=int,
        default=BOOTSTRAP_RESAMPLES,
        help="Number of bootstrap resamples (default 10000).",
    )
    parser.add_argument(
        "--permutation-resamples",
        type=int,
        default=PERMUTATION_RESAMPLES,
        help="Number of paired-permutation resamples (default 10000).",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args(argv)

    try:
        rows = load_results(Path(args.results))
        rater_rows = load_raters(Path(args.raters)) if args.raters else []
        summary = summarize(
            rows,
            rater_rows,
            seed=args.seed,
            bootstrap_resamples=args.bootstrap_resamples,
            permutation_resamples=args.permutation_resamples,
        )
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
