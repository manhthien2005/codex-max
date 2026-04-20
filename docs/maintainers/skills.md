# Maintainer Guide: Curated Skills Library

This document explains how to maintain the curated skill surface in this repository.

## Library layers

| Layer | Path | Purpose |
|---|---|---|
| Runtime core / optional skills | `skills/` | Installed skills used directly by the workspace |
| Maintainer-only skills | `skills/_maintainers/` | Curation and library-management workflows not meant for default runtime routing |
| Source of truth | `skills/CATALOG.md`, `skills/manifest.yaml` | Human + machine-readable inventory |

## Classification model

Use these buckets:

- **active runtime** — part of the curated execution surface
- **optional** — installed and available, but not default routing
- **maintainer-only** — installed for library curation or maintenance only
- **archive / defer** — not part of the current curated surface

## Required files to update

Whenever a skill is added, promoted, demoted, or rewritten, update at least:

- `skills/CATALOG.md`
- `skills/manifest.yaml`
- `skills/README.md` if the visible surface changed
- `docs/PROJECT_STRUCTURE.md`
- `docs/PROJECT_STRUCTURE.vi.md`

Update `AGENTS.md` or router skills only if routing behavior changes.

## Recommended workflow

1. Classify with `agent-sort`
2. Apply structural changes with `manage-skills`
3. Compact context at logical boundaries with `strategic-compact` if needed
4. Run verification after each batch

## Verification baseline

Typical verification for this repository should include:

- Python compile checks for hook Python files
- JSON parse check for `hooks.json`
- content checks for catalog, manifest, and structure docs
- smoke execution of PowerShell hook wrappers

## Notes

- Maintainer-only skills should not be auto-loaded in normal routing
- Optional skills may be installed without becoming default behavior
- Keep the daily surface small and evidence-backed
