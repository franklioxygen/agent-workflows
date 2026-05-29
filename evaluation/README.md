<!--
Function Name: README
Description: Pre-registered evaluation protocol for comparing single-prompt and workflow-guided agent runs with blinded scoring, repeated runs, and statistical analysis.
-->

# Evaluation Kit

A pre-registered, two-condition, paired-task experimental protocol for comparing single-prompt and workflow-guided agent execution. The protocol is intended to be defensible under empirical-software-engineering review when the report follows the design, blinding, reliability, and power rules below.

## 1. Purpose and Scope

This kit answers one question with measurable evidence:

> Holding the model, tooling, time budget, repository snapshot, task set, and scoring rubric constant, does workflow-guided execution produce better engineering outcomes than single-prompt execution on representative tasks?

This is a *process intervention* study, not a benchmark of model capability. The kit avoids claims about absolute model performance and reports paired differences between the two conditions on the same tasks.

The method is confirmatory only if the task set, hypotheses, randomization, scoring rubric, and analysis plan are frozen before runs begin. If any of those are changed after looking at outcomes, the affected claims are exploratory.

## 2. Hypotheses (Pre-Register Before Runs)

Pre-register every hypothesis in [`PREREGISTRATION.template.md`](PREREGISTRATION.template.md) before running any task. Adding or changing hypotheses after seeing results invalidates the confirmatory analysis.

Primary directional expectations, tested with two-sided paired permutation tests:

- **H1 (TPR)**: Task Pass Rate is higher for `workflow_guided`.
- **H2 (RP@k)**: Reliable Pass@k is higher for `workflow_guided`.
- **H3 (RFR)**: Regression-Free Rate, including locked regression/evaluator checks when present, is higher for `workflow_guided`.

Secondary outcomes, two-sided and not used for primary claims:

- **H4 (CPR)**: Clean Pass Rate differs between conditions.
- **H5 (NRR)**: No-Rework Rate differs between conditions.

The raw scoring fields still include validation, human acceptance, traceability, and cycle time for audit and reliability checks, but they are not reported as comparison metrics.

## 3. Experimental Design

| Element | Choice | Rationale |
| --- | --- | --- |
| Conditions | `single_prompt`, `workflow_guided` | The intervention is the workflow scaffolding. |
| Design | Within-task paired | Same tasks under both conditions controls for task difficulty. |
| Tasks per study | Pre-registered power target, minimum 30 | The 30-task floor is not a power analysis; it is only a minimum. |
| Runs per (task, condition) | k = 5 recommended; k >= 3 minimum | Captures stochastic variance and supports reliability estimates. |
| Stratification | category x difficulty | Prevents one task type or difficulty from dominating the study. |
| Randomization | Blocked randomization across task x condition x run | Controls order, fatigue, and temporal drift. |
| Context isolation | Fresh agent context per run | Prevents cross-run learning or contamination. |
| Environment | Locked per study | Model, parameters, tool access, repo SHA, prompt templates, and harness version. |

### 3.1 Evaluation Modes

The runner supports two modes. Pick one before running and record it in the environment.

- **`controlled`**: both conditions receive the same task description, acceptance criteria, and public validation commands. This is the default and is the strongest design for isolating the effect of reading the workflow document.
- **`workflow-lift`**: `single_prompt` receives only a terse issue-style brief and public validation commands, while `workflow_guided` receives the issue brief, workflow document, full acceptance criteria, and final-report expectations. This mode evaluates the practical lift from a complete workflow packet over a naive prompt. It is appropriate for demos, sensitivity studies, and process-adoption evidence, but it must not be described as isolating the workflow document alone.

Use `controlled` for confirmatory claims. Use `workflow-lift` when the goal is to show whether the workflow package improves outcomes on tasks where diagnosis, blast-radius checks, tests, and handoff quality matter.

### 3.2 Task Selection

- Source tasks from an **external** authoritative list, such as an issue tracker, public bug corpus, prior PRs, or customer-reported tickets. The workflow designer must not author the task set.
- Pre-register inclusion criteria, exclusion criteria, and the random or stratified sampling procedure.
- Stratify by `category` (`bug-fix`, `feature`, `refactor`, `incident`, `migration`) and `difficulty` (`S`, `M`, `L`).
- Reject tasks where ground-truth acceptance criteria cannot be defined before execution.
- Freeze task prompts, acceptance criteria, validation commands, and known acceptance tests before either condition runs.
- Exclude tasks that appear in prompt examples, workflow examples, or training/evaluation material used by either condition when that exposure is known.

### 3.3 Discriminative Task Design

Simple one-line fixes usually saturate both conditions. To measure workflow value, include tasks that require at least two of the following:

- root-cause diagnosis before editing,
- a reproduction artifact or failing test,
- related-code-path or blast-radius review,
- a regression test that would fail before the fix,
- cross-file implementation,
- explicit requirement-to-change and requirement-to-test traceability,
- final handoff evidence that a reviewer can audit.

For `workflow-lift` studies, each task may define:

- `brief_prompt`: the terse issue report shown to `single_prompt` and `workflow_guided`;
- `acceptance_criteria`: the full criteria shown only to `workflow_guided` in `workflow-lift` mode;
- `validation_commands`: public commands shown to both conditions and run by the harness;
- `hidden_validation_commands`: locked evaluator checks not shown in either prompt, run by the harness after the agent finishes.

`hidden_validation_commands` are for objective evaluator coverage, not for changing the task after seeing outputs. They must be frozen with the task manifest and reported as locked evaluator checks. When present, these checks also contribute to RFR so the regression-protection metric is based on the same hidden acceptance surface for both conditions, not only on rare human-scored unrelated regressions.

### 3.4 Environment Lock

Every result row carries an `env` block. Studies are only valid for the environment recorded:

```json
"env": {
  "model_provider": "example-provider",
  "model_id": "example-model-2026-05-01",
  "model_parameters": {
    "temperature": 0.2,
    "top_p": 1.0,
    "seed": null
  },
  "repo_sha": "abc1234",
  "tool_access": ["read", "edit", "bash:test"],
  "time_budget_seconds": 1800,
  "prompt_template_version": "v3.1",
  "agent_harness_version": "v1.4.0",
  "kit_version": "2.1.0"
}
```

If any field changes mid-study, split the dataset and report it as a separate study. A vendor-stable model name is not enough by itself; record the model revision or date-stamped id whenever the provider exposes one.

## 4. Outcome Measurement (Blinded, Two Raters)

All human outcome scoring is **blinded** and uses **two independent raters per run**. Without this, evaluator confirmation bias can dominate the results.

### 4.1 Rubric

Operational definitions live in [`RUBRIC.md`](RUBRIC.md). Do not score runs without first reading the rubric. Each binary outcome (`passed`, `validation_passed`, `human_accepted`, `regression`, `rework_required`, `requirements_traceability`) has a written definition, decision rule, and examples.

### 4.2 Blinding Protocol

1. The runner produces a `run_artifact` containing the final diff, validation logs, and transcript for each run.
2. The runner extracts the final Claude Code report, strips condition labels, workflow document paths, and obvious workflow markers, then includes the sanitized report in the `blinded_artifact`.
3. Raters score only the `blinded_artifact` against the rubric. They never see `condition`.
4. Rater ids and timestamps are recorded; raters must not score runs they personally executed.
5. Runs with unfixable blinding leaks are excluded from the confirmatory analysis and reported separately.

### 4.3 Two Raters and Reconciliation

- Each run is scored independently by >= 2 raters drawn from a pool of >= 3.
- Inter-rater reliability is reported per binary outcome and condition. The summarizer reports raw agreement plus Cohen's kappa for a fixed two-rater design and Fleiss' kappa for rotating raters.
- Because kappa can be unstable when one class is rare, reports must include the raw positive rate for each outcome and must not rely on kappa alone.
- Disagreements are resolved by a third blinded adjudicator. The adjudicated value is the final score; both original rater scores remain in `raters.jsonl` for reliability analysis.
- If kappa < 0.6 on any primary outcome, the study is flagged as low-reliability and primary claims are not confirmatory. Revising the rubric after seeing outcomes requires a new pre-registered scoring round; do not silently replace the original scoring.

## 5. Metrics

All metrics are point estimates accompanied by 95% bootstrap confidence intervals. Paired comparisons also include a paired permutation-test p-value. Point estimates without intervals are not reported.

### Primary

- **Task Pass Rate (TPR)**: for each task and condition, the mean of `passed` over all k repeated runs; the study estimate is the mean of task-level rates. This is the primary quality endpoint.
- **Reliable Pass@k (RP@k)**: share of task-condition pairs where every pre-registered run passed. This measures robust success at the chosen k; it is not a generic consistency metric because all-fail outcomes do not count as reliable success.
- **Regression-Free Rate (RFR)**: share of runs with no human-scored unrelated regression and, when `hidden_validation_passed` is present, all locked evaluator checks passing. This is summarized as a task-weighted mean. If locked checks are absent, RFR falls back to the human `regression` outcome and should be interpreted as a weaker safety signal.

### Secondary

- **Clean Pass Rate (CPR)**: share of runs that satisfy `passed`, `validation_passed`, `regression == false`, and `rework_required == false`, summarized as a task-weighted mean.
- **No-Rework Rate (NRR)**: 1 - share of runs that required a repair pass, summarized as a task-weighted mean.

### Metric Naming Notes

Earlier versions used `RRC` for "Repeated-Run Consistency". That name was misleading because the metric counted only all-pass task-condition pairs. The protocol now calls it **Reliable Pass@k (RP@k)**.

Earlier versions also labeled two chart metrics `DER` (defect escape rate) and `CFR` (change failure rate). Those are industry terms with specific production meanings. The evaluation actually measures regression-free rate and no-rework rate inside controlled runs, so the chart labels are `RFR` and `NRR`.

## 6. Result Schema

Each row in `results.jsonl` is one (task, condition, run) triple **after rater adjudication**. Raw per-rater rows live in `raters.jsonl` (one row per rater per run).

Example row (including optional `workflow` and `notes`):

```json
{
  "task_id": "bugfix-auth-timeout-001",
  "condition": "workflow_guided",
  "workflow": "bug-fix",
  "run_id": 1,
  "run_order": 17,
  "env": {
    "model_provider": "example-provider",
    "model_id": "example-model-2026-05-01",
    "model_parameters": {
      "temperature": 0.2,
      "top_p": 1.0,
      "seed": null
    },
    "repo_sha": "abc1234",
    "tool_access": ["read", "edit", "bash:test"],
    "time_budget_seconds": 1800,
    "prompt_template_version": "v3.1",
    "agent_harness_version": "v1.4.0",
    "kit_version": "2.1.0"
  },
  "artifact_path": "artifacts/bugfix-auth-timeout-001/wg/run1/",
  "blinded_artifact_path": "artifacts/blinded/run-0017.diff",
  "passed": true,
  "validation_passed": true,
  "human_accepted": true,
  "regression": false,
  "rework_required": false,
  "requirements_traceability": true,
  "public_validation_passed": true,
  "hidden_validation_passed": true,
  "cycle_time_seconds": 1320,
  "adjudicated": false,
  "rater_ids": ["r1", "r2"],
  "notes": null
}
```

Optional fields: `workflow`, `notes`, `run_started_at_utc`, `public_validation_passed`, `hidden_validation_passed`. The result builder preserves public and hidden validation metadata from `runs.jsonl`; the summarizer uses `hidden_validation_passed` in RFR when present. All other fields above are required by the protocol and validated by the loader.

`raters.jsonl` carries one row per (run, rater) with the rater's independent scores. The summarizer reads `raters.jsonl` to compute inter-rater reliability.

## 7. Analysis Plan

The analysis plan is fixed before scoring begins. Deviations must be reported as exploratory, not confirmatory.

### 7.1 Point Estimates and CIs

For each metric and condition:

- Point estimate: empirical proportion or median over task-level values.
- Run-level outcomes are first reduced to a per-task rate so every task has equal weight.
- 95% CI: bootstrap with 10,000 resamples over tasks.
- Report k for every repeated-run metric. RP@k values are not comparable across studies with different k.

### 7.2 Paired Comparisons

Because the same tasks appear in both conditions, comparisons are paired:

- Compute per-task difference `delta_task = metric(workflow) - metric(single)`.
- Report mean `delta` with 95% bootstrap CI over tasks.
- Significance: two-sided paired permutation test with 10,000 permutations over per-task condition labels.
- Multiple-comparison correction: Holm-Bonferroni across the family of primary hypotheses only.
- Secondary p-values are descriptive unless a separate family and correction are pre-registered.

### 7.3 Reliability

- Report raw agreement and kappa per binary outcome, per condition.
- Use Cohen's kappa for a fixed two-rater design and Fleiss' kappa for rotating raters. If a later implementation supports missing-data reliability directly, Krippendorff's alpha may be reported as an additional check.
- Study is marked **low-reliability** if any primary-outcome kappa < 0.6.
- Low reliability downgrades primary claims to exploratory unless a new blinded scoring round is pre-registered before viewing condition summaries.

### 7.4 Power and Sample Size

Before running the study, pre-register:

- the minimum detectable effect for each primary metric,
- the assumed task-level variance or pilot dataset used for planning,
- the target number of tasks,
- k repeated runs per task-condition pair,
- the stopping rule.

The summarizer emits a `power_warning` field when:

- tasks per condition < 30,
- runs per (task, condition) < 3, or
- the half-width of any primary 95% CI exceeds +/-0.15.

The warning is a precision check, not a substitute for prospective power planning. Studies with `power_warning = true` may be reported but must not be used for primary-hypothesis claims.

## 8. Threats to Validity

A defensible study must state and acknowledge these.

**Construct validity**

- Binary outcomes (`passed`, `regression`, etc.) are proxies for real-world quality. Mitigated by written rubric, blinding, two raters with reliability reporting, and objective locked evaluator checks for RFR when available.
- `requirements_traceability` measures the presence of links, not the correctness of those links, so it is secondary.
- RP@k measures robust all-pass success at a fixed k, not all forms of stochastic consistency.

**Internal validity**

- Workflow designer must be separate from the rater pool.
- Raters are blinded to condition; blinding leaks are excluded from primary analysis.
- Run order is randomized with a pre-registered seed.
- Each run uses a fresh context and cannot see prior outputs for the same task.
- Same time budget, tool access, prompt-template version, and validation commands are used for both conditions.

**External validity**

- A task set sampled from one repository, organization, or issue source does not generalize to all engineering work without replication.
- Results are valid only for the recorded environment. Re-running with a different model revision, tool set, harness, or repository SHA is a new study.

**Conclusion validity**

- Bootstrap CIs and paired permutation tests are nonparametric and robust to non-normal task-level differences.
- Holm-Bonferroni corrects for multiple primary hypotheses.
- Low sample size, wide CIs, low inter-rater reliability, or post-hoc metric changes downgrade claims to exploratory.

## 9. Files

- [`README.md`](README.md): this protocol.
- [`RUBRIC.md`](RUBRIC.md): operational definitions and scoring decision rules.
- [`PREREGISTRATION.template.md`](PREREGISTRATION.template.md): pre-registration form to fill before runs.
- [`tasks.sample.json`](tasks.sample.json): example task manifest with stratification fields.
- [`results.sample.jsonl`](results.sample.jsonl): example adjudicated results.
- [`raters.sample.jsonl`](raters.sample.jsonl): example per-rater scores for reliability computation.
- [`scripts/run_claude_code_study.py`](scripts/run_claude_code_study.py): runs real Claude Code single-prompt and workflow-guided conditions and writes artifacts for blinded scoring.
- [`scripts/build_results_from_ratings.py`](scripts/build_results_from_ratings.py): combines real run metadata, blinded rater scores, and adjudications into final `results.jsonl`.
- [`scripts/summarize_results.py`](scripts/summarize_results.py): summary with CIs, paired tests, reliability, and power warnings.
- [`scripts/generate_chart_scores.py`](scripts/generate_chart_scores.py): chart-ready scores and SVG output with honest metric labels.

## 10. Usage

### 10.1 Run a Real Claude Code Study

Use a frozen task manifest with real tasks for the target repository. The sample task file is only a schema example; it is not a valid empirical study.

```bash
python3 evaluation/scripts/run_claude_code_study.py evaluation/tasks.<study_id>.json \
  --repo /path/to/target/repo \
  --output-dir evaluation/studies/<study_id> \
  --runs-per-condition 5 \
  --model sonnet \
  --max-budget-usd 50
```

The runner writes:

- `evaluation/studies/<study_id>/runs.jsonl`: real run metadata and objective validation results.
- `evaluation/studies/<study_id>/runs/*/artifact/`: prompt, Claude output, sanitized agent report, diff, validation log, status, and metadata.
- `evaluation/studies/<study_id>/blinded/*.md`: condition-stripped packets for raters, including diff, validation logs, and sanitized agent report.

Do **not** feed `runs.jsonl` directly to `summarize_results.py`; it is not adjudicated scoring data. Raters must score the blinded packets using [`RUBRIC.md`](RUBRIC.md), then the study owner must produce `raters.jsonl` and any needed `adjudications.jsonl`.

### 10.2 Run a Workflow-Lift Stress Study

Use this mode when the goal is to make the workflow advantage visible on tasks that require more than a direct code edit.

```bash
python3 evaluation/scripts/run_claude_code_study.py evaluation/tasks.<study_id>.json \
  --repo /path/to/target/repo \
  --output-dir evaluation/studies/<study_id> \
  --runs-per-condition 3 \
  --prompt-mode workflow-lift \
  --prompt-template-version claude-code-runner-v2-workflow-lift \
  --model sonnet \
  --max-budget-usd 50
```

Interpretation rule: `workflow-lift` results compare a terse baseline prompt against the full workflow package. They can support a practical adoption claim such as "the workflow packet produced better outcomes than a naive prompt on this stress suite"; they should not be worded as "the workflow document alone caused the difference."

Build adjudicated real results. This step preserves `public_validation_passed` and `hidden_validation_passed` from `runs.jsonl` so RFR remains comparable across conditions when locked checks are declared:

```bash
python3 evaluation/scripts/build_results_from_ratings.py \
  --runs evaluation/studies/<study_id>/runs.jsonl \
  --raters evaluation/studies/<study_id>/raters.jsonl \
  --adjudications evaluation/studies/<study_id>/adjudications.jsonl \
  --output evaluation/studies/<study_id>/results.jsonl
```

Omit `--adjudications` only when every rater score agrees for every binary outcome.

Once scoring is complete, summarize real results:

```bash
python3 evaluation/scripts/summarize_results.py evaluation/studies/<study_id>/results.jsonl \
  --raters evaluation/studies/<study_id>/raters.jsonl
```

Generate a real study chart:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/studies/<study_id>/results.jsonl \
  --raters evaluation/studies/<study_id>/raters.jsonl --svg \
  --title "Measured Outcome Comparison" \
  --subtitle "Study <study_id>" \
  --output assets/estimated-outcome-comparison.svg
```

### 10.3 Sample Data Smoke Tests

Markdown table summary with CIs and warnings:

```bash
python3 evaluation/scripts/summarize_results.py evaluation/results.sample.jsonl \
  --raters evaluation/raters.sample.jsonl
```

Machine-readable JSON with full statistics:

```bash
python3 evaluation/scripts/summarize_results.py evaluation/results.sample.jsonl \
  --raters evaluation/raters.sample.jsonl --json
```

Sample chart scores with honest labels:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/results.sample.jsonl
```

Regenerate the English sample SVG chart:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/results.sample.jsonl \
  --raters evaluation/raters.sample.jsonl --svg \
  --title "Sample Outcome Comparison" \
  --subtitle "Sample data from evaluation/results.sample.jsonl" \
  --description "Grouped bar chart of sample evaluation scores for Single Prompt and Workflow-Guided on TPR, RP@k, CPR, RFR, and NRR, produced by evaluation/scripts/generate_chart_scores.py." \
  --output assets/estimated-outcome-comparison.svg
```

Regenerate the Simplified Chinese sample SVG chart:

```bash
python3 evaluation/scripts/generate_chart_scores.py evaluation/results.sample.jsonl \
  --raters evaluation/raters.sample.jsonl --svg \
  --title "样例结果对比" \
  --subtitle "样例数据来自 evaluation/results.sample.jsonl" \
  --description "分组柱状图，对比 Single Prompt 与 Workflow-Guided 在 TPR、RP@k、CPR、RFR、NRR 上的样例分数，由 evaluation/scripts/generate_chart_scores.py 计算得到。" \
  --y-label "分数" \
  --output assets/estimated-outcome-comparison.zh-cn.svg
```

## 11. Reporting Checklist

A study is reportable only when all of the following hold. Each item must be cited in the final report.

- [ ] Pre-registration filed before any task was run.
- [ ] Primary hypotheses, MDEs, task count, k, and stopping rule frozen before execution.
- [ ] >= 30 tasks and >= 3 runs per (task, condition).
- [ ] Tasks sampled from an external source with stated inclusion and exclusion criteria.
- [ ] Task prompts, acceptance criteria, validation commands, and scoring rubric frozen before execution.
- [ ] `env` block identical, modulo timestamps, for every row in a study.
- [ ] Fresh context used for every run.
- [ ] Run order randomized with a recorded seed.
- [ ] Scoring blinded to `condition` for every rater.
- [ ] >= 2 raters per run; raw agreement and kappa reported for every binary outcome.
- [ ] No primary-outcome kappa below 0.6.
- [ ] Bootstrap 95% CIs reported for every metric.
- [ ] Paired permutation p-values reported for every primary hypothesis.
- [ ] Holm-Bonferroni correction applied across primary hypotheses.
- [ ] Threats to validity discussed.
- [ ] Raw artifacts and `raters.jsonl` released or archived with access constraints stated.

Anything less is exploratory.
