from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
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

            self.assertIn("[CONTEXTO GLOBAL]", prompt)
            self.assertIn("[SKILL: demo]", prompt)
            self.assertIn("[ALVO DA EXECUÇÃO]", prompt)
            self.assertIn("[INSTRUÇÃO ESPECÍFICA]", prompt)

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

            self.assertNotIn("[CONTEXTO GLOBAL]", prompt)
            self.assertNotIn("[ALVO DA EXECUÇÃO]", prompt)
            self.assertNotIn("[INSTRUÇÃO ESPECÍFICA]", prompt)

    def test_build_prompt_with_long_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            context = root / "context.md"
            long_context = "a" * 2500  # Mais de 2000 chars
            context.write_text(long_context, encoding="utf-8")
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

            self.assertIn("[CONTEXTO GLOBAL]", prompt)
            self.assertIn("... (contexto truncado)", prompt)
            self.assertEqual(
                len(
                    prompt.split("[CONTEXTO GLOBAL]\n")[1].split("\n\n[SKILL: demo]")[0]
                ),
                2000 + len("... (contexto truncado)"),
            )

    def test_parse_skill_frontmatter_valid(self) -> None:
        content = """---
name: test_skill
description: A test skill
---
body"""
        name, desc = skills.parse_skill_frontmatter(content)
        self.assertEqual(name, "test_skill")
        self.assertEqual(desc, "A test skill")

    def test_parse_skill_frontmatter_missing_opening(self) -> None:
        content = "name: test\n---\nbody"
        with self.assertRaises(ValueError):
            skills.parse_skill_frontmatter(content)

    def test_parse_skill_frontmatter_missing_closing(self) -> None:
        content = "---\nname: test\nbody"
        with self.assertRaises(ValueError):
            skills.parse_skill_frontmatter(content)

    def test_get_skill_body_with_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_path = Path(temp_dir) / "SKILL.md"
            skill_path.write_text(
                "---\nname: test\n---\nbody content", encoding="utf-8"
            )
            body = skills.get_skill_body(skill_path)
            self.assertEqual(body, "body content")

    def test_get_skill_body_malformed_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_path = Path(temp_dir) / "SKILL.md"
            skill_path.write_text("---\nname: test\nmalformed", encoding="utf-8")
            body = skills.get_skill_body(skill_path)
            self.assertEqual(body, "---\nname: test\nmalformed")


class CliTests(unittest.TestCase):
    def test_run_command_uses_project_root(self) -> None:
        fake_result = types.SimpleNamespace(returncode=9)
        with mock.patch.object(
            cli.subprocess, "run", return_value=fake_result
        ) as run_mock:
            self.assertEqual(cli.run_command(["python3", "--version"]), 9)
        run_mock.assert_called_once_with(["python3", "--version"], cwd=cli.ROOT)

    def test_cmd_add(self) -> None:
        args = argparse.Namespace(content="ideia", model=None)
        with (
            mock.patch.object(
                cli, "VAULT_NOTES", new_callable=mock.MagicMock
            ) as vault_notes_mock,
            mock.patch.object(
                cli, "build_prompt", return_value="prompt"
            ) as prompt_mock,
            mock.patch.object(cli, "ask", return_value="response") as ask_mock,
            mock.patch("builtins.print") as print_mock,
        ):
            # Make VAULT_NOTES.exists() return False to trigger fallback
            vault_notes_mock.exists.return_value = False
            self.assertEqual(cli.cmd_add(args), 0)
        prompt_mock.assert_called_once_with(
            "brain_orchestrator", "ideia", str(cli.NOTES_DIR)
        )
        ask_mock.assert_called_once_with("prompt", None)
        # Check that the response was printed (among other feedback messages)
        print_mock.assert_any_call("response")

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
            mock.patch.object(
                cli, "build_prompt", return_value="refine-prompt"
            ) as prompt_mock,
            mock.patch.object(cli, "ask", return_value="response") as ask_mock,
            mock.patch("builtins.print") as print_mock,
        ):
            self.assertEqual(
                cli.cmd_refine(
                    argparse.Namespace(file=None, instruction=None, model=None)
                ),
                0,
            )
        prompt_mock.assert_called_once_with(
            "note_refinement",
            "Refinar as notas em vault/notes/",
            str(cli.NOTES_DIR),
        )
        ask_mock.assert_called_once_with("refine-prompt", None)
        print_mock.assert_called_once_with("response")

        with (
            mock.patch.object(
                cli, "build_prompt", return_value="file-refine-prompt"
            ) as prompt_mock_2,
            mock.patch.object(cli, "ask", return_value="response2") as ask_mock_2,
            mock.patch("builtins.print") as print_mock_2,
        ):
            self.assertEqual(
                cli.cmd_refine(
                    argparse.Namespace(
                        file="vault/notes/comando-cat.md",
                        instruction=None,
                        model=None,
                    )
                ),
                0,
            )
        prompt_mock_2.assert_called_once_with(
            "note_refinement",
            "Refinar a nota em vault/notes/comando-cat.md",
            "vault/notes/comando-cat.md",
        )
        ask_mock_2.assert_called_once_with("file-refine-prompt", None)
        print_mock_2.assert_called_once_with("response2")

        with (
            mock.patch.object(
                cli, "build_prompt", return_value="custom-refine-prompt"
            ) as prompt_mock_3,
            mock.patch.object(cli, "ask", return_value="response3") as ask_mock_3,
            mock.patch("builtins.print") as print_mock_3,
        ):
            self.assertEqual(
                cli.cmd_refine(
                    argparse.Namespace(
                        file="vault/notes/comando-cat.md",
                        instruction="Refinar so a introducao",
                        model=None,
                    )
                ),
                0,
            )
        prompt_mock_3.assert_called_once_with(
            "note_refinement",
            "Refinar so a introducao",
            "vault/notes/comando-cat.md",
        )
        ask_mock_3.assert_called_once_with("custom-refine-prompt", None)
        print_mock_3.assert_called_once_with("response3")

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

        with mock.patch.object(cli, "build_prompt", return_value="run-prompt"):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    cli.cmd_skills_run(
                        argparse.Namespace(
                            name="demo",
                            instruction="instrucao",
                            target="alvo",
                            dry_run=True,
                            model=None,
                        )
                    ),
                    0,
                )
            self.assertEqual(stdout.getvalue().strip(), "run-prompt")

        with (
            mock.patch.object(cli, "build_prompt", return_value="run-prompt"),
            mock.patch.object(cli, "ask", return_value="response") as ask_mock,
            mock.patch("builtins.print") as print_mock,
        ):
            self.assertEqual(
                cli.cmd_skills_run(
                    argparse.Namespace(
                        name="demo",
                        instruction="instrucao",
                        target="alvo",
                        dry_run=False,
                        model=None,
                    )
                ),
                0,
            )
            ask_mock.assert_called_once_with("run-prompt", None)
            print_mock.assert_called_once_with("response")

    def test_main_dispatches_add_and_search(self) -> None:
        with mock.patch.object(sys, "argv", ["brain", "add", "uma", "ideia"]):
            with mock.patch.object(cli, "cmd_add", return_value=21) as add_mock:
                self.assertEqual(cli.main(), 21)
            add_args = add_mock.call_args.args[0]
            self.assertEqual(add_args.content, "uma ideia")

        with mock.patch.object(
            sys, "argv", ["brain", "add", "uma", "ideia", "--modal", "ollama:qwen3.5"]
        ):
            with mock.patch.object(cli, "cmd_add", return_value=21) as add_mock:
                self.assertEqual(cli.main(), 21)
            add_args = add_mock.call_args.args[0]
            self.assertEqual(add_args.content, "uma ideia")
            self.assertEqual(add_args.model, "ollama:qwen3.5")

        with mock.patch.object(sys, "argv", ["brain", "search", "minha", "busca"]):
            with mock.patch.object(cli, "cmd_search", return_value=22) as search_mock:
                self.assertEqual(cli.main(), 22)
            search_args = search_mock.call_args.args[0]
            self.assertEqual(search_args.query, "minha busca")

    def test_cmd_eval(self) -> None:
        args = argparse.Namespace(
            eval_set="test.json",
            skill="test_skill",
            description=None,
            num_workers=10,
            timeout=30,
            runs_per_query=3,
            trigger_threshold=0.5,
            model=None,
            verbose=False,
        )
        fake_result = types.SimpleNamespace(returncode=0)
        with mock.patch("subprocess.run", return_value=fake_result) as run_mock:
            self.assertEqual(cli.cmd_eval(args), 0)
        run_mock.assert_called_once()
        cmd = run_mock.call_args[0][0]
        self.assertIn(sys.executable, cmd)
        self.assertIn(str(cli.ROOT / "skills" / "scripts" / "run_eval.py"), cmd)
        self.assertIn("--eval-set", cmd)
        self.assertIn("test.json", cmd)
        self.assertIn("--skill-path", cmd)
        self.assertIn(str(cli.SKILLS_DIR / "test_skill"), cmd)

    def test_cmd_eval_with_optional_args(self) -> None:
        args = argparse.Namespace(
            eval_set="test.json",
            skill="test_skill",
            description="test desc",
            num_workers=10,
            timeout=30,
            runs_per_query=3,
            trigger_threshold=0.5,
            model="ollama:mistral",
            verbose=True,
        )
        fake_result = types.SimpleNamespace(returncode=0)
        with mock.patch("subprocess.run", return_value=fake_result) as run_mock:
            self.assertEqual(cli.cmd_eval(args), 0)
        run_mock.assert_called_once()
        cmd = run_mock.call_args[0][0]
        self.assertIn("--description", cmd)
        self.assertIn("test desc", cmd)
        self.assertIn("--model", cmd)
        self.assertIn("ollama:mistral", cmd)
        self.assertIn("--verbose", cmd)

    def test_parse_skill_frontmatter_multiline_tabs(self) -> None:
        content = """---
name: test_skill
description: |
	This is a multiline
	description with tabs
---
body"""
        name, desc = skills.parse_skill_frontmatter(content)
        self.assertEqual(name, "test_skill")
        self.assertEqual(desc, "This is a multiline description with tabs")

    def test_parse_skill_with_various_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_path = Path(temp_dir) / "SKILL.md"
            skill_path.write_text(
                "---\nname: test_skill\ndescription: A test skill\n---\n- tool: use hammer\n- constraint: no nails\n- instruction here\n1. First step\n2. Second step\n",
                encoding="utf-8",
            )
            contract = skills.parse_skill(skill_path)
            self.assertIn("tool: use hammer", contract["tools"])
            self.assertIn("constraint: no nails", contract["constraints"])
            self.assertIn("instruction here", contract["instructions"])
            self.assertIn("1. First step", contract["instructions"])
            self.assertIn("2. Second step", contract["instructions"])

    def test_build_prompt_generic_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            context = root / "context.md"
            context.write_text("contexto", encoding="utf-8")

            with mock.patch.object(skills, "CONTEXT_FILE", context):
                prompt = skills.build_prompt(None, "fazer algo", "vault/notes")

            self.assertIn("[CONTEXTO GLOBAL]", prompt)
            self.assertIn("[GENERIC TASK]", prompt)
            self.assertIn("[ALVO DA EXECUÇÃO]", prompt)
            self.assertIn("[INSTRUÇÃO ESPECÍFICA]", prompt)

    def test_cmd_eval_run(self) -> None:
        eval_set_data = [
            {
                "id": "test1",
                "instruction": "Test instruction",
                "target": "test target",
                "expectations": "Good output",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_set_path = Path(temp_dir) / "eval_set.json"
            eval_set_path.write_text(json.dumps(eval_set_data), encoding="utf-8")

            args = argparse.Namespace(
                eval_set=str(eval_set_path), skill="test_skill", model=None
            )
            fake_summary = {"eval_id": "test1", "run_id": 123}

            with (
                mock.patch.object(
                    cli, "ensure_skill_exists", return_value=Path("/tmp/test_skill")
                ),
                mock.patch.object(
                    cli, "run_eval_pipeline", return_value=fake_summary
                ) as pipeline_mock,
                mock.patch.object(cli, "ROOT", Path("/home/jonas/HD/brain_system")),
                mock.patch("builtins.print") as print_mock,
            ):
                self.assertEqual(cli.cmd_eval_run(args), 0)
            pipeline_mock.assert_called_once()
            print_mock.assert_called_once_with(
                "Eval completo. Resumo salvo em /home/jonas/HD/brain_system/runs/eval_summary_test_skill.json"
            )

    def test_cmd_improve(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            analysis_path = Path(temp_dir) / "analysis.json"
            analysis_path.write_text('{"summary": "test"}', encoding="utf-8")

            args = argparse.Namespace(
                skill="test_skill",
                analysis=str(analysis_path),
                model=None,
                version=None,
            )
            fake_result = {
                "skill_path": "/tmp/improved_skill.md",
                "history_path": "/tmp/history.json",
            }

            with (
                mock.patch.object(cli, "ensure_skill_exists"),
                mock.patch.object(
                    cli, "improve_skill", return_value=fake_result
                ) as improve_mock,
                mock.patch("builtins.print") as print_mock,
            ):
                self.assertEqual(cli.cmd_improve(args), 0)
            improve_mock.assert_called_once_with(
                "test_skill", analysis_path, model=None, version=None
            )
            print_mock.assert_called_once_with(
                "Skill aprimorada salva em /tmp/improved_skill.md"
            )

    def test_cmd_eval_run_invalid_eval_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_set_path = Path(temp_dir) / "eval_set.json"
            eval_set_path.write_text('{"not": "a list"}', encoding="utf-8")

            args = argparse.Namespace(
                eval_set=str(eval_set_path), skill="test_skill", model=None
            )
            with self.assertRaises(SystemExit):
                cli.cmd_eval_run(args)

    def test_cmd_eval_run_invalid_item(self) -> None:
        eval_set_data = ["not a dict"]
        with tempfile.TemporaryDirectory() as temp_dir:
            eval_set_path = Path(temp_dir) / "eval_set.json"
            eval_set_path.write_text(json.dumps(eval_set_data), encoding="utf-8")

            args = argparse.Namespace(
                eval_set=str(eval_set_path), skill="test_skill", model=None
            )
            with (
                mock.patch.object(
                    cli, "ensure_skill_exists", return_value=Path("/tmp/test_skill")
                ),
                mock.patch.object(cli, "run_eval_pipeline", return_value={}),
                mock.patch.object(cli, "ROOT", Path("/tmp")),
            ):
                self.assertEqual(cli.cmd_eval_run(args), 0)  # Should skip invalid item
