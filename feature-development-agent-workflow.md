# Feature Development Agent Workflow

This document defines a reusable agent workflow for moving a medium-to-large feature from requirements intake to design, review, implementation, validation, and final handoff.

The workflow is designed for AI coding agents working in a repository. It is intended for features with meaningful ambiguity, cross-file changes, user-facing behavior, data model impact, API impact, permissions, migrations, rollout risk, or non-trivial testing needs. For small bug fixes or narrowly scoped changes, use a lighter workflow instead of forcing every step.

It emphasizes requirement clarity, careful design, structured review, scoped implementation, test coverage, final validation, and avoiding unauthorized commits or pushes.

## Preflight Repository Check

Use [Standard Coding Preflight](shared/repository-preflight.md#standard-coding-preflight) before the triage gate.

## Triage Gate

Before starting the workflow, classify the change to select the right level of process:

```text
Classify this change into one of the following categories:

1. Small: Single-file or narrowly scoped change. Low ambiguity. No data model, API, permission, or migration impact. Examples: bug fix, copy change, config update, adding a straightforward utility.

2. Medium: Cross-file change with some ambiguity. May touch data models, APIs, or user-facing behavior, but the scope is well understood. Examples: adding a new API endpoint, extending an existing feature, adding a new validation rule.

3. Large: Significant ambiguity, cross-cutting concerns, or high risk. Involves data migrations, permission changes, new integrations, backward compatibility constraints, or rollout risk. Examples: new feature with schema changes, auth system changes, billing logic, multi-service coordination.

Based on the classification:

- Small: Use the Small-Change Implementation Prompt below instead of Steps 0 through 6. Write a brief description of the change and acceptance criteria inline. Run validation commands afterward.
- Medium: Start at Step 0 (Clarify Requirements). The design document (Step 1) can omit sections marked "if any" that do not apply. One design review pass (Step 2) is sufficient if no Critical or Major issues are found. Steps 3 and 4 can run in the same session, but do not edit code until the implementation plan is presented first.
- Large: Follow the full workflow from Step 0 through Step 6.

Change description:

<brief description of the change>

Classify this change and recommend which steps to follow.
```

## Global Rule

Use [Standard Coding Rule](shared/safety-rules.md#standard-coding-rule) in every implementation or review prompt.

## Small-Change Implementation Prompt

Use this prompt for `Small` changes from the triage gate instead of Steps 0 through 6:

```text
Implement the following small, low-risk change without creating a full design document.

Change description:

<brief description of the change>

Acceptance criteria:

<acceptance criteria>

Important instructions:

1. Inspect the existing codebase and follow existing patterns.
2. Keep the change scoped to the described task.
3. If you discover ambiguity, cross-file risk, data model impact, API impact, permission impact, migration impact, or rollout risk, stop and recommend switching to the full feature workflow.
4. Add or update tests when the change affects behavior.
5. Run relevant validation commands.
6. Do not commit or push without my explicit permission.
7. Do not overwrite or revert unrelated workspace changes.

At the end, provide:

1. Files changed
2. Behavior implemented
3. Tests added or updated
4. Commands run and results
5. Known risks or follow-ups
```

## Step 0: Clarify Requirements

Use this prompt before creating a design document:

```text
Review the feature requirements below and inspect the existing codebase enough to identify ambiguity, missing context, and implementation risk.

Requirements:

<feature overview>
<execution logic 1, 2, 3...>
<acceptance criteria>

Your goals:

1. Determine whether the requirements are clear enough to design safely.
2. Identify requirements that affect data models, API contracts, user-facing behavior, security, privacy, permissions, migrations, billing, logging, backward compatibility, or rollout risk.
3. Separate the result into:
   - Confirmed requirements
   - Inferred assumptions
   - Open questions
4. Ask clarifying questions before finalizing the design when an answer could change product behavior, API behavior, schema shape, permission logic, migration strategy, or compatibility.
5. Do not create the design document yet unless the requirements are clear enough and any remaining assumptions are low risk.

Do not commit or push without my explicit permission.

If the requirements are clear enough, say so and provide the confirmed requirements, inferred assumptions, and any low-risk open questions.

If the requirements are not clear enough, ask only the questions needed to unblock the design.
```

## Step 1: Create the Design Document

Use this prompt after requirements are clear enough:

```text
Create a detailed feature design document for the requirements below.

Write the document as Markdown. Place it in a `reports/` folder if one exists, or in whatever location the repository uses for design documents. If no convention is obvious, create a `reports/` folder.
Use a clear filename that includes the feature name and current date, for example:

`reports/<feature-name>-design-YYYY-MM-DD.md`

The document should include:

1. Feature Overview
2. Confirmed Requirements
3. Goals and Non-goals
4. Current Behavior / Existing System Context
5. Proposed Design
6. Execution Logic
   - Step-by-step flow
   - Edge cases
   - Error handling
   - Data validation
7. API / Interface Changes, if any
8. Database / Schema Changes, if any
9. UI / UX Changes, if any
10. Security / Privacy / Permission Considerations, if any
11. Backward Compatibility Considerations, if any
12. Testing Plan
13. Rollout / Migration Plan, if any
14. Assumptions and Dependencies
15. Open Questions
16. Implementation Checklist
17. Definition of Done

Omit any "if any" section that does not apply to this feature. Do not fill sections with placeholder or filler content.

Requirements:

<feature overview>
<confirmed requirements>
<execution logic 1, 2, 3...>
<acceptance criteria>

If any proposed logic has a better approach, revise it and explain why.

If anything is unclear or risky, list it under “Open Questions” and ask me before making assumptions.

Record every assumption explicitly. Do not treat a guess as a requirement.

The design should be detailed enough that another engineer can implement it directly without needing additional context.

Do not commit or push without my explicit permission.

Now begin.
```

### Recommended Definition of Done

Add this section to every design document:

```markdown
## Definition of Done

- Feature behavior matches the confirmed requirements.
- Acceptance criteria are covered.
- Edge cases are handled.
- Security, privacy, and permission considerations are addressed.
- Tests are added or updated.
- Relevant validation commands pass.
- No unresolved Open Questions affect implemented behavior.
- No unrelated files are changed.
- Design checklist is fully marked complete.
- Known limitations are documented.
```

## Step 2: Review the Design Document

After the design document is created, start a new session and use this prompt:

```text
There is a feature design document at:

<path-to-design-document>

Review the design carefully.

Your goals:

1. Check whether the design is complete and ready for implementation.
2. Identify missing requirements, unclear logic, edge cases, compatibility risks, security risks, privacy risks, permission risks, migration risks, or testing gaps.
3. Verify that the proposed design fits the existing codebase and does not introduce unnecessary risk.
4. Classify each finding by severity:
   - Critical: must fix before implementation
   - Major: should fix before implementation
   - Minor: improvement or cleanup
   - Question: needs product or engineering clarification
5. For factual corrections and clearly missing sections, update the document directly.
6. For product decisions, API behavior, schema changes, permission behavior, migration strategy, or tradeoff decisions, add them as Review Findings or Open Questions instead of silently changing the design.
7. If you make changes, add or update a “Review Findings” section explaining what changed and why.

Use this format for every finding:

### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed / Needs decision

Do not implement the feature yet.
Do not commit or push without my explicit permission.

If the document is already ready for implementation, clearly say so and do not make unnecessary edits.
```

Repeat this step in new sessions until the reviewer finds no meaningful issues.

Recommended stop condition:

```text
Stop repeating review sessions when two consecutive independent reviews find no Critical or Major issues.
```

## Step 3: Create Implementation Plan

Once the design document is stable, use this prompt before editing code:

```text
There is a finalized feature design document at:

<path-to-design-document>

Read the design document and inspect the existing codebase. Before editing code, provide a concise implementation plan.

The plan should include:

1. Files likely to change
2. Existing patterns to follow
3. Tests to add or update
4. Validation commands to run
5. Any unresolved Open Questions that would block implementation
6. Any security, privacy, permission, migration, or compatibility risks to watch during implementation

Do not implement any part of the feature that depends on unresolved Open Questions.
Do not commit or push without my explicit permission.

If the plan reveals ambiguity or risk, stop and ask for clarification before editing code.
If the plan does not reveal blocking ambiguity or risk, present the plan and then wait for explicit approval before continuing to Step 4.
```

## Step 4: Implement the Feature

Use this prompt after the implementation plan is clear:

```text
There is a finalized feature design document at:

<path-to-design-document>

This prompt assumes a finalized design document already exists. For `Small` changes from the triage gate, use the Small-Change Implementation Prompt instead.

Begin implementing the feature according to the design and implementation plan.

Important instructions:

1. Read the design document carefully before editing code.
2. Inspect the existing codebase and follow existing patterns.
3. Create a new branch if the repository workflow allows it; otherwise, explain why you are staying on the current branch.
4. Implement the feature step by step.
5. Do not implement any part of the feature that depends on unresolved Open Questions.
6. Keep changes scoped to this feature.
7. Do not commit or push without my explicit permission.
8. Add or update tests based on the testing plan.
9. Run relevant tests, linters, and type checks where available.
10. If you discover a design issue during implementation, stop and document it before choosing a solution.
11. Update the implementation checklist only after meaningful milestones or at the end of implementation. Avoid noisy checklist-only edits.

Quality bar:

This feature must be production-ready. Be careful with compatibility, edge cases, error handling, security, privacy, permissions, migrations, and test coverage.

At the end, provide:

1. Files changed
2. Behavior implemented
3. Tests added or updated
4. Commands run and results
5. Known risks or follow-ups

Now begin.
```

## Step 5: Review Workspace Changes

After implementation, start a new session and use this prompt:

```text
Review the current workspace changes against the design document at:

<path-to-design-document>

Your goals:

1. Compare the implementation against the design.
2. Identify any missing functionality, incorrect behavior, edge cases, regressions, security risks, privacy risks, permission gaps, migration risks, or test gaps.
3. Review the changed files carefully.
4. Classify each finding by severity:
   - Critical: must fix before merge
   - Major: should fix before merge
   - Minor: improvement or cleanup
   - Question: needs product or engineering clarification
5. If you find issues, document them in the design document under “Implementation Review Findings.”
6. Fix the issues if they are safe and clearly within scope.
7. Run relevant validation commands after fixing.
8. Do not commit or push without my explicit permission.

Use this format for every finding:

### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed / Needs decision

If there are no issues, say that the implementation matches the design and list what validation was performed.
```

Repeat this review in new sessions until no issues are found.

Recommended stop condition:

```text
Stop repeating implementation review sessions when two consecutive independent reviews find no Critical or Major issues.
```

## Step 6: Final Validation / Handoff

Use this prompt after implementation reviews are complete:

```text
Perform final validation for the implemented feature using the design document at:

<path-to-design-document>

Produce a final validation report with:

1. Requirement coverage
2. Acceptance criteria coverage
3. Files changed
4. Tests added or updated
5. Commands run and results
6. Known risks
7. Manual QA checklist
8. Items intentionally not implemented
9. Confirmation that no commit or push was performed

Also verify:

1. No unresolved Open Questions affect implemented behavior.
2. Security, privacy, and permission considerations were addressed or explicitly marked not applicable.
3. Validation commands relevant to the repository were run or skipped with a clear reason.

Do not commit or push without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- Use the design document as the source of truth throughout the workflow.
- Use this full workflow for medium-to-large features. For small, low-risk changes, prefer a lighter process with clear requirements, scoped implementation, and validation.
- Treat open questions as blockers unless the answer is obvious from the existing codebase.
- Do not implement behavior that depends on unresolved Open Questions.
- Prefer specific findings over vague comments.
- Use the structured finding format for design reviews and implementation reviews.
- Avoid silent design changes for product decisions, API behavior, schema changes, permission behavior, migration strategy, or tradeoff decisions.
- Avoid noisy checklist-only edits. Update checklists after meaningful milestones or at the end of implementation.
- Avoid emotional pressure in prompts. A clear quality bar and concrete validation steps produce better results.
