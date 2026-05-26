<!--
Function Name: docs-maintenance-checklist
Description: Checklist for maintaining agent-workflows documentation and cross-file references.
-->

# Docs Maintenance Checklist

## Cross-Reference Checks

- README lists every workflow, shared doc, and bundled skill.
- Repository structure block matches actual files.
- Markdown links and heading anchors resolve.
- Workflow routing references match actual workflow filenames.
- Library-loading references match actual shared docs and scripts.
- Each installable skill has one canonical `agents/interface.yaml`.
- Legacy per-agent files such as `agents/openai.yaml` and `agents/claude.yaml` are not present.
- Skill default prompts mention the literal `$skill-name`.

## Content Checks

- New files include function name and description headers where repo instructions require them.
- Repeated boilerplate is moved to `shared/` instead of copied.
- Workflow-specific guidance stays in the workflow file.
- Safety rules remain consistent with `shared/safety-rules.md`.
- Examples use placeholders clearly and avoid fake claims about execution.

## Final Checks

- Run workflow-maintainer audit.
- Run affected helper scripts.
- State docs changed, commands run, skipped validation, and whether commit or push was performed.
