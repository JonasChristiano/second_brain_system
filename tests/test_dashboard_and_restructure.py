from __future__ import annotations

import contextlib
import io
import os
import runpy
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

import restructure


class FakeStreamlit:
    def __init__(self, search_value: str) -> None:
        self.search_value = search_value
        self.calls: list[tuple[str, object]] = []

    def title(self, text: str) -> None:
        self.calls.append(("title", text))

    def metric(self, label: str, value: int) -> None:
        self.calls.append(("metric", (label, value)))

    def text_input(self, label: str) -> str:
        self.calls.append(("text_input", label))
        return self.search_value

    def write(self, text: str) -> None:
        self.calls.append(("write", text))


class DashboardTests(unittest.TestCase):
    def run_dashboard(self, search_value: str, note_names: list[str]) -> FakeStreamlit:
        streamlit = FakeStreamlit(search_value)
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        notes_dir = Path(temp_dir.name)

        for name in note_names:
            (notes_dir / name).write_text("# nota", encoding="utf-8")

        fake_paths = types.ModuleType("brain_system.paths")
        fake_paths.NOTES_DIR = notes_dir
        path_without_src = [path for path in sys.path if path != str(SRC_DIR)]

        with (
            mock.patch.dict(
                sys.modules,
                {
                    "streamlit": streamlit,
                    "brain_system.paths": fake_paths,
                },
                clear=False,
            ),
            mock.patch.object(sys, "path", path_without_src),
        ):
            runpy.run_path(str(ROOT / "dashboard.py"), run_name="__main__")

        return streamlit

    def test_dashboard_lists_matching_notes(self) -> None:
        streamlit = self.run_dashboard("ls", ["comando-ls.md", "python.md"])
        self.assertIn(("title", "🧠 Brain Dashboard"), streamlit.calls)
        self.assertIn(("metric", ("Notas totais", 2)), streamlit.calls)
        self.assertIn(("write", "comando-ls.md"), streamlit.calls)

    def test_dashboard_skips_non_matching_notes(self) -> None:
        streamlit = self.run_dashboard("zzz", ["comando-ls.md", "python.md"])
        writes = [call for call in streamlit.calls if call[0] == "write"]
        self.assertEqual(writes, [])


class RestructureTests(unittest.TestCase):
    def test_reorganize_vault_moves_markdown_and_attachments_and_creates_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / "vault"
            base.mkdir()
            nested = base / "raw"
            nested.mkdir()
            (nested / "note.md").write_text("nota", encoding="utf-8")
            (nested / "file.txt").write_text("arquivo", encoding="utf-8")
            (nested / "keep.py").write_text("print('ok')", encoding="utf-8")

            result = restructure.reorganize_vault(base)

            self.assertTrue((base / "notes" / "note.md").exists())
            self.assertTrue((base / "attachments" / "file.txt").exists())
            self.assertTrue((nested / "keep.py").exists())
            self.assertTrue((base / "templates").exists())
            self.assertTrue((base / "inbox").exists())
            self.assertTrue((base / "archive").exists())
            self.assertEqual(result["notes_moved"], 1)
            self.assertEqual(result["attachments_moved"], 1)

    def test_reorganize_vault_preserves_standard_directories_and_git(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / "vault"
            notes = base / "notes"
            attachments = base / "attachments"
            git_dir = base / ".git"
            notes.mkdir(parents=True)
            attachments.mkdir(parents=True)
            git_dir.mkdir(parents=True)
            (notes / "existing.md").write_text("ok", encoding="utf-8")
            (attachments / "existing.txt").write_text("ok", encoding="utf-8")
            (git_dir / "config").write_text("git", encoding="utf-8")

            result = restructure.reorganize_vault(base)

            self.assertTrue((notes / "existing.md").exists())
            self.assertTrue((attachments / "existing.txt").exists())
            self.assertTrue((git_dir / "config").exists())
            self.assertEqual(result["notes_moved"], 0)
            self.assertEqual(result["attachments_moved"], 0)

    def test_reorganize_vault_skips_nested_standard_named_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir) / "vault"
            nested_notes = base / "legacy" / "notes"
            nested_notes.mkdir(parents=True)
            (nested_notes / "keep.md").write_text("ok", encoding="utf-8")

            result = restructure.reorganize_vault(base)

            self.assertTrue((nested_notes / "keep.md").exists())
            self.assertFalse((base / "notes" / "keep.md").exists())
            self.assertEqual(result["notes_moved"], 0)

    def test_main_prints_message(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with mock.patch.object(restructure, "reorganize_vault") as reorganize_mock:
                reorganize_mock.return_value = {
                    "notes_moved": 2,
                    "attachments_moved": 3,
                }
                restructure.main()
        reorganize_mock.assert_called_once_with()
        self.assertIn("Vault reorganizado.", stdout.getvalue())
        self.assertIn("Notas movidas: 2.", stdout.getvalue())

    def test_script_entrypoint_runs_main(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            (workdir / "vault").mkdir()
            stdout = io.StringIO()
            previous_cwd = Path.cwd()
            try:
                os.chdir(workdir)
                with contextlib.redirect_stdout(stdout):
                    runpy.run_path(str(ROOT / "restructure.py"), run_name="__main__")
            finally:
                os.chdir(previous_cwd)
        self.assertIn("Vault reorganizado.", stdout.getvalue())
