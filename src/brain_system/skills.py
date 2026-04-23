from __future__ import annotations

import re
from pathlib import Path

from .paths import CONTEXT_FILE, SKILLS_DIR


def ensure_skill_exists(skill_name: str) -> Path:
    skill_path = SKILLS_DIR / skill_name / "SKILL.md"
    if skill_path.exists():
        return skill_path
    raise SystemExit(f"Skill nao encontrada: {skill_name}")


def list_skills() -> list[Path]:
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item)
    return sorted(skills)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def parse_skill_frontmatter(content: str) -> tuple[str, str]:
    """Parse frontmatter from SKILL.md, returning (name, description)."""
    lines = content.split("\n")
    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:") :].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:") :].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ")
                    or frontmatter_lines[i].startswith("\t")
                ):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description


def get_skill_body(skill_path: Path) -> str:
    """Get the body of the skill (content after frontmatter)."""
    content = load_text(skill_path)
    lines = content.split("\n")
    if lines[0].strip() != "---":
        return content  # No frontmatter, return all

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i+1:]).strip()
    return content  # Malformed, return all


def build_prompt(
    skill_name: str, instruction: str | None = None, target: str | None = None
) -> str:
    context = load_text(CONTEXT_FILE) if CONTEXT_FILE.exists() else ""
    skill_path = ensure_skill_exists(skill_name)
    skill_body = get_skill_body(skill_path)

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
