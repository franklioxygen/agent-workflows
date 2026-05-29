<!--
Function Name: RUBRIC
Description: Operational definitions and scoring decision rules for every binary outcome in the evaluation kit.
-->

# Scoring Rubric

Raters must read this document before scoring any run. Score from the `blinded_artifact` only. If the artifact reveals the condition (e.g., phase headings, tool-banner traces), report it as a blinding leak in `notes` and continue.

For every outcome below, the rule is binary: `true` only when the listed conditions are all met. If unsure, score `false` and explain in `notes`. Conservative defaults reduce inflation.

## passed

**Definition.** The submission meets the task's pre-registered acceptance criteria (in `tasks.jsonl`).

**Score `true` iff:**
- Every acceptance criterion is satisfied by the diff or accompanying artifacts.
- Behavior described in the criteria is verifiable from the diff or logs.

**Score `false` if:**
- Any acceptance criterion is unmet, partially met, or unverifiable.
- The submission solves a *different* problem than the one stated.

**Examples.**
- ✅ Acceptance criteria say "fix logout during slow requests" and the diff modifies the session refresh path with a covering test.
- ❌ Diff adds a UI tweak unrelated to the auth timeout symptom, even if the test suite passes.

## validation_passed

**Definition.** The pre-declared public validation commands and any locked evaluator checks for the task exit zero on the diff applied to the locked `repo_sha`.

**Score `true` iff:**
- The exact commands listed in the task's `validation_commands` ran and exited 0.
- If the task declares `hidden_validation_commands`, those locked evaluator checks also ran and exited 0.
- No public command or locked evaluator check was added, removed, disabled, skipped, or modified by the submission.

**Score `false` if:**
- Any public validation command or locked evaluator check failed.
- The submission disabled, skipped, or modified a validation command or locked evaluator check (including `--no-verify`).
- Commands were not run (artifact does not contain their output).

## human_accepted

**Definition.** The rater would accept the submission as-is in a code review without requesting changes.

**Score `true` iff:**
- No correctness, safety, or style issues that a reasonable reviewer would block on.
- The submission is comprehensible without rater rewriting it mentally.

**Score `false` if:**
- The rater would request changes (even minor blocking ones).
- Critical comments would be required to make the change safe or reviewable.

Cosmetic preferences (e.g., naming style) are not grounds for `false` unless they violate documented project conventions.

## regression

**Definition.** The submission introduces a behavior change *unrelated to the task* that would degrade an existing feature.

**Score `true` iff:**
- A reasonable reader can identify a specific existing behavior that now misbehaves.
- The regression is not a stated tradeoff in the task description.

**Score `false` if:**
- The diff stays within the scope of the acceptance criteria.
- Side effects are explicitly justified by the task.

**Examples.**
- ✅ regression: bug fix narrows session-refresh window but also breaks SSO login flow that was working.
- ❌ no regression: refactor renames a helper used only by the changed module.

**RFR note.** Raters score only the human `regression` field here. The summarized RFR metric also requires `hidden_validation_passed == true` when locked evaluator checks are present in `results.jsonl`, so objective locked-check failures reduce RFR even when the human `regression` flag is `false`.

## rework_required

**Definition.** A second repair pass would be necessary before the change could ship.

**Score `true` iff:**
- The rater can name a specific follow-up change that must happen before shipping (e.g., missing test, missing migration, broken edge case identified in artifact).
- The submission is "almost there" but not complete.

**Score `false` if:**
- The submission is shippable as-is, OR
- The submission is so broken that it would be reverted rather than repaired (score `passed = false` instead).

## requirements_traceability

**Definition.** The artifact contains *explicit* links between each acceptance criterion and (a) the change that implements it and (b) the validation that demonstrates it.

**Score `true` iff:**
- For every acceptance criterion, the diff, validation log, or sanitized agent report identifies the file/region implementing it AND the test/command that validates it.
- Links are explicit (e.g., "criterion 2 → `src/auth/session.ts:142` → `tests/auth/session.test.ts:test_refresh_window`"), not implied.

**Score `false` if:**
- Any criterion lacks an explicit implementation pointer.
- Any criterion lacks an explicit validation pointer.
- The artifact contains only a high-level narrative without specific references.

## Adjudication

If two raters disagree on any outcome:

1. The adjudicator reviews both rationales (in `notes`) and the blinded artifact.
2. The adjudicator selects the final value and records their rationale in `adjudication_notes`.
3. Both original rater scores remain in `raters.jsonl` for κ computation.
4. The adjudicated row in `results.jsonl` carries `adjudicated: true`.

Adjudicators do not score runs they originally rated.

## Blinding Leak Reporting

If the blinded artifact contains a marker that reveals the condition (e.g., a workflow phase heading, a tool-name banner, a known prompt-template token), the rater must:

1. Stop scoring that run.
2. Add a `blinding_leak` entry to `notes` describing the marker.
3. Submit the run to be re-blinded.

Runs with blinding leaks that cannot be re-blinded are excluded from the primary analysis and reported separately.
