from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import os
import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logging.warning("python-dotenv não instalado, continuando sem carregar .env")
    pass  # python-dotenv not installed, continue without .env loading

from .help import HelpSystem, cmd_help
from .llm_adapter import ask
from .agents.improver import improve_skill
from .agents.pipeline import run_eval_pipeline
from .paths import NOTES_DIR, ROOT, SKILLS_DIR, VAULT_NOTES
from .skills import build_prompt, ensure_skill_exists, list_skills, load_text, slugify

# Second Brain Core modules
from .core.ingestion import ingest_note
from .core.search import smart_search
from .core.optimizer import optimize_vault, cleanup_vault


def run_command(args: list[str]) -> int:
    result = subprocess.run(args, cwd=ROOT)
    logger.info(f"[COMMAND] Executado: {args}")
    stdout = getattr(result, "stdout", None)
    stderr = getattr(result, "stderr", None)
    if stdout is not None:
        logger.info(f"[COMMAND] Saida: #{stdout}#")
    if stderr is not None:
        logger.info(f"[COMMAND] Erro: #{stderr}#")
    return result.returncode


def cmd_add(args: argparse.Namespace) -> int:
    """Add and process a new note using Second Brain ingestion pipeline."""
    logger.info("[CLI] Comando 'add' iniciado")

    # Handle both old format (string) and new format (list)
    content = args.content
    if isinstance(content, list):
        content = " ".join(content)

    # Set timeout for local LLM if provided
    timeout = getattr(args, "timeout", None)
    if timeout:
        os.environ["BRAIN_LLM_TIMEOUT"] = str(timeout)
        logger.debug(f"[CLI] Timeout configurado: {timeout}s")

    MODEL = getattr(args, "model", None) or os.environ.get("BRAIN_MODEL", "qwen3:4b")

    logger.info(
        f"[CLI] Adicionando nota - Modelo: {MODEL}, Tamanho: {len(content)} chars"
    )
    logger.debug(
        f"[CLI] Conteúdo: {content[:100]}{'...' if len(content) > 100 else ''}"
    )

    print("🧠 Iniciando processamento da nota...")
    print(f"   Conteúdo: {content[:50]}{'...' if len(content) > 50 else ''}")
    print(f"   Modelo: {MODEL}")
    if timeout:
        print(f"   Timeout: {timeout}s")

    # Try to use new Second Brain pipeline, but fallback to old behavior
    try:
        # Check if we should use new pipeline (vault exists)
        vault_notes = VAULT_NOTES
        if not vault_notes.exists() or not (VAULT_NOTES.parent / "inbox").exists():
            # Fallback to old behavior when vault structure doesn't exist
            raise FileNotFoundError("Vault structure not found")

        logger.info("[CLI] Usando pipeline moderno de ingestão")
        print("\n📝 Salvando nota na inbox...")
        result = ingest_note(
            content=content,
            title=getattr(args, "title", None),
            model=getattr(args, "model", MODEL),
            auto_link=not getattr(args, "no_link", False),
            auto_index=not getattr(args, "no_index", False),
        )

        if result["success"]:
            logger.info(f"[CLI] Nota adicionada com sucesso: {result['note_path']}")
            print("\n✅ Nota adicionada com sucesso!")
            print(f"   📄 Arquivo: {result['note_path']}")
            print(f"   🔄 Processos: {', '.join(result['steps'])}")
            return 0
        else:
            logger.error(f"[CLI] Erro ao adicionar nota: {result['error']}")
            print(f"\n❌ Erro ao adicionar nota: {result['error']}", file=sys.stderr)
            return 1
    except (FileNotFoundError, Exception) as e:
        # Fallback to old behavior for compatibility with existing tests
        logger.warning(f"[CLI] Vault não encontrado, usando pipeline legado: {e}")
        print("\n🔄 Usando pipeline legado (vault não encontrado)...")
        print("   Construindo prompt...")
        prompt = build_prompt("brain_orchestrator", content, str(NOTES_DIR))
        print("   Consultando LLM...")
        response = ask(prompt, args.model)
        print("\n✅ Resposta do LLM:")
        print(response)
        return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Smart search with related notes and suggestions."""
    logger.info("[CLI] Comando 'search' iniciado")

    query = args.query
    # Handle both string and list formats
    if isinstance(query, list):
        query = " ".join(query)

    logger.info(f"[CLI] Busca iniciada - Query: '{query}'")
    top_k = getattr(args, "top_k", 5)
    logger.debug(f"[CLI] Parâmetros: top_k={top_k}")

    try:
        result = smart_search(query, top_k=top_k)
        logger.info(
            f"[CLI] Busca concluída - {result.get('total_results', 0)} resultado(s)"
        )
    except Exception as e:
        logger.warning(f"[CLI] Erro na busca inteligente, usando fallback: {e}")
        result = {
            "top_notes": [],
            "related_notes": [],
            "suggested_links": [],
            "total_results": 0,
        }

    if not result["top_notes"]:
        # Fallback para o comportamento legado quando não há resultados do novo search
        logger.info("[CLI] Nenhum resultado encontrado, usando busca legado")
        return run_command([sys.executable, "rag/search.py", query])

    print(f"\n🔍 Resultado da busca: '{query}'")
    print(f"   Total: {result['total_results']} nota(s)\n")

    # Show top notes
    print("📌 Notas principais:")
    for i, note in enumerate(result["top_notes"], 1):
        relevance = (
            f"{note.get('relevance', 0.8) * 100:.0f}%"
            if note.get("relevance")
            else "N/A"
        )
        tags = f" [{', '.join(note.get('tags', []))}]" if note.get("tags") else ""
        print(f"   {i}. {note['title']} ({relevance}){tags}")
        if note.get("summary"):
            print(f"      {note['summary']}")

    # Show related notes
    if result["related_notes"]:
        print("\n🔗 Notas relacionadas:")
        for note in result["related_notes"]:
            print(f"   - {note['title']} ({note.get('reason', 'relacionada')})")

    # Show suggested links
    if result["suggested_links"]:
        print("\n💡 Links sugeridos:")
        for link in result["suggested_links"]:
            print(f"   - [[{link['to']}]] ({link.get('reason', 'sugerido')})")

    print()
    return 0


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

    result = improve_skill(
        args.skill, analysis_path, model=args.model, version=args.version
    )
    print(f"Skill aprimorada salva em {result['skill_path']}")
    return 0


def cmd_autonomous(args: argparse.Namespace) -> int:
    from .agents.autonomous import start_autonomous_mode

    start_autonomous_mode(model=args.model, max_cycles=args.max_cycles)
    return 0


def cmd_optimize(args: argparse.Namespace) -> int:
    """Optimize the entire vault through refinement, re-linking, and re-indexing."""
    print("\n🔧 Iniciando otimização do vault...")
    print("   Esta operação pode levar alguns minutos.\n")

    result = optimize_vault(
        relink=not args.no_relink,
        reindex=not args.no_reindex,
    )

    print(f"\n✅ Otimização concluída:")
    print(f"   📝 Notas refinadas: {result['refinement']['processed']}")
    print(f"   ❌ Erros: {result['refinement']['errors']}")

    if "relinking" in result:
        print(f"   🔗 Links adicionados: {result['relinking']['links_added']}")
        print(f"   📄 Notas modificadas: {result['relinking']['notes_modified']}")

    if "reindex" in result:
        status = "✓" if result["reindex"]["success"] else "✗"
        print(f"   🗂️  Re-indexação: {status}")

    print(f"\n   Total de notas: {result['total_notes']}")

    # Show cleanup option
    if args.cleanup:
        print("\n🗑️  Executando limpeza de notas antigas...")
        cleanup_result = cleanup_vault(days=args.cleanup_days)
        print(f"   Arquivadas: {cleanup_result['total']} nota(s)")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brain",
        description="CLI para orquestrar notas, skills e buscas do Brain System.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser(
        "add", help="Adiciona e processa uma nova nota via Second Brain."
    )
    add_parser.add_argument(
        "content", nargs="+", help="Conteúdo da nota a ser adicionada."
    )
    add_parser.add_argument(
        "--title", help="Título opcional para a nota (auto-gerado se omitido)."
    )
    add_parser.add_argument(
        "--model",
        default=os.environ.get("BRAIN_MODEL", "qwen3:4b"),
        help="Modelo LLM a usar (padrão: ollama:qwen3:4b).",
    )
    add_parser.add_argument(
        "--modal",
        dest="model",
        help="Alias para --model. Modelos como ollama:qwen3:4b são aceitos.",
    )
    add_parser.add_argument(
        "--no-link", action="store_true", help="Desabilita auto-linking."
    )
    add_parser.add_argument(
        "--no-index", action="store_true", help="Desabilita re-indexação automática."
    )
    add_parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout para modelos locais em segundos (padrão: 600). Útil para ollama:modelos lentos.",
    )
    add_parser.set_defaults(
        func=lambda ns: cmd_add(
            argparse.Namespace(
                content=" ".join(ns.content)
                if isinstance(ns.content, list)
                else ns.content,
                title=getattr(ns, "title", None),
                model=getattr(ns, "model", "ollama:qwen3:4b"),
                no_link=getattr(ns, "no_link", False),
                no_index=getattr(ns, "no_index", False),
                timeout=getattr(ns, "timeout", None),
            )
        )
    )

    search_parser = subparsers.add_parser(
        "search", help="Busca inteligente com notas relacionadas e sugestões."
    )
    search_parser.add_argument("query", nargs="+", help="Consulta da busca semântica.")
    search_parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Número de resultados principais (padrão: 5).",
    )
    search_parser.set_defaults(
        func=lambda ns: cmd_search(
            argparse.Namespace(
                query=" ".join(ns.query) if isinstance(ns.query, list) else ns.query,
                top_k=getattr(ns, "top_k", 5),
            )
        )
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
    eval_run_parser.add_argument(
        "--skill", required=True, help="Nome da skill a avaliar."
    )
    eval_run_parser.add_argument("--model", help="Modelo a usar para a avaliacao.")
    eval_run_parser.set_defaults(func=cmd_eval_run)

    improve_parser = subparsers.add_parser(
        "improve", help="Melhora uma skill a partir de uma analise de execucao."
    )
    improve_parser.add_argument(
        "--skill", required=True, help="Nome da skill a aprimorar."
    )
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

    autonomous_parser = subparsers.add_parser(
        "autonomous", help="Inicia o modo autônomo de operação."
    )
    autonomous_parser.add_argument(
        "--model", help="Modelo LLM a usar para operações autônomas."
    )
    autonomous_parser.add_argument(
        "--max-cycles", type=int, default=10, help="Número máximo de ciclos autônomos."
    )
    autonomous_parser.set_defaults(func=cmd_autonomous)

    help_parser = subparsers.add_parser(
        "help", help="Exibe ajuda detalhada sobre comandos e uso do Brain System."
    )
    help_parser.add_argument(
        "command_name",
        nargs="?",
        help="Comando específico para ajuda detalhada (opcional).",
    )
    help_parser.add_argument(
        "--list", action="store_true", help="Lista todos os comandos por categoria."
    )
    help_parser.add_argument(
        "--quick", action="store_true", help="Exibe referência rápida de comandos."
    )
    help_parser.add_argument(
        "--examples", action="store_true", help="Exibe guia com exemplos práticos."
    )
    help_parser.set_defaults(func=cmd_help)

    optimize_parser = subparsers.add_parser(
        "optimize",
        help="Otimiza o vault através de refinamento, relinking e re-indexação.",
    )
    optimize_parser.add_argument(
        "--no-relink", action="store_true", help="Desabilita re-linking automático."
    )
    optimize_parser.add_argument(
        "--no-reindex", action="store_true", help="Desabilita re-indexação."
    )
    optimize_parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Arquiva notas antigas durante otimização.",
    )
    optimize_parser.add_argument(
        "--cleanup-days",
        type=int,
        default=90,
        help="Dias de inatividade antes de arquivar (padrão: 90).",
    )
    optimize_parser.set_defaults(func=cmd_optimize)

    return parser


def main() -> int:
    # Configurar logging para toda a aplicação
    from .logging_config import setup_logging

    setup_logging(level=logging.INFO)

    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)
