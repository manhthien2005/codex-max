#!/usr/bin/env bash
# bootstrap-mcp-wsl.sh — create WSL-local MCP launchers and Python environments under ~/.codex/mcp
set -euo pipefail

USER_NAME="${USER:-$(id -un)}"
export HOME="/home/$USER_NAME"
export CODEX_HOME="$HOME/.codex"

TEMPLATE_ROOT="$CODEX_HOME/mcp_template"
MCP_ROOT="$CODEX_HOME/mcp"
NODE_ROOT="$MCP_ROOT/npm"
QDRANT_ROOT="$MCP_ROOT/qdrant"
SEMANTIC_ROOT="$MCP_ROOT/semantic"
MEMPALACE_ROOT="$MCP_ROOT/mempalace"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"
MEMPALACE_SRC="${MEMPALACE_SRC:-$CODEX_HOME/.tmp/mempalace}"

if [ -z "$PYTHON_BIN" ]; then
    echo "python3 is required for MCP bootstrap" >&2
    exit 1
fi

ensure_venv() {
    local target="$1"

    if [ -x "$target/bin/python" ] && [ -x "$target/bin/pip" ]; then
        return 0
    fi

    rm -rf "$target"

    if "$PYTHON_BIN" -m venv "$target" >/dev/null 2>&1; then
        return 0
    fi

    "$PYTHON_BIN" -m pip install --user --upgrade --break-system-packages virtualenv
    "$PYTHON_BIN" -m virtualenv "$target"
}

install_node_shim() {
    local name="$1"
    local shim_dir="$HOME/.local/bin"
    local shim_path="$shim_dir/$name"

    mkdir -p "$shim_dir"
    cat > "$shim_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail

USER_NAME="\${USER:-\$(id -un)}"
exec "/home/\$USER_NAME/.codex/scripts/run-with-nvm.sh" "/home/\$USER_NAME/.codex/mcp/npm/node_modules/.bin/$name" "\$@"
EOF
    chmod 755 "$shim_path"
}

node_bin_ready() {
    local name="$1"
    [ -x "$NODE_ROOT/node_modules/.bin/$name" ]
}

ensure_node_packages() {
    if node_bin_ready "mcp-server-memory" \
        && node_bin_ready "mcp-server-sequential-thinking" \
        && node_bin_ready "playwright-mcp" \
        && node_bin_ready "gitnexus"; then
        return 0
    fi

    "$CODEX_HOME/scripts/run-with-nvm.sh" npm install \
        --prefix "$NODE_ROOT" \
        --no-audit \
        --no-fund \
        --loglevel=warn \
        @modelcontextprotocol/server-memory \
        @modelcontextprotocol/server-sequential-thinking \
        @playwright/mcp \
        gitnexus
}

mkdir -p "$QDRANT_ROOT" "$SEMANTIC_ROOT" "$MEMPALACE_ROOT" "$NODE_ROOT"

ensure_venv "$QDRANT_ROOT"
install -m 755 "$TEMPLATE_ROOT/qdrant/run-qdrant-mcp.sh" "$QDRANT_ROOT/run-qdrant-mcp.sh"
"$QDRANT_ROOT/bin/python" -m pip install --upgrade pip setuptools wheel
"$QDRANT_ROOT/bin/pip" install --upgrade fastmcp qdrant-client mcp-server-qdrant watchdog

ensure_venv "$MEMPALACE_ROOT"
install -m 755 "$TEMPLATE_ROOT/mempalace/run-mempalace-mcp.sh" "$MEMPALACE_ROOT/run-mempalace-mcp.sh"
"$MEMPALACE_ROOT/bin/python" -m pip install --upgrade pip setuptools wheel
if [ -f "$MEMPALACE_SRC/pyproject.toml" ] || [ -f "$MEMPALACE_SRC/setup.py" ]; then
    "$MEMPALACE_ROOT/bin/pip" install --upgrade "$MEMPALACE_SRC"
else
    "$MEMPALACE_ROOT/bin/pip" install --upgrade mempalace
fi

install -m 755 "$TEMPLATE_ROOT/semantic/run-semantic-qdrant-stdio.sh" "$SEMANTIC_ROOT/run-semantic-qdrant-stdio.sh"
install -m 644 "$TEMPLATE_ROOT/semantic/semantic_qdrant_http.py" "$SEMANTIC_ROOT/semantic_qdrant_http.py"
install -m 644 "$TEMPLATE_ROOT/semantic/repo-index.py" "$SEMANTIC_ROOT/repo-index.py"

ensure_node_packages

install_node_shim "mcp-server-memory"
install_node_shim "mcp-server-sequential-thinking"
install_node_shim "playwright-mcp"
install_node_shim "gitnexus"

printf 'MCP bootstrap ready under %s\n' "$MCP_ROOT"
printf '  qdrant launcher: %s\n' "$QDRANT_ROOT/run-qdrant-mcp.sh"
printf '  semantic launcher: %s\n' "$SEMANTIC_ROOT/run-semantic-qdrant-stdio.sh"
printf '  mempalace launcher: %s\n' "$MEMPALACE_ROOT/run-mempalace-mcp.sh"
