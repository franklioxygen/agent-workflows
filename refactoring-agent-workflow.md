# Refactoring Agent Workflow

This document defines a reusable agent workflow for improving code structure without changing behavior. The input can be a specific refactoring goal, a code smell, a tech debt item, or a module that needs restructuring.

The workflow is designed for AI coding agents working in a repository. The core constraint is: behavior must not change. Every step exists to ensure the refactoring improves the code while preserving existing functionality.

## Preflight Repository Check

Use [Standard Coding Preflight](shared/repository-preflight.md#standard-coding-preflight) before the triage gate.

## Global Rule

Use [Behavior-Preserving Rule](shared/safety-rules.md#behavior-preserving-rule) in every prompt.

## Triage Gate

Before starting, classify the refactoring to select the right level of process:

```text
Classify this refactoring into one of the following categories:

1. Safe: Mechanical change with no behavior risk. Fully covered by existing tests or type checks. Examples: rename variable/function/file, extract a local helper, remove dead code, reorder imports, apply consistent formatting.

2. Moderate: Structural change within a module or a small number of files. Behavior should not change but the transformation is non-trivial. Examples: extract class/module, inline abstraction, replace conditional with polymorphism, consolidate duplicated logic, change function signatures with known callers.

3. Architectural: Cross-cutting structural change that affects module boundaries, data flow, dependency graph, or public interfaces. Examples: split a monolith module, change a shared data structure, replace a pattern across the codebase, migrate to a new abstraction, restructure a directory layout.

Based on the classification:

- Safe: Start at Step 0 (Establish Baseline). If the baseline confirms the change is truly low risk, proceed to Step 3 (Execute). One execution/validation loop is usually sufficient unless the risk increases during the work.
- Moderate: Start at Step 0 (Establish Baseline), then Step 2 (Plan). Use Step 1 (Understand the Current State) if the scope, dependencies, or interfaces are not already clear.
- Architectural: Follow the full workflow from Step 0 through Step 5.

Refactoring goal:

<description of what to refactor and why>

Classify this refactoring and recommend which steps to follow.
```

## Step 0: Establish Baseline

Use this prompt before editing code for any refactoring, including Safe ones:

```text
Establish a validation baseline before refactoring.

Refactoring goal:

<description of what to refactor and why>

Your goals:

1. Identify the validation commands relevant to the affected code:
   - Tests
   - Type checks
   - Linters or format checks
   - Build/package commands
   - Manual smoke tests or targeted runtime checks
2. Run the full relevant validation set now and record the results.
3. Separate the result into:
   - Passing baseline checks
   - Pre-existing failures
   - Missing coverage or validation gaps
4. Determine whether the refactoring is safe to start with the current safety net.
5. If validation coverage is too weak, recommend whether to:
   - Add tests first
   - Reduce the refactoring scope
   - Escalate to a higher-risk workflow path
6. If the refactoring appears broader or riskier than originally classified, say so before any edits are made.

Do not start editing code yet.
Do not commit or push without my explicit permission.

Provide:
- Validation commands to use during the refactoring
- Passing baseline checks
- Pre-existing failures to watch
- Coverage gaps and risks
- Recommended next step
```

The rest of the workflow assumes this baseline is recorded and will be compared against after each execution pass.

## Step 1: Understand the Current State

Use this prompt for Architectural refactorings or when the scope is unclear:

```text
Before planning the refactoring, understand the current state of the code to be changed.

Refactoring goal:

<description of what to refactor and why>

Your goals:

1. Identify the files, modules, classes, and functions affected by the refactoring.
2. Map the dependencies: what depends on the code being refactored, and what does it depend on.
3. Identify the public interfaces (APIs, exports, shared types, database contracts) that must remain stable.
4. Assess existing test coverage for the affected code:
   - Which behaviors are tested?
   - Which behaviors are untested?
   - Are the existing tests testing behavior (safe to refactor around) or implementation details (will break during refactoring)?
5. Identify constraints:
   - Backward compatibility requirements
   - Performance-sensitive paths
   - Code ownership or approval requirements
   - Downstream consumers (other services, packages, or teams)
6. Determine whether the refactoring can be done incrementally or requires a single coordinated change.

Do not start editing code yet.
Do not commit or push without my explicit permission.

Provide:
- Affected files and modules
- Dependency map (what depends on this, what this depends on)
- Public interfaces that must remain stable
- Test coverage assessment
- Constraints and risks
- Whether the refactoring is incremental or coordinated
```

## Step 2: Plan the Refactoring

Use this prompt after the current state is understood (or directly after Step 0 for Moderate refactorings with clear scope):

```text
Create a refactoring plan for the following change.

Refactoring goal:

<description of what to refactor and why>

Current state:

<affected files, dependency map, public interfaces, test coverage, and constraints from Step 1 — or a brief description if skipping Step 1>

Baseline:

<validation commands, baseline results, and coverage gaps from Step 0>

The plan should include:

1. Ordered list of transformation steps. Each step should be:
   - Small enough to verify independently
   - Behavior-preserving on its own (the code should work after each step, not just after all steps)
   - Described as a concrete action ("extract function X from Y", "move file A to B and update imports"), not a vague goal
2. For each step, the validation to run afterward (test suite, type check, linter, manual smoke test).
3. Public interfaces that must remain stable throughout.
4. Tests that may need to change because they test implementation details rather than behavior. Distinguish these from tests that should NOT change (behavior tests — if these break, the refactoring introduced a regression).
5. Any new tests to add before or during the refactoring to increase confidence.
6. Rollback strategy: how to undo the refactoring if it goes wrong partway through.

Do not start editing code yet.
Do not commit or push without my explicit permission.

If the plan reveals that the refactoring is riskier than expected, say so and recommend whether to proceed, reduce scope, or add tests first.
```

## Step 3: Execute the Refactoring

Use this prompt after the plan is clear (or directly after Step 0 for Safe refactorings):

```text
Execute the following refactoring.

Refactoring goal:

<description of what to refactor and why>

Plan:

<ordered transformation steps from Step 2 — or a brief description for Safe refactorings>

Baseline:

<validation commands, baseline results, and coverage gaps from Step 0>

Important instructions:

1. Confirm that the baseline is recorded before making any changes. The baseline may include pre-existing failures, but they must be documented so they are not confused with regressions introduced by the refactoring.
2. If the baseline shows missing coverage, unstable interfaces, or broader dependency impact than expected, stop and escalate to Step 1 or Step 2 before continuing.
3. Execute one transformation step at a time.
4. After each step, run the specified validation (tests, type checks, linters, build checks, smoke tests).
5. If validation fails after a step, stop. Determine whether the failure is:
   - A regression introduced by the refactoring (fix it or revert the step)
   - A test that was testing implementation details (update the test, but document what changed and why)
   - A pre-existing failure unrelated to the refactoring (note it and continue)
6. Do not change observable behavior. If a step requires a behavior change, stop and ask.
7. Do not mix refactoring with feature work, bug fixes, or unrelated cleanup.
8. Follow existing code style and conventions.
9. Do not commit or push without my explicit permission.
10. If you discover that the plan needs adjustment mid-execution, stop and explain before continuing.

Observable behavior includes:
- Return values, side effects, and error behavior of public functions
- API responses (status codes, body shape, headers)
- Database writes (schema, data shape, query behavior)
- UI rendering and user-visible text
- Log output that downstream systems depend on
- Event emissions and message payloads

At the end, provide:

1. Transformation steps completed
2. Files changed
3. Tests updated and why (implementation-detail tests vs. regressions)
4. Validation results after each step
5. Any steps skipped or adjusted, with explanation
```

## Step 4: Validate the Refactoring

Use this prompt after execution is complete or after a repair pass in Step 3:

```text
Validate the completed refactoring against the original goal and recorded validation baseline.

Refactoring goal:

<description of what to refactor and why>

Baseline:

<validation commands, baseline results, and known pre-existing failures from Step 0>

Execution summary:

<completed transformation steps, tests updated, and validation results from Step 3>

Your goals:

1. Re-run the full validation set established in Step 0 and Step 2, if any, then compare results against the recorded baseline.
   - Same passing checks and no new failures: good.
   - New failures: investigate — regression, implementation-detail test, or unrelated issue?
   - Checks skipped now that were part of the baseline or plan: explain why.
   - Tests removed or weakened: justify each removal.
2. Verify that all public interfaces remain stable:
   - Function signatures, return types, error types
   - API contracts
   - Database schemas and query behavior
   - Exports and module boundaries
3. Review the diff for unintended behavior changes:
   - Changed return values or error messages
   - Reordered operations with side effects
   - Altered control flow that affects timing or concurrency
   - Removed or added logging, metrics, or events
4. Verify that the refactoring achieved its stated goal. Did the code actually improve?
5. Check for incomplete transformations: old patterns left behind, inconsistent naming, orphaned files or dead code introduced by the refactoring itself.
6. If the validation shows the refactoring is broader or riskier than originally classified, say so and recommend whether additional planning or scope reduction is needed before continuing.

Do not commit or push without my explicit permission.

Provide:
- Validation results compared to baseline (before vs. after, command by command)
- Public interface stability check (stable / changed — with justification if changed)
- Unintended behavior changes found (none / list)
- Goal achieved (yes / partially / no — with explanation)
- Cleanup needed (none / list)
```

Repeat Step 3 and Step 4 until validation finds no unresolved regressions, unstable interfaces, or incomplete transformations.

Recommended stop condition:

```text
If Step 4 finds new regressions, unintended behavior changes, unstable interfaces, or incomplete transformations, return to Step 3, fix them, and run Step 4 again. Stop when the recorded validation set is acceptable relative to the baseline and no unresolved refactoring risks remain.
```

## Step 5: Final Report

Use this prompt for Architectural refactorings or when a handoff summary is needed after Step 4 is clean:

```text
Produce a final refactoring report.

Refactoring goal:

<description of what to refactor and why>

The report should include:

1. Refactoring summary (what changed and why)
2. Before and after: structural comparison (modules, dependencies, interfaces)
3. Files changed
4. Tests updated, added, or removed (with justification for each removal)
5. Validation results (baseline vs. final, including tests, type checks, lint, build, and smoke checks)
6. Public interfaces: confirmed stable or changed with justification
7. Behavior changes: confirmed none, or documented with justification
8. Incomplete items or follow-up work
9. Confirmation that no commit or push was performed

Do not commit or push without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- The cardinal rule: do not change behavior. If you need to change behavior, that is a feature change or bug fix — use the appropriate workflow.
- Work incrementally. Large refactorings that touch everything at once are hard to validate and hard to revert. Each step should leave the code in a working state.
- Distinguish implementation-detail tests from behavior tests. Refactoring will legitimately break tests that assert on internal structure (mock call counts, private method names, specific SQL strings). These should be updated. Tests that assert on observable behavior should NOT break — if they do, the refactoring changed behavior.
- Do not mix refactoring with other work. A refactoring PR that also fixes a bug or adds a feature is harder to review and harder to revert.
- If the affected code has no tests, seriously consider adding behavior tests before refactoring. Refactoring untested code is high-risk — you have no safety net to catch regressions.
- If the refactoring reveals a design flaw or a bug, document it and handle it separately. Do not fix it as part of the refactoring.
