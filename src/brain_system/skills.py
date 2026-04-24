from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from .paths import CONTEXT_FILE, SKILLS_DIR


class Skill:
    """Representa uma skill independente de LLM provider."""

    def __init__(self, name: str, description: str, body: str):
        self.name = name
        self.description = description
        self.body = body

    @classmethod
    def from_path(cls, skill_path: Path) -> Skill:
        """Carrega uma skill de um caminho SKILL.md."""
        content = load_text(skill_path)
        name, description = parse_skill_frontmatter(content)
        body = get_skill_body(skill_path)
        return cls(name, description, body)


@lru_cache(maxsize=32)
def load_skill(skill_name: str) -> Skill:
    """Carrega e cacheia uma skill por nome."""
    skill_path = ensure_skill_exists(skill_name)
    return Skill.from_path(skill_path)


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
            return "\n".join(lines[i + 1 :]).strip()
    return content  # Malformed, return all


def build_prompt(
    skill_name: str, instruction: str | None = None, target: str | None = None
) -> str:
    """Constrói um prompt estruturado e determinístico para execução de skill."""
    context = load_text(CONTEXT_FILE) if CONTEXT_FILE.exists() else ""
    # Limitar tamanho do contexto para evitar prompts gigantes
    if len(context) > 2000:
        context = context[:2000] + "... (contexto truncado)"

    skill = load_skill(skill_name)

    prompt_parts = [
        "Execute a tarefa de forma precisa e determinística usando o contexto e skill fornecidos.",
    ]

    if context:
        prompt_parts.extend(
            [
                "",
                "[CONTEXTO GLOBAL]",
                context,
            ]
        )

    prompt_parts.extend(
        [
            "",
            f"[SKILL: {skill.name}]",
            f"Descrição: {skill.description}",
            "",
            skill.body,
        ]
    )

    if target:
        prompt_parts.extend(
            [
                "",
                "[ALVO DA EXECUÇÃO]",
                target,
            ]
        )

    if instruction:
        prompt_parts.extend(
            [
                "",
                "[INSTRUÇÃO ESPECÍFICA]",
                instruction,
            ]
        )

    return "\n".join(prompt_parts).strip()


def slugify(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")
