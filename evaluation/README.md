<!--
Function Name: README
Description: Evaluation kit for comparing single-prompt and workflow-guided agent runs with measured outcomes.
-->

# Evaluation Kit

This folder turns the README comparison from a qualitative illustration into a measurable experiment.

## Goal

Compare two execution conditions on the same task set:

- `single_prompt`: one direct task prompt with no workflow routing.
- `workflow_guided`: the same task executed through the matching workflow or workflow automation skill.

## Recommended Protocol

1. Build a task set of at least 20 tasks.
2. Use the same repository snapshot, model, tool access, and time budget for both conditions.
3. Run each task 3 to 5 times per condition.
4. Record outcomes as one JSON object per run in a JSONL file.
5. Aggregate the file with `scripts/summarize_results.py`.

## Metrics

- `pass_at_1`: share of tasks whose first run succeeded.
- `pass_hat_k`: share of tasks that succeeded on every repeated run for a condition. This is a strict repeated-run reliability metric.
- `validation_pass_rate`: share of runs where validation commands passed.
- `human_acceptance_rate`: share of runs accepted without manual correction.
- `regression_rate`: share of runs that introduced unrelated regressions.
- `rework_rate`: share of runs that needed another repair pass.
- `requirements_traceability_rate`: share of runs with explicit requirement-to-change or requirement-to-test links in the final output.
- `median_cycle_time_seconds`: median wall-clock time per run.

## Files

- `tasks.sample.json`: sample task manifest.
- `results.sample.jsonl`: sample recorded run data.
- `scripts/summarize_results.py`: aggregates JSONL runs into per-condition metrics.
- `scripts/generate_chart_scores.py`: converts measured metrics into README-style 0-10 chart scores and Mermaid output.

## Result Schema

Each line in `results.jsonl` should be a JSON object with these fields:

```json
{
  "task_id": "bugfix-auth-timeout-001",
  "condition": "workflow_guided",
  "run_id": 1,
  "workflow": "bug-fix",
  "passed": true,
  "validation_passed": true,
  "human_accepted": true,
  "regression": false,
  "rework_required": false,
  "requirements_traceability": true,
  "cycle_time_seconds": 1320
}
```

Required fields:

- `task_id`
- `condition`
- `run_id`
- `passed`
- `validation_passed`
- `human_accepted`
- `regression`
- `rework_required`
- `requirements_traceability`
- `cycle_time_seconds`

Optional fields:

- `workflow`
- `notes`

## Usage

```bash
python3 evaluation/scripts/summarize_results.py evaluation/results.sample.jsonl
```

For machine-readable output:

```bash
python3 evaluation/scripts/summarize_results.py evaluation/results.sample.jsonl --json
```

To generate chart-ready scores:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/results.sample.jsonl
```

To generate a Mermaid chart block directly:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/results.sample.jsonl --mermaid
```

## Notes

- `pass_at_1` is task-based and uses only `run_id == 1`.
- `pass_hat_k` is also task-based and only counts a task as successful when every recorded run for that task and condition passed.
- Lower is better for `regression_rate` and `rework_rate`.
- The chart-score script uses this normalization:
  - `Pass@1` -> `round(pass_at_1 * 10)`
  - `RRC` -> `round(pass_hat_k * 10)`
  - `DER` -> `round((1 - regression_rate) * 10)`
  - `CFR` -> `round((1 - rework_rate) * 10)`
  - `RTM` -> `round(requirements_traceability_rate * 10)`
- This is a display mapping for README charts. If you later capture true defect-escape-rate or change-failure-rate fields, you can replace the `DER` and `CFR` formulas with those direct measurements.
