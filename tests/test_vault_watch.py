from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from brain_system import vault_watch


class VaultWatchTests(unittest.TestCase):
    def test_git_invokes_git_in_vault(self) -> None:
        fake_result = types.SimpleNamespace(returncode=0)
        with mock.patch.object(vault_watch.subprocess, "run", return_value=fake_result) as run_mock:
            result = vault_watch.git(["status"])
        self.assertIs(result, fake_result)
        run_mock.assert_called_once_with(
            ["git", "-C", str(vault_watch.VAULT_DIR), "status"],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_ensure_vault_repo_success_and_failure(self) -> None:
        with mock.patch.object(vault_watch, "VAULT_GIT_DIR", Path("/tmp/.git")):
            with mock.patch.object(Path, "exists", return_value=True):
                vault_watch.ensure_vault_repo()

        with mock.patch.object(vault_watch, "VAULT_GIT_DIR", Path("/tmp/.git")):
            with mock.patch.object(Path, "exists", return_value=False):
                with self.assertRaises(SystemExit):
                    vault_watch.ensure_vault_repo()

    def test_snapshot_and_change_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_dir = Path(temp_dir) / "vault"
            git_dir = vault_dir / ".git"
            notes_dir = vault_dir / "notes"
            git_dir.mkdir(parents=True)
            notes_dir.mkdir(parents=True)
            (notes_dir / "a.md").write_text("a", encoding="utf-8")
            (git_dir / "ignored").write_text("ignored", encoding="utf-8")

            with (
                mock.patch.object(vault_watch, "VAULT_DIR", vault_dir),
                mock.patch.object(vault_watch, "VAULT_GIT_DIR", git_dir),
            ):
                snapshot = vault_watch.snapshot_vault()

            self.assertIn("notes/a.md", snapshot)
            self.assertNotIn(".git/ignored", snapshot)

        changes = vault_watch.describe_changes(
            {"a": (1, 1), "b": (1, 1)},
            {"b": (2, 1), "c": (1, 1)},
        )
        self.assertEqual(changes, ["c", "b", "a"])
        self.assertEqual(
            vault_watch.build_commit_message(["a", "b", "c", "d"]),
            "Auto-commit vault: a, b, c e mais 1",
        )

    def test_commit_changes_status_error_and_clean_repo(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(
                vault_watch,
                "git",
                return_value=types.SimpleNamespace(returncode=1, stdout="", stderr="erro"),
            ):
                vault_watch.commit_changes(["a"])
        self.assertIn("erro", stdout.getvalue())

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(
                vault_watch,
                "git",
                return_value=types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            ) as git_mock:
                vault_watch.commit_changes(["a"])
        self.assertEqual(git_mock.call_count, 1)
        self.assertEqual(stdout.getvalue(), "")

    def test_commit_changes_add_error_commit_success_and_commit_failure(self) -> None:
        stdout = io.StringIO()
        responses = [
            types.SimpleNamespace(returncode=0, stdout=" M file\n", stderr=""),
            types.SimpleNamespace(returncode=1, stdout="", stderr="falha add"),
        ]
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(vault_watch, "git", side_effect=responses):
                vault_watch.commit_changes(["a"])
        self.assertIn("falha add", stdout.getvalue())

        stdout = io.StringIO()
        responses = [
            types.SimpleNamespace(returncode=0, stdout=" M file\n", stderr=""),
            types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            types.SimpleNamespace(returncode=0, stdout="commit ok", stderr=""),
        ]
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(vault_watch, "git", side_effect=responses):
                vault_watch.commit_changes(["a"])
        self.assertIn("commit ok", stdout.getvalue())

        stdout = io.StringIO()
        responses = [
            types.SimpleNamespace(returncode=0, stdout=" M file\n", stderr=""),
            types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            types.SimpleNamespace(returncode=1, stdout="stdout erro", stderr=""),
        ]
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(vault_watch, "git", side_effect=responses):
                vault_watch.commit_changes(["a"])
        self.assertIn("stdout erro", stdout.getvalue())

        stdout = io.StringIO()
        responses = [
            types.SimpleNamespace(returncode=0, stdout=" M file\n", stderr=""),
            types.SimpleNamespace(returncode=0, stdout="", stderr=""),
            types.SimpleNamespace(returncode=1, stdout="", stderr=""),
        ]
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(vault_watch, "git", side_effect=responses):
                vault_watch.commit_changes(["a"])
        self.assertIn("Falha ao criar auto-commit do vault.", stdout.getvalue())

    def test_main_runs_loop_and_handles_keyboard_interrupt(self) -> None:
        stdout = io.StringIO()
        sleep_calls = {"count": 0}

        def fake_sleep(_seconds: float) -> None:
            sleep_calls["count"] += 1
            if sleep_calls["count"] >= 3:
                raise KeyboardInterrupt

        with contextlib.redirect_stdout(stdout):
            with (
                mock.patch.object(vault_watch, "ensure_vault_repo"),
                mock.patch.object(
                    vault_watch,
                    "snapshot_vault",
                    side_effect=[{"a": (1, 1)}, {"a": (1, 1)}, {"a": (2, 1)}, {"a": (2, 1)}],
                ),
                mock.patch.object(vault_watch, "describe_changes", side_effect=[[], ["a"]]),
                mock.patch.object(vault_watch, "commit_changes") as commit_mock,
                mock.patch.object(vault_watch.time, "sleep", side_effect=fake_sleep),
            ):
                vault_watch.main()

        self.assertEqual(commit_mock.call_count, 1)
        output = stdout.getvalue()
        self.assertIn("Vault auto-commit ativo.", output)
        self.assertIn("Watcher encerrado.", output)
