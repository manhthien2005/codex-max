#!/usr/bin/env python3
from __future__ import annotations

import codex_hook_adapter as adapter


def main() -> None:
    payload = adapter.load_payload()
    root = adapter.cwd_from_payload(payload)
    plan_file = adapter.find_plan_file(root)
    if plan_file is None:
        return

    adapter.emit_json(
        {
            "systemMessage": (
                "[planning-with-files] Update progress.md with what you just did. "
                f"If a phase is complete, update {plan_file.name} status."
            )
        }
    )


if __name__ == "__main__":
    raise SystemExit(adapter.main_guard(main))
