from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from .llm_adapter import ask
from .agents.improver import improve_skill
from .agents.pipeline import run_eval_pipeline
from .paths import NOTES_DIR, ROOT, SKILLS_DIR
from .skills import build_prompt, ensure_skill_exists, list_skills, load_text, slugify


def run_command(args: list[str]) -> int:
    result = subprocess.run(args, cwd=ROOT)
    return result.returncode


def cmd_add(args: argparse.Namespace) -> int:
    prompt = build_prompt("brain_orchestrator", args.content, str(NOTES_DIR))
    response = ask(prompt, args.model)
    print(response)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "rag/search.py", args.query])


def cmd_index(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "rag/indexer.py"])


def cmd_watch(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "whatcher.py"])


def cmd_restructure(args: argparse.Namespace) -> int:
    return run_command([sys.executable, "restructure.py"])


def cmd_refine(args: argparse.Namespace) -> int:
    target = args.file or str(NOTES_DIR)

    if args.instruction:
        instruction = args.instruction
    elif args.file:
        instruction = f"Refinar a nota em {args.file}"
    else:
        instruction = "Refinar as notas em vault/notes/"

    prompt = build_prompt("note_refinement", instruction, target)
    response = ask(prompt, args.model)
    print(response)
    return 0


def cmd_skills_list(args: argparse.Namespace) -> int:
    skills = list_skills()
    if not skills:
        print("Nenhuma skill encontrada.")
        return 0

    for skill_path in skills:
        print(skill_path.name)
    return 0


def cmd_skills_show(args: argparse.Namespace) -> int:
    skill_path = ensure_skill_exists(args.name)
    print(load_text(skill_path))
    return 0


def cmd_skills_new(args: argparse.Namespace) -> int:
    skill_id = slugify(args.name)
    skill_dir = SKILLS_DIR / skill_id
    skill_path = skill_dir / "SKILL.md"

    if skill_path.exists():
        raise SystemExit(f"A skill '{skill_id}' ja existe.")

    skill_dir.mkdir(parents=True, exist_ok=True)

    template = "\n".join(
        [
            "---",
            f"name: {skill_id}",
            f"description: {args.goal or 'Descrever o objetivo principal da skill'}",
            "---",
            "",
            f"id: {skill_id}",
            f"title: {args.name.strip()}",
            "version: 1.0",
            "last_updated: 2026-04-23",
            "scope: vault/notes",
            "",
            "Objetivo:",
            f"- {args.goal or 'Descrever o objetivo principal da skill'}",
            "",
            "Quando usar:",
            "- descrever os cenarios em que a skill deve ser aplicada",
            "",
            "Passos:",
            "1. descrever a sequencia principal de execucao",
            "",
            "Regras:",
            "- definir comportamento principal",
            "- indicar limites e cuidados",
            "- apontar formato de saida esperado",
            "",
            "Saida esperada:",
            "- descrever o resultado ideal da execucao",
        ]
    )

    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(template + "\n", encoding="utf-8")
    print(f"Skill criada em {skill_path.relative_to(ROOT)}")
    return 0


def cmd_skills_run(args: argparse.Namespace) -> int:
    prompt = build_prompt(args.name, args.instruction, args.target)

    if args.dry_run:
        print(prompt)
        return 0

    response = ask(prompt, args.model)
    print(response)
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    import sys
    from pathlib import Path
    import subprocess

    # Run the eval script directly
    script_path = ROOT / "skills" / "scripts" / "run_eval.py"
    cmd = [
        sys.executable,
        str(script_path),
        "--eval-set",
        args.eval_set,
        "--skill-path",
        str(SKILLS_DIR / args.skill),
        "--num-workers",
        str(args.num_workers),
        "--timeout",
        str(args.timeout),
        "--runs-per-query",
        str(args.runs_per_query),
        "--trigger-threshold",
        str(args.trigger_threshold),
    ]
    if args.description:
        cmd.extend(["--description", args.description])
    if args.model:
        cmd.extend(["--model", args.model])
    if args.verbose:
        cmd.append("--verbose")

    return subprocess.run(cmd, cwd=ROOT).returncode


def cmd_eval_run(args: argparse.Namespace) -> int:
    eval_set_data = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    if not isinstance(eval_set_data, list):
        raise SystemExit("O eval set deve ser uma lista de itens JSON.")

    skill_dir = SKILLS_DIR / args.skill
    ensure_skill_exists(args.skill)

    summaries = []
    for item in eval_set_data:
        if not isinstance(item, dict):
            continue
        summary = run_eval_pipeline(skill_dir, item, model=args.model)
        summaries.append(summary)

    output_path = ROOT / "runs" / f"eval_summary_{args.skill}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    print(f"Eval completo. Resumo salvo em {output_path}")
    return 0


def cmd_improve(args: argparse.Namespace) -> int:
    ensure_skill_exists(args.skill)
    analysis_path = Path(args.analysis)
    if not analysis_path.exists():
        raise SystemExit(f"Arquivo de análise não encontrado: {analysis_path}")

    result = improve_skill(args.skill, analysis_path, model=args.model, version=args.version)
    print(f"Skill aprimorada salva em {result['skill_path']}")
    return 0


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
    add_parser.add_argument(
        "--model", help="Modelo LLM a usar (codex ou ollama:modelo)."
    )
    add_parser.set_defaults(
        func=lambda ns: cmd_add(
            argparse.Namespace(
                content=" ".join(ns.content), model=getattr(ns, "model", None)
            )
        )
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

    restructure_parser = subparsers.add_parser(
        "restructure",
        help="Reorganiza um vault existente para a estrutura padrao do projeto.",
    )
    restructure_parser.set_defaults(func=cmd_restructure)

    watch_parser = subparsers.add_parser(
        "watch", help="Ativa auto-commit para mudancas no vault."
    )
    watch_parser.set_defaults(func=cmd_watch)

    refine_parser = subparsers.add_parser(
        "refine", help="Aplica a skill de refinamento nas notas."
    )
    refine_parser.add_argument(
        "file",
        nargs="?",
        help="Arquivo especifico para refinamento. Se omitido, usa vault/notes/.",
    )
    refine_parser.add_argument(
        "--instruction", help="Instrucao opcional para o refinamento."
    )
    refine_parser.add_argument(
        "--model", help="Modelo LLM a usar (codex ou ollama:modelo)."
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
        "run", help="Executa uma skill com o LLM."
    )
    skills_run.add_argument("name", help="Nome da skill.")
    skills_run.add_argument("--target", help="Caminho ou escopo principal da execucao.")
    skills_run.add_argument("--instruction", help="Instrucao complementar.")
    skills_run.add_argument(
        "--model", help="Modelo LLM a usar (codex ou ollama:modelo)."
    )
    skills_run.add_argument(
        "--dry-run", action="store_true", help="Mostra o prompt sem executar."
    )
    skills_run.set_defaults(func=cmd_skills_run)

    eval_parser = subparsers.add_parser(
        "eval", help="Avalia triggers de skills usando queries de teste."
    )
    eval_parser.add_argument(
        "--eval-set", required=True, help="Caminho para o arquivo JSON de eval set."
    )
    eval_parser.add_argument("--skill", required=True, help="Nome da skill a avaliar.")
    eval_parser.add_argument("--description", help="Descricao alternativa da skill.")
    eval_parser.add_argument(
        "--num-workers", type=int, default=10, help="Numero de workers paralelos."
    )
    eval_parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout por query em segundos."
    )
    eval_parser.add_argument(
        "--runs-per-query", type=int, default=3, help="Numero de runs por query."
    )
    eval_parser.add_argument(
        "--trigger-threshold", type=float, default=0.5, help="Limite de trigger rate."
    )
    eval_parser.add_argument("--model", help="Modelo a usar para claude -p.")
    eval_parser.add_argument("--verbose", action="store_true", help="Saida verbosa.")
    eval_parser.set_defaults(func=cmd_eval)

    eval_run_parser = subparsers.add_parser(
        "eval-run",
        help="Executa o pipeline de avaliacao de skill usando agent pipeline interno.",
    )
    eval_run_parser.add_argument(
        "--eval-set", required=True, help="Caminho para o arquivo JSON de eval set."
    )
    eval_run_parser.add_argument("--skill", required=True, help="Nome da skill a avaliar.")
    eval_run_parser.add_argument("--model", help="Modelo a usar para a avaliacao.")
    eval_run_parser.set_defaults(func=cmd_eval_run)

    improve_parser = subparsers.add_parser(
        "improve", help="Melhora uma skill a partir de uma analise de execucao."
    )
    improve_parser.add_argument("--skill", required=True, help="Nome da skill a aprimorar.")
    improve_parser.add_argument(
        "--analysis",
        required=True,
        help="Caminho para o arquivo JSON/md de analise da execucao.",
    )
    improve_parser.add_argument("--model", help="Modelo LLM a usar.")
    improve_parser.add_argument(
        "--version",
        type=int,
        help="Versao da skill melhorada (salva em skills/<skill>/v<version>/SKILL.md).",
    )
    improve_parser.set_defaults(func=cmd_improve)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)
