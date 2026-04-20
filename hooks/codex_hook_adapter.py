#!/usr/bin/env python3
"""
codex_hook_adapter.py — Windows-compatible hook adapter for Codex.

Detects platform and uses PowerShell on Windows, sh on Unix.
Falls back gracefully if shell is not found.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


HOOK_DIR = Path(__file__).resolve().parent
IS_WINDOWS = sys.platform == "win32"


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def cwd_from_payload(payload: dict[str, Any]) -> Path:
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return Path(cwd)
    return Path.cwd()


def emit_json(payload: dict[str, Any]) -> None:
    if not payload:
        return
    json.dump(payload, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def parse_json(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _find_sh() -> str | None:
    """Find a sh-compatible shell on Windows (Git bash, WSL, etc.)"""
    candidates = [
        r"C:\Program Files\Git\bin\sh.exe",
        r"C:\Program Files\Git\usr\bin\sh.exe",
        r"C:\Program Files (x86)\Git\bin\sh.exe",
        r"C:\msys64\usr\bin\sh.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    # Try PATH
    import shutil
    found = shutil.which("sh")
    if found:
        return found
    return None


def run_shell_script(script_name: str, cwd: Path) -> tuple[str, str]:
    """Run a shell script, using PowerShell on Windows if no sh available."""
    # Try native ps1 version first on Windows
    if IS_WINDOWS:
        ps1_name = script_name.replace(".sh", ".ps1")
        ps1_path = HOOK_DIR / ps1_name
        if ps1_path.exists():
            return _run_powershell(ps1_path, cwd)

        # Try to find sh (Git for Windows)
        sh_bin = _find_sh()
        if sh_bin:
            return _run_sh(sh_bin, HOOK_DIR / script_name, cwd)

        # Fallback: inline equivalent via Python
        return _run_python_fallback(script_name, cwd)
    else:
        return _run_sh("sh", HOOK_DIR / script_name, cwd)


def _run_powershell(ps1_path: Path, cwd: Path) -> tuple[str, str]:
    if not ps1_path.exists():
        return "", ""
    result = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps1_path),
        ],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return result.stdout.strip(), result.stderr.strip()


def _run_sh(sh_bin: str, script_path: Path, cwd: Path) -> tuple[str, str]:
    if not script_path.exists():
        return "", ""
    result = subprocess.run(
        [sh_bin, str(script_path)],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip(), result.stderr.strip()


def _run_python_fallback(script_name: str, cwd: Path) -> tuple[str, str]:
    """Python-based fallback for common hook scripts when no shell is available."""
    plan_file = cwd / "task_plan.md"
    progress_file = cwd / "progress.md"

    if script_name in ("pre-tool-use.sh",):
        # Plan dump removed — was injecting 30 lines before every Bash call
        return '{"decision": "allow"}', ""

    elif script_name in ("post-tool-use.sh",):
        # Reminder removed — was spamming context after every Bash call
        return "", ""

    elif script_name in ("user-prompt-submit.sh",):
        if plan_file.exists():
            try:
                plan = plan_file.read_text(encoding="utf-8", errors="replace").splitlines()
                out = ["[planning-with-files] ACTIVE PLAN — current state:"]
                out.extend(plan[:50])
                if progress_file.exists():
                    prog = progress_file.read_text(encoding="utf-8", errors="replace").splitlines()
                    out.append("\n=== recent progress ===")
                    out.extend(prog[-20:])
                out.append("\n[planning-with-files] Read findings.md for research context. Continue from the current phase.")
                return "\n".join(out), ""
            except OSError:
                pass
        return "", ""

    elif script_name in ("stop.sh",):
        # Gate 1: MemPalace diary sentinel
        codex_root = HOOK_DIR.parent
        sentinel = codex_root / ".tmp" / "diary_pending"
        if sentinel.exists():
            try:
                ts = sentinel.read_text(encoding="utf-8", errors="replace").strip() or "unknown time"
            except OSError:
                ts = "unknown time"
            msg = (
                "\u26a0\ufe0f  MANDATORY BEFORE STOP \u2014 MemPalace Session Diary\n"
                f"Session started at: {ts}\n"
                "The diary sentinel is still active. You MUST:\n"
                "1. Call MCP tool: mempalace_diary_write\n"
                "   - wing: 'context'\n"
                "   - room: 'session_<YYYY-MM-DD>'\n"
                "   - content: What was done, decisions, issues, next steps.\n"
                f"2. Delete sentinel to unlock stop:\n"
                f"   del '{sentinel}'  (Windows) or  rm '{sentinel}'  (Unix)\n"
                "Do NOT skip this. MemPalace persistence depends on this entry."
            )
            return json.dumps({"followup_message": msg}), ""
        # Gate 2: planning-with-files plan check
        if plan_file.exists():
            try:
                content = plan_file.read_text(encoding="utf-8", errors="replace")
                if "ALL PHASES COMPLETE" in content.upper() or "DONE" in content.upper():
                    return json.dumps({"followup_message": "ALL PHASES COMPLETE \u2014 plan finished."}), ""
                return json.dumps({"followup_message": "Plan is still active. Review task_plan.md before closing."}), ""
            except OSError:
                pass
        return "{}", ""

    elif script_name in ("session-start.sh",):
        # Create MemPalace diary sentinel
        import datetime
        codex_root = HOOK_DIR.parent
        tmp_dir = codex_root / ".tmp"
        try:
            tmp_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            (tmp_dir / "diary_pending").write_text(ts, encoding="utf-8")
        except OSError:
            pass
        # Run session-catchup.py only — do NOT call user-prompt-submit here
        # (UserPromptSubmit hook fires separately; double-injection removed)
        catchup_path = HOOK_DIR.parent / "skills" / "planning-with-files" / "scripts" / "session-catchup.py"
        catchup_out = ""
        if catchup_path.exists():
            result = subprocess.run(
                [sys.executable, str(catchup_path), str(cwd)],
                cwd=str(cwd),
                text=True,
                capture_output=True,
                check=False,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            catchup_out = result.stdout.strip()
        # Minimal session status
        status = "[codex-max] Session ready."
        if plan_file.exists():
            status = f"[codex-max] Plan active. Session ready."
        combined = "\n".join(filter(None, [catchup_out, status]))
        return combined, ""

    return "", ""


def main_guard(func) -> int:
    try:
        func()
    except Exception as exc:  # pragma: no cover
        print(f"[planning-with-files hook] {exc}", file=sys.stderr)
        return 0
    return 0
