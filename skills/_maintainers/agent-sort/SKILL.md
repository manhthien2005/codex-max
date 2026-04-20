---
name: agent-sort
description: "Maintainer-only curation workflow for codex-max. Build an evidence-backed plan to sort skills, hooks, docs, and related surfaces into runtime core, optional library, maintainer-only, or archive buckets."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Agent Sort

## Overview

`agent-sort` is a maintainer-only curation skill.
Use it when this repository needs an evidence-backed decision about which skills or related surfaces belong in the curated runtime, which should stay optional, and which should remain maintainer-only.

The goal is not opinion-driven trimming. The goal is repo-aware classification backed by actual evidence from the current workspace.

## Use when

- The curated skill surface feels too large or too noisy
- A new batch of upstream skills needs classification
- You need to decide whether something belongs in runtime core, optional, maintainer-only, or archive
- A repository has drifted away from its intended daily workflow surface
- You want a documented curation plan instead of ad-hoc edits

## Buckets

Use these buckets for this workspace:

- **runtime core**
  - installed and relevant for regular task execution
- **optional library**
  - installed and available, but not default routing
- **maintainer-only**
  - useful for library curation, compaction, or administration
- **archive / defer**
  - keep out of the active surface for now

## Evidence sources

Base the classification on concrete repo evidence:

- installed skill set in `skills/`
- routing contract in `AGENTS.md`
- hook behavior in `hooks/`
- current catalog/manifest
- actual task patterns and repository workflows
- docs that define the intended operating model

## Output contract

When this skill is used, produce:

- **Stack / workflow summary**
- **Runtime core inventory**
- **Optional inventory**
- **Maintainer-only inventory**
- **Archive / defer list**
- **Install or cleanup plan**
- **Verification notes**

## Rules

- Every promotion to runtime core must cite repo evidence
- Optional does not mean useless; it means not worth loading by default
- Maintainer-only tools must not silently become default runtime dependencies
- Prefer a small, reviewable daily surface over a broad “maybe useful” surface

## Related skills

- `manage-skills` — apply curation decisions to the library structure
- `strategic-compact` — preserve context during long curation sessions
