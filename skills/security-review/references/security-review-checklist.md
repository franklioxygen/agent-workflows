<!--
Function Name: security-review-checklist
Description: Checklist for focused security reviews of code changes.
-->

# Security Review Checklist

## Authentication And Session Handling

- Authentication source is trusted and cannot be spoofed.
- Session, token, and cookie handling follows project conventions.
- Login, logout, refresh, impersonation, and service-account paths are considered when touched.
- Error messages do not reveal credential validity or account existence unless intended.

## Authorization And Tenancy

- Every affected entry point has an authorization decision.
- Object ownership, tenant boundaries, and role checks are enforced server-side.
- Bulk operations and list endpoints do not bypass per-object checks.
- Admin, support, and background-job paths do not inherit unintended permissions.

## Input, Injection, And Execution

- SQL, NoSQL, command, path, template, HTML, redirect, and header sinks are checked.
- User-controlled strings are parameterized, escaped, normalized, or rejected before reaching sinks.
- File upload paths validate type, size, extension, content, storage path, and access policy.
- Deserialization and dynamic code execution are avoided or strictly constrained.

## Secrets And Sensitive Data

- Secrets are not hardcoded, logged, returned, committed, or exposed in errors.
- PII and credentials are redacted in logs, metrics, traces, analytics, and third-party calls.
- Sensitive data in transit and at rest follows project conventions.
- Test fixtures do not contain real credentials or production data.

## Dependencies And Configuration

- New or upgraded dependencies are necessary, maintained, and not known-vulnerable.
- Security-relevant defaults are explicit: CORS, TLS verification, debug mode, cookie flags, CSP, rate limits.
- Feature flags and rollout gates fail closed where appropriate.

## Review Output

- Findings include exploit or failure scenario, not just generic risk.
- Severity reflects actual exploitability and impact.
- Validation commands and skipped checks are reported.
- If no findings exist, residual risk is still stated.
