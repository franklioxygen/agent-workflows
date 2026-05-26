# Shared Repository Preflight Prompts

Description: Reusable repository-aware preflight prompts shared by the workflow documents in `agent-workflows`.

Use the matching preflight block below instead of copying the same repository checks into every workflow file.

## Standard Coding Preflight

Use for feature development, bug fixing, refactoring, and tech debt cleanup.

```text
Inspect the repository before starting work.

Your goals:

1. Read repo-local instructions that apply to this directory, such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or equivalent workflow docs.
2. Check the current branch and workspace status.
3. Identify uncommitted changes that are unrelated to this task.
4. Note any repo rules about branching, testing, approvals, code style, or file ownership.
5. State how you will avoid overwriting, reverting, or reformatting unrelated user changes.
6. Confirm that you will not commit or push without explicit permission.

Provide:

- Applicable repo instructions found
- Current branch / workspace state
- Unrelated local changes to avoid touching
- Workflow constraints that affect this task

Do not commit or push without my explicit permission.
Do not revert or overwrite changes you did not make unless I explicitly ask.
```

## Code Review Preflight

Use for reviewing a pull request, branch, or workspace diff.

```text
Inspect the repository before starting the review.

Your goals:

1. Read repo-local instructions that apply to this directory, such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or equivalent workflow docs.
2. Check the current branch and workspace status.
3. Determine the exact review target and comparison base:
   - If a GitHub PR link is provided, identify the PR base branch from the PR metadata.
   - If a branch name is provided, determine the most likely base branch using repo conventions and merge-base information.
   - If reviewing workspace changes, determine whether the review covers the full workspace or only a specific subset of files.
4. Identify uncommitted changes that are unrelated to the review target.
5. Note any repo rules about branching, testing, approvals, code style, ownership, or review expectations.
6. If the review target or comparison base is ambiguous, stop and ask before continuing.
7. Confirm that you will not edit code, commit, or push without explicit permission.

Provide:

- Applicable repo instructions found
- Current branch / workspace state
- Review target and comparison base
- Unrelated local changes to avoid confusing with the review target
- Workflow constraints that affect this review

Do not edit code, commit, or push without my explicit permission.
Do not revert or overwrite changes you did not make unless I explicitly ask.
```

## Incident Response Preflight

Use for production incident or post-incident debugging workflows.

```text
Inspect the repository before starting work.

Your goals:

1. Read repo-local instructions that apply to this directory, such as `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `RUNBOOK.md`, or equivalent workflow and incident docs.
2. Check the current branch and workspace status.
3. Identify uncommitted changes that are unrelated to this incident.
4. Note any repo rules about branching, testing, approvals, hotfix procedures, or deployment.
5. Identify available observability tools: logging, monitoring dashboards, error tracking, APM, or alerting systems referenced in the codebase or docs.
6. State how you will avoid overwriting, reverting, or reformatting unrelated user changes.
7. Confirm that you will not commit, push, deploy, or run destructive commands without explicit permission.

Provide:

- Applicable repo instructions found
- Hotfix or incident procedures documented in the repo, if any
- Current branch / workspace state
- Unrelated local changes to avoid touching
- Observability tools and dashboards identified

Do not commit, push, or deploy without my explicit permission.
Do not revert or overwrite changes you did not make unless I explicitly ask.
```
