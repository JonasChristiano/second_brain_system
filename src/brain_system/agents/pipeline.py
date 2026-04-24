from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..paths import ROOT, SKILLS_DIR
from ..agents.comparator import compare
from ..agents.executor import execute_skill
from ..agents.grader import grade
from ..agents.analyzer import analyze
from ..skills import parse_skill


def run_eval_pipeline(skill_path: Path, eval_item: dict[str, Any], model: str | None = None) -> dict[str, Any]:
    run_id = int(time.time())
    eval_id = eval_item.get("id") or eval_item.get("name") or skill_path.name
    run_dir = ROOT / "runs" / f"eval_{eval_id}" / f"run_{run_id}"
    with_skill_dir = run_dir / "with_skill"
    without_skill_dir = run_dir / "without_skill"
    with_skill_dir.mkdir(parents=True, exist_ok=True)
    without_skill_dir.mkdir(parents=True, exist_ok=True)

    instruction = eval_item.get("instruction")
    target = eval_item.get("target")
    expectations = eval_item.get("expectations", "")
    comparator_prompt = eval_item.get(
        "comparison_prompt",
        "Escolha a melhor resposta com base nas expectativas e clareza.",
    )

    result_with = execute_skill(
        skill_path.name,
        instruction,
        target,
        model,
        with_skill_dir,
    )

    if eval_item.get("alternative_skill"):
        alternative = eval_item["alternative_skill"]
        result_without = execute_skill(
            alternative,
            instruction,
            target,
            model,
            without_skill_dir,
        )
    else:
        result_without = execute_skill(
            None,
            instruction,
            target,
            model,
            without_skill_dir,
        )

    grading_a = grade(
        expectations,
        Path(result_with["transcript"]),
        Path(result_with["output"]).parent,
        model=model,
        save_path=with_skill_dir / "grading.json",
    )
    grading_b = grade(
        expectations,
        Path(result_without["transcript"]),
        Path(result_without["output"]).parent,
        model=model,
        save_path=without_skill_dir / "grading.json",
    )

    comparison = compare(
        Path(result_with["output"]),
        Path(result_without["output"]),
        comparator_prompt,
        model=model,
        save_path=run_dir / "comparison.json",
    )

    winner = "with_skill"
    loser = "without_skill"
    analysis = analyze(
        Path(result_with["transcript"]),
        Path(result_without["transcript"]),
        skill_path,
        model=model,
        save_path=run_dir / "analysis.json",
    )

    summary = {
        "eval_id": eval_id,
        "run_id": run_id,
        "with_skill": result_with,
        "without_skill": result_without,
        "grading": {"with_skill": grading_a, "without_skill": grading_b},
        "comparison": comparison,
        "analysis": analysis,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
