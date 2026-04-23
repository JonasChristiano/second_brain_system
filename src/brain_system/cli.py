from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from .paths import NOTES_DIR, ROOT, SKILLS_DIR
from .skills import build_prompt, ensure_skill_exists, list_skills, load_text, slugify


def run_command(args: list[str]) -> int:
    result = subprocess.run(args, cwd=ROOT)
    return result.returncode


def ensure_codex_available() -> None:
    if shutil.which("codex"):
        return
    raise SystemExit("O comando 'codex' nao esta disponivel no PATH.")


def cmd_add(args: argparse.Namespace) -> int:
    ensure_codex_available()
    prompt = build_prompt("brain_orchestrator", args.content, str(NOTES_DIR))
    return run_command(["codex", prompt])


def cmd_search(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "rag/search.py", args.query])


def cmd_index(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "rag/indexer.py"])


def cmd_watch(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "whatcher.py"])


def cmd_refine(args: argparse.Namespace) -> int:
    ensure_codex_available()
    instruction = args.instruction or "Refinar as notas em vault/notes/"
    prompt = build_prompt("note_refinement", instruction, str(NOTES_DIR))
    return run_command(["codex", prompt])


def cmd_skills_list(args: argparse.Namespace) -> int:
    skills = list_skills()
    if not skills:
        print("Nenhuma skill encontrada.")
        return 0

    for skill_path in skills:
        print(skill_path.stem)
    return 0


def cmd_skills_show(args: argparse.Namespace) -> int:
    skill_path = ensure_skill_exists(args.name)
    print(load_text(skill_path))
    return 0


def cmd_skills_new(args: argparse.Namespace) -> int:
    skill_id = slugify(args.name)
    skill_path = SKILLS_DIR / f"{skill_id}.md"

    if skill_path.exists():
        raise SystemExit(f"A skill '{skill_id}' ja existe.")

    template = "\n".join(
        [
            f'id="{skill_id}"',
            "",
            "Objetivo:",
            f"- {args.goal or 'Descrever o objetivo principal da skill'}",
            "",
            "Regras:",
            "- definir comportamento principal",
            "- indicar limites e cuidados",
            "- apontar formato de saida esperado",
        ]
    )

    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(template + "\n", encoding="utf-8")
    print(f"Skill criada em {skill_path.relative_to(ROOT)}")
    return 0


def cmd_skills_run(args: argparse.Namespace) -> int:
    ensure_codex_available()
    prompt = build_prompt(args.name, args.instruction, args.target)

    if args.dry_run:
        print(prompt)
        return 0

    return run_command(["codex", prompt])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brain",
        description="CLI para orquestrar notas, skills e buscas do Brain System.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser(
        "add", help="Processa uma ideia via brain_orchestrator."
    )
    add_parser.add_argument(
        "content", nargs="+", help="Conteudo da ideia a ser processada."
    )
    add_parser.set_defaults(
        func=lambda ns: cmd_add(argparse.Namespace(content=" ".join(ns.content)))
    )

    search_parser = subparsers.add_parser("search", help="Busca no indice vetorial.")
    search_parser.add_argument(
        "query", nargs="+", help="Consulta a ser enviada ao RAG."
    )
    search_parser.set_defaults(
        func=lambda ns: cmd_search(argparse.Namespace(query=" ".join(ns.query)))
    )

    index_parser = subparsers.add_parser("index", help="Reconstrui o indice vetorial.")
    index_parser.set_defaults(func=cmd_index)

    watch_parser = subparsers.add_parser(
        "watch", help="Ativa auto-commit para mudancas no vault."
    )
    watch_parser.set_defaults(func=cmd_watch)

    refine_parser = subparsers.add_parser(
        "refine", help="Aplica a skill de refinamento nas notas."
    )
    refine_parser.add_argument(
        "--instruction", help="Instrucao opcional para o refinamento."
    )
    refine_parser.set_defaults(func=cmd_refine)

    skills_parser = subparsers.add_parser("skills", help="Gerencia skills locais.")
    skills_subparsers = skills_parser.add_subparsers(
        dest="skills_command", required=True
    )

    skills_list = skills_subparsers.add_parser("list", help="Lista skills disponiveis.")
    skills_list.set_defaults(func=cmd_skills_list)

    skills_show = skills_subparsers.add_parser(
        "show", help="Exibe o conteudo de uma skill."
    )
    skills_show.add_argument("name", help="Nome da skill.")
    skills_show.set_defaults(func=cmd_skills_show)

    skills_new = skills_subparsers.add_parser("new", help="Cria um template de skill.")
    skills_new.add_argument("name", help="Nome da nova skill.")
    skills_new.add_argument("--goal", help="Objetivo principal da skill.")
    skills_new.set_defaults(func=cmd_skills_new)

    skills_run = skills_subparsers.add_parser(
        "run", help="Executa uma skill com o Codex."
    )
    skills_run.add_argument("name", help="Nome da skill.")
    skills_run.add_argument("--target", help="Caminho ou escopo principal da execucao.")
    skills_run.add_argument("--instruction", help="Instrucao complementar.")
    skills_run.add_argument(
        "--dry-run", action="store_true", help="Mostra o prompt sem executar."
    )
    skills_run.set_defaults(func=cmd_skills_run)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)
