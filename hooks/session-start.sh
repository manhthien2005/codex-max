#!/bin/sh
# session-start.sh — planning-with-files SessionStart hook for Codex

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CODEX_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
SKILL_DIR="$CODEX_ROOT/skills/planning-with-files"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 || command -v python)}"

# ── MemPalace diary sentinel ─────────────────────────────────────────────────
TMP_DIR="$CODEX_ROOT/.tmp"
mkdir -p "$TMP_DIR"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z' 2>/dev/null || date)"
printf "%s\n" "$TIMESTAMP" > "$TMP_DIR/diary_pending"
# ─────────────────────────────────────────────────────────────────────────────

if [ -n "$PYTHON_BIN" ] && [ -f "$SKILL_DIR/scripts/session-catchup.py" ]; then
    "$PYTHON_BIN" "$SKILL_DIR/scripts/session-catchup.py" "$(pwd)"
fi

sh "$SCRIPT_DIR/user-prompt-submit.sh"
exit 0
