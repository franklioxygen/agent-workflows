---
name: release-prep
description: Prepare the agent-workflows library for release by checking release readiness, gathering changed files, running workflow-maintainer audits, drafting release notes, producing validation evidence, and creating a final publish checklist. Use when Codex is asked to prepare, verify, summarize, package, or hand off an agent-workflows release.
---

<!--
Function Name: release-prep
Description: Codex skill instructions for preparing agent-workflows releases.
-->

# Release Prep

## Quick Start

- Run `scripts/prepare_release_report.py` from this skill directory, or by absolute path, to collect release inputs.
- Run the `workflow-maintainer` audit before drafting release notes if that skill is available in this repository.
- Read [references/release-checklist.md](references/release-checklist.md) for release judgment checks and final handoff content.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Do not create tags, commits, pushes, GitHub releases, or package uploads without explicit permission.

## Release Workflow

1. Establish repository state:

```bash
python3 scripts/prepare_release_report.py
```

2. Run deterministic validation:

```bash
python3 ../workflow-maintainer/scripts/audit_workflow_library.py
python3 ../workflow-automation/scripts/find_workflow_library.py --json
```

3. Inspect changed files and classify release impact:

- `major`: breaking workflow semantics, renamed files, removed workflows, or incompatible skill behavior.
- `minor`: new workflows, new skills, new checks, or backward-compatible capability additions.
- `patch`: typo fixes, docs clarifications, metadata corrections, non-breaking script fixes.

4. Draft release notes with:

- Summary
- User-facing changes
- New or changed skills
- Validation performed
- Breaking changes, if any
- Migration notes, if any
- Known limitations or follow-ups

5. Final handoff must state whether commits, tags, pushes, and publish actions were performed. Default answer should be no unless the user explicitly approved them.

## Maintenance Rules

- Keep release notes factual and tied to observed changes.
- Do not invent version numbers if the repo does not define a versioning convention; ask or label the release as “unversioned draft.”
- Treat failed audits, broken links, missing required files, stale README inventory, invalid skill metadata, or unvalidated helper scripts as release blockers.
- If the working tree is not a Git repository, produce a filesystem-based release report and state that Git diff metadata was unavailable.
