# Installation Guide

This document contains the detailed installation and setup flow for the Codex workspace.

It is intentionally separated from the main [`README.md`](../README.md) so the landing page stays concise.

---

## 1. Goal of the Setup

The purpose of the installation flow is to make this repository usable as a stable Codex workspace with:
- the correct runtime configuration,
- active hook wiring,
- reusable agent roles,
- curated skills,
- a clean boundary between source files and local runtime data.

---

## 2. Prerequisites

Before using this workspace, confirm the following are available on your machine:

| Requirement | Notes |
|---|---|
| **Windows 11** | Primary supported OS |
| **Git** | For cloning and version control |
| **Node.js ≥ 18** | Required for MCP servers (memory, playwright, sequential-thinking, gitnexus) |
| **Python ≥ 3.10** | Required for hook scripts (`pre_tool_use.py`, `post_tool_use.py`, `stop.py`) |
| **PowerShell 5+** | Available by default on Windows 11 |
| **Git Bash or WSL** | Required for `.sh` hook scripts referenced in `hooks.json` |
| **Codex CLI** | Installed and authenticated with your API key |
| **Docker Desktop** | Required to run the local Qdrant vector database (`mcp/semantic`) |
| **Ollama** | Required locally for semantic embeddings (pull `qwen3-embedding:0.6b`) |

> [!NOTE]
> The `hooks.json` hooks use `sh` (Bash syntax). On Windows, this requires **Git Bash** (bundled with Git for Windows) or **WSL**. Pure `cmd.exe` will not work for those hooks.

---

## 3. Clone the Repository

```powershell
# Replace <your-username> with your Windows username
git clone https://github.com/manhthien2005/codex-max.git C:\Users\<your-username>\.codex
```

> [!IMPORTANT]
> The workspace **must** live at `C:\Users\<your-username>\.codex` for Codex to auto-detect it.
> Codex loads `AGENTS.md`, `config.toml`, and `hooks.json` from this path on startup.

Verify the clone:

```powershell
ls C:\Users\$env:USERNAME\.codex
```

Expected top-level entries: `AGENTS.md`, `config.toml`, `hooks.json`, `agents/`, `hooks/`, `skills/`, `.gitignore`.

---

## 4. Adapt Configuration to Your Machine

### 4.1 Replace all hardcoded paths in `config.toml`

Open `config.toml` and search for every occurrence of `MrThien`. Replace with your Windows username.

```powershell
# Preview all paths that need replacing
Select-String -Path "C:\Users\$env:USERNAME\.codex\config.toml" -Pattern "MrThien"
```

Key sections that contain absolute paths:

```toml
# MCP server launchers — each marked with ← EDIT in config.toml:
[mcp_servers.gitnexus]
command = "node"
args = ['C:\Users\<YOUR_USERNAME>\AppData\Roaming\npm\node_modules\gitnexus\dist\cli\index.js', "mcp"] # ← EDIT

[mcp_servers.qdrant]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\qdrant\\run-qdrant-mcp.cmd" # ← EDIT

[mcp_servers.semantic_qdrant_http]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\semantic\\run-semantic-qdrant-stdio.cmd" # ← EDIT

[mcp_servers.mempalace]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\mempalace\\run-mempalace-mcp.cmd" # ← EDIT
```

### 4.2 Update trusted project paths

In `config.toml`, the `[projects.'...']` entries list paths Codex treats as trusted. Replace or remove entries that are specific to the original machine:

```toml
[projects.'D:\DoAn2\VSmartwatch']
trust_level = "trusted"
```

Add your own project paths as needed.

---

## 5. Set Up Local MCP Servers (`mcp/`)

> [!WARNING]
> The `mcp/` directory is **excluded from Git** (see `.gitignore`). It is **not cloned** — you must set it up manually on each machine.
> The repository includes a **`mcp_template/`** folder with all necessary launcher scripts and the semantic adapter source.

### 5.1 Bootstrap `mcp/` from the template

```powershell
$src = "C:\Users\$env:USERNAME\.codex\mcp_template"
$dst = "C:\Users\$env:USERNAME\.codex\mcp"

# Create mcp/ sub-directories
New-Item -Force -ItemType Directory "$dst\qdrant"
New-Item -Force -ItemType Directory "$dst\semantic"
New-Item -Force -ItemType Directory "$dst\mempalace"

# Copy launchers and source files from the template
Copy-Item "$src\qdrant\*"    "$dst\qdrant\"
Copy-Item "$src\semantic\*"  "$dst\semantic\"
Copy-Item "$src\mempalace\*" "$dst\mempalace\"
```

After copying, `mcp/` will have:

| Path | What it is |
|---|---|
| `mcp/qdrant/run-qdrant-mcp.cmd` | Upstream Qdrant MCP server launcher |
| `mcp/semantic/run-semantic-qdrant-stdio.cmd` | Semantic adapter launcher (used by Codex via stdio) |
| `mcp/semantic/run-semantic-qdrant-http.cmd` | Semantic adapter launcher (HTTP, manual/debug use) |
| `mcp/semantic/semantic_qdrant_http.py` | Semantic adapter source |
| `mcp/semantic/repo-index.py` | Generic repo indexer — one-shot or `--watch` mode |
| `mcp/mempalace/run-mempalace-mcp.cmd` | MemPalace MCP server launcher |

### 5.2 Install the Python venv and dependencies

The `qdrant` and `semantic` servers share a single Python venv located at `mcp/qdrant/`:

```powershell
$venv = "C:\Users\$env:USERNAME\.codex\mcp\qdrant"

# Create the venv
python -m venv $venv

# Install all required packages
& "$venv\Scripts\pip" install fastmcp qdrant-client mcp-server-qdrant

# Install watchdog (optional — only needed for --watch mode)
& "$venv\Scripts\pip" install watchdog
```

> [!NOTE]
> The `memory`, `playwright`, `sequential-thinking`, `context7`, `github`, `exa` MCP servers do **not** require `mcp/` setup — they use `npx` or remote URLs and install automatically on first use.

### 5.3 Install MemPalace

```powershell
pip install mempalace
```

`run-mempalace-mcp.cmd` uses the global `python` (or the venv activated by the system PATH).

### 5.4 Start backend services in Docker (Qdrant + Ollama)

Before the semantic adapter can work, start its dependencies.

> [!IMPORTANT]
> Both Qdrant and Ollama should be run in Docker for this install flow.
> Do **not** install Ollama separately on the host machine for these steps.
> This install flow expects GPU acceleration to be available for Ollama because the embedding model should run with GPU support.

```powershell
# 1. Start Ollama in Docker
#    Then exec into the container and pull the required embedding model (0.6 GB)
docker run -d -p 11434:11434 `
    --name ollama `
    -v ollama_data:/root/.ollama `
    ollama/ollama

docker exec -it ollama ollama pull qwen3-embedding:0.6b

# 2. Start Qdrant in Docker with a persistent volume
docker run -d -p 6333:6333 -p 6334:6334 `
    --name qdrant `
    -v qdrant_data:/qdrant/storage `
    qdrant/qdrant
```

### 5.5 Index your repos into Qdrant

Use `repo-index.py` to populate Qdrant with embeddings for your codebase.

**One-shot index** (index once and exit):

```powershell
$python = "C:\Users\$env:USERNAME\.codex\mcp\qdrant\Scripts\python.exe"
$script = "C:\Users\$env:USERNAME\.codex\mcp\semantic\repo-index.py"

# Index a Dart/Flutter repo (default extensions: .dart)
& $python $script --repo "D:\MyProject\health_system" --subdir lib

# Index a Python repo
& $python $script --repo "D:\MyProject\backend" --exts .py

# Index a TypeScript repo (no subdirectory filter)
& $python $script --repo "D:\MyProject\frontend" --exts .ts,.tsx
```

**Watch mode** (auto-update Qdrant on every file save):

```powershell
# Keeps running in background — re-indexes changed files automatically
& $python $script --repo "D:\MyProject\health_system" --subdir lib --watch
```

The collection name defaults to `semantic-<repo-folder-name>` and is auto-discovered by the semantic adapter.

**Indexing multiple repos:**

```powershell
@(
    @{repo="D:\MyProject\health_system"; subdir="lib"; exts=".dart"},
    @{repo="D:\MyProject\backend"; subdir=""; exts=".py"},
    @{repo="D:\MyProject\frontend"; subdir="src"; exts=".ts,.tsx"}
) | ForEach-Object {
    & $python $script --repo $_.repo --subdir $_.subdir --exts $_.exts
}
```

### 5.6 Install `gitnexus` globally

```powershell
npm install -g gitnexus
```

Verify:

```powershell
node "C:\Users\$env:USERNAME\AppData\Roaming\npm\node_modules\gitnexus\dist\cli\index.js" --version
```

---

## 6. Verify Hook Scripts

```powershell
ls "C:\Users\$env:USERNAME\.codex\hooks\"
```

All scripts referenced by `hooks.json` must exist. Expected files:
- `session-start.sh` (and optionally `.ps1`)
- `user-prompt-submit.sh`
- `pre_tool_use.py`
- `post_tool_use.py`
- `stop.py`

> [!IMPORTANT]
> The `hooks.json` hook commands use `sh` to run `.sh` scripts. This requires **Git Bash** to be installed and `sh` to be on the `PATH`. Test with:
> ```powershell
> sh --version
> ```
> If `sh` is not found, install [Git for Windows](https://gitforwindows.org/) and ensure the Git Bash `bin/` directory is on your `PATH`.

---

## 7. Post-Install Verification Checklist

Run these checks after setup:

```powershell
# 1. Confirm required files exist
$base = "C:\Users\$env:USERNAME\.codex"
@("AGENTS.md","config.toml","hooks.json",".gitignore") | ForEach-Object {
    $p = Join-Path $base $_
    if (Test-Path $p) { Write-Host "OK  $_" } else { Write-Host "MISSING  $_" }
}

# 2. Confirm required directories exist
@("agents","hooks","skills","rules","docs") | ForEach-Object {
    $p = Join-Path $base $_
    if (Test-Path $p) { Write-Host "OK  $_\" } else { Write-Host "MISSING  $_\" }
}

# 3. Confirm no hardcoded MrThien paths remain
Select-String -Path "$base\config.toml" -Pattern "MrThien"
# Expected: no output (zero matches)

# 4. Confirm node is available
node --version

# 5. Confirm python is available
python --version

# 6. Confirm sh (Git Bash) is available
sh --version
```

---

## 8. Recommended Operational Discipline

After installation:
- keep `mcp/` and other local runtime directories fully ignored — never commit them,
- avoid mixing reference clones into the main source surface,
- prefer deliberate documentation updates over ad hoc notes,
- keep configuration changes reviewable and minimal,
- update `[projects.'...']` in `config.toml` for each new project you want Codex to trust.

---

## 9. Related Documents

- Main overview: [`README.md`](../README.md)
- Vietnamese overview: [`README.vi.md`](../README.vi.md)
- English structure guide: [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- Vietnamese structure guide: [`PROJECT_STRUCTURE.vi.md`](PROJECT_STRUCTURE.vi.md)