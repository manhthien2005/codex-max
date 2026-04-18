#!/usr/bin/env python3
"""
pre_tool_use.py — Pre-Bash hook for Codex.

Checks:
  1. Plan alignment (existing planning-with-files logic)
  2. GitNexus index presence — warns agent if working in an unindexed repo
"""
from __future__ import annotations

import codex_hook_adapter as adapter
import json
import subprocess
from pathlib import Path


# ── GitNexus missing-index detection ────────────────────────────────────────
_REGISTRY_FILE = Path.home() / ".codex" / ".tmp" / "indexed_repos.json"

# Known-indexed repo paths (from AGENTS.md) — supplement with registry
_KNOWN_INDEXED: set[str] = {
    r"D:\DoAn2\VSmartwatch\health_system",
    r"D:\DoAn2\VSmartwatch\Iot_Simulator",
    r"D:\DoAn2\VSmartwatch\HealthGuard",
    r"D:\DoAn2\VSmartwatch\healthguard-model-api",
}


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
    """Return a warning string if the current repo is not indexed, else None."""
    git_root = _find_git_root(cwd)
    if git_root is None:
        return None  # Not a git repo — skip check

    repo_str = str(git_root)

    # Check .gitnexus dir (most reliable indicator)
    if (git_root / ".gitnexus").exists():
        return None  # Already indexed

    # Check known list + registry
    all_known = _KNOWN_INDEXED | _load_registry_paths()
    for known in all_known:
        try:
            if Path(known).resolve() == git_root.resolve():
                return None  # Known indexed
        except Exception:
            pass

    # .codex config repo — never needs gitnexus
    codex_root = Path.home() / ".codex"
    try:
        if git_root.resolve() == codex_root.resolve():
            return None
    except Exception:
        pass

    return (
        f"⚠️  GitNexus index not found for: {repo_str}\n"
        "    Code-graph features (symbol lookup, dependency tracing) are unavailable.\n"
        "    Run: python ~/.codex/scripts/repo-onboard.py \"" + repo_str + "\"\n"
        "    This will index the repo and register it in the intelligence stack."
    )


# ── Main ─────────────────────────────────────────────────────────────────────
def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)
    stdout, stderr = adapter.run_shell_script("pre-tool-use.sh", root)

    result = adapter.parse_json(stdout)
    decision = result.get("decision")
    if decision and decision != "allow":
        adapter.emit_json(result)
        return

    # GitNexus warning injection (non-blocking — always allow, just warn)
    warning = _check_gitnexus_warning(root)
    if warning:
        adapter.emit_json({"systemMessage": warning})
        return

    if stderr:
        adapter.emit_json({"systemMessage": stderr})


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
