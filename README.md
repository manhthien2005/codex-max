**Language:** [English](README.md) | [Tiếng Việt](README.vi.md)

<div align="center">

# AI Agent Workspace — WSL-First Codex Configuration

<img src="https://github.com/user-attachments/assets/0fcfb1a2-5f0b-4450-95d0-d55c9da57d09" alt="Project Logo" width="300" />

> Curated Codex workflows, persistent planning, local MCP integrations, and a reproducible WSL runtime for multi-repo engineering work.

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/manhthien2005/codex-max/releases/tag/v1.0.0)
![Platform](https://img.shields.io/badge/platform-WSL2%20Ubuntu-0F4C81)
![Runtime](https://img.shields.io/badge/runtime-Windows%20host%20bridge%20%E2%86%92%20WSL-1F2937)
![Mode](https://img.shields.io/badge/focus-Codex%20Workspace-111827)

</div>

---

## Overview

This repository is a Codex workspace, not a generic project template. It combines:

- a strict operational contract in [`AGENTS.md`](AGENTS.md),
- WSL-native Codex configuration in [`config.toml`](config.toml),
- hook automation through [`hooks.json`](hooks.json) and [`hooks/`](hooks),
- curated skills in [`skills/`](skills) with runtime discovery exposed through [`.agents/skills`](.agents/skills),
- machine-local MCP launchers and venvs in `~/.codex/mcp/`, published from [`mcp_template/`](mcp_template),
- local semantic search, GitNexus, and MemPalace integrations when their services are available.

The canonical runtime home is `~/.codex` inside WSL. The PowerShell launcher is only a thin handoff into that WSL runtime.

## Runtime Model

### Canonical paths

- Canonical Codex home: `~/.codex`
- Repo-local runtime skills: `./.agents/skills`
- User-scope runtime skills: `$HOME/.agents/skills`
- Published MCP source: `./mcp_template`
- Machine-local MCP runtime: `~/.codex/mcp`

### Intelligence layers

| Layer | Purpose | Requirement |
|---|---|---|
| MemPalace | Persistent project memory | Local Python venv under `~/.codex/mcp/mempalace` |
| Semantic search | Concept search across indexed code | Qdrant + Ollama + semantic adapter |
| GitNexus | Structural code graph and impact lookup | Node/npm in WSL |
| Context7 | Current library/framework docs | Remote MCP |
| Exa | Web search | Remote MCP |

The workspace now treats these layers as **lazy-degrade**. If a task does not need MemPalace or semantic search, their health is not a blocker.

## How Requests Flow

1. Codex loads [`AGENTS.md`](AGENTS.md).
2. Hooks from [`hooks.json`](hooks.json) run from `~/.codex/hooks/` when enabled.
3. The agent identifies the active repo, related repos, write scope, and git scope.
4. The PLAN phase routes through `task-router-lite`.
5. The BUILD phase selects the narrowest matching skill from the runtime skill surface.
6. Optional MCP layers are probed only when the task actually needs them.

## Repository Layout

- [`AGENTS.md`](AGENTS.md), [`config.toml`](config.toml), [`hooks.json`](hooks.json): runtime contract
- [`agents/`](agents): reusable subagent roles
- [`hooks/`](hooks): WSL hook implementations and adapters
- [`skills/`](skills): curated source library, catalog, and maintainer material
- [`.agents/`](.agents): repo-local runtime discovery surface
- [`mcp_template/`](mcp_template): published WSL launcher/source templates
- `mcp/`: ignored machine-local launchers, venvs, and caches

Detailed structure guides:

- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- [docs/PROJECT_STRUCTURE.vi.md](docs/PROJECT_STRUCTURE.vi.md)

## Quick Start

### 1. Keep the canonical home in WSL

Clone or migrate this repo so the active runtime home becomes:

```bash
/home/<your-user>/.codex
```

If your working copy is still under `/mnt/c/...`, run the WSL bootstrap once. It copies the workspace into `~/.codex` and configures the rest from there.

### 2. Run the bootstrap

If the clone is already at `~/.codex`, run:

```bash
bash ~/.codex/scripts/wsl-setup.sh
```

If you are migrating once from a Windows filesystem clone, run for example:

```bash
bash /mnt/c/Users/<your-user>/.codex/scripts/wsl-setup.sh
```

The bootstrap:

- migrates the repo into `~/.codex`,
- installs or activates `nvm`, Node, Codex CLI, and RTK in WSL,
- syncs the runtime skill surface into `.agents/skills` and `$HOME/.agents/skills`,
- bootstraps `~/.codex/mcp` from `mcp_template/`,
- skips Node MCP reinstalls when the expected local binaries already exist,
- runs config and runtime verification.

### 3. Launch Codex

Inside WSL:

```bash
bash ~/.codex/scripts/launch-codex-rtk.sh
```

From Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<your-user>\.codex\scripts\launch-codex-rtk.ps1
```

That PowerShell script only hands off into `~/.codex/scripts/launch-codex-rtk.sh` inside WSL.

## Installation

The full install and verification guide lives here:

- [docs/INSTALLATION.md](docs/INSTALLATION.md)
- [docs/INSTALLATION.vi.md](docs/INSTALLATION.vi.md)

## Notes

- `mcp/` stays local-only and gitignored.
- Publish launcher or MCP source changes via [`mcp_template/`](mcp_template), not `mcp/`.
- `skills/` remains the curated source library. `.agents/skills` is the runtime mirror that Codex discovers.
- `github` MCP can stay configured without a token; verification reports it as `auth_missing` until `GITHUB_TOKEN` is exported.
