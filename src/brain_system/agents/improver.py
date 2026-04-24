from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..llm_adapter import ask
from ..paths import ROOT


def improve_skill(
    skill_name: str,
    analysis_path: Path,
    model: str | None = None,
    version: int | None = None,
) -> dict[str, str]:
    skill_dir = ROOT / "skills" / skill_name
    skill_path = skill_dir / "SKILL.md"
    history_path = skill_dir / "history.json"
    analysis = analysis_path.read_text(encoding="utf-8")
    skill_text = skill_path.read_text(encoding="utf-8")

    prompt = f"""
Você é um agente de melhoria de skills. Use a skill atual e a análise da execução para gerar uma nova versão da skill.
Mantenha o formato SKILL.md intacto e apenas melhore a descrição, instruções ou regras quando for apropriado.

Skill atual:
{skill_text}

Análise:
{analysis}

Retorne apenas o conteúdo completo do novo SKILL.md.
"""

    improved = ask(prompt, model)

    version = version or 2
    version_dir = skill_dir / f"v{version}"
    version_dir.mkdir(parents=True, exist_ok=True)
    new_path = version_dir / "SKILL.md"
    new_path.write_text(improved.strip() + "\n", encoding="utf-8")

    history = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))

    record = {
        "version": version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": model,
        "skill_path": str(new_path),
        "analysis": str(analysis_path),
    }
    history.append(record)
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return {"skill_path": str(new_path), "history_path": str(history_path)}
