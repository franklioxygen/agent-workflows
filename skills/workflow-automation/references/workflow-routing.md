# Workflow Routing Reference

Description: Route a user request to the correct agent-workflows document and know when to hand off between workflows.

## Primary Workflow Selection

- `project-initialization-agent-workflow.md`
Use for new projects, greenfield codebases, initial repository scaffolds, choosing initial tooling, package manager setup, baseline README/.gitignore/configuration, and initial scaffold validation.

- `feature-development-agent-workflow.md`
Use for new capabilities, product behavior changes, cross-file features, new APIs, migrations, permissions, rollout work, or any task that needs design before coding.

- `bug-fix-agent-workflow.md`
Use when something is broken, incorrect, regressed, or failing and the goal is to restore correct behavior.

- `code-review-agent-workflow.md`
Use when the user asks for a review of code, a pull request, a branch, or workspace changes, and the default behavior should be read-only findings.

- `incident-debugging-agent-workflow.md`
Use for production or live-environment failures, alerts, outages, data corruption, degraded performance, or post-incident root cause analysis.

- `refactoring-agent-workflow.md`
Use when the goal is structural improvement with no intended behavior change.

- `tech-debt-cleanup-agent-workflow.md`
Use for cleanup, dead code removal, dependency upgrades, TODO/FIXME resolution, debt surveys, and general hygiene work that is broader than a single refactor.

## Hand-off Rules

- Incident -> Bug Fix
Use the incident workflow until impact is mitigated and evidence is captured. If the remaining work is a normal code fix, continue with the bug-fix workflow.

- Bug Fix -> Feature
If the diagnosis reveals a design or product-decision problem rather than a narrow defect, switch to the feature workflow.

- Tech Debt -> Refactoring
If the cleanup resolves into a behavior-preserving structural change on a specific area, the refactoring workflow is often the better primary path.

- Tech Debt or Refactoring -> Feature
If the work requires a behavior change, public contract change, or design decision, stop treating it as cleanup or refactoring and move to the feature workflow.

- Code Review -> Fix
Stay in the review workflow unless the user explicitly asks to address findings. If asked to fix them, continue from the fix path inside the review workflow or switch to the more specific coding workflow if the findings reveal a feature, bug, or refactor task.

## Ambiguity Handling

- Ask one short clarifying question only when the choice of workflow would materially change the action you take.
- If the ambiguity is low-risk, choose the most likely workflow, state the assumption, and proceed.
- If the user names a workflow explicitly, use it unless it is clearly unsafe.
