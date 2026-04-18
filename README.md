**Language:** [English](README.md) | [Tiếng Việt](README.vi.md)

<div align="center">

# AI Agent Workspace — Production-Grade Codex Configuration

<img src="https://github.com/user-attachments/assets/0fcfb1a2-5f0b-4450-95d0-d55c9da57d09" alt="Project Logo" width="300" />

> Structured agent workflows, persistent context, curated skills, automation hooks, and multi-repo operational discipline for advanced Codex usage.

<br/>

**Production-oriented AI agent workspace for Codex and adjacent agent tooling**

This repository packages a disciplined working environment for AI-assisted software engineering: reusable agents, hardened operational rules, persistent planning patterns, session automation, local memory integrations, and supporting workspace conventions.

<br/>

[![Version](https://img.shields.io/badge/version-v1.0.0-blue)](https://github.com/manhthien2005/codex-max/releases/tag/v1.0.0)
![Platform](https://img.shields.io/badge/platform-Windows%2011-0078D4)
![Shell](https://img.shields.io/badge/shell-cmd%20%2B%20PowerShell-2C2D72)
![Mode](https://img.shields.io/badge/focus-Codex%20Workspace-111827)

</div>

---

## Introduction

This workspace is designed as a serious operational environment for agent-assisted software engineering. It is not intended to be a generic scratch directory. Instead, it provides a stable Codex-centered control plane with reusable roles, workflow automation, skill loading, and strict separation between reusable repository assets and machine-local runtime data.

---

## Overview

This repository serves as a Codex-centric orchestration layer for daily engineering work. It combines hardened workflows, local code intelligence, semantic search, persistent memory, and project-specific configuration into a repeatable workspace.

### Core components

- **ECC-inspired workflow hardening** — structured rules, skills, hooks, and agent roles help keep planning, validation, review, and reporting consistent across tasks.
- **GitNexus codebase indexing** — structural code navigation supports symbol lookup, dependency tracing, call graph analysis, and impact awareness for real project repositories.
- **Ollama + Qdrant semantic search** — local embeddings and vector search enable concept-level code discovery without relying on external search infrastructure.
- **MemPalace session memory** — persistent memory keeps project context, decisions, and technical notes available across sessions instead of losing them between runs.
- **Project-local customization** — configuration can be adjusted per project, allowing each repository to have its own active rules, tools, MCP servers, and execution boundaries.

### Core goals

- Maintain a repeatable Codex workspace that can run locally
- Support multi-repo work with explicit boundaries
- Combine workflow discipline with local code intelligence
- Preserve useful project memory across sessions
- Avoid pushing caches, session traces, temp clones, or local state

---

## Project Structure

This workspace is organized around a small number of core layers:

- [`AGENTS.md`](AGENTS.md), [`config.toml`](config.toml), and [`hooks.json`](hooks.json) define the operational contract and runtime behavior
- [`agents/`](agents) stores reusable subagent role definitions
- [`hooks/`](hooks) contains lifecycle automation scripts
- [`skills/`](skills) provides curated reusable workflows and operational knowledge
- [`rules/`](rules) stores additional workspace rule material
- ignored local-only areas such as caches, sessions, SQLite state, sandbox traces, and temp clones remain outside the clean source surface

For the full structure reference, including the main files inside each important directory, open the English structure guide by default:

- Default detailed guide: [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md)
- Vietnamese version: [`docs/PROJECT_STRUCTURE.vi.md`](docs/PROJECT_STRUCTURE.vi.md)

---

## Quick Start

### 1. Open the workspace root
Use this directory as the active Codex workspace so the runtime can detect:

- [`AGENTS.md`](AGENTS.md)
- [`config.toml`](config.toml)
- [`hooks.json`](hooks.json)
- [`agents/`](agents)
- [`hooks/`](hooks)
- [`skills/`](skills)

### 2. Read the operating contract
Review [`AGENTS.md`](AGENTS.md) first. It defines:

- active repo detection,
- write-scope discipline,
- Git-scope boundaries,
- skill-loading flow,
- MCP usage expectations,
- reporting format.

### 3. Review runtime configuration
Inspect [`config.toml`](config.toml) to verify:

- model defaults,
- approval policy,
- sandbox settings,
- MCP server bindings,
- multi-agent role configuration.

### 4. Keep the workspace clean
Review [`.gitignore`](.gitignore) before versioning this workspace. It already excludes machine-local artifacts such as caches, sessions, local databases, temporary clones, and sandbox traces.

---

## How to Install

> Full guide: [`docs/INSTALLATION.md`](docs/INSTALLATION.md) · Vietnamese: [`docs/INSTALLATION.vi.md`](docs/INSTALLATION.vi.md)

### TL;DR — four things to do after cloning

```powershell
# 1. Clone to the correct path (Codex auto-detects this location)
git clone https://github.com/ThienPhanNoLife/codex-workspace.git C:\Users\$env:USERNAME\.codex

# 2. Replace all hardcoded paths that reference the original username
Select-String -Path "C:\Users\$env:USERNAME\.codex\config.toml" -Pattern "MrThien"
# Edit config.toml — replace every "MrThien" with your Windows username

# 3. Create .tmp/ and set up local MCP launchers (not tracked by Git)
New-Item -ItemType Directory -Path "C:\Users\$env:USERNAME\.codex\.tmp" -Force

# 4. Install gitnexus globally
npm install -g gitnexus
```

The full guide covers all steps in detail, including:
- prerequisites (Node.js ≥ 18, Python ≥ 3.10, Git Bash),
- path replacement in `config.toml`,
- setting up `.tmp/` MCP launchers (qdrant, mempalace, semantic search),
- hook script verification,
- post-install checklist with ready-to-run PowerShell commands.

---

## Author

<div align="center">

<img src="https://avatars.githubusercontent.com/u/65497946?v=4" alt="Mr. Thien" width="96" style="border-radius: 50%;" />

## Mr. Thien

[![Facebook](https://img.shields.io/badge/Facebook-ThienPhanNoLife-1877F2?logo=facebook&logoColor=white)](https://www.facebook.com/ThienPhanNoLife/)

| Platform | Link |
|---|---|
| Facebook | [facebook.com/ThienPhanNoLife](https://www.facebook.com/ThienPhanNoLife/) |

**Inspired by [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code), [GitNexus](https://github.com/0xPlaygrounds/gitnexus), and [MemPalace](https://github.com/MemPalace/mempalace).**

**Made with Mr. Thien**

</div>
