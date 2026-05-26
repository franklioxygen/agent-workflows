---
name: performance-review
description: Perform focused performance reviews of code changes, pull requests, branches, or workspace diffs for algorithmic complexity, database query patterns, N+1 risks, pagination, caching, batching, memory use, synchronous I/O, latency, and load behavior. Use when Codex is asked for a performance review, scalability review, profiling plan, benchmark plan, or latency-risk assessment.
---

<!--
Function Name: performance-review
Description: Codex skill instructions for focused performance reviews and profiling plans.
-->

# Performance Review

## Quick Start

- Run `scripts/performance_signal_scan.py <path>` when a repository or changed-file path is available.
- Read [references/performance-review-checklist.md](references/performance-review-checklist.md) before finalizing findings.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Focus on hot paths, data size, request rate, and operational cost.
- Stay read-only unless the user explicitly asks for fixes.

## Review Workflow

1. Establish expected scale: records, requests per second, concurrency, payload size, memory budget, latency budget.
2. Identify hot paths and expensive dependencies: database, network, filesystem, CPU, serialization, rendering, queues.
3. Run signal scan:

```bash
python3 scripts/performance_signal_scan.py /path/to/repo-or-file
```

4. Trace loops, queries, API calls, and allocations through realistic worst-case inputs.
5. Recommend validation: targeted tests, profiling, explain plans, benchmarks, load tests, or production metrics.

## Output Rules

- Findings must include scale assumptions and the cost mechanism.
- Distinguish measured issues from plausible risks.
- Prefer concrete mitigations: add pagination, batch calls, add index, cache with invalidation, stream data, avoid repeated work.
- If no findings are found, state residual risk and whether profiling or benchmarks were skipped.
