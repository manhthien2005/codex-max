#!/usr/bin/env bash
# wsl-setup.sh — migrate this workspace to ~/.codex and bootstrap the WSL-native runtime
set -euo pipefail

USER_NAME="${USER:-$(id -un)}"
WSL_HOME="/home/$USER_NAME"
export HOME="$WSL_HOME"
export CODEX_HOME="$HOME/.codex"

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
SOURCE_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"

ensure_bootstrap_block() {
    local file="$1"
    local begin="# >>> codex-max wsl bootstrap >>>"
    local end="# <<< codex-max wsl bootstrap <<<"

    touch "$file"
    if grep -Fq "$begin" "$file" 2>/dev/null; then
        return 0
    fi

    cat >> "$file" <<EOF
$begin
export HOME=$WSL_HOME
export CODEX_HOME="\$HOME/.codex"
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && . "\$NVM_DIR/nvm.sh"
export PATH="\$HOME/.local/bin:\$PATH"
$end
EOF
}

migrate_repo_to_home() {
    local source_real
    local target_real=""
    local -a rsync_excludes=(
        "--exclude=.tmp/"
        "--exclude=.codex-global-state.json"
        "--exclude=archived_sessions/"
        "--exclude=backup/"
        "--exclude=cache/"
        "--exclude=history.jsonl"
        "--exclude=logs_2.sqlite*"
        "--exclude=mcp/"
        "--exclude=models_cache.json"
        "--exclude=shell_snapshots/"
        "--exclude=state_5.sqlite*"
        "--exclude=tmp/"
    )
    source_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$SOURCE_ROOT")"

    if [ -e "$CODEX_HOME" ]; then
        target_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$CODEX_HOME")"
    fi

    if [ "$source_real" = "$target_real" ]; then
        echo "  Workspace already canonical: $CODEX_HOME"
        return 0
    fi

    if [ -e "$CODEX_HOME" ]; then
        local backup_path="${CODEX_HOME}.backup.$TIMESTAMP"
        mv "$CODEX_HOME" "$backup_path"
        echo "  Backed up existing ~/.codex to $backup_path"
    fi

    mkdir -p "$CODEX_HOME"
    if command -v rsync >/dev/null 2>&1; then
        rsync -a "${rsync_excludes[@]}" "$SOURCE_ROOT/" "$CODEX_HOME/"
    else
        cp -a "$SOURCE_ROOT/." "$CODEX_HOME/"
    fi

    echo "  Canonical workspace copied to $CODEX_HOME"
}

mirror_local_runtime() {
    local source_real
    local target_real

    source_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$SOURCE_ROOT")"
    target_real="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$CODEX_HOME")"

    if [ "$source_real" = "$target_real" ]; then
        return 0
    fi

    mkdir -p "$SOURCE_ROOT/mcp"
    if command -v rsync >/dev/null 2>&1; then
        rsync -a --delete "$CODEX_HOME/mcp/" "$SOURCE_ROOT/mcp/"
    else
        rm -rf "$SOURCE_ROOT/mcp"
        mkdir -p "$SOURCE_ROOT/mcp"
        cp -a "$CODEX_HOME/mcp/." "$SOURCE_ROOT/mcp/"
    fi

    echo "  Mirrored local MCP runtime to $SOURCE_ROOT/mcp"
}

echo "=== [1/8] Fix WSL shell bootstrap ==="
BASH_PROFILE="$HOME/.bash_profile"
BASHRC="$HOME/.bashrc"
ensure_bootstrap_block "$BASH_PROFILE"
ensure_bootstrap_block "$BASHRC"
# shellcheck source=/dev/null
[ -f "$BASH_PROFILE" ] && . "$BASH_PROFILE"
# shellcheck source=/dev/null
[ -f "$BASHRC" ] && . "$BASHRC"

echo ""
echo "=== [2/8] Canonicalize workspace home ==="
migrate_repo_to_home

echo ""
echo "=== [3/8] Install nvm + Node.js LTS inside WSL ==="
if [ ! -s "$HOME/.nvm/nvm.sh" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi

export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    set +u
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
    set -u
fi

if ! command -v node >/dev/null 2>&1; then
    nvm install --lts
    nvm alias default node
fi
set +u
nvm use --lts >/dev/null
set -u

echo ""
echo "=== [4/8] Install Codex CLI inside WSL ==="
CODEX_BIN="$(command -v codex || true)"
if [ -z "$CODEX_BIN" ] || [ "${CODEX_BIN#/mnt/c/}" != "$CODEX_BIN" ]; then
    npm install -g @openai/codex
fi

echo ""
echo "=== [5/8] Install RTK inside WSL ==="
export PATH="$HOME/.local/bin:$PATH"
if ! command -v rtk >/dev/null 2>&1; then
    if ! curl -sSfL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | bash; then
        echo "  WARN: RTK install script failed; continuing without RTK"
    fi
fi

echo ""
echo "=== [6/8] Sync runtime skills into .agents/skills ==="
bash "$CODEX_HOME/scripts/sync-runtime-skills.sh"

echo ""
echo "=== [7/8] Bootstrap local MCP runtime ==="
bash "$CODEX_HOME/scripts/bootstrap-mcp-wsl.sh"
mirror_local_runtime

echo ""
echo "=== [8/8] Verify WSL runtime ==="
python3 "$CODEX_HOME/scripts/config-lint.py"
python3 "$CODEX_HOME/scripts/verify-wsl-runtime.py" || true
echo -n "  node: "; node --version 2>/dev/null || echo "MISSING"
echo -n "  npm: "; npm --version 2>/dev/null || echo "MISSING"
echo -n "  codex: "; codex --version 2>/dev/null | head -1 || echo "MISSING"
echo -n "  rtk: "; rtk --version 2>/dev/null | head -1 || echo "MISSING"
echo -n "  docker: "; docker --version 2>/dev/null | head -1 || echo "MISSING"
echo -n "  python3: "; python3 --version 2>/dev/null || echo "MISSING"
echo -n "  codex_hooks: "; codex features list 2>/dev/null | awk '$1 == "codex_hooks" { print $3 }' || echo "UNKNOWN"

echo ""
echo "=== Setup complete ==="
echo "Canonical Codex home: $CODEX_HOME"
echo "Launch inside WSL:"
echo "  bash ~/.codex/scripts/launch-codex-rtk.sh"
echo "Launch from Windows PowerShell:"
echo "  powershell -NoProfile -ExecutionPolicy Bypass -File $(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$SOURCE_ROOT/scripts/launch-codex-rtk.ps1")"
