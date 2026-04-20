#!/usr/bin/env python3
r"""
hook-probe.py — Test xem Codex Desktop có fire hooks không.

Cách dùng:
  Mở Codex Desktop → chạy lệnh Bash bất kỳ (vd: "ls" hoặc "echo test")
  Sau đó kiểm tra file: C:\Users\MrThien\.codex\.tmp\hook_probe.jsonl

Nếu file có entries → Codex Desktop đang fire PreToolUse hooks ✅
Nếu file trống/không tồn tại → hooks không được fire ❌
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

# Ghi proof file để biết hook đã fire
PROBE_FILE = Path.home() / ".codex" / ".tmp" / "hook_probe.jsonl"

def main() -> None:
    # Đọc payload nếu có
    try:
        raw = sys.stdin.read(2000).strip()
        payload = json.loads(raw) if raw else {}
    except Exception:
        payload = {}

    PROBE_FILE.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "hook": "PreToolUse",
        "payload_keys": list(payload.keys()),
        "tool_name": payload.get("tool_name", "unknown"),
        "command": (payload.get("tool_input") or {}).get("command", "unknown")[:100],
        "cwd": payload.get("cwd", "unknown"),
    }

    with PROBE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # Allow the command through — không can thiệp
    print('{"decision": "allow"}')

if __name__ == "__main__":
    main()
