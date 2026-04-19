# `mcp/` — Local MCP Server Template

> This is a **template** for the `mcp/` directory that Codex uses to launch local MCP servers.
> The real `mcp/` is gitignored (contains Python venvs ~305 MB and machine-local binaries).
> Copy/adapt this template when setting up a new machine.

---

## Directory layout

```
mcp/
├── qdrant/                      ← Upstream Qdrant MCP server (mcp-server-qdrant)
│   ├── run-qdrant-mcp.cmd       ← Launcher — copy here after pip install
│   └── (Scripts/ venv created by pip install)
│
├── semantic/                    ← Custom semantic adapter (multi-repo Ollama+Qdrant)
│   ├── run-semantic-qdrant-stdio.cmd   ← Launcher for stdio transport (Codex uses this)
│   ├── run-semantic-qdrant-http.cmd    ← Launcher for HTTP transport (manual/debug use)
│   └── semantic_qdrant_http.py         ← Adapter source (copy from this template)
│
└── mempalace/                   ← MemPalace MCP server
    └── run-mempalace-mcp.cmd    ← Launcher — works after pip install mempalace
```

---

## Quick setup (copy all launchers)

```powershell
# 1. Create mcp/ directories
$base = "C:\Users\$env:USERNAME\.codex\mcp"
New-Item -Force -ItemType Directory "$base\qdrant"
New-Item -Force -ItemType Directory "$base\semantic"
New-Item -Force -ItemType Directory "$base\mempalace"

# 2. Copy launchers from mcp_template/
Copy-Item mcp_template\qdrant\run-qdrant-mcp.cmd        "$base\qdrant\"
Copy-Item mcp_template\semantic\run-semantic-qdrant-stdio.cmd  "$base\semantic\"
Copy-Item mcp_template\semantic\run-semantic-qdrant-http.cmd   "$base\semantic\"
Copy-Item mcp_template\semantic\semantic_qdrant_http.py  "$base\semantic\"
Copy-Item mcp_template\mempalace\run-mempalace-mcp.cmd   "$base\mempalace\"
```

Then follow each server's full install instructions below (see `qdrant/`, `semantic/`, `mempalace/`).

---

## Relationship to `config.toml`

`config.toml` references these launchers with absolute paths:

```toml
[mcp_servers.qdrant]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\qdrant\\run-qdrant-mcp.cmd"

[mcp_servers.semantic_qdrant_http]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\semantic\\run-semantic-qdrant-stdio.cmd"

[mcp_servers.mempalace]
command = "C:\\Users\\<YOUR_USERNAME>\\.codex\\mcp\\mempalace\\run-mempalace-mcp.cmd"
```

Replace `<YOUR_USERNAME>` with your Windows username in `config.toml` after cloning.
