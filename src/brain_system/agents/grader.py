from __future__ import annotations

import json
from pathlib import Path

from ..llm_adapter import ask


def grade(
    expectations: str,
    transcript_path: Path,
    outputs_dir: Path,
    model: str | None = None,
    save_path: Path | None = None,
) -> dict[str, str]:
    if save_path is None:
        save_path = outputs_dir.parent / "grading.json"

    transcript = transcript_path.read_text(encoding="utf-8")
    output_path = outputs_dir / "output.txt"
    output = output_path.read_text(encoding="utf-8")

    prompt = (
        "Você é um avaliador de saída de agente.\n"
        "Avalie a resposta abaixo segundo as expectativas fornecidas e responda com um JSON simples contendo {\"score\": \"<valor>\", \"comment\": \"<comentario>\"}.\n\n"
        "Expectativas:\n"
        + expectations
        + "\n\nSaída do agente:\n"
        + output
        + "\n\nTranscrição:\n"
        + transcript
    )

    result = ask(prompt, model)
    grading = {
        "expectations": expectations,
        "output": output,
        "grading": result.strip(),
    }
    save_path.write_text(json.dumps(grading, indent=2), encoding="utf-8")
    return grading
