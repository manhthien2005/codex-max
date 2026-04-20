---
name: gateguard
description: "Fact-forcing pre-action gate for codex-max. On this runtime, Bash can be gated by hooks while Edit/Write discipline is enforced through AGENTS.md and routing instructions."
risk: safe
source: ECC-adapted
origin: ECC
date_added: "2026-04-19"
---

# GateGuard

## Overview

`gateguard` is a fact-forcing pre-action discipline.
Its purpose is to stop guess-first behavior by forcing investigation before risky actions.

In this workspace, the enforcement model is intentionally split:

- **Bash actions** → lightweight gating and reminders via `hooks/pre_tool_use.py`
- **Edit/Write decisions** → enforced through `AGENTS.md`, `task-router-lite`, and skill instructions

This reflects the current Codex runtime reality: PreToolUse/PostToolUse hooks are reliably available for Bash, not for every edit action.

## Core principle

Before risky action, gather concrete facts.
Do not rely on self-confidence or vague intent.

## Use when

- About to run destructive or high-impact Bash commands
- About to add dependencies without checking existing repo solutions
- About to change behavior that may affect importers, schemas, or conventions
- Working in a codebase where guessing patterns causes regressions

## Bash gate patterns for this workspace

### Destructive Bash gate

Before destructive Bash, gather:

1. Which files or data will be affected
2. A one-line rollback step
3. The exact current user instruction being followed

Examples:

- `rm -rf`
- `git reset --hard`
- `git clean -fd`
- `git push --force`
- destructive data commands

### Dependency-install gate

Before installing a package, gather:

1. Evidence that the repo does not already contain an equivalent solution
2. Evidence that the chosen dependency is the smallest acceptable fit
3. Evidence that current docs were checked first when API behavior matters

## Non-Bash enforcement note

Because this runtime does not reliably gate every Edit/Write action through hooks, the same discipline must remain in:

- `AGENTS.md`
- `task-router-lite`
- skills such as `search-first` and `documentation-lookup`

## Output contract

When this skill is active, the pre-action note should contain:

- **Action**
- **Facts gathered**
- **Risk**
- **Rollback**

## Related skills

- `search-first` — for dependency and utility decisions
- `documentation-lookup` — for current library behavior
- `task-router-lite` — for routing the task into the right discipline before execution
