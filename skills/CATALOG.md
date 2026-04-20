# Skill Catalog

This catalog is the human-readable inventory for the curated skill surface in this repository.

## Installed runtime skills

| Name | Tier | Status | Origin | Purpose | Path |
|---|---|---|---|---|---|
| `concise-planning` | daily | active | codex-max | Lightweight planning for medium tasks | `skills/concise-planning/` |
| `planning-with-files` | daily | active | codex-max | Persistent file-based planning for multi-step work | `skills/planning-with-files/` |
| `systematic-debugging` | daily | active | codex-max | Root-cause-first debugging workflow | `skills/systematic-debugging/` |
| `lint-and-validate` | daily | active | codex-max | Mandatory validation after code changes | `skills/lint-and-validate/` |
| `search-first` | library | active | ECC-adapted | Research-before-coding and dependency-choice discipline | `skills/search-first/` |
| `documentation-lookup` | library | active | ECC-adapted | Current docs lookup for libraries, frameworks, and APIs | `skills/documentation-lookup/` |
| `gateguard` | library | active | ECC-adapted | Fact-forcing pre-action gate adapted to Bash-hook reality | `skills/gateguard/` |
| `brainstorming` | library | active | Antigravity-adapted | Design-first clarification before implementation | `skills/brainstorming/` |
| `test-driven-development` | library | active | Antigravity-adapted | Test-first behavior implementation workflow | `skills/test-driven-development/` |
| `codebase-onboarding` | library | active | ECC-adapted | Structured onboarding workflow for unfamiliar repositories | `skills/codebase-onboarding/` |
| `architecture-decision-records` | library | active | ECC-adapted | ADR recording and decision-history discipline | `skills/architecture-decision-records/` |
| `git-workflow` | library | active | ECC-adapted | Branch, commit, PR, merge, and release discipline | `skills/git-workflow/` |
| `e2e-testing` | library | active | ECC-adapted | End-to-end user-journey and browser verification workflow | `skills/e2e-testing/` |
| `security-review` | library | active | ECC-adapted | Security-focused review workflow for risky changes | `skills/security-review/` |
| `task-router-lite` | daily | active | codex-max | Thin Phase PLAN router that selects at most one primary and one optional secondary skill | `skills/task-router-lite/` |
| `task-intelligence` | daily | legacy alias | codex-max | Compatibility alias that preserves older references while routing through `task-router-lite` behavior | `skills/task-intelligence/` |
| `verification-before-completion` | daily | active | codex-max | Evidence-first completion gate | `skills/verification-before-completion/` |

## Installed optional library skills

| Name | Tier | Status | Origin | Purpose | Path |
|---|---|---|---|---|---|
| `browser-automation` | library | optional | Antigravity-adapted | Browser automation and scraping-oriented workflow | `skills/browser-automation/` |
| `security-auditor` | library | optional | Antigravity-adapted | Deeper security audit workflow beyond standard security review | `skills/security-auditor/` |
| `context7-auto-research` | library | optional | third-party-adapted | Alternative Context7-driven docs-current workflow | `skills/context7-auto-research/` |

## Installed maintainer-only skills

| Name | Tier | Status | Origin | Purpose | Path |
|---|---|---|---|---|---|
| `agent-sort` | maintainer | maintainer-only | ECC-adapted | Evidence-backed curation workflow for sorting runtime, optional, maintainer-only, and deferred surfaces | `skills/_maintainers/agent-sort/` |
| `strategic-compact` | maintainer | maintainer-only | ECC-adapted | Context compaction guidance for long curation or migration sessions | `skills/_maintainers/strategic-compact/` |
| `manage-skills` | maintainer | maintainer-only | Antigravity-adapted | Structural management of the curated skill library | `skills/_maintainers/manage-skills/` |

## Internal support assets

| Path | Status | Notes |
|---|---|---|
| `skills/.system/` | internal | Workspace support assets; not part of the user-selectable skill surface |

## Planned imports

No additional import wave is currently scheduled in the curated roadmap.
Optional and maintainer-only skills are installed but are not part of the core routing path by default.

## Catalog rules

- Only the installed sections represent the current curated skill surface.
- `legacy alias` means the name still works, but the canonical behavior lives elsewhere.
- `optional` means installed and usable, but not part of the core routing default.
- `maintainer-only` means installed for library curation or maintenance and should not be auto-loaded in normal execution.
- Any change to the curated skill surface should update this file together with `skills/manifest.yaml`.
