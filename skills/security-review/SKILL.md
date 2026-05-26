---
name: security-review
description: Perform focused security reviews of code changes, pull requests, branches, or workspace diffs for authentication, authorization, input validation, injection, secrets handling, sensitive data exposure, dependency risk, insecure transport, and unsafe operational behavior. Use when Codex is asked for a security review, threat-focused code review, auth/permission review, or security-risk assessment.
---

<!--
Function Name: security-review
Description: Codex skill instructions for focused security reviews of code changes.
-->

# Security Review

## Quick Start

- Use this skill as a focused review layer, not a replacement for normal correctness review.
- Run `scripts/security_signal_scan.py <path>` when a repository or changed-file path is available.
- Read [references/security-review-checklist.md](references/security-review-checklist.md) before finalizing findings.
- Follow shared safety, validation, and scope rules in [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md).
- Stay read-only unless the user explicitly asks for fixes.
- Do not commit, push, deploy, rotate secrets, revoke keys, or run destructive commands without explicit permission.

## Review Workflow

1. Establish scope:

- Review target: PR, branch, workspace changes, or specific files.
- Comparison base, if reviewing a diff.
- Trust boundaries affected by the change.
- Security-sensitive domains touched: auth, permissions, secrets, payments, PII, file upload, network calls, command execution, database access, dependency upgrades, logging, or telemetry.

2. Run signal scan:

```bash
python3 scripts/security_signal_scan.py /path/to/repo-or-file
```

3. Manually trace high-risk flows:

- External input to sink: database query, shell command, HTML/template rendering, file path, network request, deserialization, logging, or redirect.
- Identity to authorization decision: authentication source, user/session lookup, role/permission check, tenant or ownership boundary.
- Secret creation to storage/use/logging.
- Sensitive data from storage to response, logs, analytics, or third-party calls.

4. Report findings first, ordered by severity. Use this format:

```markdown
### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Attack or failure scenario:
- Recommended fix:
- Severity: Critical / Major / Minor / Nit
```

5. If no findings are found, state that explicitly and list residual risks, skipped checks, and validation performed.

## Severity Guidance

- Critical: Direct data exposure, authentication bypass, authorization bypass, credential leak, remote code execution, destructive data mutation, or exploitable injection.
- Major: Missing edge-case authorization, unsafe input handling with plausible exploit path, sensitive logs, insecure defaults, unsafe dependency upgrade, or tenant-boundary risk.
- Minor: Defense-in-depth gap, weak validation, incomplete audit trail, ambiguous security behavior, or low-likelihood exposure.
- Nit: Naming, comment, or structure issue with no meaningful security impact.

## Coordination With Other Workflows

- Use `code-review-agent-workflow.md` for broad review and this skill for focused security depth.
- If the security review finds a bug, hand off to the bug-fix workflow after reporting the finding.
- If the review finds a design or policy decision gap, hand off to the feature workflow rather than inventing security policy.
