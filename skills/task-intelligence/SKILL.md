---
name: task-intelligence
description: "Legacy compatibility alias for task-router-lite. Keeps older codex-max references working while using a thin Phase PLAN routing model."
risk: safe
source: codex-max
date_added: "2026-04-19"
---

# Task Intelligence (Compatibility Shim)

## Overview

This skill name is kept only for backward compatibility.
It no longer behaves like a broad multi-agent amplification or orchestration layer.

Current behavior: **act as the thin Phase PLAN router used by `task-router-lite`.**

## Compatibility rules

- Treat `task-router-lite` as the canonical PLAN behavior.
- Keep older references to `task-intelligence` working without changing the runtime contract abruptly.
- Select at most:
  - `0-1` primary execution skill
  - `0-1` optional secondary skill
- Prefer installed local skills first.
- Never call missing orchestration scripts.
- Never expand this skill back into a fan-out orchestrator.

## Thin routing behavior

### Choose the primary skill

| Situation | Primary skill |
|---|---|
| Bug, failing test, unexpected behavior | `systematic-debugging` |
| Multi-step or high-context task | `planning-with-files` |
| Medium planning task | `concise-planning` |
| Validation after code changes | `lint-and-validate` |
| Completion / fixed / passed claim | `verification-before-completion` |
| Underspecified feature | `brainstorming` if installed; otherwise `concise-planning` or `planning-with-files` |
| Library / framework / API lookup | `documentation-lookup` if installed; otherwise local docs / repo evidence / Context7 |
| Before coding, dependency, or utility choice | `search-first` if installed; otherwise targeted repository search |
| Unfamiliar repo onboarding | `codebase-onboarding` if installed; otherwise targeted repository discovery |
| Significant architecture decision or trade-off | `architecture-decision-records` if installed; otherwise ADR-style structured notes |
| Git branching / commit / PR / merge / release discipline | `git-workflow` if installed; otherwise repo git conventions |
| Critical user journey or browser-flow verification | `e2e-testing` if installed; otherwise existing test tools |
| Auth / secrets / sensitive endpoints / risky data handling | `security-review` if installed; otherwise direct security checklist |

### Optional secondary skill

Use a secondary skill only when it clearly adds value and keep it to **one**:

- `verification-before-completion` for completion gates
- `lint-and-validate` after code changes
- `planning-with-files` for persistent state on long tasks

## Output contract

Before implementation, produce the workspace readiness table:

| Context Element | Details |
| :--- | :--- |
| **Active repo** | `[path]` |
| **Related repos** | `[paths]` |
| **Context readiness** | `Ready` / `Incomplete` |
| **Execution intent** | `[brief description]` |
| **Difficulty level** | `easy`, `medium`, or `hard` |
| **Subagent decision** | `Spawning Subagent` / `Direct Execution` |
| **Phase BUILD Skills** | `[selected skills]` |

## Explicitly removed from legacy behavior

- No blanket activation of many agents.
- No references to missing `agent-orchestrator` scripts.
- No mandatory time-estimation theater.
- No speculative fan-out before understanding the actual task.

## Maintainer note

When all workspace references have migrated, `task-intelligence` should remain only as a compatibility alias or be retired cleanly.
