# Project Initialization Agent Workflow

This document defines a reusable agent workflow for bootstrapping a new project from scratch — from requirements gathering through scaffolding, tooling setup, initial validation, and handoff to ongoing development.

The workflow is designed for AI coding agents setting up a new repository or greenfield codebase. It is intended for projects with meaningful decisions around tech stack, directory structure, build tooling, CI/CD, testing infrastructure, dependency management, or deployment targets. For trivially small projects (single script, throwaway prototype), skip this workflow and scaffold directly.

It emphasizes requirement clarity, deliberate technology choices, reproducible builds, early validation, and avoiding unauthorized commits or pushes.

## Preflight Environment Check

Before the triage gate, gather context about the target environment:

```text
Before scaffolding a new project, check the following:

1. What exact target directory should contain the project?
2. Does the target directory or repository already exist? If so, note its current state.
3. Is the target directory inside an existing git repository, monorepo, workspace, or organizational template?
4. Are there local instructions that apply to the target directory, such as AGENTS.md, CLAUDE.md, .editorconfig, CONTRIBUTING.md, or equivalent workflow docs?
5. If the target is inside an existing repository, what is the current branch and workspace status?
6. Are there uncommitted changes unrelated to this project that must not be touched?
7. What language runtimes, package managers, and build tools are available on this machine?
8. Are there any organizational constraints (required linters, CI providers, license headers, security policies)?

If the target directory is missing, ambiguous, or pre-populated unexpectedly, stop and ask before creating files.
Do not overwrite, revert, delete, or reformat unrelated user changes.

Provide:

- Target directory and its current state (empty, non-existent, or pre-populated)
- Parent workspace or template constraints, if any
- Applicable repo-local instructions
- Current branch / workspace state, if inside a repository
- Unrelated local changes to avoid touching
- Available tooling versions
- Organizational constraints discovered
```

## Triage Gate

Before starting the workflow, classify the project to select the right level of process:

```text
Classify this project into one of the following categories:

1. Minimal: Single-purpose script, CLI tool, or library with one entry point. No server, no database, no multi-service coordination. Examples: utility CLI, data processing script, small npm package, single-file Lambda.

2. Standard: Application or library with meaningful structure. May include a server, database, API layer, frontend, or build pipeline. Examples: REST API service, web application, SDK or client library, microservice.

3. Complex: Multi-component system, monorepo, or project with significant infrastructure needs. Involves multiple services, deployment targets, data stores, auth, or cross-team integration. Examples: full-stack app with separate frontend/backend, multi-service platform, project requiring infrastructure-as-code.

Based on the classification:

- Minimal: Use the Minimal Project Prompt below instead of Steps 0 through 5. Scaffold directly with sensible defaults.
- Standard: Start at Step 0 (Gather Requirements). The project plan (Step 1) can omit sections that do not apply. Steps 2 and 3 can run in the same session.
- Complex: Follow the full workflow from Step 0 through Step 5.

Project description:

<brief description of the project>

Classify this project and recommend which steps to follow.
```

## Global Rule

Use [Standard Coding Rule](shared/safety-rules.md#standard-coding-rule) in every prompt.

## Minimal Project Prompt

Use this prompt for `Minimal` projects from the triage gate instead of Steps 0 through 5:

```text
Scaffold the following minimal project without creating a full project plan.

Target directory:

<absolute or repository-relative path to the project directory>

Project description:

<brief description of the project>

Requirements:

<requirements or acceptance criteria, if any>

Important instructions:

1. Confirm the exact target directory before creating files.
2. Stop and ask if the target directory is missing, ambiguous, or pre-populated unexpectedly.
3. Create a sensible directory structure for the project type inside the target directory.
4. Initialize version control (git init) if the target directory is not already in a repository.
5. Set up the package manager and dependency file (package.json, pyproject.toml, go.mod, Cargo.toml, etc.) appropriate to the language.
6. Add a minimal README with project name, purpose, and how to run it.
7. Add a .gitignore appropriate to the language and tooling.
8. Include a basic linter or formatter config if the ecosystem has a strong default (e.g., ESLint, Black, rustfmt).
9. If the project has a clear entry point, create a stub implementation that runs successfully.
10. Run any available validation (build, lint, type check) to confirm the scaffold is clean.
11. If you discover the project is more complex than expected, stop and recommend switching to the Standard or Complex workflow.
12. Do not commit or push without my explicit permission.
13. Do not overwrite, revert, delete, or reformat unrelated user changes.

At the end, provide:

1. Directory structure created
2. Tooling and dependencies configured
3. Commands to run the project
4. Validation commands run and results
5. Suggested next steps
```

## Step 0: Gather Requirements

Use this prompt to clarify what the project needs before making technology or structural decisions:

```text
Review the project requirements below and identify decisions that need to be made before scaffolding.

Project description:

<project overview>
<target users or consumers>
<key features or capabilities>
<constraints or preferences>

Your goals:

1. Determine whether the requirements are clear enough to make technology and structure decisions.
2. Identify requirements that affect:
   - Language and runtime choice
   - Framework selection
   - Data storage needs
   - API style (REST, GraphQL, RPC, etc.)
   - Authentication and authorization
   - Deployment target (cloud provider, container, serverless, static hosting, etc.)
   - CI/CD requirements
   - Testing strategy
   - Monorepo vs. multi-repo
3. Separate the result into:
   - Confirmed requirements
   - Inferred assumptions (with rationale)
   - Open questions
4. Ask clarifying questions when an answer could change the tech stack, project structure, or deployment strategy.
5. Do not begin scaffolding yet.

Do not commit or push without my explicit permission.

If the requirements are clear enough, say so and provide the confirmed requirements, inferred assumptions, and any low-risk open questions.

If the requirements are not clear enough, ask only the questions needed to unblock the project plan.
```

## Step 1: Create the Project Plan

Use this prompt after requirements are clear enough:

```text
Create a project initialization plan for the requirements below.

Write the plan as Markdown. Place it in a `reports/` folder using the filename:

`reports/<project-name>-init-plan-YYYY-MM-DD.md`

The plan should include:

1. Project Overview
2. Target Directory
   - Exact path
   - Current state (non-existent, empty, or pre-populated)
   - Parent repository, workspace, or template constraints, if any
3. Confirmed Requirements
4. Technology Choices
   - Language and runtime (with version)
   - Framework, if any (with rationale)
   - Package manager
   - Build tooling
   - Linter, formatter, and type checker
   - Testing framework
5. Directory Structure
   - Proposed layout with brief rationale for non-obvious choices
6. Dependency Inventory
   - Production dependencies (name, purpose, version constraint)
   - Development dependencies (name, purpose, version constraint)
7. Configuration Files
   - List of config files to create and their purpose (tsconfig, eslint, dockerfile, etc.)
8. CI/CD Setup, if applicable
   - Pipeline provider and trigger strategy
   - Steps (lint, test, build, deploy)
9. Environment and Secrets Management, if applicable
   - Environment variable strategy (.env, secrets manager, etc.)
   - Example .env template (no real secrets)
10. Database / Data Storage Setup, if applicable
   - Schema initialization strategy
   - Migration tooling
11. Authentication / Authorization Setup, if applicable
12. Deployment Strategy, if applicable
    - Target environment
    - Build and deploy steps
    - Infrastructure-as-code, if any
13. Assumptions and Open Questions
14. Initialization Checklist
15. Definition of Done

Omit any section that does not apply to this project. Do not fill sections with placeholder or filler content.

Requirements:

<confirmed requirements>
<technology preferences or constraints>

If any proposed choice has a clearly better alternative for this use case, suggest it and explain why.

If anything is unclear or risky, list it under "Open Questions" and ask me before making assumptions.

Record every assumption explicitly. Do not treat a guess as a requirement.

Do not commit or push without my explicit permission.

Now begin.
```

### Definition of Done

Add this section to every project plan:

```markdown
## Definition of Done

- Project builds and runs successfully after a fresh install from the scaffolded working tree.
- All configured validation commands pass (lint, type check, build, test).
- Directory structure matches the plan.
- Dependencies are pinned or version-constrained appropriately.
- README documents how to install, run, test, and deploy.
- .gitignore covers language, tooling, and IDE artifacts.
- No secrets or credentials are committed.
- CI pipeline runs successfully, if applicable.
- Known limitations and next steps are documented.
```

## Step 2: Review the Project Plan

After the plan is created, start a new session and use this prompt:

```text
There is a project initialization plan at:

<path-to-plan>

Review the plan carefully.

Your goals:

1. Check whether the plan is complete and ready for execution.
2. Identify missing decisions, risky technology choices, dependency concerns, security risks, or gaps in the initialization checklist.
3. Verify that the proposed structure and tooling choices are appropriate for the stated requirements.
4. Classify each finding by severity:
   - Critical: must resolve before scaffolding
   - Major: should resolve before scaffolding
   - Minor: improvement or suggestion
   - Question: needs clarification
5. For clearly missing items (e.g., no .gitignore listed), update the plan directly.
6. For technology tradeoffs, architecture decisions, or preference-dependent choices, add them as Review Findings instead of silently changing the plan.
7. If you make changes, add or update a "Review Findings" section explaining what changed and why.

Use this format for every finding:

### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed / Needs decision

Do not begin scaffolding yet.
Do not commit or push without my explicit permission.

If the plan is already ready for execution, clearly say so and do not make unnecessary edits.
```

## Step 3: Scaffold the Project

Once the plan is stable, use this prompt:

```text
There is a finalized project initialization plan at:

<path-to-plan>

Target directory:

<absolute or repository-relative path to the project directory>

Begin scaffolding the project according to the plan.

Important instructions:

1. Read the plan carefully before creating any files.
2. Confirm the exact target directory from the prompt and plan before creating files.
3. Stop and ask if the target directory is missing, ambiguous, or pre-populated unexpectedly.
4. Initialize git if the target directory is not already in a repository.
5. Create the directory structure as specified in the plan inside the target directory.
6. Initialize the package manager and install dependencies.
7. Create all configuration files listed in the plan.
8. Create stub entry points or application skeletons that build and run cleanly.
9. Set up the test framework with at least one passing example test.
10. Create a README with project name, description, prerequisites, install steps, run commands, test commands, and deployment notes (if applicable).
11. Create a .gitignore covering the language, framework, tooling, OS, and IDE artifacts.
12. Set up CI/CD configuration if specified in the plan.
13. Create an .env.example if the project uses environment variables (no real secrets).
14. Run all available validation: build, lint, type check, and tests.
15. Do not commit or push without my explicit permission.
16. Do not overwrite, revert, delete, or reformat unrelated user changes.
17. If you encounter a decision not covered by the plan, stop and ask rather than guessing.

At the end, provide:

1. Directory structure created
2. Dependencies installed
3. Configuration files created
4. Validation commands run and results
5. Any deviations from the plan (with rationale)
6. Known issues or incomplete items
```

## Step 4: Validate the Scaffold

After scaffolding, start a new session and use this prompt:

```text
A new project has been scaffolded according to the plan at:

<path-to-plan>

Target directory:

<absolute or repository-relative path to the project directory>

Validate that the scaffold is correct and ready for development.

Your goals:

1. Verify the directory structure matches the plan.
2. Verify all dependencies install cleanly from a cold start by removing only generated install/build artifacts inside the confirmed target directory, then reinstalling.
3. Run the full validation suite: build, lint, type check, tests.
4. Verify the README instructions work as documented (install, run, test).
5. Check that .gitignore covers appropriate artifacts.
6. Check that no secrets, credentials, or sensitive data are present in the scaffold.
7. Verify CI configuration is syntactically valid, if applicable.
8. Classify each finding by severity:
   - Critical: must fix before development begins
   - Major: should fix before development begins
   - Minor: improvement or cleanup
   - Question: needs clarification
9. Fix issues that are safe and clearly within scope.
10. Do not commit or push without my explicit permission.
11. Do not overwrite, revert, delete, or reformat unrelated user changes.

Use this format for every finding:

### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Recommended fix:
- Status: Open / Fixed / Needs decision

If the scaffold is clean, say so and list the validation performed.
```

## Step 5: Final Report / Handoff

Use this prompt after validation is complete:

```text
Produce a final initialization report for the project scaffolded according to the plan at:

<path-to-plan>

Target directory:

<absolute or repository-relative path to the project directory>

The report should include:

1. Project summary
2. Technology stack (language, framework, tooling, versions)
3. Directory structure
4. Dependencies (production and development)
5. Configuration files created
6. CI/CD setup status
7. Validation results (build, lint, type check, tests)
8. README completeness
9. Known limitations or deferred items
10. Suggested next steps for development
11. Confirmation that no commit or push was performed

Also verify:

1. No secrets or credentials are committed.
2. All validation commands pass or failures are documented.
3. The project builds and runs after a fresh install from the scaffolded working tree.

Do not commit or push without my explicit permission.
```

## Practical Notes

- Also follow the shared conventions in [shared/workflow-conventions.md](shared/workflow-conventions.md) where applicable. Some conventions (e.g., baselines, behavior preservation) are oriented toward existing codebases and may not apply to greenfield work.
- Use the project plan as the source of truth throughout the workflow.
- Prefer ecosystem defaults and widely adopted tooling over novel or niche choices unless requirements dictate otherwise.
- Pin or constrain dependency versions to avoid surprise breakage.
- Do not install dependencies you do not need yet. Start lean and add as requirements emerge.
- Treat open questions as blockers unless the answer is obvious from the stated requirements.
- When the project is ready, hand off to the [feature-development-agent-workflow.md](feature-development-agent-workflow.md) for building the first feature.
