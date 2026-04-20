# Skills Directory

This directory is the curated runtime skill surface for this workspace.
It is intentionally small, reviewable, and versioned with the repository.
This repo does **not** ship the full upstream ECC or Antigravity libraries as part of the active runtime surface.

## Source of truth

Two files define the current skill surface:

- `skills/CATALOG.md` — human-readable catalog for maintainers
- `skills/manifest.yaml` — machine-readable manifest for installed and planned skills

If a skill is not listed there, it should not be treated as part of the active curated bundle.

## Current installed runtime skills

| Skill | Tier | Status | Purpose |
|---|---|---|---|
| `concise-planning` | daily | active | Lightweight planning for medium tasks |
| `planning-with-files` | daily | active | Persistent file-based planning for multi-step work |
| `systematic-debugging` | daily | active | Root-cause-first debugging workflow |
| `lint-and-validate` | daily | active | Mandatory validation after code changes |
| `search-first` | library | active | Research-before-coding and dependency-choice discipline |
| `documentation-lookup` | library | active | Current docs lookup for libraries, frameworks, and APIs |
| `gateguard` | library | active | Fact-forcing pre-action gate adapted to Bash-hook reality |
| `brainstorming` | library | active | Design-first clarification before implementation |
| `test-driven-development` | library | active | Test-first behavior implementation workflow |
| `codebase-onboarding` | library | active | Structured onboarding workflow for unfamiliar repositories |
| `architecture-decision-records` | library | active | ADR recording and decision-history discipline |
| `git-workflow` | library | active | Branch, commit, PR, merge, and release discipline |
| `e2e-testing` | library | active | End-to-end user-journey and browser verification workflow |
| `security-review` | library | active | Security-focused review workflow for risky changes |
| `task-router-lite` | daily | active | Thin Phase PLAN router that selects at most one primary and one optional secondary skill |
| `task-intelligence` | daily | legacy alias | Compatibility entrypoint that now routes through the thin PLAN behavior |
| `verification-before-completion` | daily | active | Evidence-first completion gate |

## Installed optional library skills

| Skill | Status | Purpose |
|---|---|---|
| `browser-automation` | optional | Browser automation and scraping-oriented workflow |
| `security-auditor` | optional | Deeper security audit workflow beyond standard security review |
| `context7-auto-research` | optional | Alternative Context7-driven docs-current workflow |

## Installed maintainer-only skills

| Skill | Status | Purpose |
|---|---|---|
| `agent-sort` | maintainer-only | Evidence-backed curation workflow for sorting surfaces into runtime / optional / maintainer buckets |
| `strategic-compact` | maintainer-only | Context compaction guidance for long curation or migration sessions |
| `manage-skills` | maintainer-only | Structural management of the curated skill library |

## Internal support assets

| Path | Role |
|---|---|
| `.system/` | Internal workspace support assets; not a user-selectable skill |

## How skills are used in this workspace

- Skills are primarily loaded by the workspace contract in `AGENTS.md` and by the runtime decision flow.
- Some skills act as mandatory discipline layers rather than optional convenience tools.
- This repository does not treat marketplace-style `@skill-name` chat syntax as its primary contract.
- New external skills should be reviewed, curated, and registered before becoming part of the runtime surface.

## Directory structure

```text
skills/
├── .system/
├── _maintainers/
│   ├── agent-sort/
│   ├── manage-skills/
│   └── strategic-compact/
├── architecture-decision-records/
├── brainstorming/
├── browser-automation/
├── codebase-onboarding/
├── concise-planning/
├── context7-auto-research/
├── documentation-lookup/
├── e2e-testing/
├── gateguard/
├── git-workflow/
├── lint-and-validate/
├── planning-with-files/
├── search-first/
├── security-auditor/
├── security-review/
├── systematic-debugging/
├── task-intelligence/
├── task-router-lite/
├── test-driven-development/
├── verification-before-completion/
├── CATALOG.md
└── manifest.yaml
```

## Change policy

- Keep exactly one canonical skill per capability.
- Prefer hardening an existing native skill over importing a duplicate.
- `task-router-lite` is the canonical Phase PLAN router.
- `task-intelligence` remains only as a compatibility alias until all references migrate.
- Optional skills are installed but should not automatically displace the core routing defaults.
- Maintainer-only skills live under `skills/_maintainers/` and must not be auto-loaded for normal execution.
- Any newly imported skill must update both `skills/CATALOG.md` and `skills/manifest.yaml` in the same change set.
- Planned skills may be documented in the catalog before import, but they are not part of the active runtime until installed.

## Planned next wave

No additional import wave is currently scheduled in the curated roadmap.
Optional and maintainer-only skills remain available without becoming part of the core routing path.

See `skills/CATALOG.md` for the rollout view and `skills/manifest.yaml` for structured metadata.
