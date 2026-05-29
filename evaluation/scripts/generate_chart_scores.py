#!/usr/bin/env python3
# Function Name: chart_scores, render_svg, write_svg, main
# Description: Convert measured per-condition metrics into 0-10 chart scores using outcome-oriented labels (TPR, RP@k, CPR, RFR, NRR) and emit JSON or reproducible SVG chart output.

from __future__ import annotations

import argparse
from html import escape
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


CHART_METRICS = (
    ("task_pass_rate", "TPR"),
    ("reliable_pass_at_k", "RP@k"),
    ("clean_pass_rate", "CPR"),
    ("regression_free_rate", "RFR"),
    ("no_rework_rate", "NRR"),
)

SINGLE_COLOR = "#4f83c2"
WORKFLOW_COLOR = "#f59e0b"
CHART_TOP = 130
CHART_BOTTOM = 540
PIXELS_PER_SCORE = (CHART_BOTTOM - CHART_TOP) // 10


def load_summary_module():
    script_path = Path(__file__).with_name("summarize_results.py")
    spec = importlib.util.spec_from_file_location("summarize_results", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _clamp_score(value: float) -> int:
    return max(0, min(10, round(value)))


def _score_from_point(point: float | None) -> int:
    if point is None:
        return 0
    return _clamp_score(point * 10)


def _entry_point(condition_block: dict[str, Any] | None, metric: str) -> float | None:
    if not isinstance(condition_block, dict):
        return None
    entry = condition_block.get(metric)
    if isinstance(entry, dict):
        return entry.get("point")
    return entry if isinstance(entry, (int, float)) else None


def chart_scores(summary: dict[str, Any]) -> dict[str, list[int]]:
    conditions_block = summary.get("conditions", summary)
    output: dict[str, list[int]] = {}
    for condition, block in conditions_block.items():
        if not isinstance(block, dict):
            continue
        output[condition] = [
            _score_from_point(_entry_point(block, metric)) for metric, _ in CHART_METRICS
        ]
    return output


def _bar(score: int, x: int, color: str) -> tuple[str, str]:
    height = max(2, score * PIXELS_PER_SCORE)
    y = CHART_BOTTOM - height
    rect = f'  <rect x="{x}" y="{y}" width="40" height="{height}" fill="{color}"/>'
    value = f'  <text class="value" x="{x + 20}" y="{y - 6}" text-anchor="middle">{score}</text>'
    return rect, value


def render_svg(
    scores: dict[str, list[int]],
    *,
    title: str,
    subtitle: str,
    y_label: str,
    description: str,
) -> str:
    labels = [label for _, label in CHART_METRICS]
    single = scores.get("single_prompt", [0] * len(labels))
    workflow = scores.get("workflow_guided", [0] * len(labels))
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="980" height="620" viewBox="0 0 980 620" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{escape(title)}</title>',
        f'  <desc id="desc">{escape(description)}</desc>',
        "  <style>",
        "    .bg { fill: #ffffff; }",
        "    .title { font: 700 30px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #111827; }",
        "    .subtitle { font: 500 14px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #6b7280; }",
        "    .label { font: 500 16px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #374151; }",
        "    .tick { font: 500 14px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #6b7280; }",
        "    .axis { stroke: #374151; stroke-width: 2; }",
        "    .grid { stroke: #e5e7eb; stroke-width: 1; }",
        "    .legend { font: 600 15px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #1f2937; }",
        "    .value { font: 600 13px -apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif; fill: #111827; }",
        "  </style>",
        '  <rect class="bg" width="980" height="620"/>',
        "",
        f'  <text class="title" x="490" y="44" text-anchor="middle">{escape(title)}</text>',
        f'  <text class="subtitle" x="490" y="64" text-anchor="middle">{escape(subtitle)}</text>',
        "",
        f'  <rect x="300" y="78" width="18" height="18" fill="{SINGLE_COLOR}"/>',
        '  <text class="legend" x="326" y="92">Single Prompt</text>',
        f'  <rect x="500" y="78" width="18" height="18" fill="{WORKFLOW_COLOR}"/>',
        '  <text class="legend" x="526" y="92">Workflow-Guided</text>',
        "",
        f'  <line class="axis" x1="90" y1="{CHART_BOTTOM}" x2="920" y2="{CHART_BOTTOM}"/>',
        f'  <line class="axis" x1="90" y1="{CHART_TOP}" x2="90" y2="{CHART_BOTTOM}"/>',
        "",
    ]
    for tick in range(11):
        y = CHART_BOTTOM - tick * PIXELS_PER_SCORE
        lines.append(f'  <line class="grid" x1="90" y1="{y}" x2="920" y2="{y}"/>')
    lines.append("")
    for tick in range(11):
        y = CHART_BOTTOM + 4 - tick * PIXELS_PER_SCORE
        lines.append(f'  <text class="tick" x="74" y="{y}" text-anchor="end">{tick}</text>')
    lines.extend(
        [
            "",
            f'  <text class="label" transform="translate(28 {(CHART_TOP + CHART_BOTTOM) // 2}) rotate(-90)" text-anchor="middle">{escape(y_label)}</text>',
            "",
        ]
    )
    for index, label in enumerate(labels):
        group_x = 130 + index * 160
        label_x = group_x + 43
        single_rect, single_value = _bar(single[index], group_x, SINGLE_COLOR)
        workflow_rect, workflow_value = _bar(
            workflow[index], group_x + 46, WORKFLOW_COLOR
        )
        lines.extend(
            [
                single_rect,
                workflow_rect,
                single_value,
                workflow_value,
                f'  <text class="label" x="{label_x}" y="570" text-anchor="middle">{escape(label)}</text>',
                "",
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines)


def write_svg(svg: str, output: Path) -> None:
    output.write_text(svg + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Generate chart-ready scores from evaluation results."
    )
    parser.add_argument("results", help="Path to a JSONL results file.")
    parser.add_argument(
        "--raters",
        default=None,
        help="Optional per-rater scores file (forwarded to the summarizer).",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="Print chart scores as JSON.")
    output_group.add_argument(
        "--svg",
        action="store_true",
        help="Print or write an SVG chart.",
    )
    parser.add_argument(
        "--title",
        default="Measured Outcome Comparison",
        help="Chart title when using --svg.",
    )
    parser.add_argument(
        "--subtitle",
        default="Output of evaluation/scripts/generate_chart_scores.py",
        help="SVG subtitle.",
    )
    parser.add_argument(
        "--description",
        default=(
            "Grouped bar chart of measured evaluation scores for Single Prompt "
            "and Workflow-Guided on TPR, RP@k, CPR, RFR, and NRR, produced "
            "by evaluation/scripts/generate_chart_scores.py."
        ),
        help="Accessible SVG description.",
    )
    parser.add_argument(
        "--y-label",
        default="Score",
        help="SVG y-axis label.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write SVG output to this path. Only valid with --svg.",
    )
    args = parser.parse_args(argv)
    if args.output and not args.svg:
        parser.error("--output is only supported with --svg")

    summary_module = load_summary_module()
    try:
        rows = summary_module.load_results(Path(args.results))
        rater_rows = (
            summary_module.load_raters(Path(args.raters)) if args.raters else []
        )
        summary = summary_module.summarize(rows, rater_rows)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    scores = chart_scores(summary)
    if args.svg:
        svg = render_svg(
            scores,
            title=args.title,
            subtitle=args.subtitle,
            y_label=args.y_label,
            description=args.description,
        )
        if args.output:
            write_svg(svg, Path(args.output))
        else:
            print(svg)
    else:
        print(json.dumps(scores, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
