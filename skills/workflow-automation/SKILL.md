---
name: workflow-automation
description: Select and execute the right engineering workflow from an agent-workflows library for project initialization, feature work, bug fixes, code review, incident response, refactoring, and tech debt cleanup. Use when Codex should automate workflow selection, apply the workflow steps directly, or route a user request into the correct workflow instead of manually reading the markdown workflow files.
---

# Workflow Automation

Description: Automate the agent-workflows library by routing a task to the correct workflow and executing the matching steps directly.

## Quick Start

- Run `scripts/find_workflow_library.py --json` from this skill directory, or run the script by its absolute path, to locate the nearest `agent-workflows` library and get the file map.
- If the library is not near the current workspace, set `AGENT_WORKFLOWS_ROOT` to the library root before running the script.
- Read [references/workflow-routing.md](references/workflow-routing.md) to classify the task.
- Read [references/library-loading.md](references/library-loading.md) to know which shared docs and workflow file to load.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Apply the workflow directly. Do not just restate the prompt text unless the user explicitly asks for prompt templates.

## Operating Rules

- Treat the workflow markdown files as operating instructions, not as documentation to paraphrase back to the user.
- Use one primary workflow at a time. If a task crosses workflow boundaries, complete or pause the current workflow and then hand off explicitly to the next one.
- Respect an explicitly requested workflow unless it is clearly unsafe or mismatched; if you override it, explain why.
- Keep context lean: load `README.md`, the relevant shared docs, and the selected workflow file. Do not load every workflow file.
- For code-changing workflows, execute the workflow steps in the repository, including validation and final reporting.
- For read-only workflows such as code review or survey-only cleanup, stay read-only unless the user explicitly asks for edits.

## Route the Task

Read [references/workflow-routing.md](references/workflow-routing.md) when the correct workflow is not obvious. Use these defaults:

- New capability, design change, or product behavior change: feature workflow.
- New project, greenfield codebase, repository scaffold, or initial tooling setup: project initialization workflow.
- Existing behavior is wrong or regressed: bug-fix workflow.
- User asks for review, findings, PR review, or diff review: code-review workflow.
- Live or recent production outage, mitigation, alert, or incident: incident workflow.
- Behavior must stay the same while structure improves: refactoring workflow.
- Cleanup, dependency upgrade, dead code removal, TODO resolution, or debt survey: tech-debt cleanup workflow.

If the classification is materially ambiguous, ask one short clarifying question. If the ambiguity is low-risk, choose the most likely workflow and state the assumption.

## Locate the Library

- Use `scripts/find_workflow_library.py --json` first, resolving the path relative to this skill directory if the current working directory is elsewhere.
- The script checks `AGENT_WORKFLOWS_ROOT`, then script-relative paths, then walks upward from the start path.
- If the script finds a library root, use the returned paths.
- If no library is found, ask the user for the `agent-workflows` path instead of guessing.

## Execute the Workflow

- Read [references/library-loading.md](references/library-loading.md) before opening files.
- Run the workflow’s preflight, safety rule, triage gate, and only the necessary steps for the current task.
- Follow the library’s shared conventions plus the workflow-specific rules.
- For incident work, prioritize mitigation first and treat destructive actions as approval-gated.
- For review work, default to findings-first and avoid edits unless explicitly asked.

## References

- [references/workflow-routing.md](references/workflow-routing.md)
- [references/library-loading.md](references/library-loading.md)
- [scripts/find_workflow_library.py](scripts/find_workflow_library.py)
