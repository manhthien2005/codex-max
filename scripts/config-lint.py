#!/usr/bin/env python3
"""Lint the WSL-first Codex config surface for stale Windows-native assumptions."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path


WINDOWS_MARKERS = ("C:\\", "\\\\?\\UNC\\", "/mnt/c/")


def main() -> int:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    config_path = codex_home / "config.toml"
    if not config_path.exists():
        print(f"CONFIG_LINT_FAIL missing {config_path}")
        return 1

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    issues: list[str] = []

    if "persistent_instructions" in data:
        issues.append("persistent_instructions is present; use developer_instructions instead")

    if data.get("web_search") != "cached":
        issues.append(f"default web_search should be cached, found {data.get('web_search')!r}")

    for project_path in data.get("projects", {}):
        if any(marker in project_path for marker in WINDOWS_MARKERS):
            issues.append(f"Windows-native trusted path remains active: {project_path}")

    for name, server in data.get("mcp_servers", {}).items():
        if "url" in server:
            continue
        command = str(server.get("command", ""))
        args = [str(arg) for arg in server.get("args", [])]
        joined = " ".join([command, *args])
        if ".cmd" in joined:
            issues.append(f"{name}: .cmd launcher still referenced")
        if any(marker in joined for marker in WINDOWS_MARKERS):
            issues.append(f"{name}: Windows path remains in launcher config")

    if issues:
        for issue in issues:
            print(f"CONFIG_LINT_FAIL {issue}")
        return 1

    print(f"CONFIG_LINT_OK {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
