# Workflow Library Loading Reference

Description: Load the agent-workflows library efficiently by reading only the files needed for the selected workflow.

## Loading Order

1. Find the library root with `scripts/find_workflow_library.py --json`, resolving the script path relative to the skill directory when needed.
   - If needed, set `AGENT_WORKFLOWS_ROOT` to the library root first.
2. Read `README.md` in the library root.
3. Read the minimum shared files required for the workflow:
   - `shared/repository-preflight.md`
   - `shared/safety-rules.md`
   - `shared/workflow-conventions.md`
4. Read the selected workflow file.
5. Open any additional sections only when the workflow requires them.

## File Map

- `project-initialization` -> `project-initialization-agent-workflow.md`
- `feature` -> `feature-development-agent-workflow.md`
- `bug-fix` -> `bug-fix-agent-workflow.md`
- `code-review` -> `code-review-agent-workflow.md`
- `incident` -> `incident-debugging-agent-workflow.md`
- `refactoring` -> `refactoring-agent-workflow.md`
- `tech-debt` -> `tech-debt-cleanup-agent-workflow.md`

## Shared Files by Default

- Project initialization:
Read the matching workflow file, safety rule, workflow conventions, and any target repository or parent workspace preflight instructions referenced by the workflow.

- Feature, bug fix, refactoring, tech debt:
Read the standard coding preflight, the matching safety rule, and workflow conventions.

- Code review:
Read the code review preflight, the review-only rule, and workflow conventions.

- Incident:
Read the incident-response preflight, the incident-response rule, and workflow conventions.

## Loading Discipline

- Do not load every workflow file just because it exists.
- Keep one workflow primary at a time.
- Prefer portable discovery. Do not hard-code user-specific absolute paths into the skill or workflow docs.
- When a hand-off is needed, finish the current workflow step that establishes the hand-off, then load the next workflow file.
- Treat the shared docs as canonical for repeated boilerplate and the workflow file as canonical for task-specific steps.
