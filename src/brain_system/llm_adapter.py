from __future__ import annotations
import logging

from .llm.client import get_client

logger = logging.getLogger(__name__)


def ask(prompt: str, model: str | None = None) -> str:
    """Envia um prompt para um LLM provider-agnóstico e retorna a resposta."""
    logger.info(f"[LLM] Iniciando consulta - Modelo: {model or 'padrão'}")
    logger.debug(f"[LLM] Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    try:
        client = get_client(model)
        logger.debug(f"[LLM] Cliente selecionado: {type(client).__name__}")

        response = client.run(prompt)
        logger.info("[LLM] Consulta concluída com sucesso")
        logger.debug(
            f"[LLM] Resposta: {response[:100]}{'...' if len(response) > 100 else ''}"
        )

        return response
    except Exception as e:
        logger.error(f"[LLM] Erro na consulta: {e}", exc_info=True)
        raise


def stream_ask(prompt: str, model: str | None = None):
    """Versão futura para streaming. Por enquanto, apenas chama ask."""
    logger.info(f"[LLM] Iniciando consulta streaming - Modelo: {model or 'padrão'}")
    return ask(prompt, model)
