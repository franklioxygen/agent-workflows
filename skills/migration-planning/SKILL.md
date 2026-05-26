---
name: migration-planning
description: Plan safe schema, data, API, contract, and configuration migrations with rollout phases, backward compatibility, validation, rollback, data backfill, and deployment sequencing. Use when Codex is asked to design or review a migration, breaking API change, database change, data backfill, feature-flag rollout, or compatibility-sensitive release.
---

<!--
Function Name: migration-planning
Description: Codex skill instructions for safe migration planning and review.
-->

# Migration Planning

## Quick Start

- Run `scripts/migration_signal_scan.py <path>` when a repository or change path is available.
- Read [references/migration-checklist.md](references/migration-checklist.md) before finalizing the plan.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Prefer expand-contract migrations for databases and public contracts.
- Do not run migrations, mutate data, deploy, commit, or push without explicit permission.

## Planning Workflow

1. Identify what is migrating: schema, data, API, event contract, config, dependency, or runtime behavior.
2. Define compatibility requirements: old code with new data, new code with old data, old clients with new API, rollback path.
3. Split rollout into phases:

- Prepare: additive changes, dual-read or dual-write, feature flags.
- Backfill: idempotent, resumable, observable data changes.
- Switch: traffic or behavior moves to the new path.
- Contract: remove old fields, code, flags, or compatibility shims only after safety is proven.

4. Produce a migration plan with validation and rollback for every phase.
5. Mark irreversible steps explicitly and require approval before execution.

## Output Rules

- Include deployment order and rollback order.
- Include data validation queries or checks.
- Include monitoring and alerting signals.
- Include blast radius and expected duration.
- State what must be true before removing compatibility code.
