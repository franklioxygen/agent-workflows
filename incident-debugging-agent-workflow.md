# Incident / Production Debugging Agent Workflow

This document defines a reusable agent workflow for diagnosing and resolving production incidents. The input can be an alert, error log, monitoring dashboard observation, user report, or PagerDuty/Slack escalation.

The workflow is designed for AI coding agents working in a repository during or after a production incident. It prioritizes **mitigation first, root cause second**. The goal is to stop the bleeding, then understand why it happened, then fix it properly.

This workflow differs from the bug fix workflow in urgency and approach:
- Bug fix workflow: methodical diagnosis, then fix, then validate.
- Incident workflow: mitigate impact immediately, then diagnose, then apply a proper fix or hand off to the bug fix workflow.

## Preflight Repository Check

Use [Incident Response Preflight](shared/repository-preflight.md#incident-response-preflight) before the triage gate.

## Global Rule

Use [Incident Response Rule](shared/safety-rules.md#incident-response-rule) in every prompt.

## Triage Gate

Before starting, classify the incident to select the right level of urgency:

```text
Classify this incident into one of the following categories:

1. Active: The system is currently impaired. Users are affected right now. Examples: service is down, errors are spiking, data is being corrupted, payments are failing, authentication is broken.

2. Degraded: The system is partially working but something is wrong. Impact is limited or growing slowly. Examples: elevated latency, intermittent errors for a subset of users, one region affected, background jobs failing, non-critical feature broken.

3. Post-incident: The immediate impact has been resolved or mitigated, but the root cause is not yet understood. Examples: service recovered after a restart, a rollback stopped the errors, a manual fix was applied but the underlying issue remains.

Based on the classification:

- Active: Start at Step 0 (Assess and Mitigate). Speed matters. Focus on stopping the impact before diagnosing the root cause.
- Degraded: Start at Step 0 (Assess and Mitigate), but take time to understand the scope before acting. A wrong mitigation can make a degraded system worse.
- Post-incident: Skip to Step 2 (Root Cause Analysis). The system is stable — focus on understanding what happened.

Incident report:

<alert, error log, monitoring observation, user report, or escalation message>

Classify this incident and recommend which steps to follow.
```

## Step 0: Assess and Mitigate

Use this prompt when the system is actively impaired or degraded:

```text
Assess the production incident and identify mitigation options.

Incident report:

<alert, error log, monitoring observation, user report, or escalation message>

### Part A: Rapid Assessment

Your goals:

1. Determine what is broken: which service, endpoint, feature, or data path is affected.
2. Determine the blast radius: how many users, requests, or operations are impacted.
3. Determine the timeline: when did it start? Is it getting worse, stable, or improving?
4. Check for recent changes that correlate with the incident:
   - Recent deployments (git log, deployment history, CI/CD)
   - Recent configuration changes
   - Recent database migrations
   - Recent dependency updates
   - Recent infrastructure changes
5. Check for external factors:
   - Third-party service outages
   - Traffic spikes
   - Scheduled maintenance
6. Identify what is working: which parts of the system are unaffected. This narrows the search.

### Part B: Mitigation Options

Based on the assessment, propose mitigation options ranked by speed and safety:

For each option, provide:
- Action: what to do
- Expected effect: what it will fix
- Risk: what could go wrong
- Reversibility: can it be undone easily
- Time to effect: how quickly it will help

Common mitigation patterns (consider in order):
1. Rollback to last known good deployment
2. Disable a feature flag
3. Scale up resources
4. Block or rate-limit problematic traffic
5. Restart affected services
6. Apply a targeted hotfix
7. Failover to a secondary system
8. Manual data correction

Do not apply any mitigation without my explicit permission.
Do not commit, push, or deploy without my explicit permission.
Do not run destructive commands without my explicit permission.

Provide:
- What is broken and since when
- Blast radius (users, requests, revenue, data integrity)
- Likely trigger (recent change, external factor, or unknown)
- Mitigation options ranked by recommendation
- What you need from me to proceed
```

## Step 1: Stabilize and Gather Evidence

Use this prompt after mitigation is applied or while monitoring a degraded system:

```text
The following mitigation has been applied (or the system is being monitored):

Mitigation applied:

<what was done, or "none yet — monitoring">

Current status:

<current system state — recovered, partially recovered, still degraded>

Your goals:

1. Confirm whether the mitigation is working:
   - Are error rates dropping?
   - Are affected users recovering?
   - Are there new symptoms or side effects from the mitigation?
2. Gather evidence for root cause analysis while the incident is fresh:
   - Relevant log entries (errors, warnings, unusual patterns)
   - Stack traces or error messages
   - Timestamps correlating symptoms with changes or events
   - Affected request paths, user segments, or data subsets
   - Monitoring data (latency, error rates, throughput, resource usage)
3. Identify what the mitigation does NOT fix — residual issues, data inconsistencies, or degraded functionality that remains.
4. Determine whether the mitigation is temporary (needs a proper fix) or permanent (the issue is fully resolved).

Do not commit, push, or deploy without my explicit permission.

Provide:
- Mitigation effectiveness (working / partially working / not working)
- Evidence gathered (logs, traces, metrics, timestamps)
- Residual issues
- Whether a proper fix is still needed
- Recommended next step: root cause analysis, additional mitigation, or escalation
```

## Step 2: Root Cause Analysis

Use this prompt after the system is stable:

```text
Perform a root cause analysis for the following production incident.

Incident summary:

<what happened, when, blast radius, mitigation applied>

Evidence:

<logs, traces, metrics, timestamps, and observations from Step 1 — or from the incident report if skipping earlier steps>

Your goals:

1. Trace the failure from symptom to root cause. Follow the evidence, not assumptions.
2. Establish the causal chain:
   - Trigger: what initiated the failure (deployment, config change, traffic spike, data condition, external dependency)
   - Mechanism: how the trigger caused the symptoms (code path, data flow, resource exhaustion, race condition)
   - Impact: what broke and why it was not caught earlier
3. Identify contributing factors:
   - Missing monitoring or alerting
   - Missing input validation or error handling
   - Missing tests that would have caught the issue
   - Deployment or rollback process gaps
   - Documentation or runbook gaps
4. Determine the root cause category:
   - Code defect
   - Configuration error
   - Data integrity issue
   - Infrastructure / capacity issue
   - External dependency failure
   - Process / human error
5. Assess whether the mitigation fully resolved the issue or only masked it.
6. Check for related risks: could the same root cause manifest differently elsewhere?

Do not commit, push, or deploy without my explicit permission.

Provide:
- Root cause (one paragraph)
- Causal chain (trigger → mechanism → impact)
- Contributing factors
- Root cause category
- Whether the mitigation is sufficient or a proper code fix is needed
- Related risks
```

## Step 3: Apply a Proper Fix

Use this prompt when the root cause is understood and a code fix is needed:

```text
Apply a proper fix for the following production incident based on the root cause analysis.

Root cause:

<root cause explanation, causal chain, and related risks from Step 2>

Mitigation currently in place:

<what temporary mitigation is active, if any>

Important instructions:

1. Read the relevant code carefully before editing.
2. Fix the root cause, not the symptom. The mitigation stopped the bleeding — the fix should prevent it from recurring.
3. Follow existing patterns in the codebase.
4. Keep changes scoped to the incident. Do not refactor, clean up, or improve surrounding code.
5. If the same root cause affects other code paths (identified in the RCA), fix those too.
6. Add or update tests that cover:
   - The exact scenario that caused the incident
   - Edge cases related to the root cause
   - Regression prevention (the test should fail without the fix)
7. If a temporary mitigation is in place (feature flag, config override, rollback), note whether it can be removed after this fix is deployed.
8. Run relevant tests, linters, and type checks.
9. Do not commit, push, or deploy without my explicit permission.
10. If the proper fix is too risky or complex for a hotfix, say so and recommend a safer short-term fix with a follow-up for the full fix.

At the end, provide:

1. Root cause (one sentence)
2. What was changed and why
3. Files changed
4. Tests added or updated
5. Commands run and results
6. Whether the temporary mitigation can be removed after deployment
7. Anything the fix does NOT address (follow-ups, related risks)
```

## Step 4: Post-Incident Report

Use this prompt after the incident is fully resolved:

```text
Produce a post-incident report for the following production incident.

Incident summary:

<what happened, when, blast radius, mitigation, root cause, fix applied>

The report should include:

1. Incident Timeline
   - When the incident started (or was first detected)
   - When the team was alerted
   - When mitigation was applied
   - When the system recovered
   - When the proper fix was deployed (if applicable)
   - Total duration of user impact

2. Impact Summary
   - Users, requests, or operations affected
   - Revenue or data impact, if known
   - SLA or SLO implications, if applicable

3. Root Cause
   - Trigger
   - Mechanism
   - Why it was not caught earlier

4. Mitigation and Fix
   - Mitigation applied and its effectiveness
   - Proper fix applied (or planned)
   - Files changed
   - Tests added

5. Contributing Factors
   - What made the incident possible beyond the direct root cause
   - Process, tooling, monitoring, or testing gaps

6. Action Items
   For each action item, provide:
   - Description
   - Priority: P0 (immediate) / P1 (this sprint) / P2 (next sprint) / P3 (backlog)
   - Owner (leave blank if unknown — do not assign without permission)
   - Status: Open / In Progress / Done

   Common action item categories:
   - Code fixes (if not yet deployed)
   - Monitoring and alerting improvements
   - Test coverage additions
   - Runbook creation or updates
   - Process improvements
   - Documentation updates

7. Lessons Learned
   - What went well during the response
   - What could be improved

Do not commit, push, or deploy without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md).
- Mitigate first, diagnose second. A rolled-back deployment that stops errors in 2 minutes is better than a root cause analysis that takes 30 minutes while users are affected. Speed of mitigation and thoroughness of diagnosis are separate priorities — do not sacrifice one for the other.
- Do not run destructive commands without explicit permission. This includes database mutations, force pushes, service restarts, and cache clears. State what you want to do and wait for approval.
- Preserve evidence before it disappears. Logs rotate, metrics age out, and ephemeral state resets after restarts. Capture relevant logs, traces, and metrics early.
- Separate mitigation from fix. A rollback or feature flag toggle is a mitigation, not a fix. The underlying code defect, configuration error, or data issue still needs to be addressed. Track both.
- If the root cause analysis reveals a design flaw rather than a code bug, escalate to the feature development workflow for a proper redesign. Do not patch around architectural issues during incident response.
- If the proper fix is too risky for a hotfix, apply a safe short-term fix and track the full fix as a follow-up. A second incident caused by a rushed fix is worse than a known limitation with a timeline.
- Action items without owners decay. Flag unassigned items but do not assign them — that is a team decision.
- If you are unsure whether an action is safe, ask. During incidents, the cost of asking is seconds; the cost of a wrong action can be hours.
