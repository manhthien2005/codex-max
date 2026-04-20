import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOKS_JSON = REPO_ROOT / "hooks.json"
HOOKS_DIR = REPO_ROOT / "hooks"


class HooksRuntimeTests(unittest.TestCase):
    def run_python_hook(
        self,
        script_name: str,
        payload: dict,
        cwd: Path,
        env: dict | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HOOKS_DIR / script_name)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            cwd=str(cwd),
            env=env,
            check=False,
        )

    def run_shell_hook(
        self,
        script_name: str,
        cwd: Path,
        env: dict | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", str(HOOKS_DIR / script_name)],
            text=True,
            capture_output=True,
            cwd=str(cwd),
            env=env,
            check=False,
        )

    def test_hooks_json_declares_all_expected_codex_events(self) -> None:
        payload = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop"},
            set(payload["hooks"]),
        )

    def test_session_start_reuses_plan_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as codex_home:
            root = Path(tmpdir)
            root.joinpath("task_plan.md").write_text(
                "# Task Plan\n\n## Task\nShip Codex hooks\n\n## Status\n- align session-start\n",
                encoding="utf-8",
            )
            root.joinpath("progress.md").write_text(
                "# Progress\n\n### Step 3\nFinished adapter draft.\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["CODEX_HOME"] = codex_home
            result = self.run_shell_hook("session-start.sh", root, env=env)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("ACTIVE PLAN", result.stdout)
        self.assertIn("Ship Codex hooks", result.stdout)
        self.assertIn("Finished adapter draft", result.stdout)

    def test_pre_tool_use_emits_plan_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("task_plan.md").write_text(
                "# Task Plan\n\n## Task\nAudit MCP launchers\n",
                encoding="utf-8",
            )

            result = self.run_python_hook(
                "pre_tool_use.py",
                {"cwd": str(root), "tool_input": {"command": "pwd"}},
                root,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("ACTIVE PLAN", payload["systemMessage"])
        self.assertIn("Audit MCP launchers", payload["systemMessage"])

    def test_user_prompt_submit_emits_additional_context_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as codex_home:
            root = Path(tmpdir)
            root.joinpath("task_plan.md").write_text(
                "# Task Plan\n\n## Task\nReview hook outputs\n\n## Status\n- current phase: fix user prompt submit\n",
                encoding="utf-8",
            )
            root.joinpath("progress.md").write_text(
                "# Progress\n\n### Step 2\n- Reproduced the invalid hook output.\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["CODEX_HOME"] = codex_home

            result = self.run_python_hook(
                "user_prompt_submit.py",
                {"cwd": str(root), "prompt": "Please inspect the hooks."},
                root,
                env=env,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        hook_output = payload["hookSpecificOutput"]
        self.assertEqual("UserPromptSubmit", hook_output["hookEventName"])
        self.assertIn("ACTIVE PLAN", hook_output["additionalContext"])
        self.assertIn("Review hook outputs", hook_output["additionalContext"])
        self.assertIn("recent progress", hook_output["additionalContext"])

    def test_post_tool_use_emits_progress_reminder(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("task_plan.md").write_text("# Task Plan\n", encoding="utf-8")

            result = self.run_python_hook(
                "post_tool_use.py",
                {"cwd": str(root), "tool_response": "ok"},
                root,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("progress.md", payload["systemMessage"])
        self.assertIn("task_plan.md", payload["systemMessage"])

    def test_stop_blocks_when_diary_sentinel_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, tempfile.TemporaryDirectory() as codex_home:
            root = Path(tmpdir)
            codex_root = Path(codex_home)
            sentinel = codex_root / ".tmp" / "diary_pending"
            sentinel.parent.mkdir(parents=True, exist_ok=True)
            sentinel.write_text("2026-04-20 10:00:00 +0700\n", encoding="utf-8")

            env = os.environ.copy()
            env["CODEX_HOME"] = codex_home

            result = self.run_python_hook(
                "stop.py",
                {"cwd": str(root), "stop_hook_active": False},
                root,
                env=env,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("block", payload["decision"])
        self.assertIn("mempalace_diary_write", payload["reason"])


if __name__ == "__main__":
    unittest.main()
