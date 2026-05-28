#!/usr/bin/env python3
# Function Name: generate_chart_scores, EvaluationChartScores
# Description: Convert measured evaluation metrics into README-style 0-10 chart scores and Mermaid output.

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def load_summary_module():
    script_path = Path(__file__).with_name("summarize_results.py")
    spec = importlib.util.spec_from_file_location("summarize_results", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clamp_score(value: float) -> int:
    return max(0, min(10, round(value)))


def score_from_rate(rate: float | None) -> int:
    if rate is None:
        return 0
    return clamp_score(rate * 10)


def score_from_inverse_rate(rate: float | None) -> int:
    if rate is None:
        return 0
    return clamp_score((1 - rate) * 10)


def chart_scores(summary: dict[str, dict[str, float | int | None]]) -> dict[str, list[int]]:
    scored: dict[str, list[int]] = {}
    for condition, row in summary.items():
        scored[condition] = [
            score_from_rate(row.get("pass_at_1")),
            score_from_rate(row.get("pass_hat_k")),
            score_from_inverse_rate(row.get("regression_rate")),
            score_from_inverse_rate(row.get("rework_rate")),
            score_from_rate(row.get("requirements_traceability_rate")),
        ]
    return scored


def print_mermaid(scores: dict[str, list[int]], title: str) -> None:
    single_prompt = scores.get("single_prompt", [0, 0, 0, 0, 0])
    workflow_guided = scores.get("workflow_guided", [0, 0, 0, 0, 0])
    print("```mermaid")
    print("---")
    print("config:")
    print("  xychart:")
    print("    width: 1100")
    print("    xAxis:")
    print("      labelFontSize: 12")
    print("---")
    print("xychart-beta")
    print(f'    title "{title}"')
    print('    x-axis ["Pass@1", "RRC", "DER", "CFR", "RTM"]')
    print('    y-axis "Score" 0 --> 10')
    print(f'    bar "Single Prompt" [{", ".join(str(v) for v in single_prompt)}]')
    print(f'    bar "Workflow-Guided" [{", ".join(str(v) for v in workflow_guided)}]')
    print("```")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate chart-ready scores from evaluation results.")
    parser.add_argument("results", help="Path to a JSONL results file.")
    parser.add_argument("--json", action="store_true", help="Print chart scores as JSON.")
    parser.add_argument(
        "--mermaid",
        action="store_true",
        help="Print a Mermaid xychart block instead of JSON.",
    )
    parser.add_argument(
        "--title",
        default="Measured Outcome Comparison",
        help="Mermaid chart title when using --mermaid.",
    )
    args = parser.parse_args(argv)

    summary_module = load_summary_module()
    try:
        rows = summary_module.load_results(Path(args.results))
        summary = summary_module.summarize(rows)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    scores = chart_scores(summary)
    if args.mermaid:
        print_mermaid(scores, args.title)
    else:
        print(json.dumps(scores, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
