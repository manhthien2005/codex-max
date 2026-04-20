#!/usr/bin/env bash
# launch-codex-rtk.sh — start a WSL-native Codex lane with RTK shims
set -euo pipefail

USER_NAME="${USER:-$(id -un)}"
export HOME="/home/$USER_NAME"
export CODEX_HOME="$HOME/.codex"
export NVM_DIR="$HOME/.nvm"

load_user_shell_env() {
    local shell_file
    for shell_file in "$HOME/.bash_profile" "$HOME/.bashrc"; do
        if [ -f "$shell_file" ]; then
            set +u
            # shellcheck source=/dev/null
            . "$shell_file" >/dev/null 2>&1 || true
            set -u
        fi
    done
}

load_interactive_env_var() {
    local var_name="$1"
    local value=""

    if [ -n "${!var_name:-}" ]; then
        return 0
    fi

    value="$(bash -ic "printf '%s' \"\${$var_name-}\"" 2>/dev/null || true)"
    if [ -n "$value" ]; then
        export "$var_name=$value"
    fi
}

load_user_shell_env
load_interactive_env_var "GITHUB_TOKEN"

if [ -s "$NVM_DIR/nvm.sh" ]; then
    set +u
    # shellcheck source=/dev/null
    . "$NVM_DIR/nvm.sh"
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/bash_completion" ] && . "$NVM_DIR/bash_completion"
    set -u
fi
export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$CODEX_HOME/.tmp"

if command -v rtk >/dev/null 2>&1; then
    export RTK_BIN="$(command -v rtk)"
    export CODEX_MAX_RTK_STATUS="active"
else
    export CODEX_MAX_RTK_STATUS="degraded"
fi

export CODEX_MAX_RTK_MODE="${CODEX_MAX_RTK_MODE:-balanced}"
if [ -f "$CODEX_HOME/hooks/rtk-shell-init.sh" ]; then
    export BASH_ENV="$CODEX_HOME/hooks/rtk-shell-init.sh"
fi

if ! command -v node >/dev/null 2>&1; then
    echo "[codex-max] Node.js is missing from the WSL PATH." >&2
    echo "[codex-max] Run scripts/wsl-setup.sh first." >&2
    exit 1
fi

CODEX_BIN="$(command -v codex || true)"
if [ -z "$CODEX_BIN" ] || [ "${CODEX_BIN#/mnt/c/}" != "$CODEX_BIN" ]; then
    echo "[codex-max] WSL-native codex CLI not found in PATH." >&2
    echo "[codex-max] Run scripts/wsl-setup.sh first so codex is installed inside WSL." >&2
    exit 1
fi

exec "$CODEX_BIN" "$@"
