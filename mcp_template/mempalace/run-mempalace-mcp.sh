#!/usr/bin/env bash
# run-mempalace-mcp.sh — WSL/Linux launcher for the MemPalace MCP server
set -euo pipefail

export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"
export MEMPALACE_PALACE_PATH="${MEMPALACE_PALACE_PATH:-$HOME/.mempalace/palace}"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-}"

if [ -z "$PYTHON_BIN" ] && [ -x "$SCRIPT_DIR/bin/python" ]; then
    PYTHON_BIN="$SCRIPT_DIR/bin/python"
fi

if [ -z "$PYTHON_BIN" ]; then
    PYTHON_BIN="$(command -v python3 || command -v python || true)"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "python3 is required to launch MemPalace MCP" >&2
    exit 1
fi

exec "$PYTHON_BIN" -m mempalace.mcp_server --palace "$MEMPALACE_PALACE_PATH"
