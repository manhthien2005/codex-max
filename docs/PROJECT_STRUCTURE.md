# Project Structure

This document describes the actual working structure of the Codex workspace in a more precise way than the main [`README.md`](../README.md).

It focuses on:
- important source and configuration files,
- the main files inside important directories,
- what each area is responsible for,
- which areas are operationally important versus purely local.

---

## Top-Level Layout

```text
.
├── AGENTS.md
├── config.toml
├── hooks.json
├── README.md
├── README.vi.md
├── agents/
├── docs/
├── hooks/
├── mcp/           ← gitignored, machine-local
├── rules/
├── skills/
└── vendor_imports/
```

The workspace also contains multiple local-only operational directories such as caches, sessions, temp clones, and SQLite state. Those are intentionally excluded by [`.gitignore`](../.gitignore) and are not part of the clean publishable surface.

---

## Core Root Files

### [`AGENTS.md`](../AGENTS.md)
Primary operational contract for the workspace.

It defines:
- task startup protocol,
- active repo detection,
- multi-repo safety rules,
- skill strategy,
- MCP usage rules,
- reporting format.

### [`config.toml`](../config.toml)
Main Codex runtime configuration.

Key responsibilities:
- model and reasoning defaults,
- approval and sandbox policy,
- MCP server declarations,
- trusted project paths,
- multi-agent role binding.

### [`hooks.json`](../hooks.json)
Hook registration file for lifecycle automation.

Key events:
- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `Stop`

### [`README.md`](../README.md)
English landing page for the repository.

### [`README.vi.md`](../README.vi.md)
Vietnamese landing page for the repository.

---

## Main Directories

## [`agents/`](../agents)
Reusable subagent role definitions.

Current main files:

```text
agents/
├── docs-researcher.toml
├── explorer.toml
└── reviewer.toml
```

### Role summary
- [`agents/explorer.toml`](../agents/explorer.toml): read-only exploration role for evidence gathering
- [`agents/reviewer.toml`](../agents/reviewer.toml): review role for correctness, security, and regression checks
- [`agents/docs-researcher.toml`](../agents/docs-researcher.toml): documentation and API verification role

---

## [`hooks/`](../hooks)
Implementation directory for workspace lifecycle hooks.

Current main files:

```text
hooks/
├── codex_hook_adapter.py
├── hook-probe.py
├── post_tool_use.py
├── post-tool-use.ps1
├── pre_tool_use.py
├── pre-tool-use.ps1
├── session-start.ps1
├── stop.ps1
├── stop.py
└── user-prompt-submit.ps1
```

### Functional grouping
- session startup: [`hooks/session-start.ps1`](../hooks/session-start.ps1)
- prompt submission injection: [`hooks/user-prompt-submit.ps1`](../hooks/user-prompt-submit.ps1)
- pre-tool checks: [`hooks/pre_tool_use.py`](../hooks/pre_tool_use.py), [`hooks/pre-tool-use.ps1`](../hooks/pre-tool-use.ps1)
- post-tool review: [`hooks/post_tool_use.py`](../hooks/post_tool_use.py), [`hooks/post-tool-use.ps1`](../hooks/post-tool-use.ps1)
- stop/finalization: [`hooks/stop.py`](../hooks/stop.py), [`hooks/stop.ps1`](../hooks/stop.ps1)
- probe / diagnostics: [`hooks/hook-probe.py`](../hooks/hook-probe.py)
- adapter support: [`hooks/codex_hook_adapter.py`](../hooks/codex_hook_adapter.py)

---

## [`rules/`](../rules)
Workspace rule assets.

Current main file:

```text
rules/
└── default.rules
```

### Purpose
- stores default policy-oriented rule material used by the workspace.

---

## [`skills/`](../skills)
Curated skill surface for reusable workflows.

Current visible main items include:

```text
skills/
├── README.md
├── CATALOG.md
├── manifest.yaml
├── workflow_bundles_readme.md
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
└── .system/
```

### Key skill directories
- [`skills/_maintainers/agent-sort/`](../skills/_maintainers/agent-sort): maintainer-only curation workflow for classifying surfaces into runtime, optional, maintainer-only, or deferred buckets
- [`skills/_maintainers/manage-skills/`](../skills/_maintainers/manage-skills): maintainer-only workflow for structurally managing the curated skill library
- [`skills/_maintainers/strategic-compact/`](../skills/_maintainers/strategic-compact): maintainer-only guidance for logical context compaction during long curation sessions
- [`skills/architecture-decision-records/`](../skills/architecture-decision-records): record architectural decisions with context, alternatives, and consequences
- [`skills/brainstorming/`](../skills/brainstorming): design-first clarification before implementation
- [`skills/browser-automation/`](../skills/browser-automation): optional browser automation and scraping-oriented workflow
- [`skills/codebase-onboarding/`](../skills/codebase-onboarding): structured onboarding workflow for unfamiliar repositories
- [`skills/concise-planning/`](../skills/concise-planning): lightweight planning support
- [`skills/context7-auto-research/`](../skills/context7-auto-research): optional alternative docs-current workflow using Context7-style retrieval
- [`skills/documentation-lookup/`](../skills/documentation-lookup): current docs lookup for frameworks, libraries, and APIs
- [`skills/e2e-testing/`](../skills/e2e-testing): end-to-end user-journey and browser-flow verification workflow
- [`skills/gateguard/`](../skills/gateguard): fact-forcing pre-action gate adapted to the current Bash-hook runtime
- [`skills/git-workflow/`](../skills/git-workflow): branch, commit, PR, merge, and release discipline
- [`skills/lint-and-validate/`](../skills/lint-and-validate): mandatory validation discipline after changes
- [`skills/planning-with-files/`](../skills/planning-with-files): persistent markdown-based planning workflow
- [`skills/search-first/`](../skills/search-first): research-before-coding and dependency-choice discipline
- [`skills/security-auditor/`](../skills/security-auditor): optional deeper security audit workflow
- [`skills/security-review/`](../skills/security-review): security-focused review workflow for risky changes
- [`skills/systematic-debugging/`](../skills/systematic-debugging): root-cause-first debugging patterns
- [`skills/task-router-lite/`](../skills/task-router-lite): canonical thin Phase PLAN router for the curated runtime surface
- [`skills/task-intelligence/`](../skills/task-intelligence): legacy compatibility alias that preserves older references while routing through the thin PLAN behavior
- [`skills/test-driven-development/`](../skills/test-driven-development): test-first behavior implementation workflow
- [`skills/verification-before-completion/`](../skills/verification-before-completion): completion gate with evidence requirement

### Support subtree
- [`skills/.system/`](../skills/.system): internal/system support skills

---

## [`vendor_imports/`](../vendor_imports)
Vendor-managed imported material.

This area should generally be treated as external or imported support content rather than first-choice hand-edited workspace source.

---

## `mcp/` (gitignored)
Local MCP server binaries and launcher scripts. This directory is **excluded from Git** because it contains machine-specific Python virtual environments (~305 MB) and hardcoded paths.

```text
mcp/
├── mempalace/
│   └── run-mempalace-mcp.cmd
├── qdrant/
│   ├── run-qdrant-mcp.cmd
│   └── Scripts/           ← Python venv (~305 MB)
└── semantic/
    ├── run-semantic-qdrant-stdio.cmd
    └── semantic_qdrant_http.py
```

See [`docs/INSTALLATION.md`](INSTALLATION.md) section 5 for setup instructions.

---

## Local-Only Operational Areas

These directories and files are important at runtime but are not part of the clean publishable source layer:

- temp clones and planning scratch
- archived sessions and backups
- caches and temporary binary downloads
- sandbox traces
- session history
- SQLite and state files
- machine-local credentials and auth artifacts

These are intentionally excluded by [`.gitignore`](../.gitignore).

---

## Recommended Reading Order

For someone new to the workspace, the clean reading order is:

1. [`AGENTS.md`](../AGENTS.md)
2. [`config.toml`](../config.toml)
3. [`hooks.json`](../hooks.json)
4. [`agents/`](../agents)
5. [`skills/`](../skills)
6. [`README.md`](../README.md) or [`README.vi.md`](../README.vi.md)

That order gives both policy context and implementation context without mixing in ignored runtime noise.