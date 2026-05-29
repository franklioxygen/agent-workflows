<!--
Function Name: PREREGISTRATION
Description: Pre-registration template — fill in completely and freeze before any task is run.
-->

# Pre-Registration

Fill in every section before running any task. Commit this file to a tag (e.g., `prereg-YYYYMMDD-<study>`) so the registration is immutable. Deviations after this point become **exploratory** analyses and must be reported as such.

## Study Identifier

- **Study id**: `study-YYYYMMDD-<short-name>`
- **Date filed (UTC)**: `YYYY-MM-DD`
- **Filed by**: `<name or handle>`
- **Kit version**: `<semver of evaluation/ at registration>`

## Hypotheses

Primary directional expectations (tested with two-sided paired permutation tests):

- **H1 (TPR)**: …
- **H2 (RP@k)**: …
- **H3 (RFR)**: … Specify whether RFR includes locked evaluator checks via `hidden_validation_passed`.

Secondary (two-sided, descriptive unless separately corrected):

- **H4 (CPR)**: …
- **H5 (NRR)**: …

Each hypothesis must include: outcome metric, direction, and the operational definition (cite `RUBRIC.md`).

## Conditions

- `single_prompt` description: …
- `workflow_guided` description (workflow name + version): …

The prompt template for each condition is fixed at version `<prompt_template_version>` and committed to the study tag.

## Task Set

- **Source**: `<external bug tracker / corpus / etc.>`
- **Inclusion criteria**: …
- **Exclusion criteria**: …
- **Sampling procedure**: `<random / stratified by category × difficulty>`
- **N tasks**: `<≥ 30>`
- **Stratification**:
  - bug-fix: …
  - feature: …
  - refactor: …
  - incident: …
  - migration: …
- **Difficulty distribution**: `<S / M / L counts>`
- **Tasks file (frozen)**: `tasks.<study_id>.json` (committed to study tag).

## Runs

- **k runs per (task, condition)**: `<≥ 3, recommended 5>`
- **Run order randomization seed**: `<integer>`
- **Randomization procedure**: `<blocked by task × condition × run / other, with rationale>`
- **Fresh context for every run**: yes / no, with rationale.
- **Same runner for all conditions**: yes / no, with rationale.

## Environment Lock

- `model_id`: …
- `model_provider`: …
- `model_parameters`: `<temperature, top_p, seed if available>`
- `repo_sha`: …
- `tool_access`: …
- `time_budget_seconds`: …
- `prompt_template_version`: …
- `agent_harness_version`: …
- `kit_version`: …

If any field changes mid-study, the study is split and re-reported as two separate studies.

## Scoring Protocol

- Rater pool ids: …
- Raters per run: `<≥ 2>`
- Adjudicator id(s): …
- Blinding pipeline version: …
- Rubric version (commit hash): …
- κ threshold for primary outcomes: `0.6`
- Blinding leak handling rule: exclude from confirmatory analysis / re-blind before scoring.

Raters do not score runs they personally executed. Adjudicators do not adjudicate runs they originally rated.

## Analysis Plan

- Point estimate method: empirical proportion / median.
- CI method: bootstrap, 10,000 resamples, percentile interval, seed = `<integer>`.
- Paired comparison: paired permutation test, 10,000 permutations, seed = `<integer>`.
- Multiple-comparison correction: Holm–Bonferroni across primary hypotheses.
- Significance level: α = 0.05 family-wise.
- Reliability computed per outcome per condition; report raw agreement and κ. Use Cohen's κ for a fixed two-rater design and Fleiss' κ for rotating raters. Report 95% bootstrap CI on κ.
- Minimum detectable effect for TPR: …
- Minimum detectable effect for RP@k: …
- Minimum detectable effect for RFR: …
- RFR locked-check basis: `<human regression only / human regression + hidden_validation_passed>`.
- Sample-size or pilot-variance rationale: …

## Stopping Rules

- Stop scoring early only if: `<pre-registered futility / safety / budget rule>`
- Do not add tasks after registration unless the addition is reported as a separate exploratory analysis.
- Do not revise the rubric after seeing condition summaries. If rubric revision is necessary, open a new pre-registered scoring round and report the original reliability issue.

## Deviations Log

Record every deviation with timestamp and rationale. Any item here moves the corresponding hypothesis from confirmatory to exploratory in the final report.

| Date | Field changed | From → To | Rationale |
| --- | --- | --- | --- |
|  |  |  |  |

## Sign-off

- Principal investigator: …
- Methodologist reviewer: …
- Date frozen (UTC): …
- Commit hash of this registration: …
