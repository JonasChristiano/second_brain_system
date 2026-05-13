from __future__ import annotations

import os
import subprocess
import logging
from pathlib import Path
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("BRAIN_MODEL", "gemini")

    @abstractmethod
    def run(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, model: str | None = None):
        super().__init__(model)
        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("OpenAI client is not installed") from exc

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for OpenAIClient")

        self.openai = openai
        self.openai.api_key = api_key

    def run(self, prompt: str) -> str:
        model_name = "gpt-3.5-turbo"
        if ":" in self.model:
            _, model_name = self.model.split(":", 1)
        response = self.openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()


class ClaudeClient(LLMClient):
    def __init__(self, model: str | None = None):
        super().__init__(model)
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError("Anthropic client is not installed") from exc

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required for ClaudeClient")

        self.anthropic = anthropic
        self.client = anthropic.Client(api_key)

    def run(self, prompt: str) -> str:
        model_name = "claude-2"
        if ":" in self.model:
            _, model_name = self.model.split(":", 1)
        response = self.client.completions.create(
            model=model_name,
            prompt=prompt,
            max_tokens_to_sample=1024,
        )
        return response.completion.strip()


class GeminiClient(LLMClient):
    def __init__(self, model: str | None = None):
        super().__init__(model)
        self.use_genai = True
        self.genai_lib = None
        self.requests = None

        # Tentar importar google-genai
        try:
            from google import genai

            self.genai_lib = genai
        except ImportError:
            self.use_genai = False

        # Tentar importar requests como fallback
        try:
            import requests

            self.requests = requests
        except ImportError:
            if not self.use_genai:
                raise RuntimeError(
                    "Nem google-genai nem requests estão instalados para Gemini"
                )

        # Suporta tanto GEMINI_API_KEY quanto o padrão GOOGLE_API_KEY
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            # Tentar carregar do .env se não estiver definido
            try:
                from dotenv import load_dotenv

                # Carregar do diretório do projeto
                project_root = Path(__file__).parent.parent.parent
                env_path = project_root / ".env"
                load_dotenv(env_path)
                api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get(
                    "GOOGLE_API_KEY"
                )
            except ImportError:
                pass
        if not api_key:
            raise RuntimeError(
                "Configuração ausente: GEMINI_API_KEY ou GOOGLE_API_KEY é obrigatória. "
                "Defina a chave no seu ambiente: export GEMINI_API_KEY='sua-chave'"
            )

        self.api_key = api_key
        if self.use_genai:
            self.client = self.genai_lib.Client(api_key=api_key)

    def run(self, prompt: str) -> str:
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        if ":" in self.model:
            _, model_name = self.model.split(":", 1)

        # Tentar usar google-genai primeiro
        if self.use_genai:
            try:
                response = self.client.models.generate_content(
                    model=model_name, contents=prompt
                )
                return response.text.strip()
            except Exception as e:
                # Verificar se é erro de segurança - não tentar fallback
                error_str = str(e).lower()
                if (
                    "blocked" in error_str
                    or "safety" in error_str
                    or "content" in error_str
                ):
                    raise RuntimeError(
                        f"Gemini falhou ao retornar texto (possível bloqueio de segurança): {str(e)}"
                    ) from e

                # Se falhar por outro motivo, tentar com requests como fallback
                if self.requests:
                    return self._run_with_requests(prompt, model_name)
                else:
                    raise RuntimeError(
                        f"Gemini falhou com google-genai e requests não disponível: {str(e)}"
                    ) from e

        # Fallback para requests
        if self.requests:
            return self._run_with_requests(prompt, model_name)

        raise RuntimeError("Nenhum método disponível para Gemini")

    def _run_with_requests(self, prompt: str, model_name: str) -> str:
        """Fallback usando requests para API REST."""
        base_url = os.environ.get(
            "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"
        )
        url = f"{base_url}/models/{model_name}:generateContent?key={self.api_key}"

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        try:
            response = self.requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Verificar se há erro na resposta JSON
            if "error" in data:
                error = data["error"]
                error_code = error.get("code", "Unknown")
                error_message = error.get("message", "Unknown error")
                raise RuntimeError(
                    f"Erro da API Gemini ({error_code}): {error_message}"
                )

            # Verificar se há candidatos na resposta
            if "candidates" in data and data["candidates"]:
                candidate = data["candidates"][0]

                # Verificar se há conteúdo bloqueado
                if (
                    "finishReason" in candidate
                    and candidate["finishReason"] == "SAFETY"
                ):
                    raise RuntimeError(
                        "Conteúdo bloqueado por filtros de segurança do Gemini"
                    )

                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0]["text"]
                    if text and text.strip():
                        return text.strip()

            # Resposta inesperada
            raise RuntimeError(f"Resposta inesperada da API Gemini: {data}")

        except self.requests.exceptions.HTTPError as e:
            # Erros HTTP específicos
            if e.response.status_code == 400:
                raise RuntimeError(
                    "Erro 400: Requisição inválida para Gemini API"
                ) from e
            elif e.response.status_code == 401:
                raise RuntimeError("Erro 401: Chave API inválida ou expirada") from e
            elif e.response.status_code == 403:
                raise RuntimeError("Erro 403: Acesso negado à API Gemini") from e
            elif e.response.status_code == 404:
                raise RuntimeError(
                    f"Erro 404: Modelo '{model_name}' não encontrado"
                ) from e
            elif e.response.status_code == 429:
                raise RuntimeError(
                    "Erro 429: Limite de requisições excedido. Tente novamente mais tarde"
                ) from e
            elif e.response.status_code == 500:
                raise RuntimeError("Erro 500: Erro interno do servidor Gemini") from e
            elif e.response.status_code == 503:
                raise RuntimeError(
                    "Erro 503: Serviço Gemini indisponível. Tente novamente mais tarde"
                ) from e
            else:
                raise RuntimeError(
                    f"Erro HTTP {e.response.status_code} na API Gemini"
                ) from e

        except self.requests.exceptions.Timeout as e:
            raise RuntimeError("Timeout na requisição para Gemini API") from e

        except self.requests.exceptions.ConnectionError as e:
            raise RuntimeError("Erro de conexão com a API Gemini") from e

        except ValueError as e:
            raise RuntimeError(
                f"Erro ao processar resposta JSON da API Gemini: {str(e)}"
            ) from e

        except Exception as e:
            raise RuntimeError(f"Erro inesperado na API Gemini: {str(e)}") from e


class LocalClient(LLMClient):
    def __init__(self, model: str | None = None):
        super().__init__(model)

    def run(self, prompt: str) -> str:
        if self.model.startswith("ollama:"):
            model_name = self.model[6:]
        elif self.model.startswith("local:"):
            model_name = self.model[5:]
        else:
            raise ValueError(
                "Local model must be specified as ollama:<model> or local:<model>"
            )
        print(f"Executando modelo local '{model_name}' com prompt: {prompt[:50]}...")

        try:
            # Local models can take longer, use generous timeout
            # Default 300s for quick models, but allow up to 30min via env var
            timeout = int(os.environ.get("BRAIN_LLM_TIMEOUT", "600"))
            result = subprocess.run(
                ["ollama", "run", model_name],
                input=prompt,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            logger.error("Local LLM failed: %s", exc)
            raise RuntimeError("Local LLM execution failed") from exc
        except FileNotFoundError as exc:
            raise RuntimeError("O comando 'ollama' não foi encontrado no PATH") from exc


def get_client(model: str | None = None) -> LLMClient:
    target = model or os.environ.get("BRAIN_MODEL", "gemini")

    logger.debug(f"Inicializando LLM Client para: {target}")

    if target.startswith("openai"):
        return OpenAIClient(target)
    if target.startswith("claude"):
        return ClaudeClient(target)
    if target.startswith("gemini"):
        return GeminiClient(target)
    if target.startswith("ollama:") or target.startswith("local:"):
        return LocalClient(target)
    raise ValueError(
        "Modelo não suportado. Use 'openai', 'claude', 'gemini', 'ollama:<model>' ou 'local:<model>'"
    )
