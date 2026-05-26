---
name: workflow-maintainer
description: Audit and maintain the agent-workflows library for documentation drift, broken Markdown links, missing required workflow files, stale README inventories, invalid skill metadata, and automation-script inconsistencies. Use when Codex is asked to review, validate, update, or release changes to agent-workflows docs or bundled skills.
---

<!--
Function Name: workflow-maintainer
Description: Codex skill instructions for auditing and maintaining the agent-workflows library.
-->

# Workflow Maintainer

## Quick Start

- Locate the library root. The audit script auto-checks `AGENT_WORKFLOWS_ROOT`, script-relative paths, and the current workspace.
- Run `scripts/audit_workflow_library.py` from this skill directory, or by absolute path.
- Read [references/audit-checklist.md](references/audit-checklist.md) before making maintenance edits.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Fix only the reported drift or the user-requested maintenance scope. Do not rewrite workflow content unless the issue requires it.
- Re-run the audit script and any affected helper scripts before final handoff.

## Maintenance Rules

- Preserve the library's separation of concerns: workflow-specific guidance stays in workflow files; repeated safety, preflight, and conventions stay in `shared/`; skill-specific routing stays in the relevant skill.
- When workflow names, filenames, or shared docs change, update all references together: `README.md`, `skills/workflow-automation/references/library-loading.md`, `skills/workflow-automation/references/workflow-routing.md`, and related scripts.
- Treat broken links, missing required files, stale skill metadata, and invalid manifests as blocking issues.
- Treat style-only edits, wording improvements, and optional examples as non-blocking unless the user asked for them.
- Never commit or push without explicit permission.

## Audit Workflow

1. Run the audit script:

```bash
python3 scripts/audit_workflow_library.py
```

2. If the script reports errors, inspect only the affected files first.
3. If the issue concerns judgment rather than deterministic validation, use the checklist reference.
4. Apply narrow fixes.
5. Re-run:

```bash
python3 scripts/audit_workflow_library.py
python3 skills/workflow-automation/scripts/find_workflow_library.py --json
```

6. Report findings fixed, commands run, remaining warnings, and whether any validation was skipped.

## When to Read the Checklist

Read [references/audit-checklist.md](references/audit-checklist.md) when the user asks for a human review of the library, release readiness, docs consistency, routing changes, or when the script reports no errors but the change may still have workflow-design risk.
