#!/usr/bin/env python3
"""
stop.py — Stop hook for codex-max.
Pure Python — no dependency on stop.sh.
Gate 1: MemPalace diary sentinel must be written.
Gate 2: task_plan.md incomplete items block stop.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import codex_hook_adapter as adapter


def _check_diary_sentinel() -> str | None:
    sentinel = adapter.codex_root() / ".tmp" / "diary_pending"
    if not sentinel.exists():
        return None
    try:
        ts = sentinel.read_text(encoding="utf-8", errors="replace").strip() or "unknown"
    except OSError:
        ts = "unknown"
    return (
        "⚠️  MANDATORY BEFORE STOP — MemPalace Session Diary\n"
        f"Session started at: {ts}\n"
        "You MUST call mempalace_diary_write before stopping:\n"
        "  wing: 'context' | room: 'session_<YYYY-MM-DD>'\n"
        "  content: what was done, decisions, issues, next steps\n"
        "Then delete the sentinel to unlock stop."
    )


def _check_task_plan(root: Path) -> str | None:
    plan_file = root / "task_plan.md"
    if not plan_file.exists():
        return None
    try:
        content = plan_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    upper = content.upper()
    if "ALL PHASES COMPLETE" in upper:
        return None  # plan done, allow stop
    if "- [ ]" in content:
        return "Task plan has incomplete items (- [ ]). Complete them or mark done before stopping."
    return None


def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)

    # Gate 1: diary sentinel
    diary_msg = _check_diary_sentinel()
    if diary_msg:
        if bool(payload.get("stop_hook_active")):
            adapter.emit_json({"systemMessage": diary_msg})
        else:
            adapter.emit_json({"decision": "block", "reason": diary_msg})
        return

    # Gate 2: task plan completeness
    plan_msg = _check_task_plan(root)
    if plan_msg:
        if bool(payload.get("stop_hook_active")):
            adapter.emit_json({"systemMessage": plan_msg})
        else:
            adapter.emit_json({"decision": "block", "reason": plan_msg})
        return

    # All clear — allow stop silently


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
