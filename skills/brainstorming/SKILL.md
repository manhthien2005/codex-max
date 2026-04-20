---
name: brainstorming
description: "Use before creative or constructive work when requirements or solution shape are still unclear. Turns vague ideas into confirmed designs before implementation begins."
risk: safe
source: codex-max
origin: Antigravity-adapted
date_added: "2026-04-19"
---

# Brainstorming

## Overview

Use `brainstorming` before implementation when the request is still underspecified, ambiguous, or design-heavy.
The goal is to slow down just enough to confirm intent, constraints, assumptions, and trade-offs before code is written.

In this workspace, `brainstorming` is a **design and clarification mode**, not an implementation mode.

## Use when

- A feature request is vague or incomplete
- The user asks for a design before coding
- Multiple approaches are possible and trade-offs matter
- Behavior, UX flow, or architecture is still unclear
- The request sounds like “figure out what we should build” before “build it now”

## Do not use when

- The task is already concrete and implementation-ready
- The user wants execution only and the design is already agreed
- A narrow execution skill already matches the task clearly

## Core rules

- Do not jump into implementation while this skill is active
- Ask one focused question at a time when clarification is still needed
- Prefer multiple-choice framing when possible
- Make assumptions explicit
- Summarize understanding before proposing a final design
- Keep the design discussion incremental and reviewable

## Recommended flow

### 1. Understand the current context

Before proposing solutions:

- Inspect the current repo or available context
- Identify what already exists
- Note explicit constraints and likely hidden constraints
- Separate confirmed facts from assumptions

### 2. Clarify the idea

Clarify, one step at a time:

- purpose
- target users
- constraints
- success criteria
- non-goals

### 3. Surface non-functional requirements

Explicitly cover:

- performance expectations
- scale
- security/privacy constraints
- reliability expectations
- maintenance ownership

If the user is unsure, propose defaults and mark them as assumptions.

### 4. Understanding lock

Before moving to a design recommendation, present:

- a short understanding summary
- assumptions
- open questions

Then require confirmation before continuing.

### 5. Explore approaches

Present 2–3 viable approaches when appropriate.
Lead with the recommended option, but explain trade-offs clearly.
Favor YAGNI and avoid speculative scope growth.

### 6. Handoff to implementation

Only after the design is accepted should the task move back into implementation routing.
At that point, hand off to the appropriate execution skill, often:

- `planning-with-files`
- `concise-planning`
- `test-driven-development`
- `lint-and-validate`

## Output contract

When this skill is used, the result should include:

- **Understanding summary**
- **Assumptions**
- **Open questions**
- **Recommended approach**
- **Alternatives considered**
- **Decision checkpoint**

## Related skills

- `task-router-lite` — routes here when the request is underspecified
- `planning-with-files` — persists the clarified plan once the design is accepted
- `test-driven-development` — use after behavior is clear enough to implement test-first
