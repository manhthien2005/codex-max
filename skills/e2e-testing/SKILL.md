---
name: e2e-testing
description: "Use for end-to-end testing of critical user journeys, especially browser-driven flows. Focus on stable, maintainable Playwright-style testing patterns and evidence collection."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# E2E Testing

## Overview

Use `e2e-testing` when a task requires validating a user journey across the full stack, not just unit or integration boundaries.
The emphasis is on stable scenarios, maintainable structure, and useful artifacts when failures happen.

## Use when

- Testing critical browser flows
- Verifying auth, checkout, onboarding, search, or dashboard journeys end-to-end
- Adding Playwright-style tests
- Defining where E2E fits relative to unit and integration coverage
- Capturing traces, screenshots, or video for full-stack verification

## Core principles

- Test user-visible behavior, not implementation details
- Keep scenarios focused and business-relevant
- Prefer stable locators and explicit conditions over arbitrary sleeps
- Collect useful failure artifacts
- Reserve E2E for critical paths; do not use it to replace lower-level tests

## Recommended workflow

### 1. Define the journey

State:

- start state
- user actions
- expected visible result
- data or environment dependencies

### 2. Structure the test suite

Prefer:

- dedicated E2E directory
- shared fixtures for login/data setup
- page object or helper abstraction where it reduces duplication

### 3. Stabilize the test

Use:

- stable selectors
- explicit waits for the correct condition
- retries only as a last resort
- screenshots/traces/videos on failure

### 4. Report evidence

When an E2E run matters, keep:

- test outcome
- failing step if any
- artifact location if generated

## Output contract

When this skill is used, the result should include:

- **Journey under test**
- **Coverage scope**
- **Test structure recommendation**
- **Stability considerations**
- **Artifacts/evidence strategy**

## Related skills

- `test-driven-development` — for lower-level behavior-first implementation before E2E
- `verification-before-completion` — for evidence-based completion claims
- `task-router-lite` — routes here when the task is primarily E2E or user-journey verification
