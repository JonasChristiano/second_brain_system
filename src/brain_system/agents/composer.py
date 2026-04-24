from __future__ import annotations

from .router import select_skills


def build_pipeline(task: str) -> list[str]:
    """
    Build a logical pipeline of skills for the given task.

    Uses heuristics based on task keywords and selected skills.
    """
    selected = select_skills(task, k=5)  # Get more candidates

    # Heuristics for ordering
    pipeline = []

    # Always start with brain_orchestrator if available
    if "brain_orchestrator" in selected:
        pipeline.append("brain_orchestrator")
        selected.remove("brain_orchestrator")

    # Add contextual_linking early for context
    if "contextual_linking" in selected:
        pipeline.append("contextual_linking")
        selected.remove("contextual_linking")

    # Add refinement skills later
    refinement_skills = [
        s for s in selected if "refinement" in s or "refine" in s.lower()
    ]
    for skill in refinement_skills:
        pipeline.append(skill)
        selected.remove(skill)

    # Add remaining skills
    pipeline.extend(selected)

    # Limit to reasonable length
    return pipeline[:3]  # Return top 3 for pipeline
