from __future__ import annotations

import json
from pathlib import Path

from ..llm_adapter import ask


def analyze(
    winner_transcript: Path,
    loser_transcript: Path,
    skill_path: Path,
    model: str | None = None,
    save_path: Path | None = None,
) -> dict[str, str]:
    if save_path is None:
        save_path = winner_transcript.parent / "analysis.json"

    winner_text = winner_transcript.read_text(encoding="utf-8")
    loser_text = loser_transcript.read_text(encoding="utf-8")
    skill_text = skill_path.read_text(encoding="utf-8")

    prompt = (
        "Você é um analista de agentes. Compare o vencedor e o perdedor, e explique onde o agente vencedor se saiu melhor.\n"
        "Use o texto da skill para contextualizar o comportamento esperado.\n"
        "Retorne um JSON com {\"summary\": \"<resumo>\", \"recommendation\": \"<melhoria>\"}.\n\n"
        "Skill:\n"
        + skill_text
        + "\n\nTranscrição vencedora:\n"
        + winner_text
        + "\n\nTranscrição perdedora:\n"
        + loser_text
    )

    result = ask(prompt, model)
    analysis = {
        "skill_path": str(skill_path),
        "analysis": result.strip(),
    }
    save_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    return analysis
