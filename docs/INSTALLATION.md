# Installation Guide

This workspace is supported as a **WSL2-first** Codex environment.

The intended steady state is:

- canonical Codex home at `~/.codex`,
- repo-local runtime skills at `./.agents/skills`,
- user-scope runtime skills at `$HOME/.agents/skills`,
- machine-local MCP launchers and venvs under `~/.codex/mcp`,
- only a thin Windows bridge for launching into WSL.

---

## 1. Requirements

| Requirement | Notes |
|---|---|
| **WSL2 Ubuntu** | Primary supported runtime |
| **Git** | Clone and updates |
| **Python 3.10+** | Hooks, bootstrap, local MCP venvs |
| **curl** | Bootstrap helpers |
| **Node.js LTS via nvm** | Memory, Playwright, Sequential Thinking, GitNexus |
| **Codex CLI** | Installed inside WSL |
| **Docker** | Qdrant backend |
| **Ollama** | Embedding backend for semantic search |

> [!IMPORTANT]
> Native Windows execution is not the target. Use WSL as the actual runtime and treat PowerShell only as a launcher into WSL.

---

## 2. Source and Canonical Home

You may start from a clone under `/mnt/c/...`, but the canonical runtime home must end up here:

```bash
~/.codex
```

If you already have a working copy on the Windows filesystem, the bootstrap script will back up any existing `~/.codex` and copy the workspace there.

---

## 3. Bootstrap the WSL Runtime

Run this once from inside WSL:

If the workspace is already at `~/.codex`:

```bash
bash ~/.codex/scripts/wsl-setup.sh
```

If you are migrating from a Windows filesystem clone, for example:

```bash
bash /mnt/c/Users/<your-user>/.codex/scripts/wsl-setup.sh
```

The script performs these steps:

1. updates `~/.bash_profile` and `~/.bashrc` with the WSL Codex bootstrap block
2. copies the workspace into `~/.codex`
3. installs or activates `nvm` and Node.js LTS
4. installs `@openai/codex` in the WSL npm environment
5. installs RTK when possible
6. syncs the runtime skills into `~/.codex/.agents/skills` and `$HOME/.agents/skills`
7. bootstraps `~/.codex/mcp` from `mcp_template/`
8. skips Node MCP reinstalls when local launcher binaries are already present
9. runs config and runtime verification

---

## 4. Runtime Skills

The repository keeps two distinct skill surfaces:

| Path | Role |
|---|---|
| `skills/` | Curated source library, catalog, manifest, maintainer material |
| `.agents/skills/` | Repo-local runtime discovery surface |
| `$HOME/.agents/skills` | User-scope runtime discovery surface |

Refresh the runtime mirror after changing the curated library:

```bash
bash ~/.codex/scripts/sync-runtime-skills.sh
```

---

## 5. Local MCP Bootstrap

`mcp/` is machine-local and gitignored. Do not commit it.

The published source of truth is [`mcp_template/`](../mcp_template). Bootstrap the local runtime with:

```bash
bash ~/.codex/scripts/bootstrap-mcp-wsl.sh
```

That script:

- creates `~/.codex/mcp/qdrant`, `~/.codex/mcp/semantic`, and `~/.codex/mcp/mempalace`,
- copies the published WSL launchers and Python sources from `mcp_template/`,
- creates Linux `bin/` virtual environments,
- installs Qdrant MCP dependencies,
- installs MemPalace into its own local venv, preferring the local clone at `.tmp/mempalace` when available.
- skips the Node MCP reinstall path when `~/.codex/mcp/npm/node_modules/.bin/*` is already populated.

### MCP server layout

| Server | Launch path |
|---|---|
| `memory` | `~/.codex/scripts/run-with-nvm.sh npx -y @modelcontextprotocol/server-memory` |
| `playwright` | `~/.codex/scripts/run-with-nvm.sh npx -y @playwright/mcp@latest --extension` |
| `sequential-thinking` | `~/.codex/scripts/run-with-nvm.sh npx -y @modelcontextprotocol/server-sequential-thinking` |
| `gitnexus` | `~/.codex/scripts/run-with-nvm.sh npx -y gitnexus@latest mcp` |
| `qdrant` | `~/.codex/mcp/qdrant/run-qdrant-mcp.sh` |
| `semantic_qdrant_http` | `~/.codex/mcp/semantic/run-semantic-qdrant-stdio.sh` |
| `mempalace` | `~/.codex/mcp/mempalace/run-mempalace-mcp.sh` |

---

## 6. Backends for Semantic Search

`semantic_qdrant_http` requires both Qdrant and Ollama.

Minimum local endpoints:

- Qdrant: `http://127.0.0.1:6333/healthz`
- Ollama: `http://127.0.0.1:11434/api/tags`

You can run them however you prefer, but the workspace assumes those localhost endpoints.

Typical Docker Qdrant startup:

```bash
docker run -d --name codex-qdrant -p 6333:6333 -p 6334:6334 -v qdrant_data:/qdrant/storage qdrant/qdrant
```

Typical Ollama setup:

```bash
ollama serve
ollama pull qwen3-embedding:0.6b
```

> [!NOTE]
> The workspace no longer blocks unrelated tasks when Qdrant or Ollama are down. Semantic search is checked only when needed.

---

## 7. Verification

### Static checks

```bash
python3 ~/.codex/scripts/config-lint.py
sh -n ~/.codex/hooks/session-start.sh ~/.codex/hooks/user-prompt-submit.sh ~/.codex/scripts/*.sh ~/.codex/mcp_template/*/*.sh
python3 -m py_compile ~/.codex/hooks/*.py ~/.codex/scripts/*.py
python3 -m unittest discover -s ~/.codex/tests -p 'test_*.py'
```

### Runtime verification

```bash
python3 ~/.codex/scripts/verify-wsl-runtime.py
codex features list
codex mcp list
```

Expected outcomes:

- `config-lint.py` passes with no Windows-native paths or `persistent_instructions`
- `codex_hooks` is enabled
- runtime skills exist at `$HOME/.agents/skills`
- all local MCP launchers resolve under `~/.codex`
- `github` may report `auth_missing` until `GITHUB_TOKEN` is set

---

## 8. GitHub Token

To enable the `github` MCP server in WSL, store the token in the loader file that the WSL shell bootstrap reads:

```bash
read -rsp "GitHub token: " GITHUB_TOKEN && echo
mkdir -p ~/.config/codex/env
printf '%s' "$GITHUB_TOKEN" > ~/.config/codex/env/github_token
chmod 600 ~/.config/codex/env/github_token
unset GITHUB_TOKEN
source ~/.bashrc
```

Quick verification:

```bash
test -n "${GITHUB_TOKEN:-}" && echo GITHUB_TOKEN_set
codex mcp list
```

The `github` row should stop reporting `auth_missing`.

> [!NOTE]
> `UserPromptSubmit` now runs through `~/.codex/hooks/user_prompt_submit.py`, which emits JSON `hookSpecificOutput.additionalContext`. Keep that file in sync with `hooks.json` if you customize the prompt-injection behavior.

---

## 9. Launching Codex

Inside WSL:

```bash
bash ~/.codex/scripts/launch-codex-rtk.sh
```

From Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\<your-user>\.codex\scripts\launch-codex-rtk.ps1
```

That PowerShell script does not run Codex natively on Windows. It only calls `wsl.exe ... ~/.codex/scripts/launch-codex-rtk.sh`.
