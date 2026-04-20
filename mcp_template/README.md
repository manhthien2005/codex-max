# `mcp_template/` — Published WSL MCP Source

This directory is the git-tracked source of truth for the local MCP runtime.

It exists because the real `mcp/` directory is machine-local and gitignored. The workspace bootstraps `~/.codex/mcp` from this template instead of committing local venvs or host-specific launchers.

---

## Model

| Path | Role |
|---|---|
| `mcp_template/` | Published launcher/source templates |
| `~/.codex/mcp/` | Local launchers, Linux venvs, caches, and adapter files |

Bootstrap the local runtime with:

```bash
bash ~/.codex/scripts/bootstrap-mcp-wsl.sh
```

---

## Contents

```text
mcp_template/
├── README.md
├── mempalace/
│   └── run-mempalace-mcp.sh
├── qdrant/
│   └── run-qdrant-mcp.sh
├── semantic/
│   ├── repo-index.py
│   ├── run-semantic-qdrant-stdio.sh
│   └── semantic_qdrant_http.py
└── README.md
```

### Notes

- `qdrant/` publishes the WSL launcher for the upstream Qdrant MCP server.
- `semantic/` publishes the semantic adapter source and its stdio launcher.
- `mempalace/` publishes the WSL launcher that prefers a local venv when present.
- `~/.codex/mcp/npm/` is still part of the runtime result, even though its packages are not committed here.

Legacy `.cmd` launchers may still exist in historical branches or ignored local runtimes, but they are no longer the active target for this workspace.

---

## Local Bootstrap Result

After running the bootstrap script, the local runtime should look like this:

```text
~/.codex/mcp/
├── npm/
│   ├── node_modules/
│   └── package.json
├── mempalace/
│   ├── bin/
│   └── run-mempalace-mcp.sh
├── qdrant/
│   ├── bin/
│   └── run-qdrant-mcp.sh
└── semantic/
    ├── repo-index.py
    ├── run-semantic-qdrant-stdio.sh
    └── semantic_qdrant_http.py
```

The bootstrap is idempotent: it refreshes published launchers, keeps local venvs, and skips the Node reinstall path when the expected `node_modules/.bin/*` launchers already exist.

That runtime is intentionally local-only and should not be committed.
