#!/usr/bin/env sh
# user-prompt-submit.sh — emit active planning context with a compact summary
set -eu

CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
if [ ! -d "$CODEX_ROOT/.tmp" ] && [ -d "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)/.tmp" ]; then
    CODEX_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
fi

PLAN_FILE=""
for candidate in task_plan.md PLANS.md; do
    if [ -f "$candidate" ]; then
        PLAN_FILE="$candidate"
        break
    fi
done

RESTORE_FILE="$CODEX_ROOT/.tmp/intelligence_restore_pending"
if [ -f "$RESTORE_FILE" ]; then
    echo "[planning-with-files] Session context restored for this workspace."
    rm -f "$RESTORE_FILE" 2>/dev/null || true
fi

if [ -n "$PLAN_FILE" ]; then
    echo "[planning-with-files] ACTIVE PLAN — current state:"
    awk '
        /^# / && !title { title = $0 }
        /^## Task/ { section = "task"; next }
        /^## Goal/ { if (section == "task") section = "" }
        /^## Status/ { section = "status"; next }
        /^## Work Plan/ { if (section == "status") section = "" }
        /^## / && $0 !~ /^## (Task|Status)$/ { section = "" }
        section == "task" && NF && task_count < 2 { task[++task_count] = $0 }
        section == "status" && /^- / && status_count < 3 { status[++status_count] = $0 }
        END {
            if (title) print title
            for (i = 1; i <= task_count; i++) print task[i]
            for (i = 1; i <= status_count; i++) print status[i]
        }
    ' "$PLAN_FILE"

    echo ""
    echo "=== recent progress ==="
    if [ -f progress.md ]; then
        recent_block="$(awk '
            /^### Step/ {
                block = $0 ORS
                capture = 1
                count = 0
                next
            }
            capture && count < 3 {
                block = block $0 ORS
                count++
            }
            END {
                printf "%s", block
            }
        ' progress.md)"
        if [ -n "$recent_block" ]; then
            printf '%s\n' "$recent_block"
        else
            tail -5 progress.md 2>/dev/null || true
        fi
    fi

    echo ""
    echo "[planning-with-files] Read findings.md for research context. Continue from the current phase."
fi
exit 0
