---
name: manage-skills
description: "Maintainer-only workflow for managing the codex-max curated skill library. Covers import, rewrite, promote, demote, optionalize, archive, and documentation synchronization."
risk: safe
source: codex-max
origin: Antigravity-adapted
date_added: "2026-04-19"
---

# Manage Skills

## Overview

`manage-skills` is a maintainer-only workflow for this repository's curated skill library.
Use it to evolve the library without letting runtime behavior drift away from the documented source of truth.

This skill is specific to codex-max and its curated structure.
It is **not** a generic multi-tool skill manager.

## Managed surfaces

This workflow can act on:

- `skills/` runtime and optional skills
- `skills/_maintainers/` maintainer-only skills
- `skills/CATALOG.md`
- `skills/manifest.yaml`
- supporting docs such as project-structure files
- onboarding / ADR maintainer docs when needed

## Typical operations

### Add or import a skill

- create the skill directory
- add `SKILL.md`
- decide whether it belongs to runtime core, optional, or maintainer-only
- update catalog and manifest in the same change set
- update structure docs if the library layout changes
- verify the resulting surface

### Promote a skill

Move a skill toward default usage when repo evidence justifies it.
Examples:
- optional → active runtime
- maintainer-only → optional or active

### Demote a skill

Reduce context load when a skill is too noisy or too niche.
Examples:
- active runtime → optional
- optional → maintainer-only
- maintainer-only → archive/defer

### Rewrite or replace a skill

Use when the current behavior is too heavy, duplicated, or mismatched with the workspace contract.
Examples:
- replacing a legacy router with a thinner one
- adapting upstream guidance to current runtime constraints

## Non-negotiable rules

- Every structural change must update both `skills/CATALOG.md` and `skills/manifest.yaml`
- Do not let optional or maintainer-only skills silently become default routing dependencies
- Keep exactly one canonical skill per capability where possible
- Prefer adaptation over raw copy when upstream assumptions do not fit this workspace
- Verify the library surface after every change set

## Output contract

When this skill is used, report:

- **Operation performed**
- **Files added or changed**
- **New classification** (runtime / optional / maintainer-only / deferred)
- **Docs synchronized**
- **Verification evidence**

## Related skills

- `agent-sort` — decide the right bucket before changing the library
- `strategic-compact` — manage context during long curation sessions
