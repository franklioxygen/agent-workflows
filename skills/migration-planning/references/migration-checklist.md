<!--
Function Name: migration-checklist
Description: Checklist for planning safe schema, data, API, and contract migrations.
-->

# Migration Planning Checklist

## Compatibility

- New code can run against old and new data where rollout overlap exists.
- Old code can tolerate new additive data or fields.
- Public APIs remain backward compatible or have a versioned/deprecation path.
- Events and queues tolerate mixed producers and consumers.
- Feature flags fail safe and have an owner for removal.

## Data Safety

- Backfills are idempotent, resumable, batched, and rate-limited.
- Large-table changes avoid long locks and table rewrites.
- Destructive steps have backups, verification, and explicit approval.
- Validation checks cover row counts, constraints, nullability, duplicates, and referential integrity.

## Rollout And Rollback

- Each phase has prechecks, execution steps, validation, monitoring, and rollback.
- Rollback does not require restoring from backup unless explicitly accepted.
- Observability covers errors, latency, data drift, queue lag, and user impact.
- Final cleanup happens only after compatibility window closes.
