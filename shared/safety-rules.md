# Shared Safety Rules

Description: Reusable safety-rule prompt blocks shared by the workflow documents in `agent-workflows`.

Use the narrowest rule that matches the workflow instead of duplicating these blocks in every file.

## Standard Coding Rule

Use for feature development and bug-fix workflows.

```text
Do not commit or push without my explicit permission.
```

## Review-Only Rule

Use for code-review workflows.

```text
Do not edit code, commit, or push without my explicit permission.
```

## Behavior-Preserving Rule

Use for refactoring workflows.

```text
Do not commit or push without my explicit permission.
Do not change observable behavior unless I explicitly ask.
```

## Cleanup Rule

Use for tech-debt cleanup workflows.

```text
Do not commit or push without my explicit permission.
Do not change observable behavior unless I explicitly ask.
Keep each cleanup unit small enough to review and revert independently.
```

## Incident Response Rule

Use for incident-response workflows.

```text
Do not commit, push, or deploy without my explicit permission.
Do not run destructive commands (DROP, DELETE, TRUNCATE, rm -rf, force push, etc.) without my explicit permission.
```
