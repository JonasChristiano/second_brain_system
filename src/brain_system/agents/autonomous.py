from __future__ import annotations

import time
import random
from pathlib import Path
from typing import Any

from ..infra.observability import observer
from ..llm_adapter import ask
from ..paths import ROOT
from .auto_improve import auto_improve_cycle
from .pipeline import run_multi_agent_pipeline


class AutonomousAgent:
    def __init__(self, model: str | None = None):
        self.model = model
        self.cycle_count = 0
        self.goals = self._load_goals()

    def _load_goals() -> list[str]:
        """Load autonomous goals from config."""
        goals_file = ROOT / "config" / "autonomous_goals.txt"
        if goals_file.exists():
            return goals_file.read_text(encoding="utf-8").strip().split("\n")
        return [
            "Melhorar a qualidade das skills",
            "Expandir o conhecimento na base RAG",
            "Otimizar performance do sistema",
            "Descobrir novas capacidades",
        ]

    def select_task(self) -> str:
        """Select next task based on goals and current state."""
        goal = random.choice(self.goals)

        # Generate specific task from goal
        prompt = f"""
Baseado na meta: "{goal}"

Gere uma tarefa específica e acionável que o sistema possa executar para avançar nessa meta.
A tarefa deve ser concreta e executável por uma pipeline de agentes.
"""
        task = ask(prompt, self.model).strip()
        return task

    def run_cycle(self) -> dict[str, Any]:
        """Run one autonomous cycle."""
        self.cycle_count += 1

        # Select and execute task
        task = self.select_task()
        result = run_multi_agent_pipeline(task, self.model)

        # Auto-improve based on results
        improvement_result = auto_improve_cycle()

        # Log cycle
        observer.log_execution(
            observer.get_run_id(),
            "autonomous_cycle",
            result.get("duration", 0),
            None,
            True,
            {
                "cycle": self.cycle_count,
                "task": task,
                "pipeline_length": len(result.get("pipeline", [])),
                "improvements_applied": improvement_result.get("status")
                == "improvements_applied",
            },
        )

        return {
            "cycle": self.cycle_count,
            "task": task,
            "result": result,
            "improvements": improvement_result,
        }

    def run_continuous(self, max_cycles: int = 10, delay_seconds: int = 300):
        """Run autonomous cycles continuously."""
        for _ in range(max_cycles):
            try:
                result = self.run_cycle()
                print(f"Ciclo {result['cycle']} concluído: {result['task'][:50]}...")

                if delay_seconds > 0:
                    time.sleep(delay_seconds)

            except Exception as e:
                print(f"Erro no ciclo autônomo: {e}")
                observer.log_execution(
                    observer.get_run_id(),
                    "autonomous_error",
                    0,
                    None,
                    False,
                    {"error": str(e)},
                )
                time.sleep(delay_seconds)  # Still wait before retry


def start_autonomous_mode(model: str | None = None, max_cycles: int = 10):
    """Start the autonomous agent mode."""
    agent = AutonomousAgent(model)
    agent.run_continuous(max_cycles)
