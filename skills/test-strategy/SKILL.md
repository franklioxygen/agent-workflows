---
name: test-strategy
description: Design high-value test strategies for features, bug fixes, refactors, migrations, and reviews by mapping behavior to coverage, identifying missing edge cases, selecting validation commands, and avoiding brittle or low-signal tests. Use when Codex is asked for a test plan, coverage matrix, regression strategy, QA checklist, or validation approach.
---

<!--
Function Name: test-strategy
Description: Codex skill instructions for planning high-value test coverage and validation.
-->

# Test Strategy

## Quick Start

- Run `scripts/test_inventory.py <path>` when a repository path is available.
- Read [references/test-strategy-checklist.md](references/test-strategy-checklist.md) before finalizing the test plan.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Map tests to observable behavior, not implementation details.
- Prefer targeted validation first, then broader validation when risk justifies it.
- Do not edit code unless the user explicitly asks for implementation.

## Strategy Workflow

1. Identify changed or proposed behavior.
2. List risk areas: permissions, data shape, API contracts, UI states, errors, concurrency, migrations, performance, and integrations.
3. Inventory existing test structure and commands:

```bash
python3 scripts/test_inventory.py /path/to/repo
```

4. Produce a coverage matrix:

```markdown
| Behavior | Existing coverage | Needed test | Priority |
| --- | --- | --- | --- |
| <behavior> | covered / partial / missing | <test idea> | P0 / P1 / P2 |
```

5. Separate automated tests from manual QA and validation commands.
6. Call out tests that should not be updated because they assert stable behavior.

## Output Rules

- Include exact scenarios, inputs, expected results, and why each test matters.
- Mark regression tests that should fail before the fix and pass after it.
- State skipped tests or validations with reasons.
- Flag weak tests: broad snapshots, tautological assertions, timing-sensitive tests, and tests that mirror implementation instead of behavior.
