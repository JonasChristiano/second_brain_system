from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import os
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

from brain_system import cli, paths, skills


class PathsTests(unittest.TestCase):
    def test_resolve_root_prefers_brain_root(self) -> None:
        with mock.patch.dict(os.environ, {"BRAIN_ROOT": "/tmp/brain-root"}, clear=True):
            self.assertEqual(paths.resolve_root(), Path("/tmp/brain-root"))

    def test_resolve_root_uses_pwd_when_brain_root_missing(self) -> None:
        with mock.patch.dict(os.environ, {"PWD": "/tmp/pwd-root"}, clear=True):
            self.assertEqual(paths.resolve_root(), Path("/tmp/pwd-root"))

    def test_resolve_root_falls_back_to_project_root(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(paths.resolve_root(), ROOT)


class SkillsTests(unittest.TestCase):
    def test_ensure_skill_exists_success_and_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = Path(temp_dir)
            demo_dir = skills_dir / "demo"
            demo_dir.mkdir()
            (demo_dir / "SKILL.md").write_text("demo", encoding="utf-8")

            with mock.patch.object(skills, "SKILLS_DIR", skills_dir):
                self.assertEqual(
                    skills.ensure_skill_exists("demo"), demo_dir / "SKILL.md"
                )
                with self.assertRaises(SystemExit):
                    skills.ensure_skill_exists("missing")

    def test_list_skills_load_text_and_slugify(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = Path(temp_dir)
            (skills_dir / "b").mkdir()
            (skills_dir / "b" / "SKILL.md").write_text(" b \n", encoding="utf-8")
            (skills_dir / "a").mkdir()
            (skills_dir / "a" / "SKILL.md").write_text(" a \n", encoding="utf-8")

            with mock.patch.object(skills, "SKILLS_DIR", skills_dir):
                listed = skills.list_skills()

            self.assertEqual([path.name for path in listed], ["a", "b"])
            self.assertEqual(skills.load_text(skills_dir / "a" / "SKILL.md"), "a")
            self.assertEqual(skills.slugify("Meu-Teste Legal"), "meu_teste_legal")

    def test_build_prompt_with_all_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            context = root / "context.md"
            context.write_text("contexto", encoding="utf-8")
            skills_dir = root / "skills"
            skills_dir.mkdir()
            demo_dir = skills_dir / "demo"
            demo_dir.mkdir()
            (demo_dir / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill\n---\nskill-body",
                encoding="utf-8",
            )

            with (
                mock.patch.object(skills, "CONTEXT_FILE", context),
                mock.patch.object(skills, "SKILLS_DIR", skills_dir),
            ):
                prompt = skills.build_prompt("demo", "fazer algo", "vault/notes")

            self.assertIn("[Contexto global]", prompt)
            self.assertIn("[Skill: demo]", prompt)
            self.assertIn("[Alvo]", prompt)
            self.assertIn("[Instrucao]", prompt)

    def test_build_prompt_without_optional_sections(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            context = root / "context.md"
            skills_dir = root / "skills"
            skills_dir.mkdir()
            demo_dir = skills_dir / "demo"
            demo_dir.mkdir()
            (demo_dir / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill\n---\nskill-body",
                encoding="utf-8",
            )

            with (
                mock.patch.object(skills, "CONTEXT_FILE", context),
                mock.patch.object(skills, "SKILLS_DIR", skills_dir),
            ):
                prompt = skills.build_prompt("demo")

            self.assertNotIn("[Contexto global]", prompt)
            self.assertNotIn("[Alvo]", prompt)
            self.assertNotIn("[Instrucao]", prompt)


class CliTests(unittest.TestCase):
    def test_run_command_uses_project_root(self) -> None:
        fake_result = types.SimpleNamespace(returncode=9)
        with mock.patch.object(
            cli.subprocess, "run", return_value=fake_result
        ) as run_mock:
            self.assertEqual(cli.run_command(["python3", "--version"]), 9)
        run_mock.assert_called_once_with(["python3", "--version"], cwd=cli.ROOT)

    def test_ensure_codex_available_success_and_failure(self) -> None:
        with mock.patch.object(cli.shutil, "which", return_value="/usr/bin/codex"):
            cli.ensure_codex_available()

        with mock.patch.object(cli.shutil, "which", return_value=None):
            with self.assertRaises(SystemExit):
                cli.ensure_codex_available()

    def test_cmd_add(self) -> None:
        args = argparse.Namespace(content="ideia")
        with (
            mock.patch.object(cli, "ensure_codex_available") as ensure_mock,
            mock.patch.object(
                cli, "build_prompt", return_value="prompt"
            ) as prompt_mock,
            mock.patch.object(cli, "run_command", return_value=11) as run_mock,
        ):
            self.assertEqual(cli.cmd_add(args), 11)
        ensure_mock.assert_called_once_with()
        prompt_mock.assert_called_once_with(
            "brain_orchestrator", "ideia", str(cli.NOTES_DIR)
        )
        run_mock.assert_called_once_with(["codex", "prompt"])

    def test_cmd_search_index_watch_and_refine(self) -> None:
        with mock.patch.object(cli, "run_command", return_value=3) as run_mock:
            self.assertEqual(cli.cmd_search(argparse.Namespace(query="busca")), 3)
            self.assertEqual(cli.cmd_index(argparse.Namespace()), 3)
            self.assertEqual(cli.cmd_restructure(argparse.Namespace()), 3)
            self.assertEqual(cli.cmd_watch(argparse.Namespace()), 3)

        self.assertEqual(
            run_mock.call_args_list,
            [
                mock.call([sys.executable, "rag/search.py", "busca"]),
                mock.call([sys.executable, "rag/indexer.py"]),
                mock.call([sys.executable, "restructure.py"]),
                mock.call([sys.executable, "whatcher.py"]),
            ],
        )

        with (
            mock.patch.object(cli, "ensure_codex_available"),
            mock.patch.object(
                cli, "build_prompt", return_value="refine-prompt"
            ) as prompt_mock,
            mock.patch.object(cli, "run_command", return_value=4) as run_mock_2,
        ):
            self.assertEqual(
                cli.cmd_refine(argparse.Namespace(file=None, instruction=None)), 4
            )
        prompt_mock.assert_called_once_with(
            "note_refinement",
            "Refinar as notas em vault/notes/",
            str(cli.NOTES_DIR),
        )
        run_mock_2.assert_called_once_with(["codex", "refine-prompt"])

        with (
            mock.patch.object(cli, "ensure_codex_available"),
            mock.patch.object(
                cli, "build_prompt", return_value="file-refine-prompt"
            ) as prompt_mock_2,
            mock.patch.object(cli, "run_command", return_value=5) as run_mock_3,
        ):
            self.assertEqual(
                cli.cmd_refine(
                    argparse.Namespace(
                        file="vault/notes/comando-cat.md",
                        instruction=None,
                    )
                ),
                5,
            )
        prompt_mock_2.assert_called_once_with(
            "note_refinement",
            "Refinar a nota em vault/notes/comando-cat.md",
            "vault/notes/comando-cat.md",
        )
        run_mock_3.assert_called_once_with(["codex", "file-refine-prompt"])

        with (
            mock.patch.object(cli, "ensure_codex_available"),
            mock.patch.object(
                cli, "build_prompt", return_value="custom-refine-prompt"
            ) as prompt_mock_3,
            mock.patch.object(cli, "run_command", return_value=6) as run_mock_4,
        ):
            self.assertEqual(
                cli.cmd_refine(
                    argparse.Namespace(
                        file="vault/notes/comando-cat.md",
                        instruction="Refinar so a introducao",
                    )
                ),
                6,
            )
        prompt_mock_3.assert_called_once_with(
            "note_refinement",
            "Refinar so a introducao",
            "vault/notes/comando-cat.md",
        )
        run_mock_4.assert_called_once_with(["codex", "custom-refine-prompt"])

    def test_cmd_skills_list_show_new_and_run(self) -> None:
        fake_skill = Path("/tmp/demo.md")
        with mock.patch.object(cli, "list_skills", return_value=[]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(cli.cmd_skills_list(argparse.Namespace()), 0)
            self.assertIn("Nenhuma skill encontrada.", stdout.getvalue())

        with mock.patch.object(cli, "list_skills", return_value=[fake_skill]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(cli.cmd_skills_list(argparse.Namespace()), 0)
            self.assertIn("demo", stdout.getvalue())

        with (
            mock.patch.object(
                cli, "ensure_skill_exists", return_value=fake_skill
            ) as ensure_mock,
            mock.patch.object(cli, "load_text", return_value="conteudo") as load_mock,
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    cli.cmd_skills_show(argparse.Namespace(name="demo")), 0
                )
            self.assertEqual(stdout.getvalue().strip(), "conteudo")
        ensure_mock.assert_called_once_with("demo")
        load_mock.assert_called_once_with(fake_skill)

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_dir = root / "skills"
            with (
                mock.patch.object(cli, "ROOT", root),
                mock.patch.object(cli, "SKILLS_DIR", skills_dir),
            ):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    self.assertEqual(
                        cli.cmd_skills_new(
                            argparse.Namespace(name="Nova Skill", goal="Objetivo teste")
                        ),
                        0,
                    )
                created = skills_dir / "nova_skill" / "SKILL.md"
                self.assertTrue(created.exists())
                created_text = created.read_text(encoding="utf-8")
                self.assertIn("Objetivo teste", created_text)
                self.assertIn("last_updated: 2026-04-23", created_text)
                self.assertIn("skills/nova_skill/SKILL.md", stdout.getvalue())

                with self.assertRaises(SystemExit):
                    cli.cmd_skills_new(
                        argparse.Namespace(name="Nova Skill", goal="Objetivo teste")
                    )

        with (
            mock.patch.object(cli, "ensure_codex_available"),
            mock.patch.object(cli, "build_prompt", return_value="run-prompt"),
            mock.patch.object(cli, "run_command", return_value=8) as run_mock_3,
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    cli.cmd_skills_run(
                        argparse.Namespace(
                            name="demo",
                            instruction="instrucao",
                            target="alvo",
                            dry_run=True,
                        )
                    ),
                    0,
                )
            self.assertEqual(stdout.getvalue().strip(), "run-prompt")
            run_mock_3.assert_not_called()

            self.assertEqual(
                cli.cmd_skills_run(
                    argparse.Namespace(
                        name="demo",
                        instruction="instrucao",
                        target="alvo",
                        dry_run=False,
                    )
                ),
                8,
            )
            run_mock_3.assert_called_once_with(["codex", "run-prompt"])

    def test_main_dispatches_add_and_search(self) -> None:
        with mock.patch.object(sys, "argv", ["brain", "add", "uma", "ideia"]):
            with mock.patch.object(cli, "cmd_add", return_value=21) as add_mock:
                self.assertEqual(cli.main(), 21)
            add_args = add_mock.call_args.args[0]
            self.assertEqual(add_args.content, "uma ideia")

        with mock.patch.object(sys, "argv", ["brain", "search", "minha", "busca"]):
            with mock.patch.object(cli, "cmd_search", return_value=22) as search_mock:
                self.assertEqual(cli.main(), 22)
            search_args = search_mock.call_args.args[0]
            self.assertEqual(search_args.query, "minha busca")
