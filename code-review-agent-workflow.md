# Code Review Agent Workflow

This document defines a reusable agent workflow for reviewing code changes. The input can be a GitHub pull request link, a branch name, or uncommitted workspace changes.

The workflow is designed for AI coding agents working in a repository. It covers correctness, security, performance, test coverage, maintainability, and compatibility. It produces structured findings and does not apply fixes unless explicitly asked.

## Preflight Repository Check

Use [Code Review Preflight](shared/repository-preflight.md#code-review-preflight) before the triage gate.

## Global Rule

Use [Review-Only Rule](shared/safety-rules.md#review-only-rule) in every review prompt.

## Triage Gate

Before starting, classify the review to select the right level of depth:

```text
Classify this code review into one of the following categories:

1. Quick: Small, low-risk change. Few files, narrow scope, no data model or API impact. Examples: copy fix, config change, test addition, style cleanup, dependency bump.

2. Standard: Moderate change with meaningful logic. Touches multiple files or has user-facing, API, or data impact. Examples: new endpoint, business logic change, permission update, UI feature.

3. Deep: Large or high-risk change. Cross-cutting concerns, schema migrations, security-sensitive code, performance-critical paths, or backward compatibility constraints. Examples: auth changes, payment logic, data migration, new integration, infrastructure change.

Based on the classification:

- Quick: Skip to Step 1 (Review). Focus on correctness and obvious issues. One pass is sufficient if the review confirms the change is truly low-risk. **Escalation check:** if you discover unexpected security, compatibility, migration, performance, or test-risk concerns during the review, stop and reclassify as Standard or Deep before finalizing the assessment.
- Standard: Follow Steps 0 through 2. Cover all review dimensions and report relevant validation commands that were run or skipped.
- Deep: Follow the full workflow from Step 0 through Step 3. Apply extra scrutiny to security, performance, compatibility, and edge cases.

Code to review:

<GitHub PR link, branch name, or "current workspace changes">

Classify this review and recommend which steps to follow.
```

## Step 0: Understand the Context

Use this prompt to build context before reviewing:

```text
Before reviewing the code, understand the context of the change.

Code to review:

<GitHub PR link, branch name, or "current workspace changes">

Your goals:

1. Identify what the change is trying to accomplish.
   - If a GitHub PR link is provided, read the PR title, description, comments, linked issues, and labels.
   - If a branch name is provided, read the commit history and diff against the correct base branch.
   - If reviewing workspace changes, read the diff of all staged and unstaged changes that are in scope for the review.
2. Identify the scope: which files, modules, or subsystems are affected.
3. Determine the type of change: feature, bug fix, refactor, dependency update, configuration, test, documentation, or mixed.
4. Note the blast radius: what existing behavior, callers, consumers, or contracts could be affected.
5. Check if there is a related design document, issue, or specification that defines the expected behavior.
6. Determine whether the comparison base is correct and explicit enough for a reliable review.
   - If reviewing a PR, record the base branch from the PR metadata.
   - If reviewing a branch, record the chosen base branch and why it is the correct comparison target.
   - If reviewing workspace changes, separate the review target from unrelated local edits.
7. If the review target or comparison base is still ambiguous, stop and ask before reviewing.

Do not start reviewing the code yet.
Do not edit code, commit, or push without my explicit permission.

Provide:
- Change summary (what and why)
- Change type
- Files and modules affected
- Blast radius
- Review target and comparison base
- Related context (linked issues, design docs, PR description) if available
```

## Step 1: Review the Code

Use this prompt after context is established (or directly for Quick reviews):

```text
Review the following code change.

Code to review:

<GitHub PR link, branch name, or "current workspace changes">

Context:

<change summary, change type, and blast radius from Step 0 — or a brief description if skipping Step 0>

Review the change across these dimensions. Skip any dimension that clearly does not apply.

### Correctness
- Does the code do what it claims to do?
- Are there logic errors, off-by-one mistakes, wrong conditions, or missing cases?
- Are edge cases handled (nulls, empty inputs, boundary values, concurrent access)?
- Does error handling cover failure modes without swallowing errors silently?

### Security
- Does the change introduce injection risks (SQL, command, XSS, template)?
- Are inputs validated and sanitized at system boundaries?
- Are secrets, tokens, or credentials handled safely (no hardcoding, no logging)?
- Are permissions and authorization checks correct and complete?
- Is sensitive data (PII, credentials, tokens) protected in transit, at rest, and in logs?

### Performance
- Does the change introduce unnecessary database queries, API calls, or loops?
- Are there N+1 query patterns, unbounded iterations, or missing pagination?
- Could the change degrade performance under load or with large datasets?
- Are expensive operations cached, batched, or deferred where appropriate?

### Test Coverage
- Are there tests for the new or changed behavior?
- Do the tests cover the happy path, edge cases, and error cases?
- Would the tests fail if the change were reverted (regression value)?
- Are test assertions specific enough to catch real regressions?
- Are there existing tests that should be updated but were not?

### Maintainability
- Does the code follow existing patterns and conventions in the codebase?
- Are names clear and consistent with the domain language?
- Is the change scoped appropriately, or does it mix unrelated concerns?
- Is there unnecessary complexity, duplication, or abstraction?

### Compatibility
- Does the change break existing API contracts, interfaces, or data formats?
- Is backward compatibility preserved where required?
- Are database migrations safe (reversible, non-locking on large tables, additive before destructive)?
- Are feature flags or rollout gates needed?

For every finding, use this format:

### [Severity] Finding title

- Location: file path and line range
- Problem: what is wrong
- Why it matters: impact if not addressed
- Suggested fix: concrete recommendation
- Severity: Critical / Major / Minor / Nit

Severity definitions:
- Critical: Will cause data loss, security vulnerability, crash, or broken functionality. Must fix before merge.
- Major: Incorrect behavior, missing edge case, or significant risk. Should fix before merge.
- Minor: Code quality, maintainability, or minor correctness issue. Fix is recommended but not blocking.
- Nit: Style, naming, or preference. Optional.

Before finalizing the review:
- If the change appears riskier than the current review category suggests, escalate to Standard or Deep and continue the missing steps before issuing a final assessment.
- Run relevant validation commands when feasible (tests, linters, type checks, targeted review helpers) and report the results.
- If validation cannot be run, say exactly why and limit the confidence of the final assessment accordingly.

Do not edit code, commit, or push without my explicit permission.

At the end, provide:
- Total findings by severity
- Overall assessment: Approve / Approve with minor fixes / Request changes
- One-sentence summary of the most important finding, if any
- Validation commands run and results, or skipped commands with reasons
```

## Step 2: Review Test Coverage in Depth

Use this prompt for Standard and Deep reviews when test coverage needs closer inspection:

```text
Review the test coverage for the following code change.

Code to review:

<GitHub PR link, branch name, or "current workspace changes">

Your goals:

1. List every behavior introduced or changed by this code change.
2. For each behavior, check whether a test exists that:
   - Exercises the behavior directly
   - Would fail if the behavior were removed or broken
   - Covers relevant edge cases
3. Identify missing test scenarios. Be specific: describe the input, the expected behavior, and why it matters.
4. Review existing tests that were modified:
   - Was the modification necessary and correct?
   - Did the modification weaken the test (e.g., loosening assertions, removing cases)?
5. Check for test quality issues:
   - Tests that always pass regardless of implementation (tautological tests)
   - Tests that are brittle (depend on timing, order, or external state)
   - Tests that duplicate coverage without adding value
6. Run relevant existing test commands when feasible to confirm the test suite or targeted tests execute as expected.
7. If tests cannot be run in this environment, say exactly why.

Do not edit code, commit, or push without my explicit permission.

Provide:
- Coverage matrix: behavior vs. test (covered / partially covered / missing)
- Missing test scenarios with suggested test descriptions
- Test quality issues, if any
- Validation commands run and results, or skipped commands with reasons
```

## Step 3: Deep Dive (Security, Performance, or Compatibility)

Use this prompt for Deep reviews when a specific dimension needs extra scrutiny:

```text
Perform a focused deep-dive review on the following code change.

Code to review:

<GitHub PR link, branch name, or "current workspace changes">

Focus area:

<"security" | "performance" | "compatibility" — pick one or specify multiple>

### If security:
1. Trace every external input through the code to its final use. Identify injection points.
2. Check authentication and authorization on every entry point affected by the change.
3. Review error messages and logs for information leakage.
4. Check for timing attacks, TOCTOU issues, or insecure defaults.
5. Verify that secrets management follows project conventions.
6. Check dependencies introduced or updated for known vulnerabilities.

### If performance:
1. Trace the hot path affected by the change. Identify the most expensive operations.
2. Estimate the performance impact under realistic load (typical case and worst case).
3. Check for missing indexes, unoptimized queries, or unnecessary data fetching.
4. Review memory allocation patterns (large objects in loops, unbounded caches, leaked references).
5. Identify whether the change would benefit from profiling or benchmarking before merge.

### If compatibility:
1. List every public API, interface, data format, or contract affected by the change.
2. For each, determine whether the change is additive, breaking, or ambiguous.
3. Check migration safety: can the change be deployed without downtime? Is it reversible?
4. Identify callers or consumers that may break and are not updated in this change.
5. Check whether versioning, deprecation notices, or feature flags are needed.

Use the standard finding format for every issue found.

Also:
- Run relevant validation commands for the chosen focus area when feasible (for example targeted tests, static analysis, security scans, benchmarks, migration checks, or contract checks).
- If a validation step cannot be run, state exactly why.

Do not edit code, commit, or push without my explicit permission.

Provide:
- Findings with severity
- Risk summary for the focus area
- Recommendations for mitigation, if any
- Validation commands run and results, or skipped commands with reasons
```

## Optional: Fix Findings

Use this prompt only when explicitly asked to fix review findings:

```text
Fix the review findings listed below in the current workspace.

Findings to fix:

<paste findings from the review, or "all Critical and Major findings">

Important instructions:

1. Read each finding carefully before editing.
2. Fix only the findings listed. Do not refactor, clean up, or improve surrounding code.
3. Follow existing patterns in the codebase.
4. Add or update tests for any correctness fix.
5. Run relevant tests, linters, and type checks after fixing.
6. Do not commit or push without my explicit permission.
7. If a finding is ambiguous or the fix has side effects, stop and ask before proceeding.
8. After fixing, return to review mode and verify that the targeted findings are resolved before considering the work complete.

At the end, provide:

1. Findings fixed (with file and line)
2. Findings skipped and why
3. Tests added or updated
4. Commands run and results
```

## Post-Fix Re-review

Use this prompt after Optional: Fix Findings:

```text
Re-review the current workspace after the requested review findings were fixed.

Original review target:

<GitHub PR link, branch name, or "current workspace changes">

Findings that were supposed to be fixed:

<paste findings that were fixed>

Your goals:

1. Verify that each targeted finding is actually resolved.
2. Check whether the fixes introduced new correctness, security, performance, compatibility, or test issues.
3. Re-run relevant validation commands.
4. Confirm that no unrelated files were edited while fixing the findings.
5. Report any remaining open findings or newly introduced findings using the standard finding format.

Do not edit code, commit, or push without my explicit permission.

At the end, provide:
- Fixed findings confirmed
- Remaining open findings
- New findings introduced by the fixes, if any
- Validation commands run and results, or skipped commands with reasons
- Overall assessment: Ready / More fixes required
```

Repeat Optional: Fix Findings and Post-Fix Re-review until no unresolved Critical or Major findings remain.

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- Default to review-only. Do not edit code unless the user explicitly asks you to fix findings.
- Use the triage gate to avoid over-processing trivial changes and under-processing risky ones.
- Be specific in findings. "This could be improved" is not actionable. "This SQL query is vulnerable to injection via the `name` parameter on line 42" is.
- Severity matters. Distinguish between "will break production" and "could be slightly cleaner." Reviewers who cry wolf on every nit lose trust.
- When reviewing a GitHub PR, read the full diff, not just the files list. Context lines around the change often reveal missed edge cases.
- Do not review a branch against an assumed base branch. Determine the comparison base explicitly or ask.
- If the change is too large to review effectively in one pass, say so and recommend splitting it. A review that misses issues because of scope is worse than no review.
- If you fix findings, re-review the result before declaring the review complete.
- If the review reveals a design-level concern (wrong approach, not just wrong implementation), flag it early rather than listing dozens of implementation-level findings that would all be moot if the design changes.
