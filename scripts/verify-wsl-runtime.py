#!/usr/bin/env python3
"""Verify the WSL Codex runtime, including MCP launcher readiness and initialize probes."""

from __future__ import annotations

import json
import os
import selectors
import shlex
import shutil
import subprocess
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROTOCOL_VERSIONS = ("2025-03-26", "2024-11-05")


@dataclass
class ProbeResult:
    name: str
    configured: str = "yes"
    launcher_found: str = "n/a"
    environment_ready: str = "n/a"
    initialize_ok: str = "n/a"
    backend_ready: str = "n/a"
    auth: str = "ok"
    detail: str = ""


def read_message(stdout: Any, timeout: float = 20.0) -> dict[str, Any]:
    selector = selectors.DefaultSelector()
    selector.register(stdout, selectors.EVENT_READ)
    buffer = b""
    deadline = time.time() + timeout
    last_non_json = ""

    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            detail = f" after non-JSON output: {last_non_json}" if last_non_json else ""
            raise TimeoutError(f"timed out waiting for MCP response{detail}")
        events = selector.select(remaining)
        if not events:
            continue
        chunk = os.read(stdout.fileno(), 4096)
        if not chunk:
            detail = f" after non-JSON output: {last_non_json}" if last_non_json else ""
            raise RuntimeError(f"unexpected EOF while reading MCP response{detail}")
        buffer += chunk
        while b"\n" in buffer:
            raw_line, buffer = buffer.split(b"\n", 1)
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                selector.unregister(stdout)
                return json.loads(line)
            except json.JSONDecodeError:
                last_non_json = line[:200]


def write_message(stdin: Any, payload: dict[str, Any]) -> None:
    stdin.write(json.dumps(payload).encode("utf-8") + b"\n")
    stdin.flush()


def stop_process(process: subprocess.Popen[bytes]) -> str:
    try:
        process.terminate()
        _, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        _, stderr = process.communicate()
    return stderr.decode("utf-8", errors="replace").strip()


def initialize_stdio_once(command: str, args: list[str], protocol_version: str, timeout: float) -> tuple[bool, str]:
    process = subprocess.Popen(
        [command, *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False,
    )
    assert process.stdin is not None and process.stdout is not None

    ok = False
    detail = ""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "codex-max-wsl-verify", "version": "1.0"},
            },
        }
        write_message(process.stdin, payload)
        response = read_message(process.stdout, timeout=timeout)
        if "result" in response:
            write_message(process.stdin, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            ok = True
            detail = protocol_version
        else:
            detail = json.dumps(response)
    except Exception as exc:  # noqa: BLE001
        detail = str(exc)
    finally:
        stderr = stop_process(process)
        if stderr:
            suffix = stderr.replace("\n", " ")[:240]
            if ok:
                detail = f"{detail} (stderr: {suffix})"
            else:
                detail = f"{detail} | stderr: {suffix}" if detail else f"stderr: {suffix}"
    return ok, detail


def initialize_stdio(command: str, args: list[str], timeout: float = 20.0) -> tuple[bool, str]:
    last_error = ""
    for protocol_version in PROTOCOL_VERSIONS:
        ok, detail = initialize_stdio_once(command, args, protocol_version, timeout)
        if ok:
            return True, detail
        last_error = detail
    return False, last_error or "initialize returned no result"


def resolve_local_paths(args: list[str], home: Path, codex_home: Path) -> list[Path]:
    prefixes = {
        "~/.codex/": codex_home,
        "$HOME/.codex/": codex_home,
        f"{home}/.codex/": codex_home,
        f"{codex_home}/": codex_home,
    }
    resolved: list[Path] = []
    seen: set[Path] = set()
    for arg in args:
        try:
            tokens = shlex.split(arg)
        except ValueError:
            tokens = arg.split()
        for token in tokens:
            stripped = token.strip("\"'")
            for prefix, base in prefixes.items():
                if stripped.startswith(prefix):
                    relative = stripped[len(prefix) :]
                    candidate = base / relative
                    if candidate not in seen:
                        seen.add(candidate)
                        resolved.append(candidate)
                    break
    return resolved


def format_missing_paths(paths: list[Path], base: Path) -> str:
    display = []
    for path in paths:
        try:
            display.append(str(path.relative_to(base)))
        except ValueError:
            display.append(str(path))
    return ", ".join(display)


def has_required_runtime(env_checks: dict[str, str | None], skills_root: Path) -> bool:
    required_tools = ("node", "npm", "codex", "python3", "docker", "rtk")
    return all(env_checks.get(tool) for tool in required_tools) and skills_root.exists()


def load_interactive_env_var(name: str) -> str:
    try:
        result = subprocess.run(
            ["bash", "-ic", f"printf '%s' \"${{{name}:-}}\""],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except Exception:  # noqa: BLE001
        return ""
    return result.stdout.strip()


def initialize_http(url: str, timeout: float = 20.0, bearer_token: str = "") -> tuple[bool, str]:
    last_error = ""
    for protocol_version in PROTOCOL_VERSIONS:
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": protocol_version,
                    "capabilities": {},
                    "clientInfo": {"name": "codex-max-wsl-verify", "version": "1.0"},
                },
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {bearer_token}"} if bearer_token else {}),
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
            if "\"result\"" in body:
                return True, protocol_version
            last_error = body[:200]
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
    return False, last_error or "initialize failed"


def http_ready(url: str, timeout: float = 5.0) -> str:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read(200).decode("utf-8", errors="replace")
        return "yes" if response.status < 400 else f"http_{response.status}:{body[:60]}"
    except Exception as exc:  # noqa: BLE001
        return f"no ({exc})"


def main() -> int:
    home = Path(os.environ.get("HOME", str(Path.home())))
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    config_path = codex_home / "config.toml"

    with config_path.open("rb") as handle:
        config = tomllib.load(handle)

    results: list[ProbeResult] = []
    env_checks = {
        "node": shutil.which("node"),
        "npm": shutil.which("npm"),
        "codex": shutil.which("codex"),
        "python3": shutil.which("python3"),
        "docker": shutil.which("docker"),
        "rtk": shutil.which("rtk"),
    }

    print(f"CODEX_HOME {codex_home}")
    for tool, path in env_checks.items():
        print(f"TOOL {tool} {'OK' if path else 'MISSING'} {path or ''}".rstrip())

    skills_root = home / ".agents" / "skills"
    print(f"SKILLS {'OK' if skills_root.exists() else 'MISSING'} {skills_root}")
    failure = not has_required_runtime(env_checks, skills_root)
    github_token = os.environ.get("GITHUB_TOKEN", "") or load_interactive_env_var("GITHUB_TOKEN")

    for name, server in config.get("mcp_servers", {}).items():
        result = ProbeResult(name=name)

        if "url" in server:
            result.launcher_found = "remote"
            result.environment_ready = "yes"
            if name == "github" and not github_token:
                result.auth = "auth_missing"
                result.initialize_ok = "skipped"
                result.detail = "GITHUB_TOKEN not set"
            else:
                ok, detail = initialize_http(
                    str(server["url"]),
                    bearer_token=github_token if name == "github" else "",
                )
                result.initialize_ok = "yes" if ok else "no"
                result.detail = detail
            results.append(result)
            continue

        command = str(server.get("command", ""))
        args = [str(arg) for arg in server.get("args", [])]
        result.launcher_found = "yes" if shutil.which(command) else "no"

        launcher_paths = resolve_local_paths(args, home, codex_home)
        missing_paths = [path for path in launcher_paths if not path.exists()]
        if result.launcher_found != "yes":
            result.environment_ready = "no (command missing)"
        elif missing_paths:
            result.environment_ready = f"no (missing: {format_missing_paths(missing_paths, codex_home)})"
        else:
            result.environment_ready = "yes"

        if name == "qdrant":
            result.backend_ready = http_ready("http://127.0.0.1:6333/healthz")
        elif name == "semantic_qdrant_http":
            qdrant_state = http_ready("http://127.0.0.1:6333/healthz")
            ollama_state = http_ready("http://127.0.0.1:11434/api/tags")
            result.backend_ready = "yes" if qdrant_state == "yes" and ollama_state == "yes" else f"no (qdrant={qdrant_state}, ollama={ollama_state})"
        else:
            result.backend_ready = "yes"

        if result.environment_ready != "yes":
            result.initialize_ok = "skipped"
            result.detail = result.environment_ready
        else:
            ok, detail = initialize_stdio(command, args, timeout=float(server.get("startup_timeout_sec", 20.0)))
            result.initialize_ok = "yes" if ok else "no"
            result.detail = detail
        results.append(result)

    print("")
    print("MCP_RESULTS")
    print("name|configured|launcher_found|environment_ready|initialize_ok|backend_ready|auth|detail")
    for result in results:
        detail = result.detail.replace("\n", " ")[:180]
        print(
            "|".join(
                [
                    result.name,
                    result.configured,
                    result.launcher_found,
                    result.environment_ready,
                    result.initialize_ok,
                    result.backend_ready,
                    result.auth,
                    detail,
                ]
            )
        )
        if result.name != "github" and result.environment_ready != "yes":
            failure = True
        if result.name != "github" and result.initialize_ok not in {"yes", "skipped"}:
            failure = True
        if result.backend_ready.startswith("no") and result.name in {"qdrant", "semantic_qdrant_http"}:
            failure = True

    return 1 if failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
