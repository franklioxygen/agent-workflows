# Technical Debt / Cleanup Agent Workflow

This document defines a reusable agent workflow for addressing technical debt, cleanup tasks, dependency upgrades, dead code removal, test coverage gaps, and TODO items. The input can be a specific debt item, a category of debt to survey, or a broad cleanup goal.

The workflow is designed for AI coding agents working in a repository. It differs from refactoring in scope and intent:
- Refactoring: restructure specific code to improve design while preserving behavior.
- Tech debt cleanup: survey, prioritize, and resolve accumulated issues across the codebase — dead code, outdated dependencies, missing tests, stale TODOs, inconsistent patterns, deprecated APIs.

Tech debt work is high-risk for scope creep. Every step emphasizes scoping, prioritization, and incremental completion.

## Preflight Repository Check

Use [Standard Coding Preflight](shared/repository-preflight.md#standard-coding-preflight) before the triage gate.

Add this workflow-specific preflight check before continuing:

- Check for existing tech debt tracking (TODO comments, issue labels, debt backlogs, deprecation notices) to avoid duplicating known work.

## Global Rule

Use [Cleanup Rule](shared/safety-rules.md#cleanup-rule) in every prompt.

## Triage Gate

Before starting, classify the cleanup to select the right level of process:

```text
Classify this tech debt / cleanup task into one of the following categories:

1. Targeted: A specific, well-defined cleanup item. Scope is clear, risk is low. Examples: remove a single dead file, delete unused imports, fix a specific TODO, update one deprecated API call, remove a feature flag that has been fully rolled out.

2. Scoped: A bounded cleanup effort across multiple files or a module. Scope is defined but requires surveying. Examples: remove all usages of a deprecated utility, add missing tests for a module, consolidate duplicated validation logic, upgrade a specific dependency across the codebase.

3. Survey: The scope is not yet defined. The goal is to assess the state of tech debt in an area or across the codebase before deciding what to clean up. Examples: "what tech debt do we have?", "audit test coverage gaps", "find all deprecated API usages", "what TODOs are in the codebase?"

Based on the classification:

- Targeted: Start at Step 1 (Establish Baseline). If the baseline confirms the task is truly small and low risk, proceed to Step 3 (Execute). One execution/validation loop is usually sufficient unless the risk increases during the work.
- Scoped: Start at Step 1 (Establish Baseline), then Step 2 (Plan). Use Step 0 (Assess) first if the scope still needs surveying or prioritization.
- Survey: Start at Step 0 (Assess). End with the Survey Report. Do not change code unless asked.

Cleanup task:

<description of the tech debt or cleanup goal>

Classify this task and recommend which steps to follow.
```

## Step 0: Assess the Debt

Use this prompt for Survey tasks or when the scope of a cleanup is unclear:

```text
Assess the technical debt in the area described below. Do not change any code.

Cleanup goal:

<description of the area or category to assess>

Your goals:

1. Survey the codebase for the specified category of debt. Common categories:
   - Dead code (unused functions, unreachable branches, orphaned files, commented-out code)
   - Deprecated APIs or patterns (internal or external)
   - TODO / FIXME / HACK comments
   - Missing or inadequate test coverage
   - Outdated dependencies (major version behind, known vulnerabilities, unmaintained)
   - Inconsistent patterns (same thing done differently in different places)
   - Stale configuration (unused env vars, dead feature flags, obsolete build targets)
   - Documentation drift (docs that no longer match the code)
2. For each item found, record:
   - Location (file and line)
   - Category
   - Description (what the debt is)
   - Risk if left unaddressed (what could go wrong, or what cost it imposes)
   - Effort estimate (trivial / small / medium / large)
   - Dependencies (does fixing this require fixing something else first?)
3. Group the items by category.
4. Recommend a priority order based on:
   - Risk (security, correctness, data integrity issues first)
   - Effort-to-value ratio (quick wins before large efforts)
   - Dependencies (unblock other cleanups first)
   - Blast radius (isolated changes before cross-cutting ones)

Do not change any code.
Do not commit or push without my explicit permission.

Provide:
- Inventory of debt items, grouped by category
- Priority recommendations
- Items that should NOT be cleaned up (load-bearing hacks, intentional workarounds, changes that would require a design decision)
- Recommended next step: which items to tackle first, and whether to use the Targeted or Scoped path
```

## Survey Report

Use this prompt after Step 0 for Survey tasks that do not change code:

```text
Produce a tech debt survey report.

Cleanup goal:

<original assessment goal>

Assessment summary:

<inventory of debt items, grouped categories, priorities, and exclusions from Step 0>

The report should include:

1. Inventory summary by category
2. Highest-priority debt items and why they are prioritized
3. Items that should NOT be cleaned up yet, and why
4. Dependencies or sequencing constraints between debt items
5. Recommended next step:
   - Which item or group to tackle first
   - Whether the next pass should use the Targeted or Scoped path
6. Confirmation that no code was changed
7. Confirmation that no commit or push was performed

Do not change code.
Do not commit or push without my explicit permission.
```

## Step 1: Establish Baseline

Use this prompt before editing code for any Targeted or Scoped cleanup:

```text
Establish a validation baseline before starting the cleanup.

Cleanup goal:

<description of the cleanup task>

Your goals:

1. Identify the validation commands relevant to the cleanup:
   - Tests
   - Type checks
   - Linters or format checks
   - Build/package commands
   - Usage checks (grep, search, import/export verification, dependency graph checks)
   - Manual smoke tests or targeted runtime checks
2. Run the relevant validation set now and record the results.
3. Separate the result into:
   - Passing baseline checks
   - Pre-existing failures
   - Missing coverage or validation gaps
4. Determine whether the cleanup is safe to start with the current safety net.
5. If the baseline reveals broader scope, weak coverage, or behavior risk, recommend whether to:
   - Reduce the scope
   - Add tests or checks first
   - Reclassify the task from Targeted to Scoped or Survey
6. Record any special checks needed for the cleanup category:
   - Dead code removal: usage verification and dynamic-reference checks
   - Dependency upgrades: changelog review, migration guide review, audit/security checks
   - TODO/FIXME cleanup: issue creation or tracking if the item is too large to resolve now

Do not start editing code yet.
Do not commit or push without my explicit permission.

Provide:
- Validation commands to use during cleanup
- Passing baseline checks
- Pre-existing failures to watch
- Coverage gaps and risks
- Recommended next step
```

The rest of the workflow assumes this baseline is recorded and will be compared against after each execution pass.

## Step 2: Plan the Cleanup

Use this prompt for Scoped tasks after the scope is understood:

```text
Create a cleanup plan for the following tech debt.

Cleanup goal:

<description of the cleanup, and inventory from Step 0 if available>

Baseline:

<validation commands, baseline results, and coverage gaps from Step 1>

The plan should include:

1. Items to clean up, in execution order. For each item:
   - What to change
   - Files affected
   - Why this item is included (not just "it's old" — what cost does it impose?)
   - Risk: could this change break something? What assumptions does the existing code rely on?
   - Validation: how to confirm the cleanup is safe (tests, type checks, grep for usages)
2. Items explicitly excluded from this cleanup, and why (out of scope, requires a design decision, too risky without more tests, intentional workaround).
3. Dependency order: items that must be done before others.
4. Recorded baseline validation: which checks from Step 1 will be used to detect regressions.
5. Scope boundary: a clear statement of what this cleanup WILL and WILL NOT touch. If scope creep is likely, name the specific temptations to avoid.

Do not start editing code yet.
Do not commit or push without my explicit permission.

If the plan reveals items that are riskier than expected or require design decisions, flag them and recommend handling them separately.
```

## Step 3: Execute the Cleanup

Use this prompt after the plan is clear (or directly after Step 1 for Targeted tasks):

```text
Execute the following tech debt cleanup.

Cleanup task:

<specific items to clean up, from the plan or a targeted description>

Baseline:

<validation commands, baseline results, and coverage gaps from Step 1>

Important instructions:

1. Confirm that the baseline is recorded before making changes. The baseline may include pre-existing failures, but they must be documented so they are not confused with regressions introduced by the cleanup.
2. If the baseline or early investigation shows the task is broader or riskier than expected, stop and reclassify to the Scoped or Survey path before continuing.
3. Execute one cleanup item at a time.
4. After each item, run the full validation planned for that item (tests, type checks, linters, build checks, usage checks, dependency-specific checks, smoke tests).
5. If validation fails after a cleanup item:
   - Determine whether the failure is a regression (revert or fix) or a pre-existing issue (note and continue).
   - Do not proceed to the next item until the current item is clean.
6. Do not change observable behavior unless explicitly asked. Cleanup means removing waste, not changing how things work.
7. Do not expand scope. If you discover additional debt while cleaning, note it for later — do not fix it now. If the new finding materially changes the current task, stop and re-plan instead of improvising.
8. For dead code removal:
   - Verify the code is actually unreachable (grep for usages, check dynamic references, check reflection, check configuration-driven dispatch).
   - If uncertain, flag it rather than deleting it.
9. For dependency upgrades:
   - Check changelogs and migration guides for breaking changes.
   - Run the relevant validation set after each upgrade, not just after all upgrades.
   - If a dependency upgrade requires code changes, include them in the same logical unit.
10. For TODO / FIXME resolution:
   - Resolve the TODO if the fix is clear and scoped.
   - If the TODO describes a larger task, convert it to an issue or flag it — do not attempt a large fix as part of cleanup.
11. Do not commit or push without my explicit permission.

At the end, provide:

1. Items completed
2. Items skipped and why
3. Files changed
4. Validation results after each item
5. New debt discovered during cleanup (for future work, not for this session)
6. Commands run and results
```

## Step 4: Validate the Cleanup

Use this prompt after execution is complete or after a repair pass in Step 3:

```text
Validate the completed tech debt cleanup.

Cleanup summary:

<items cleaned up, files changed, validation results after each item, and items skipped>

Baseline:

<validation commands, baseline results, and known pre-existing failures from Step 1>

Your goals:

1. Re-run the full validation set established earlier in the workflow (from Step 1 and Step 2, if any), then compare results against the recorded baseline.
   - Same passing checks and no new failures: good.
   - New failures: investigate — regression or pre-existing?
   - Checks skipped now that were part of the baseline or plan: explain why.
   - Tests removed: justify each removal (were they testing dead code that was removed?).
2. Verify that no observable behavior changed:
   - Public APIs, interfaces, and contracts are unchanged
   - No user-facing behavior was altered
   - No log formats, metric names, or event shapes were changed without intent
3. Verify that the cleanup is complete within its stated scope:
   - Are there leftover references to removed code?
   - Are there inconsistencies introduced by partial cleanup?
   - Are imports, exports, and configurations updated to reflect removals?
4. Check for cleanup artifacts:
   - Empty files or modules that should be deleted
   - Orphaned test files for removed code
   - Stale comments referencing removed code
   - Unused imports left behind
5. If the validation shows the task is broader or riskier than originally scoped, say so and recommend re-planning before continuing.

Do not commit or push without my explicit permission.

Provide:
- Validation results compared to baseline (before vs. after, command by command)
- Behavior change check (none / list)
- Completeness check (complete / incomplete items listed)
- Cleanup artifacts found (none / list)
- Overall assessment: clean / needs follow-up
```

Repeat Step 3 and Step 4 until validation finds no unresolved regressions, behavior changes, incomplete cleanup, or cleanup artifacts that are still in scope.

Recommended stop condition:

```text
If Step 4 finds regressions, unexpected behavior changes, incomplete cleanup, or cleanup artifacts that should still be fixed within scope, return to Step 3, fix them, and run Step 4 again. Stop when the recorded validation set is acceptable relative to the baseline and the scoped cleanup is complete.
```

## Step 5: Cleanup Report

Use this prompt for Targeted or Scoped cleanup tasks when a summary is needed after Step 4 is clean:

```text
Produce a tech debt cleanup report.

Cleanup goal:

<original description of the cleanup>

The report should include:

1. Cleanup summary (what was done and why)
2. Items completed, with files changed
3. Items skipped and why
4. Validation results (baseline vs. final, including tests, type checks, lint, build, usage checks, and smoke checks)
5. Observable behavior: confirmed unchanged, or documented exceptions with justification
6. New debt discovered during cleanup (items for future work)
7. Recommendations for follow-up work, ordered by priority
8. Confirmation that no commit or push was performed

Do not commit or push without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- Tech debt cleanup is where scope creep lives. The plan step exists specifically to draw a boundary. "While I'm in here, I might as well..." is the sentence that turns a 30-minute cleanup into a 3-hour refactor.
- Not all debt should be paid. Some workarounds are load-bearing. Some deprecated patterns are stable and low-risk. Some TODOs describe work that was deliberately deferred. The assessment step should identify items that should NOT be cleaned up, not just items that should.
- Dead code is only dead if nothing references it. Check for dynamic dispatch, reflection, configuration-driven routing, external consumers, and test-only usage before deleting.
- Dependency upgrades are not free. A major version bump can introduce breaking changes, behavior differences, or new vulnerabilities. Treat each upgrade as its own unit with its own validation.
- If a cleanup item turns out to require a design decision, stop. Design decisions belong in the feature development workflow, not in a cleanup session.
- If a cleanup item turns out to be a behavior change, stop. Use the bug fix workflow (if it's a bug) or the feature development workflow (if it's a feature change).
- Track new debt discovered during cleanup. Cleanup often reveals more debt. Record it for future work instead of acting on it immediately.
- Use the Survey Report for assessment-only work. Do not force code-change validation language onto a survey with no edits.
