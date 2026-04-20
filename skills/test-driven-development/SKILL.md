---
name: test-driven-development
description: "Use when implementing a feature, bugfix, refactor, or behavior change where a failing test can be written before production code."
risk: safe
source: codex-max
origin: Antigravity-adapted
date_added: "2026-04-19"
---

# Test-Driven Development

## Overview

Use TDD when behavior can be captured in a test before implementation.
The discipline is simple:

1. Write the test first
2. Watch it fail for the right reason
3. Write the minimum code to make it pass
4. Refactor while keeping tests green

## Core principle

If you did not watch the new test fail first, you do not know whether it truly verifies the intended behavior.

## Use when

- New features
- Bug fixes
- Refactors with behavior protection
- Any change where the desired behavior can be tested directly

## Usually skip when

- Pure documentation changes
- Pure configuration changes
- Non-executable design discussion
- Situations where a meaningful failing test cannot be written yet

## The cycle

### RED

Write one focused failing test that demonstrates the intended behavior.

Requirements:
- clear test name
- one behavior per test
- failure should reflect the missing behavior, not a typo or setup problem

### VERIFY RED

Run the test and confirm:
- it fails
- it fails for the expected reason
- it is not accidentally passing because the behavior already exists

### GREEN

Write the minimum production code required to make the test pass.
Do not overbuild. Do not add speculative abstractions.

### VERIFY GREEN

Run the test again and confirm it passes.
Then run the relevant surrounding checks so you do not break adjacent behavior.

### REFACTOR

Only after green:
- improve names
- reduce duplication
- extract helpers
- simplify structure

Then re-run tests to confirm behavior remains intact.

## Workspace-specific rules

- Pair this skill with `lint-and-validate` after code changes
- Pair this skill with `verification-before-completion` before claiming success
- If the task started vague, use `brainstorming` first until the behavior is clear enough to test
- Keep the first test as small and local as possible

## Output contract

When this skill is active, report progress in terms of:

- **Red test written**
- **Observed failure reason**
- **Minimal code added**
- **Passing test evidence**
- **Relevant follow-up validation**

## Anti-patterns

- Writing production code before the test
- Writing a test after implementation and calling it TDD
- Mocking everything so heavily the test no longer proves behavior
- Expanding scope during the green step
- Skipping the explicit failing-test check

## Related skills

- `brainstorming` — clarify behavior before implementation when the request is still vague
- `lint-and-validate` — validate after code changes
- `verification-before-completion` — require fresh evidence before completion claims
- `systematic-debugging` — use when the problem is diagnosis-first rather than implementation-first
