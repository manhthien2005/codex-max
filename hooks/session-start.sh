#!/usr/bin/env sh
# session-start.sh — WSL/Linux session-start hook for codex-max
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
if [ ! -d "$CODEX_ROOT/hooks" ]; then
    CODEX_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
fi
SKILL_DIR="$CODEX_ROOT/.agents/skills/planning-with-files"
if [ ! -d "$SKILL_DIR" ]; then
    SKILL_DIR="$CODEX_ROOT/skills/planning-with-files"
fi
TMP_DIR="$CODEX_ROOT/.tmp"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python || true)}"

mkdir -p "$TMP_DIR"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %z')"
printf '%s\n' "$TIMESTAMP" > "$TMP_DIR/diary_pending"
printf '%s\n' "$TIMESTAMP" > "$TMP_DIR/intelligence_restore_pending"

CATCHUP_SCRIPT="$SKILL_DIR/scripts/session-catchup.py"
if [ -n "$PYTHON_BIN" ] && [ -f "$CATCHUP_SCRIPT" ]; then
    "$PYTHON_BIN" "$CATCHUP_SCRIPT" "$(pwd)" 2>/dev/null || true
fi

sh "$SCRIPT_DIR/user-prompt-submit.sh" 2>/dev/null || true

exit 0
