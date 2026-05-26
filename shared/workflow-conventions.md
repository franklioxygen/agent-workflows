# Shared Workflow Conventions

Description: Cross-workflow operating conventions reused by the agent-workflows workflow documents.

These are the common expectations that show up across multiple workflows. Keep workflow-specific steps in the individual workflow documents; keep the shared operating rules here.

## Workspace Safety

- Run the relevant preflight before triage so repo instructions, workspace state, and unrelated local changes are known up front.
- Do not overwrite, revert, or reformat unrelated user changes.
- Keep each unit of work small enough to review, validate, and revert independently.

## Scope and Escalation

- Keep changes scoped to the current task or review target.
- If the task becomes broader, riskier, or more ambiguous than expected, stop and reclassify, re-plan, or ask before continuing.
- If the work requires a design decision, behavior change, or unrelated cleanup, switch to the appropriate workflow instead of improvising inside the current one.

## Validation and Baselines

- For code-changing workflows, establish and record a baseline when feasible before editing so regressions can be separated from pre-existing failures.
- Re-run the planned validation set after each logical unit of work and again at the end.
- Use the full validation set that matters for the task, not just tests: type checks, lint, build or package checks, usage checks, smoke tests, audits, or targeted runtime checks when relevant.

## Reporting and Handoff

- Always report which commands or validation steps were run, which passed, which failed, and which were skipped with a reason.
- Separate pre-existing failures from failures introduced by the current work.
- If a follow-up validation or re-review step exists in the workflow, repeat the execute or fix step and the validation or re-review step until blocking issues are resolved or the workflow explicitly stops.

## Review Quality

- Prefer specific, evidence-backed findings over vague comments.
- If the issue is design-level, flag it early instead of burying it under implementation-level details that may become irrelevant.
- Use the structured finding format for all findings in review and validation steps:

```
### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed / Needs decision
```

Severity definitions:
- Critical: Will cause data loss, security vulnerability, crash, or broken functionality. Must fix before merge.
- Major: Incorrect behavior, missing edge case, or significant risk. Should fix before merge.
- Minor: Code quality, maintainability, or minor correctness issue. Fix is recommended but not blocking.
- Nit: Style, naming, or preference. Optional.

## Workflow Hand-off

- Use one primary workflow at a time. Do not mix workflow steps from different workflows in a single pass.
- If a task crosses workflow boundaries (e.g., a bug fix reveals a design flaw, or a cleanup requires a behavior change), complete or pause the current workflow step and hand off explicitly to the next workflow.
- State the hand-off reason when switching: what was discovered, why the current workflow is no longer appropriate, and which workflow to continue with.
- Common hand-off paths:
  - Incident -> Bug Fix: after mitigation and evidence capture, if the remaining work is a normal code fix.
  - Bug Fix -> Feature: if diagnosis reveals a design or product-decision problem, not a narrow defect.
  - Tech Debt -> Refactoring: if the cleanup resolves into a behavior-preserving structural change on a specific area.
  - Tech Debt or Refactoring -> Feature: if the work requires a behavior change, public contract change, or design decision.
  - Code Review -> Fix workflow: if the user explicitly asks to address findings and the findings reveal a feature, bug, or refactor task.
