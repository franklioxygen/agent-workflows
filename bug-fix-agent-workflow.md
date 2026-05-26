# Bug Fix Agent Workflow

This document defines a reusable agent workflow for diagnosing and fixing bugs. The input can be a bug description, a GitHub issue link, or an error log.

The workflow is designed for AI coding agents working in a repository. It is lighter than the feature development workflow because bug fixes have a narrower scope: understand the problem, find the root cause, fix it, and verify the fix.

## Preflight Repository Check

Use [Standard Coding Preflight](shared/repository-preflight.md#standard-coding-preflight) before the triage gate.

## Global Rule

Use [Standard Coding Rule](shared/safety-rules.md#standard-coding-rule) in every prompt.

## Triage Gate

Before starting, classify the bug to select the right level of process:

```text
Classify this bug into one of the following categories:

1. Obvious: The root cause is clear from the description. The fix is a small, localized change. Examples: typo, wrong constant, missing null check, off-by-one error, incorrect config value.

2. Moderate: The symptom is clear but the root cause requires investigation. The fix likely touches 1-3 files. Examples: incorrect query logic, missing validation, wrong event handler, race condition with a known trigger.

3. Complex: The symptom is vague or intermittent, the root cause is unclear, or the fix has cross-cutting impact. Examples: data corruption, intermittent failures, performance degradation, issues involving multiple services or subsystems.

Based on the classification:

- Obvious: Use Step 2 (Fix) with the root cause and failing reproduction inline. Do not edit code until the reproduction requirement below is satisfied.
- Moderate: Start at Step 1 (Diagnose). Keep investigation focused.
- Complex: Follow the full workflow from Step 0 through Step 4.

Bug report:

<bug description, GitHub issue link, or error log>

Classify this bug and recommend which steps to follow.
```

## Reproduction Requirement

Before editing code, establish one of the following:

- A failing automated test that captures the bug
- A failing command or script that reproduces the bug
- Clear manual reproduction steps with evidence of the current failure
- An explicit explanation of why direct reproduction is not feasible (stating the specific technical reason), plus the best available evidence. "Not feasible" means the bug depends on production data, third-party state, or infrastructure that cannot be simulated locally — not that reproduction would take effort

The rest of the workflow assumes this reproduction artifact exists and can be reused during validation.

## Step 0: Understand the Bug

Use this prompt when the bug comes from a GitHub issue link or a vague report:

```text
Review the bug report below and inspect the existing codebase enough to understand the problem.

Bug report:

<bug description, GitHub issue link, or error log>

Your goals:

1. Summarize the reported behavior and the expected behavior.
2. Identify the affected area of the codebase (files, modules, endpoints, UI components).
3. Determine the reproduction path if one is described or can be inferred.
4. Separate the result into:
   - Confirmed facts (what we know from the report and codebase)
   - Hypotheses (possible root causes, ranked by likelihood)
   - Missing information (what we would need to confirm the root cause)
5. If the bug report is a GitHub issue link, also extract:
   - Related comments, linked PRs, labels, or assignees that add context
   - Any reproduction steps provided by the reporter

Do not start fixing the bug yet.
Do not commit or push without my explicit permission.

If the bug is clear enough to diagnose, say so and provide your ranked hypotheses.
If critical information is missing, list the specific questions needed to proceed.
```

## Step 1: Diagnose the Root Cause

Use this prompt after the bug is understood:

```text
Investigate the root cause of the following bug in the codebase.

Bug summary:

<confirmed behavior, expected behavior, affected area, and hypotheses from Step 0 — or a clear bug description if skipping Step 0>

Your goals:

1. Reproduce the reported behavior with a failing test, failing command, or documented manual evidence when feasible.
2. Trace the code path involved in the reported behavior.
3. Identify the exact root cause. Do not guess — follow the code.
4. Explain why the current code produces the incorrect behavior.
5. Identify whether the root cause is:
   - A logic error
   - A missing check or validation
   - A data issue (wrong input, stale state, migration gap)
   - A race condition or timing issue
   - A dependency or integration issue
   - A configuration issue
6. Identify the minimal set of files that need to change.
7. Check whether the bug has related symptoms elsewhere (same pattern repeated in other places, other callers of the same function, shared utilities with the same flaw).
8. Assess blast radius: could the fix break existing behavior, other callers, or downstream consumers?

Do not start fixing the bug yet.
Do not commit or push without my explicit permission.

Provide:
- Reproduction artifact (or explanation of why direct reproduction is not feasible)
- Root cause explanation
- Files involved
- Blast radius assessment
- Recommended fix approach
- Any risks or edge cases the fix must handle
```

## Step 2: Fix the Bug

Use this prompt after the root cause is confirmed:

```text
Fix the following bug based on the diagnosis below.

Bug summary:

<root cause explanation, files involved, recommended fix approach, and risks from Step 1 — or a clear description if skipping earlier steps>

Important instructions:

1. Read the relevant code carefully before editing.
2. Confirm that the reproduction requirement is satisfied before making code changes. If direct reproduction is not feasible, document why and use the best available evidence.
3. Follow existing patterns in the codebase.
4. Keep changes scoped to the bug fix. Do not refactor, clean up, or improve surrounding code.
5. Fix the root cause, not the symptom.
6. If the same bug pattern exists in related code paths (identified in diagnosis), fix those too — but only if they share the same root cause.
7. Add or update tests that cover:
   - The exact scenario that triggered the bug
   - Edge cases related to the fix
   - Regression prevention (the test should fail without the fix and pass with it)
8. Run relevant tests, linters, and type checks where available.
9. Do not commit or push without my explicit permission.
10. If you discover the root cause is different from what was diagnosed, stop and explain before proceeding.

At the end, provide:

1. Root cause (one sentence)
2. What was changed and why
3. Files changed
4. Reproduction used before the fix
5. Tests added or updated
6. Commands run and results
7. Anything the fix does NOT address (known limitations, related issues)
```

## Step 3: Validate the Fix

Use this prompt after the fix is applied:

```text
Validate the bug fix applied in the current workspace.

Bug summary:

<original bug description>

Root cause:

<root cause explanation>

Your goals:

1. Verify the fix addresses the root cause, not just the symptom.
2. Check that the fix does not introduce regressions in related code paths.
3. Review the changed files for correctness, edge cases, and unintended side effects.
4. Verify tests cover the bug scenario and would fail without the fix.
5. Run relevant validation commands (tests, linters, type checks).
6. Check that no unrelated files were changed.
7. Re-run the reproduction artifact from earlier in the workflow and confirm it now passes or no longer reproduces.

If you find issues, classify each by severity:

- Critical: must fix before merge
- Major: should fix before merge
- Minor: improvement or cleanup

Use this format for every finding:

### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed

Do not commit or push without my explicit permission.

If the fix is correct and complete, say so and list what validation was performed.
```

Repeat Step 3 and Step 2 as needed until no Critical or Major issues remain.

Recommended stop condition:

```text
If Step 3 finds issues, return to Step 2, fix them, and then run Step 3 again. Stop repeating the loop when a validation pass finds no Critical or Major issues.
```

## Step 4: Final Report

Use this prompt for complex bugs or when a handoff summary is needed after Step 3 is clean:

```text
Produce a final bug fix report for the following bug:

Bug summary:

<original bug description or GitHub issue link>

The report should include:

1. Bug summary (reported behavior vs. expected behavior)
2. Root cause
3. Fix description
4. Files changed
5. Tests added or updated
6. Commands run and results
7. Blast radius assessment (what else could be affected)
8. Known limitations or follow-ups
9. Confirmation that no commit or push was performed

Do not commit or push without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- Use the triage gate to avoid over-processing simple bugs.
- Establish the reproduction artifact before editing code. If direct reproduction is not feasible, explicitly say why and record the best available evidence.
- Fix the root cause, not the symptom. If the symptom disappears but the underlying logic is still wrong, the bug will return.
- A bug fix is not a refactoring opportunity.
- If the same bug pattern repeats elsewhere, fix all instances — but only if they share the same root cause. Otherwise, file them as separate issues.
- If the diagnosis reveals a design flaw rather than a code bug, escalate to the feature development workflow instead of patching around it.
