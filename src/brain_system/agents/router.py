from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from ..paths import SKILLS_DIR


def select_skills(task: str, k: int = 3) -> list[str]:
    """
    Select top-k relevant skills based on task description.

    Uses simple text similarity (word overlap) on skill descriptions.
    For production, replace with embeddings.
    """
    task_words = set(re.findall(r"\w+", task.lower()))
    skill_scores = {}

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        try:
            description = _extract_description(skill_file)
            desc_words = set(re.findall(r"\w+", description.lower()))
            # Simple Jaccard similarity
            intersection = len(task_words & desc_words)
            union = len(task_words | desc_words)
            if union > 0:
                score = intersection / union
            else:
                score = 0.0
            skill_scores[skill_dir.name] = score
        except Exception:
            # Skip malformed skills
            continue

    # Sort by score descending, take top k
    sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
    return [name for name, _ in sorted_skills[:k]]


def _extract_description(skill_file: Path) -> str:
    """Extract description from SKILL.md frontmatter."""
    content = skill_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    in_frontmatter = False
    description = ""

    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        if in_frontmatter and line.startswith("description:"):
            description = line[len("description:") :].strip().strip('"').strip("'")
            # Handle multiline if needed, but for simplicity, take first line
            break

    return description
