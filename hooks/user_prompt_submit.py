#!/usr/bin/env python3
"""
user_prompt_submit.py — JSON-safe UserPromptSubmit hook output.

Codex currently accepts either plain text or a JSON hook payload for
UserPromptSubmit. This workspace uses JSON with `additionalContext`
so the hook stays deterministic across runtimes that eagerly parse
hook stdout as structured output.
"""
from __future__ import annotations

from pathlib import Path

import codex_hook_adapter as adapter


def _build_additional_context(root: Path, codex_root: Path) -> str:
    parts: list[str] = []

    restore_file = codex_root / ".tmp" / "intelligence_restore_pending"
    if restore_file.exists():
        parts.append("[planning-with-files] Session context restored for this workspace.")
        try:
            restore_file.unlink()
        except OSError:
            pass

    plan_file = adapter.find_plan_file(root)
    if plan_file is None:
        return "\n\n".join(parts)

    lines = plan_file.read_text(encoding="utf-8", errors="replace").splitlines()

    title = ""
    task_lines: list[str] = []
    status_lines: list[str] = []
    section = ""

    for line in lines:
        if line.startswith("# ") and not title:
            title = line
            continue
        if line.startswith("## Task"):
            section = "task"
            continue
        if line.startswith("## Status"):
            section = "status"
            continue
        if line.startswith("## "):
            section = ""
            continue

        if section == "task" and line.strip() and len(task_lines) < 2:
            task_lines.append(line)
        elif section == "status" and line.startswith("- ") and len(status_lines) < 3:
            status_lines.append(line)

    summary: list[str] = ["[planning-with-files] ACTIVE PLAN — current state:"]
    if title:
        summary.append(title)
    summary.extend(task_lines)
    summary.extend(status_lines)

    progress_file = root / "progress.md"
    recent_block: list[str] = []
    if progress_file.exists():
        progress_lines = progress_file.read_text(encoding="utf-8", errors="replace").splitlines()
        current_block: list[str] = []
        capture = False
        detail_count = 0
        for line in progress_lines:
            if line.startswith("### Step"):
                current_block = [line]
                capture = True
                detail_count = 0
                continue
            if capture and detail_count < 3:
                current_block.append(line)
                detail_count += 1
        recent_block = current_block or progress_lines[-5:]

    if recent_block:
        summary.append("")
        summary.append("=== recent progress ===")
        summary.extend(recent_block)

    summary.append("")
    summary.append("[planning-with-files] Read findings.md for research context. Continue from the current phase.")
    parts.append("\n".join(summary).strip())
    return "\n\n".join(part for part in parts if part).strip()


def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)
    codex_root = adapter.codex_root()
    additional_context = _build_additional_context(root, codex_root)
    if not additional_context:
        return
    adapter.emit_json(
        {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": additional_context,
            }
        }
    )


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
