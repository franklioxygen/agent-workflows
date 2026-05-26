<!--
Function Name: performance-review-checklist
Description: Checklist for focused performance and scalability reviews.
-->

# Performance Review Checklist

## Common Risk Areas

- Nested loops over unbounded collections.
- Database queries inside loops or per-item API calls.
- Missing pagination, limits, indexes, or filters.
- Full table scans, broad joins, and unbounded sorts.
- Large payloads loaded fully into memory.
- Synchronous I/O on request paths.
- Repeated serialization, parsing, regex, or expensive computation.
- Cache without invalidation or user/tenant scoping.

## Validation Options

- Unit or integration test with large input.
- Query explain plan or index check.
- Microbenchmark for CPU-heavy logic.
- Load test or smoke benchmark for request paths.
- Profiling trace for memory, CPU, or I/O.
- Metrics check after rollout: latency, error rate, queue lag, memory, CPU, DB load.

## Review Output

- State expected scale and worst case.
- Explain why the code path is hot or bounded.
- Include exact validation commands or skipped-validation reasons.
- Separate performance blockers from optional optimizations.
