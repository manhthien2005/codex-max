#!/usr/bin/env python3
"""
repo-onboard.py — Automated onboarding for a new repo into the Codex intelligence stack.

Usage:
    python scripts/repo-onboard.py <repo-path>

What it does:
    1. Validates the repo path and detects git root
    2. Runs `gitnexus index <repo-path>` to build the code graph
    3. Checks if a Qdrant semantic collection exists for this repo
    4. Registers the repo in ~/.codex/.tmp/indexed_repos.json
    5. Prints the MemPalace KG commands the agent must run (cannot auto-call MCP)

Exit codes:
    0  — all steps succeeded
    1  — repo path invalid or gitnexus not found
    2  — gitnexus indexing failed
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────
QDRANT_URL = "http://127.0.0.1:6333"
REGISTRY_FILE = Path.home() / ".codex" / ".tmp" / "indexed_repos.json"
CODEX_ROOT = Path(__file__).resolve().parent.parent  # ~/.codex


def _log(msg: str) -> None:
    print(f"[repo-onboard] {msg}", flush=True)


def _err(msg: str) -> None:
    print(f"[repo-onboard] ERROR: {msg}", file=sys.stderr, flush=True)


# ── Step 1: Validate repo path ───────────────────────────────────────────────
def validate_repo(repo_path: Path) -> Path:
    if not repo_path.exists():
        _err(f"Path does not exist: {repo_path}")
        sys.exit(1)
    if not repo_path.is_dir():
        _err(f"Not a directory: {repo_path}")
        sys.exit(1)
    # Find git root
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        _err(f"Not a git repository (or git not found): {repo_path}")
        _log("Proceeding with the provided path as root anyway.")
        return repo_path.resolve()
    git_root = Path(result.stdout.strip())
    _log(f"Git root detected: {git_root}")
    return git_root


# ── Step 2: GitNexus indexing ─────────────────────────────────────────────────
def run_gitnexus_index(repo_path: Path) -> bool:
    gitnexus_dir = repo_path / ".gitnexus"
    if gitnexus_dir.exists():
        _log(f"GitNexus index already exists at {gitnexus_dir} — skipping re-index.")
        _log("  To force re-index: gitnexus index <path>")
        return True

    _log("Running: gitnexus index ...")
    # Try gitnexus as command
    gitnexus_bin = _find_gitnexus()
    if not gitnexus_bin:
        _err("gitnexus binary not found in PATH.")
        _log("  Install via:  pip install gitnexus  or check ~/.codex/mcp/")
        return False

    result = subprocess.run(
        [gitnexus_bin, "index", str(repo_path)],
        capture_output=False,
        check=False,
    )
    if result.returncode != 0:
        _err(f"gitnexus index failed (exit {result.returncode})")
        return False
    _log("GitNexus index complete.")
    return True


def _find_gitnexus() -> str | None:
    import shutil
    found = shutil.which("gitnexus")
    if found:
        return found
    # Check common npm/node_modules paths
    candidates = [
        Path.home() / ".npm-global" / "bin" / "gitnexus",
        Path.home() / ".local" / "bin" / "gitnexus",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ── Step 3: Qdrant collection check ──────────────────────────────────────────
def check_qdrant_collection(repo_path: Path) -> str | None:
    """Return existing collection name if found, else None."""
    repo_name = repo_path.name.lower().replace(" ", "-").replace("_", "-")
    try:
        url = f"{QDRANT_URL}/collections"
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read())
        collections = [c["name"] for c in data.get("result", {}).get("collections", [])]
        # Fuzzy match by repo name
        matches = [c for c in collections if repo_name in c or c in repo_name]
        if matches:
            _log(f"Qdrant collection found: {matches[0]}")
            return matches[0]
        _log(f"No Qdrant collection found matching '{repo_name}'.")
        _log(f"  Existing collections: {collections}")
        _log("  To index: run your repo-specific indexing script (e.g. index_<repo>_repo.py)")
        return None
    except (urllib.error.URLError, OSError):
        _log("Qdrant not reachable — skipping collection check.")
        _log("  Start Qdrant: docker start <qdrant-container>")
        return None


# ── Step 4: Registry update ───────────────────────────────────────────────────
def register_repo(repo_path: Path, gitnexus_ok: bool, qdrant_collection: str | None) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    registry: dict = {}
    if REGISTRY_FILE.exists():
        try:
            registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            registry = {}

    key = str(repo_path)
    registry[key] = {
        "name": repo_path.name,
        "path": key,
        "indexed_at": datetime.now().isoformat(),
        "gitnexus": gitnexus_ok,
        "qdrant_collection": qdrant_collection,
    }
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    _log(f"Registry updated: {REGISTRY_FILE}")


# ── Step 5: Print MemPalace instructions ──────────────────────────────────────
def print_mempalace_instructions(repo_path: Path, qdrant_collection: str | None) -> None:
    repo_name = repo_path.name
    qdrant_info = qdrant_collection or "NOT YET INDEXED — run semantic indexing script first"
    print()
    print("=" * 70)
    print("  NEXT STEP (agent must do this — cannot be automated):")
    print("=" * 70)
    print(f"""
Call these MCP tools to register the repo in MemPalace KG:

  mempalace_kg_add(
    subject="{repo_name}",
    predicate="located_at",
    object="{repo_path}"
  )

  mempalace_kg_add(
    subject="{repo_name}",
    predicate="gitnexus_indexed",
    object="{'yes' if qdrant_collection else 'pending'}"
  )

  mempalace_kg_add(
    subject="{repo_name}",
    predicate="qdrant_collection",
    object="{qdrant_info}"
  )

  mempalace_add_drawer(
    wing="projects",
    room="{repo_name}",
    content="Repo {repo_name} at {repo_path}. "
            "GitNexus graph: .gitnexus/. "
            "Qdrant: {qdrant_info}."
  )
""")
    print("=" * 70)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: python {Path(__file__).name} <repo-path>", file=sys.stderr)
        return 1

    raw_path = Path(sys.argv[1]).expanduser()
    _log(f"Onboarding repo: {raw_path}")
    print()

    repo_path = validate_repo(raw_path)

    gitnexus_ok = run_gitnexus_index(repo_path)
    if not gitnexus_ok:
        _err("GitNexus indexing failed. Fix the error above, then re-run.")
        sys.exit(2)

    qdrant_collection = check_qdrant_collection(repo_path)
    register_repo(repo_path, gitnexus_ok, qdrant_collection)
    print_mempalace_instructions(repo_path, qdrant_collection)

    _log("Onboarding complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
