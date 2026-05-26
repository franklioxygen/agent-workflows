<!--
Function Name: test-strategy-checklist
Description: Checklist for designing high-value test plans and validation matrices.
-->

# Test Strategy Checklist

## Coverage Targets

- Happy path for every changed behavior.
- Boundary values: empty, null, min, max, malformed, duplicate, and large inputs.
- Error paths: validation failure, downstream failure, timeout, permission denial, and partial success.
- Compatibility: old clients, old data, feature flags, migrations, and rollback states.
- Security-adjacent behavior: authorization, tenancy, sensitive data, and logging.
- Performance-sensitive behavior: pagination, batching, caching, and large datasets.

## Test Quality

- Test fails for the right reason when behavior is broken.
- Assertions verify externally observable outcomes.
- Fixtures are minimal and named after domain concepts.
- Mocks do not hide the behavior being tested.
- Timing, ordering, and network dependence are controlled or avoided.

## Validation Output

- Coverage matrix is explicit.
- Commands to run are listed in priority order.
- Manual QA steps are concrete and reproducible.
- Known gaps are recorded with impact.
