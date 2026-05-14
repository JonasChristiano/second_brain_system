from __future__ import annotations

import json
import time
import logging
from pathlib import Path
from typing import Any

from ..infra.observability import observer
from ..llm_adapter import ask
from ..paths import ROOT
from ..rag import search as rag_search
from ..skills import build_prompt, load_skill, parse_skill

logger = logging.getLogger(__name__)


def execute_skill(
    skill_name: str | None,
    instruction: str | None,
    target: str | None,
    model: str | None,
    run_dir: Path,
) -> dict[str, Any]:
    logger.info(f"[SKILL] Executando skill: {skill_name or 'genérica'}")
    logger.debug(f"[SKILL] Modelo: {model}, Alvo: {target}, Run dir: {run_dir}")

    run_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir = run_dir
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # RAG Integration: Query relevant context
    rag_context = ""
    if instruction:
        try:
            # Simple query: use first 50 chars of instruction as query
            query = instruction[:50].strip()
            if query:
                logger.debug(f"[SKILL] Buscando contexto RAG para: '{query}'")
                results = rag_search(query)
                if results:
                    logger.info(
                        f"[SKILL] {len(results)} resultado(s) RAG encontrado(s)"
                    )
                    rag_context = "\n".join(
                        [f"- {r['content'][:200]}..." for r in results[:3]]
                    )
        except Exception as e:
            # RAG failure shouldn't break execution
            logger.warning(f"[SKILL] Erro ao buscar contexto RAG: {e}")
            pass

    if skill_name:
        logger.debug(f"[SKILL] Carregando skill: {skill_name}")
        prompt = build_prompt(skill_name, instruction, target)
        skill_contract = parse_skill(ROOT / "skills" / skill_name / "SKILL.md")
    else:
        prompt = build_prompt(None, instruction, target)
        skill_contract = {
            "name": "generic",
            "description": "Sem skill definida",
            "instructions": [],
            "tools": [],
            "constraints": [],
        }

    # Inject RAG context into prompt if available
    if rag_context:
        logger.debug("[SKILL] Injetando contexto RAG no prompt")
        prompt = f"[CONTEXTO RAG]\n{rag_context}\n\n{prompt}"

    logger.info(f"[SKILL] Consultando LLM com modelo: {model or 'padrão'}")
    start = time.time()
    response = ask(prompt, model)
    elapsed = time.time() - start
    logger.info(f"[SKILL] Resposta recebida em {elapsed:.2f}s")

    # Log execution
    run_id = observer.get_run_id()
    success = True  # Assume success unless error
    tokens = None  # TODO: extract from response if available
    observer.log_execution(
        run_id,
        skill_contract.get("name"),
        elapsed,
        tokens,
        success,
        {"model": model, "rag_context_used": bool(rag_context)},
    )

    transcript_path = transcripts_dir / "transcript.md"
    transcript_content = [
        f"# Transcript",
        f"skill: {skill_contract.get('name')}",
        f"model: {model or 'default'}",
        f"duration: {elapsed:.2f}s",
        "",
        "## Prompt",
        prompt,
        "",
        "## Response",
        response,
    ]
    transcript_path.write_text("\n".join(transcript_content), encoding="utf-8")
    logger.debug(f"[SKILL] Transcript salvo em: {transcript_path}")

    output_path = outputs_dir / "output.txt"
    output_path.write_text(response, encoding="utf-8")
    logger.debug(f"[SKILL] Output salvo em: {output_path}")

    metrics = {
        "skill": skill_contract.get("name"),
        "model": model,
        "duration_seconds": elapsed,
        "output_path": str(output_path.name),
    }
    (run_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    return {
        "transcript": str(transcript_path),
        "output": str(output_path),
        "metrics": metrics,
        "skill_contract": skill_contract,
    }
