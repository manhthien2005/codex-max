---
name: browser-automation
description: "Optional browser automation workflow for interactive browser tasks, Playwright-style automation, and stable scraping/testing patterns."
risk: safe
source: codex-max
origin: Antigravity-adapted
date_added: "2026-04-19"
---

# Browser Automation

## Overview

Use `browser-automation` for browser-driven tasks that are more interactive or automation-oriented than the normal E2E test workflow.
This includes repeatable browser actions, scraping-style flows, UI automation, popup handling, and resilient selector/wait strategies.

This skill is installed as an **optional** library skill, not a core routing default.

## Use when

- Automating a browser workflow end-to-end
- Building or fixing Playwright-style browser automation
- Handling popups, downloads, or multi-tab flows
- Extracting information from a web UI with stable automation patterns
- Debugging flaky browser interactions caused by selectors or waits

## Core principles

- Prefer user-facing locators over brittle CSS/XPath selectors
- Let the automation framework auto-wait when possible
- Avoid arbitrary sleeps and `waitForTimeout`-style habits
- Keep browser sessions isolated when test or workflow independence matters
- Collect artifacts when failures are hard to reproduce

## Recommended workflow

### 1. Define the browser goal

State clearly:
- entry URL or app state
- actions to perform
- expected visible result
- whether the task is testing, automation, or extraction

### 2. Choose stable selectors

Prefer:
- accessible roles
- visible labels
- test IDs
- explicit text anchors when appropriate

Avoid defaulting to brittle DOM-shape selectors.

### 3. Use condition-based waits

Wait for:
- visible elements
- expected responses
- navigation completion
- popup readiness
- download events

Avoid arbitrary time delays unless no better synchronization point exists.

### 4. Capture evidence

When needed, retain:
- screenshots
- traces
- videos
- downloaded files
- extracted data snapshots

## Output contract

When this skill is used, the result should include:

- **Browser goal**
- **Automation strategy**
- **Selector/waiting approach**
- **Failure-risk notes**
- **Artifacts/evidence strategy**

## Related skills

- `e2e-testing` — for formal user-journey verification
- `documentation-lookup` — for current browser/tooling API usage
- `search-first` — before adding a browser automation dependency or wrapper
