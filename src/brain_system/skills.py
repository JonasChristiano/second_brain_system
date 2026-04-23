from __future__ import annotations

from pathlib import Path

from .paths import CONTEXT_FILE, SKILLS_DIR


def ensure_skill_exists(skill_name: str) -> Path:
    skill_path = SKILLS_DIR / f"{skill_name}.md"
    if skill_path.exists():
        return skill_path
    raise SystemExit(f"Skill nao encontrada: {skill_name}")


def list_skills() -> list[Path]:
    return sorted(SKILLS_DIR.glob("*.md"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_prompt(
    skill_name: str, instruction: str | None = None, target: str | None = None
) -> str:
    context = load_text(CONTEXT_FILE) if CONTEXT_FILE.exists() else ""
    skill_body = load_text(ensure_skill_exists(skill_name))

    prompt_parts = [
        "Use o contexto e a skill abaixo para executar a tarefa.",
    ]

    if context:
        prompt_parts.extend(
            [
                "",
                "[Contexto global]",
                context,
            ]
        )

    prompt_parts.extend(
        [
            "",
            f"[Skill: {skill_name}]",
            skill_body,
        ]
    )

    if target:
        prompt_parts.extend(
            [
                "",
                "[Alvo]",
                target,
            ]
        )

    if instruction:
        prompt_parts.extend(
            [
                "",
                "[Instrucao]",
                instruction,
            ]
        )

    return "\n".join(prompt_parts).strip()


def slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")
