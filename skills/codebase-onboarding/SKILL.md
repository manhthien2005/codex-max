---
name: codebase-onboarding
description: "Use when entering an unfamiliar repository or when the user asks to understand a codebase. Produces a structured onboarding view: stack, entry points, directory roles, request flow, and conventions."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Codebase Onboarding

## Overview

Use `codebase-onboarding` to understand an unfamiliar repository without reading everything.
The goal is to produce a fast, structured map of the codebase so future implementation work starts with correct context.

In this workspace, onboarding is **evidence-first and scope-aware**:

1. detect the active repo
2. inspect manifests, entry points, tests, tooling, and top-level structure
3. map request/data flow through the codebase
4. summarize conventions and where key work should happen

## Use when

- First time opening a repository
- The user asks “onboard me”, “walk me through this repo”, or “help me understand this codebase”
- A task depends on locating the right entry points before editing
- A project-specific onboarding guide should be produced

## Workflow

### 1. Reconnaissance

Start with signals, not blanket file reading:

- package and build manifests
- framework fingerprints
- entry points
- top-level directory map
- test layout
- CI/config/tooling files

### 2. Architecture map

Identify:

- language and framework stack
- frontend/backend split
- data layer and persistence model
- primary request flow or execution path
- key directories and their responsibilities

### 3. Convention detection

Capture patterns already in use:

- naming conventions
- testing patterns
- error-handling style
- dependency structure
- build/run commands
- git conventions if history is available and in-scope

### 4. Onboarding output

Produce a concise onboarding artifact with:

- project overview
- tech stack
- architecture summary
- key entry points
- directory map
- request lifecycle summary
- common commands
- where to look for common tasks

## Output contract

When this skill is used, the result should include:

- **Overview**
- **Tech stack**
- **Architecture map**
- **Key entry points**
- **Directory roles**
- **Conventions**
- **Common commands**

## Workspace fit

- Keep onboarding scannable rather than exhaustive
- Prefer repo-local evidence over assumptions
- If a reusable onboarding note is needed, store it under `docs/onboarding/`
- Respect active repo boundaries and do not assume the workspace root is the git scope

## Related skills

- `planning-with-files` — persist onboarding findings for a larger task
- `search-first` — use once onboarding reveals multiple implementation options
- `task-router-lite` — routes here when the repo is unfamiliar
