from __future__ import annotations

import json
from pathlib import Path

from ..llm_adapter import ask


def compare(
    output_a: Path,
    output_b: Path,
    eval_prompt: str,
    model: str | None = None,
    save_path: Path | None = None,
) -> dict[str, str]:
    if save_path is None:
        save_path = output_a.parent.parent / "comparison.json"

    text_a = output_a.read_text(encoding="utf-8")
    text_b = output_b.read_text(encoding="utf-8")

    prompt = (
        "Você é um comparador cego de duas saídas geradas por agentes.\n"
        "Use apenas os critérios fornecidos no prompt de avaliação para decidir qual saída é melhor.\n"
        "Responda com um JSON contendo {\"winner\": \"A\"|\"B\", \"reason\": \"<explicação>\"}.\n\n"
        "Critérios:\n"
        + eval_prompt
        + "\n\nSaída A:\n"
        + text_a
        + "\n\nSaída B:\n"
        + text_b
    )

    result = ask(prompt, model)
    comparison = {
        "eval_prompt": eval_prompt,
        "winner": "unknown",
        "result": result.strip(),
    }
    save_path.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    return comparison
