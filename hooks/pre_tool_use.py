#!/usr/bin/env python3
"""
pre_tool_use.py — Pre-Bash hook for codex-max.

Checks (in order):
  1. RTK classifier — suggest RTK for noisy commands (non-blocking, logged)
  2. GitNexus index presence — warn if repo not indexed
     Includes Windows ↔ WSL path normalization to avoid false positives.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import codex_hook_adapter as adapter


def _plan_context(root: Path) -> str | None:
    plan_file = adapter.find_plan_file(root)
    if plan_file is None:
        return None
    excerpt = adapter.read_text_excerpt(plan_file, max_lines=16)
    if not excerpt:
        return None
    return f"[planning-with-files] ACTIVE PLAN excerpt from {plan_file.name}:\n{excerpt}"


# ── WSL / Windows path normalization ────────────────────────────────────────

def _canonical_forms(path_str: str) -> set[str]:
    """Return lowercase canonical forms for both Windows and WSL paths."""
    s = path_str.strip()
    forms: set[str] = {s}

    # Windows → WSL: D:\Foo\Bar → /mnt/d/Foo/Bar
    m = re.match(r"^([A-Za-z]):\\(.*)$", s)
    if m:
        drive = m.group(1).lower()
        rest = m.group(2).replace("\\", "/")
        forms.add(f"/mnt/{drive}/{rest}")

    # WSL → Windows: /mnt/d/Foo/Bar → D:\Foo\Bar
    m = re.match(r"^/mnt/([a-zA-Z])/(.*)$", s)
    if m:
        drive = m.group(1).upper()
        rest = m.group(2).replace("/", "\\")
        forms.add(f"{drive}:\\{rest}")

    return {f.lower() for f in forms}


# ── GitNexus warning ─────────────────────────────────────────────────────────

_REGISTRY_FILE = Path.home() / ".codex" / ".tmp" / "indexed_repos.json"

_KNOWN_INDEXED: set[str] = {
    r"D:\DoAn2\VSmartwatch\health_system",
    r"D:\DoAn2\VSmartwatch\Iot_Simulator",
    r"D:\DoAn2\VSmartwatch\HealthGuard",
    r"D:\DoAn2\VSmartwatch\healthguard-model-api",
}

# Session-level dedup: don't warn same repo more than once per process
_warned_repos: set[str] = set()


def _load_registry_paths() -> set[str]:
    if not _REGISTRY_FILE.exists():
        return set()
    try:
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8", errors="replace"))
        return set(data.keys())
    except Exception:
        return set()


def _find_git_root(cwd: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return None


def _check_gitnexus_warning(cwd: Path) -> str | None:
    """Return warning if current repo is not indexed. Uses path normalization."""
    git_root = _find_git_root(cwd)
    if git_root is None:
        return None

    repo_str = str(git_root)

    # Already warned this session
    if repo_str in _warned_repos:
        return None

    # .gitnexus/ dir is the most reliable indicator
    if (git_root / ".gitnexus").exists():
        return None

    # .codex config repo never needs gitnexus
    codex_root = Path.home() / ".codex"
    try:
        if git_root.resolve() == codex_root.resolve():
            return None
    except Exception:
        pass

    # Check known list + registry using canonical path comparison
    root_forms = _canonical_forms(repo_str)
    all_known = _KNOWN_INDEXED | _load_registry_paths()
    for known in all_known:
        known_forms = _canonical_forms(known)
        if root_forms & known_forms:  # intersection
            return None

    _warned_repos.add(repo_str)
    return (
        f"⚠️  GitNexus index not found for: {repo_str}\n"
        "    Code-graph features (symbol lookup, dependency tracing) are unavailable.\n"
        "    Run: python ~/.codex/scripts/repo-onboard.py \"" + repo_str + "\"\n"
        "    This will index the repo and register it in the intelligence stack."
    )


# ── RTK classifier ───────────────────────────────────────────────────────────

_RTK_STATE_FILE = Path.home() / ".codex" / ".tmp" / "rtk_state.json"
_RTK_MISSED_LOG = Path.home() / ".codex" / ".tmp" / "rtk_missed.jsonl"

# Commands safe for RTK (non-composite, human-readable, high-noise)
_AUTO_RTK_PREFIXES = (
    ("git", "status"),
    ("git", "log"),
    ("git", "diff"),
    ("git", "show"),
    ("ls",),
    ("pytest",),
    ("python", "-m", "pytest"),
    ("docker", "ps"),
    ("docker", "images"),
    ("docker", "logs"),
    ("cargo", "test"),
    ("cargo", "build"),
)

# Flags that mean machine-readable output — must stay raw
_MACHINE_READABLE_FLAGS = (
    "--porcelain", "--name-only", "--name-status", "-z",
    "--raw", "rev-parse", "rev-list", "ls-files", "show-ref",
    "--format=", "for-each-ref",
)

# Shell metacharacters indicating composite command
_COMPOSITE_TOKENS = ("&&", "||", " | ", ";", "$(", "`", ">>", "> ", "< ")

# Interactive tools — always raw
_INTERACTIVE_CMDS = (
    "vim", "vi", "nano", "less", "more", "top", "htop",
    "ssh", "scp", "sftp", "psql", "mysql", "sqlite3",
    "docker exec -it", "kubectl exec -it",
)


def _is_rtk_status_active() -> bool:
    if os.environ.get("CODEX_MAX_RTK_STATUS") == "active":
        return True
    if _RTK_STATE_FILE.exists():
        try:
            state = json.loads(_RTK_STATE_FILE.read_text(encoding="utf-8", errors="replace"))
            return state.get("status") == "active"
        except Exception:
            pass
    return False


def _classify_command(cmd: str) -> tuple[str, str]:
    """
    Returns (decision, reason):
      decision: 'noop' | 'suggest_rtk'
      reason: explanation string
    """
    norm = cmd.strip()

    # Already RTK prefixed
    if norm.startswith("rtk "):
        return "noop", "already_rtk"

    # Composite shell → raw
    for token in _COMPOSITE_TOKENS:
        if token in norm:
            return "noop", "composite_shell"

    # Interactive → raw
    for ic in _INTERACTIVE_CMDS:
        if norm.startswith(ic):
            return "noop", "interactive"

    # Machine-readable flags → raw
    for flag in _MACHINE_READABLE_FLAGS:
        if flag in norm:
            return "noop", "machine_readable"

    # Check if it's a candidate for RTK
    tokens = norm.split()
    for prefix in _AUTO_RTK_PREFIXES:
        if tuple(tokens[:len(prefix)]) == prefix:
            return "suggest_rtk", f"rtk_candidate:{' '.join(prefix)}"

    return "noop", "not_rtk_candidate"


def _log_missed_opportunity(cmd: str, reason: str, shim_active: bool) -> None:
    """Log missed RTK opportunity to JSONL for later analysis."""
    import datetime
    try:
        _RTK_MISSED_LOG.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z"),
            "command": cmd[:200],
            "rtk_reason": reason,
            "shim_active": shim_active,
        }
        with _RTK_MISSED_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


_DESTRUCTIVE_BASH_PATTERNS = (
    "rm -rf",
    "git reset --hard",
    "git clean -fd",
    "git clean -xdf",
    "git push --force",
    "git push -f",
    "drop table",
)

_DEP_INSTALL_PATTERNS = (
    "npm install",
    "pnpm add",
    "yarn add",
    "pip install",
    "uv add",
    "poetry add",
    "cargo add",
    "go get",
)


def _gateguard_message(cmd: str) -> str | None:
    norm = " ".join(cmd.strip().lower().split())

    for pattern in _DESTRUCTIVE_BASH_PATTERNS:
        if pattern in norm:
            return (
                "🛡️ GateGuard: before destructive Bash, gather facts first:\n"
                "1. List the files/data this command will affect\n"
                "2. Write a one-line rollback step\n"
                "3. Quote the current user instruction verbatim"
            )

    for pattern in _DEP_INSTALL_PATTERNS:
        if pattern in norm:
            return (
                "🔎 search-first: before adding a dependency, confirm:\n"
                "1. The repo does not already contain an equivalent solution\n"
                "2. The chosen package is the smallest acceptable fit\n"
                "3. Current docs were checked before installing"
            )

    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)

    # Extract the bash command from payload
    cmd = ""
    tool_input = payload.get("tool_input", {})
    if isinstance(tool_input, dict):
        cmd = tool_input.get("command", "")
    elif isinstance(payload.get("input"), dict):
        cmd = payload["input"].get("command", "")

    messages: list[str] = []

    plan_msg = _plan_context(root)
    if plan_msg:
        messages.append(plan_msg)

    # RTK classification (non-blocking — just log missed opportunities)
    if cmd:
        rtk_active = _is_rtk_status_active()
        shim_active = bool(os.environ.get("BASH_ENV"))
        decision, reason = _classify_command(cmd)

        if decision == "suggest_rtk" and not shim_active:
            _log_missed_opportunity(cmd, reason, shim_active)
            messages.append(f"💡 RTK available: try `rtk {cmd.strip()}` for compact output")

    # GitNexus warning (non-blocking)
    warning = _check_gitnexus_warning(root)
    if warning:
        messages.append(warning)

    # Minimal GateGuard / search-first guidance for Bash actions
    if cmd:
        gate_msg = _gateguard_message(cmd)
        if gate_msg:
            messages.append(gate_msg)

    if messages:
        adapter.emit_json({"systemMessage": "\n\n".join(messages)})


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
