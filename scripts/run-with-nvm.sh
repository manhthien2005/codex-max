#!/usr/bin/env bash
# run-with-nvm.sh — source the WSL user toolchain, then exec the requested command
set -euo pipefail

USER_NAME="${USER:-$(id -un)}"
export HOME="/home/$USER_NAME"
export CODEX_HOME="$HOME/.codex"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
export PATH="$HOME/.local/bin:$PATH"

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
    set -u
fi

if [ "$#" -eq 0 ]; then
    echo "run-with-nvm.sh requires a command to execute" >&2
    exit 1
fi

exec "$@"
