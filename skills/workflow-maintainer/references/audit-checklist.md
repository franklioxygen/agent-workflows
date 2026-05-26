<!--
Function Name: audit-checklist
Description: Review checklist for maintaining agent-workflows documentation, routing, skills, and scripts.
-->

# Workflow Maintainer Audit Checklist

## Blocking Checks

- Required workflow files exist and are named consistently.
- Required shared files exist: `repository-preflight.md`, `safety-rules.md`, and `workflow-conventions.md`.
- Markdown links and heading anchors resolve.
- README inventory lists all workflow files, shared files, and bundled skills.
- Workflow routing and library-loading references match actual filenames.
- Automation scripts do not return successful manifests for incomplete libraries.
- Skill folders have valid `SKILL.md` frontmatter with `name` matching the folder.
- Each installable skill has one canonical agent metadata file: `agents/interface.yaml`.
- Legacy per-agent metadata files, such as `agents/openai.yaml` and `agents/claude.yaml`, are not present.
- Skill agent default prompts mention the literal `$skill-name`.

## Design Checks

- Workflow-specific content does not duplicate shared rules unnecessarily.
- Safety language is consistent across prompts and shared rules.
- Triage gates route small, medium, and high-risk work without contradictory next steps.
- Review-only workflows do not imply edits unless the user explicitly asks for fixes.
- Incident workflows gate destructive actions, deploys, and mitigations behind explicit approval.
- Refactoring and cleanup workflows preserve observable behavior unless a handoff is required.

## Handoff Checks

- If a workflow crosses boundaries, the docs state when to pause and which workflow takes over.
- Final reports include validation commands, skipped validations with reasons, and commit/push confirmation.
- Review and cleanup workflows state whether code was changed or the pass stayed read-only.
- Validation handoffs distinguish pre-existing failures from regressions introduced by the current task.
- Follow-up work is explicit, scoped, and separated from the completed task.
- Any unresolved ambiguity is explicit and not hidden as an assumption.
