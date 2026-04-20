---
name: task-router-lite
description: "Thin Phase PLAN router for codex-max. Select at most one primary execution skill and one optional secondary skill from the installed local skill surface."
risk: safe
source: codex-max
date_added: "2026-04-19"
---

# Task Router Lite

## Overview

`task-router-lite` is the canonical Phase PLAN router for this workspace.
Its job is to make the execution surface lighter, more predictable, and more faithful to the installed local skill set.

It does **not** fan out into many agents or many skills.
It does **not** rely on missing orchestration scripts.
It does **not** invent process overhead when a narrow local skill is enough.

## Core contract

Before implementation:

1. Identify the active repo.
2. Identify related repos for read-only context.
3. State allowed write scope and git scope.
4. Classify the task as `easy`, `medium`, or `hard`.
5. Select at most:
   - `0-1` primary execution skill
   - `0-1` optional secondary skill
6. Prefer installed local skills first.
7. If an ideal skill is not installed yet, fall back to the closest installed native behavior.

## Hard limits

- Do **not** activate many skills in parallel.
- Do **not** call missing orchestration scripts.
- Do **not** assume external skill libraries are installed just because they are planned.
- Do **not** invent time estimates unless the user explicitly asks for an estimate.
- Do **not** replace execution skills; only route into them.

## Primary routing table

| Situation | Primary skill | Optional secondary | Fallback if planned skill is not installed |
|---|---|---|---|
| Bug, failing test, unexpected behavior | `systematic-debugging` | `verification-before-completion` | none |
| Multi-step or high-context task | `planning-with-files` | `verification-before-completion` | none |
| Medium planning task without heavy execution | `concise-planning` | none | none |
| Code changes that must be validated | `lint-and-validate` | `verification-before-completion` | none |
| Completion / pass / fixed claim | `verification-before-completion` | none | none |
| Underspecified feature or vague request | `brainstorming` | `planning-with-files` | use `concise-planning` or `planning-with-files` |
| Library / framework / API lookup | `documentation-lookup` | none | use local docs, repo evidence, or Context7 |
| Before coding, dependency choice, or utility choice | `search-first` | none | use targeted codebase search and repo evidence |
| Unfamiliar repo onboarding | `codebase-onboarding` | `planning-with-files` | use targeted repository discovery |
| Significant architecture decision or trade-off | `architecture-decision-records` | `planning-with-files` | use ADR-style structured notes |
| Git branching / commit / PR / merge / release discipline | `git-workflow` | `verification-before-completion` | use direct repo git conventions |
| Critical user journey or browser-flow verification | `e2e-testing` | `verification-before-completion` | use existing test tools directly |
| Auth / secrets / sensitive endpoints / risky data handling | `security-review` | `verification-before-completion` | use direct security checklist |

## Difficulty guidance

- `easy`: direct execution, usually no subagent
- `medium`: direct execution unless the task separates cleanly
- `hard`: prefer at least one subagent when the work is separable and the current tool/runtime constraints allow it

## Output contract

Before implementation, produce the readiness table required by workspace policy:

| Context Element | Details |
| :--- | :--- |
| **Active repo** | `[path]` |
| **Related repos** | `[paths]` |
| **Context readiness** | `Ready` / `Incomplete` |
| **Execution intent** | `[brief description]` |
| **Difficulty level** | `easy`, `medium`, or `hard` |
| **Subagent decision** | `Spawning Subagent` / `Direct Execution` |
| **Phase BUILD Skills** | `[selected skills]` |

## Execution handoff rules

- Choose the narrowest skill that matches the task.
- Keep the BUILD phase small and explicit.
- If no installed skill matches perfectly, say which fallback behavior is being used.
- If the user asks for pure analysis only, stop at routing and analysis.

## Workspace fit

This router exists because the workspace is curated.
The runtime surface must stay aligned with `.agents/skills/`, while the source library stays aligned with `skills/README.md`, `skills/CATALOG.md`, and `skills/manifest.yaml`.
