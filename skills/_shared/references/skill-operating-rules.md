<!--
Function Name: skill-operating-rules
Description: Shared operating rules reused by bundled agent-workflows skills.
-->

# Shared Skill Operating Rules

## Safety

- Do not commit or push without explicit permission.
- Do not deploy, publish, create tags, rotate secrets, revoke credentials, mutate production data, or run destructive commands without explicit permission.
- Stay read-only for review, planning, audit, and documentation-analysis tasks unless the user explicitly asks for edits.

## Validation

- Run the skill's deterministic helper script when a repository or file path is available.
- Run `skills/workflow-maintainer/scripts/audit_workflow_library.py` after changing workflow docs, skill metadata, shared references, or README inventory.
- Report commands run, results, skipped validation, and remaining risks.

## Scope

- Keep changes scoped to the selected skill's task.
- If a task crosses into implementation, bug fixing, feature design, migration execution, release publishing, or incident response, hand off explicitly to the more specific workflow or skill.
- Prefer shared references for repeated rules and local skill docs for domain-specific procedure.
