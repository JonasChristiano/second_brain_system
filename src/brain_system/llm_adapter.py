from __future__ import annotations

from .llm.client import get_client


def ask(prompt: str, model: str | None = None) -> str:
    """Envia um prompt para um LLM provider-agnóstico e retorna a resposta."""
    client = get_client(model)
    return client.run(prompt)


def stream_ask(prompt: str, model: str | None = None):
    """Versão futura para streaming. Por enquanto, apenas chama ask."""
    return ask(prompt, model)
