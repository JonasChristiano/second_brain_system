from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..llm_adapter import ask
from ..paths import ROOT
from ..skills import build_prompt, load_skill, parse_skill


def execute_skill(
    skill_name: str | None,
    instruction: str | None,
    target: str | None,
    model: str | None,
    run_dir: Path,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir = run_dir
    outputs_dir = run_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    if skill_name:
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

    start = time.time()
    response = ask(prompt, model)
    elapsed = time.time() - start

    transcript_path = transcripts_dir / "transcript.md"
    transcript_content = [
        f"# Transcript",
        f"skill: {skill_contract.get('name')}",
        f"model: {model or 'default'}",
        "",
        "## Prompt",
        prompt,
        "",
        "## Response",
        response,
    ]
    transcript_path.write_text("\n".join(transcript_content), encoding="utf-8")

    output_path = outputs_dir / "output.txt"
    output_path.write_text(response, encoding="utf-8")

    metrics = {
        "skill": skill_contract.get("name"),
        "model": model,
        "duration_seconds": elapsed,
        "output_path": str(output_path.name),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return {
        "transcript": str(transcript_path),
        "output": str(output_path),
        "metrics": metrics,
        "skill_contract": skill_contract,
    }
