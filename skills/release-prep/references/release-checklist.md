<!--
Function Name: release-checklist
Description: Checklist for preparing agent-workflows release notes and release readiness handoff.
-->

# Release Prep Checklist

## Release Blockers

- Workflow-maintainer audit has errors.
- Markdown links or heading anchors are broken.
- README inventory does not mention added, removed, or renamed workflows or skills.
- Skill metadata contains placeholder text or incorrect `$skill-name` prompts.
- Helper scripts fail compilation or basic execution.
- Release notes omit breaking changes, migration notes, or validation failures.

## Release Notes Template

```markdown
# Release Notes

## Summary

<one-paragraph release summary>

## Changes

- <user-facing change>

## Skills

- <new or changed skill behavior>

## Validation

- `<command>`: <result>

## Breaking Changes

- None, or list each breaking change and required migration.

## Known Limitations

- None, or list follow-ups.
```

## Final Handoff Checklist

- Release impact classification is stated: major, minor, patch, or unversioned draft.
- Files changed are summarized by purpose, not just listed.
- Commands run and results are included.
- Skipped validations are listed with reasons.
- Commit, tag, push, and publish status are explicitly stated.
