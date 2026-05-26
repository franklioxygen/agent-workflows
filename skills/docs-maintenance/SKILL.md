---
name: docs-maintenance
description: Maintain agent-workflows documentation by updating README entries, workflow docs, shared references, skill docs, examples, links, headings, and cross-file consistency after documentation or workflow changes. Use when Codex is asked to update docs, fix stale references, add examples, improve documentation structure, or validate agent-workflows documentation.
---

<!--
Function Name: docs-maintenance
Description: Codex skill instructions for maintaining agent-workflows documentation and cross-references.
-->

# Docs Maintenance

## Quick Start

- Run `scripts/docs_inventory.py <path>` to inventory Markdown docs and common documentation signals.
- Run `../workflow-maintainer/scripts/audit_workflow_library.py` when maintaining this agent-workflows repository.
- Read [references/docs-maintenance-checklist.md](references/docs-maintenance-checklist.md) before finalizing documentation changes.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Keep edits scoped to the documentation goal; do not change workflow semantics accidentally.

## Maintenance Workflow

1. Identify the doc change type: new doc, renamed file, changed workflow step, new skill, example update, typo, or consistency fix.
2. Inventory docs:

```bash
python3 scripts/docs_inventory.py /path/to/agent-workflows
```

3. Update all cross-references affected by the change:

- README inventories and setup instructions.
- Workflow routing and library-loading references.
- Skill docs and canonical agent metadata prompts in `agents/interface.yaml`.
- Shared conventions if repeated wording appears in multiple workflow files.

4. Validate links, anchors, inventories, and helper scripts.
5. Report changed docs, validation run, and any skipped checks.

## Output Rules

- Prefer precise wording over broad rewrites.
- Preserve existing tone and structure.
- Keep examples executable or clearly marked as templates.
- Do not add duplicate safety language if a shared reference is the canonical source.
