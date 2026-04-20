---
name: search-first
description: "Research-before-coding workflow for codex-max. Check the repo, installed skills, libraries, and existing patterns before building custom code or adding dependencies."
risk: safe
source: ECC-adapted
origin: ECC
date_added: "2026-04-19"
---

# Search First

## Overview

Use `search-first` before writing net-new helpers, abstractions, or dependency-driven integrations.
The goal is to reduce duplication, avoid unnecessary packages, and anchor decisions in evidence.

In this workspace, `search-first` is **repo-first and evidence-first**:

1. Search the current repository for an existing implementation.
2. Search the installed curated skill surface.
3. Check package ecosystems or MCP capabilities if the problem likely already has a maintained solution.
4. Decide whether to adopt, wrap, compose, or build custom code.

## Use when

- Starting a feature that may already have an internal implementation
- Adding a dependency or integration
- Creating a new utility, helper, adapter, or abstraction
- Choosing between custom code and an existing library
- Looking for an existing pattern before refactoring

## Repo-first workflow

### Step 1 — Search the current repository

Gather evidence from the codebase first:

- Find similar files, functions, utilities, or tests
- Check whether an adjacent repo or existing module already solves the problem
- Check whether the skill surface already has a workflow for the task

### Step 2 — Evaluate existing options

When a candidate exists, decide using this order:

1. **Adopt** — use the existing implementation as-is
2. **Wrap** — add a thin integration layer around it
3. **Compose** — combine a small number of existing components
4. **Build** — write custom code only when the above are inadequate

### Step 3 — Document the choice

Before implementation, state briefly:

- what was searched
- what was found
- why the chosen path is appropriate

## Output contract

When this skill is used, the analysis should produce:

- **Need** — what functionality is required
- **Existing repo findings** — what already exists locally
- **External candidates** — packages, MCPs, skills, or references if relevant
- **Decision** — adopt / wrap / compose / build

## Constraints for this workspace

- Prefer repo-local evidence before external package search
- Prefer small, reviewable solutions over dependency bloat
- If network or external discovery is unavailable, use local evidence and say so explicitly
- Do not add a package until the repo has been checked for an equivalent solution

## Related skills

- `documentation-lookup` — use when the decision depends on current library or framework behavior
- `gateguard` — use to force fact gathering before risky Bash or edit actions
- `task-router-lite` — routes into `search-first` when dependency or utility choice is the main decision
