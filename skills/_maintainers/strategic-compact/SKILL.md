---
name: strategic-compact
description: "Maintainer-only context compaction guidance for long curation or migration sessions. Suggests manual compaction at logical boundaries instead of arbitrary compaction points."
risk: safe
source: codex-max
origin: ECC-adapted
date_added: "2026-04-19"
---

# Strategic Compact

## Overview

`strategic-compact` is a maintainer-only context-management skill.
Use it during long-running curation, migration, or repository-maintenance sessions when context pressure starts to reduce quality.

The goal is to compact deliberately at logical boundaries rather than in the middle of unresolved work.

## Use when

- Running a long skill-catalog curation session
- Migrating or reorganizing the workspace surface over many phases
- Switching from analysis to implementation, or from one rollout wave to another
- Context pressure is increasing and the session should be reset cleanly

## Recommended compaction points

Compact at logical boundaries such as:

- after inventory / research is complete
- after a rollout wave is verified
- before switching to a different repo or workflow surface
- after a failed approach that should not pollute the next attempt

Avoid compacting:

- in the middle of an active code edit
- while unresolved implementation details still live only in conversation state
- before important findings have been persisted to files

## Preserve before compacting

Before compacting, ensure key state is written to durable artifacts such as:

- `task_plan.md`
- `findings.md`
- `progress.md`
- `skills/CATALOG.md`
- `skills/manifest.yaml`
- docs or ADR artifacts created during the session

## Output contract

When using this skill, state:

- **Current phase**
- **Why this is a logical compact point**
- **What has been written to disk**
- **What the next phase will focus on after compacting**

## Related skills

- `planning-with-files` — persistent working memory on disk
- `agent-sort` — classify the skill surface before compaction
- `manage-skills` — apply curation changes after context has been stabilized
