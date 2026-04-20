#!/usr/bin/env python3
from __future__ import annotations

import codex_hook_adapter as adapter


def main() -> None:
    """Keep PostToolUse quiet; progress tracking is handled outside the hook."""
    adapter.load_payload()


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
