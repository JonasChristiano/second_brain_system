from __future__ import annotations

import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def ask(prompt: str, model: str | None = None) -> str:
    """
    Envia um prompt para um LLM e retorna a resposta.

    Suporta 'codex' (via subprocess) e 'ollama' (via subprocess com stdin).

    Args:
        prompt: O prompt a ser enviado.
        model: O modelo a usar. Se None, usa BRAIN_MODEL ou 'codex' como padrão.

    Returns:
        A resposta do LLM como string.

    Raises:
        RuntimeError: Se o comando falhar ou o modelo não for suportado.
    """
    if model is None:
        model = os.environ.get("BRAIN_MODEL", "codex")

    if model == "codex":
        try:
            result = subprocess.run(
                ["codex", prompt],
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minutos timeout
            )
            response = result.stdout.strip()
            logger.info(f"Codex response: {response[:100]}...")
            return response
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar codex: {e}")
            raise RuntimeError(f"Falha no codex: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error("Timeout no codex")
            raise RuntimeError("Timeout ao executar codex")
        except FileNotFoundError:
            raise RuntimeError("Comando 'codex' não encontrado no PATH")

    elif model.startswith("ollama:"):
        # Ex: ollama:mistral
        ollama_model = model.split(":", 1)[1]
        try:
            result = subprocess.run(
                ["ollama", "run", ollama_model],
                input=prompt,
                capture_output=True,
                text=True,
                check=True,
                timeout=300
            )
            response = result.stdout.strip()
            logger.info(f"Ollama ({ollama_model}) response: {response[:100]}...")
            return response
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar ollama: {e}")
            raise RuntimeError(f"Falha no ollama: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error("Timeout no ollama")
            raise RuntimeError("Timeout ao executar ollama")
        except FileNotFoundError:
            raise RuntimeError("Comando 'ollama' não encontrado no PATH")

    else:
        raise ValueError(f"Modelo '{model}' não suportado. Use 'codex' ou 'ollama:<modelo>'")

def stream_ask(prompt: str, model: str | None = None):
    """
    Versão futura para streaming. Por enquanto, apenas chama ask.
    """
    return ask(prompt, model)