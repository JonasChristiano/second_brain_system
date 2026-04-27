from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..infra.observability import observer
from ..llm_adapter import ask
from ..paths import ROOT


def analyze_performance() -> dict[str, Any]:
    """Analyze recent executions to identify improvement opportunities."""
    log_file = ROOT / "logs" / "observability.jsonl"
    if not log_file.exists():
        return {"insights": [], "recommendations": []}

    executions = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                executions.append(json.loads(line))

    # Simple analysis: find slow or failing skills
    insights = []
    recommendations = []

    if executions:
        # Group by skill
        skill_stats = {}
        for exec in executions[-100:]:  # Last 100 executions
            skill = exec.get("skill", "unknown")
            if skill not in skill_stats:
                skill_stats[skill] = {"count": 0, "total_duration": 0, "failures": 0}
            skill_stats[skill]["count"] += 1
            skill_stats[skill]["total_duration"] += exec.get("duration_seconds", 0)
            if not exec.get("success", True):
                skill_stats[skill]["failures"] += 1

        for skill, stats in skill_stats.items():
            avg_duration = stats["total_duration"] / stats["count"]
            failure_rate = stats["failures"] / stats["count"]

            if avg_duration > 10:  # Slow skill
                insights.append(f"Skill '{skill}' is slow (avg {avg_duration:.1f}s)")
                recommendations.append(f"Optimize '{skill}' for better performance")

            if failure_rate > 0.1:  # High failure rate
                insights.append(
                    f"Skill '{skill}' has high failure rate ({failure_rate:.1%})"
                )
                recommendations.append(f"Debug and fix '{skill}'")

    return {"insights": insights, "recommendations": recommendations}


def generate_improvement_plan(insights: list[str], recommendations: list[str]) -> str:
    """Generate a plan for system improvements."""
    prompt = f"""
Based on the following insights and recommendations, generate a concrete improvement plan:

Insights:
{chr(10).join(f"- {i}" for i in insights)}

Recommendations:
{chr(10).join(f"- {r}" for r in recommendations)}

Generate a step-by-step improvement plan with specific actions.
"""
    return ask(prompt, model="claude-3-haiku")


def apply_improvements(plan: str) -> bool:
    """Apply the improvement plan (placeholder for actual implementation)."""
    # For now, just log the plan
    improvement_log = ROOT / "logs" / "improvements.log"
    improvement_log.parent.mkdir(parents=True, exist_ok=True)

    with open(improvement_log, "a", encoding="utf-8") as f:
        f.write(f"Improvement Plan:\n{plan}\n\n")

    return True


def auto_improve_cycle() -> dict[str, Any]:
    """Run one cycle of auto-improvement."""
    analysis = analyze_performance()
    if not analysis["insights"]:
        return {"status": "no_improvements_needed"}

    plan = generate_improvement_plan(analysis["insights"], analysis["recommendations"])
    success = apply_improvements(plan)

    return {
        "status": "improvements_applied" if success else "improvements_failed",
        "insights": analysis["insights"],
        "recommendations": analysis["recommendations"],
        "plan": plan,
    }
