---
name: project-initialization
description: Bootstrap new projects and greenfield repositories using the agent-workflows project initialization workflow. Use when Codex is asked to create a new project, initialize a repository, scaffold a greenfield codebase, choose initial tooling, set up package management, create baseline README/.gitignore/configuration, or validate an initial scaffold.
---

<!--
Function Name: project-initialization
Description: Codex skill instructions for bootstrapping new projects with the project initialization workflow.
-->

# Project Initialization

## Quick Start

- Find the nearest `agent-workflows` library. If it is not near the workspace, ask for `AGENT_WORKFLOWS_ROOT` or the library path.
- Read `project-initialization-agent-workflow.md`.
- Read [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Apply the workflow directly. Do not just restate prompt templates unless the user explicitly asks for templates.
- Require an explicit target directory before creating files.

## Operating Rules

- Use this skill for new projects, greenfield codebases, initial repository scaffolds, and project tooling setup.
- Treat the workflow file as the source of truth for preflight, triage, planning, scaffolding, validation, and handoff.
- Run the workflow's preflight before triage so target-directory state, parent workspace rules, local instructions, available tooling, and unrelated local changes are known.
- For Minimal projects, scaffold directly with sensible defaults after confirming the target directory.
- For Standard and Complex projects, follow the plan/review/scaffold/validate/handoff sequence in the workflow.
- Do not commit or push without explicit permission.
- Do not overwrite, revert, delete, or reformat unrelated user changes.
- Stop and ask if the target directory is missing, ambiguous, or unexpectedly pre-populated.

## Execution Guidance

1. Confirm the target directory and inspect its current state.
2. Load and follow the triage gate from `project-initialization-agent-workflow.md`.
3. Select the appropriate path:
   - Minimal: use the Minimal Project Prompt.
   - Standard: gather requirements, create/review the plan, then scaffold and validate.
   - Complex: complete the full workflow with separate review and validation passes.
4. When scaffolding, keep generated files inside the confirmed target directory.
5. Validate with the ecosystem's relevant install, lint, type check, build, test, and smoke commands.
6. Report files created, tooling configured, validation results, deviations, known limitations, and next steps.

## References

- [../../project-initialization-agent-workflow.md](../../project-initialization-agent-workflow.md)
- [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md)

## Handoff

- If the initialized project is ready for feature work, hand off to the feature development workflow.
- If validation exposes a narrow defect in the scaffold, fix it inside this workflow.
- If validation exposes a larger design or technology decision, return to the project plan before changing the scaffold.
