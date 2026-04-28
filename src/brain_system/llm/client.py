from __future__ import annotations

import os
import subprocess
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("BRAIN_MODEL", "openai")

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


class LocalClient(LLMClient):
    def __init__(self, model: str | None = None):
        super().__init__(model)

    def run(self, prompt: str) -> str:
        if self.model.startswith("ollama:"):
            model_name = self.model.split(":", 1)[1]
        elif self.model.startswith("local:"):
            model_name = self.model.split(":", 1)[1]
        else:
            raise ValueError("Local model must be specified as ollama:<model> or local:<model>")

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
    target = model or os.environ.get("BRAIN_MODEL", "openai")
    if target.startswith("openai"):
        return OpenAIClient(target)
    if target.startswith("claude"):
        return ClaudeClient(target)
    if target.startswith("ollama:") or target.startswith("local:"):
        return LocalClient(target)
    raise ValueError(
        "Modelo não suportado. Use 'openai', 'claude', 'ollama:<model>' ou 'local:<model>'"
    )
