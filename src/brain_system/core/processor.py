"""Note processor - core pipeline for Second Brain system.

Orchestrates the automatic note processing pipeline:
1. split_ideas - separate mixed ideas and add initial links
2. metadata_enrichment - standardize frontmatter (type, status, dates, tags)
3. note_refinement - improve clarity and structure
4. contextual_linking - add semantic [[references]] based on content
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from brain_system.skills import build_prompt, load_skill
from brain_system.llm_adapter import ask
from brain_system.paths import VAULT_NOTES, VAULT_INBOX, VAULT_ARCHIVE

logger = logging.getLogger(__name__)


class NoteProcessor:
    """Processes notes through the automated pipeline."""

    PIPELINE_STEPS = [
        "split_ideas",
        "metadata_enrichment",
        "note_refinement",
        "contextual_linking",
    ]

    def __init__(self, model: str = "claude"):
        """Initialize processor with specified LLM model."""
        self.model = model
        self.stats = {"processed": 0, "errors": 0, "total_time": 0}

    def process_note(self, note_path: Path) -> Dict[str, Any]:
        """
        Process a note through the complete pipeline.

        Args:
            note_path: Path to the note file to process

        Returns:
            Dict with processing result: {
                "success": bool,
                "path": str,
                "steps_completed": list[str],
                "output": str,
                "error": str | None
            }
        """
        if not note_path.exists():
            return {
                "success": False,
                "path": str(note_path),
                "error": f"Note not found: {note_path}",
            }

        result = {
            "success": True,
            "path": str(note_path),
            "steps_completed": [],
            "output": None,
            "error": None,
        }

        try:
            # Read raw note
            note_content = note_path.read_text(encoding="utf-8")
            current_content = note_content

            # Execute pipeline steps
            for step in self.PIPELINE_STEPS:
                try:
                    current_content = self._execute_step(
                        step, current_content, note_path
                    )
                    result["steps_completed"].append(step)
                except Exception as e:
                    logger.warning(f"Step {step} failed: {e}")
                    # Continue even if a step fails - graceful degradation
                    break

            # Write processed note back
            note_path.write_text(current_content, encoding="utf-8")
            result["output"] = current_content

            self.stats["processed"] += 1
            logger.info(f"✓ Processed {note_path.name}: {result['steps_completed']}")

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            self.stats["errors"] += 1
            logger.error(f"Failed to process {note_path}: {e}")

        return result

    def _execute_step(self, step: str, content: str, note_path: Path) -> str:
        """
        Execute a single pipeline step.

        Args:
            step: Step name (split_ideas, metadata_enrichment, etc.)
            content: Current note content
            note_path: Path for context

        Returns:
            Processed content after step execution
        """
        try:
            # Load skill definition
            skill = load_skill(step)
            if not skill:
                logger.warning(f"Skill not found: {step}")
                return content

            # Build prompt for this step
            prompt = build_prompt(
                skill_name=step,
                instruction=f"Process this note for {step}:",
                target=content,
            )

            # Call LLM to process
            processed = ask(prompt, model=self.model)

            # Extract markdown content if wrapped in code blocks
            if "```" in processed:
                processed = self._extract_markdown(processed)

            return processed or content

        except Exception as e:
            logger.error(f"Error in step {step}: {e}")
            raise

    @staticmethod
    def _extract_markdown(text: str) -> str:
        """Extract markdown from code-wrapped response."""
        if "```markdown" in text:
            parts = text.split("```markdown")
            if len(parts) > 1:
                content = parts[1].split("```")[0].strip()
                return content
        elif "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                return parts[1].strip()
        return text

    def process_batch(self, note_paths: list[Path]) -> Dict[str, Any]:
        """
        Process multiple notes.

        Args:
            note_paths: List of note paths to process

        Returns:
            Summary of batch processing
        """
        results = []
        for path in note_paths:
            results.append(self.process_note(path))

        return {
            "total": len(note_paths),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "results": results,
            "stats": self.stats,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.stats.copy()


def process_note(note_path: Path, model: str = "claude") -> Dict[str, Any]:
    """
    Standalone function to process a single note.

    Args:
        note_path: Path to note file
        model: LLM model to use (default: claude)

    Returns:
        Processing result dictionary
    """
    processor = NoteProcessor(model=model)
    return processor.process_note(note_path)


def process_all_notes(directory: Path = None, model: str = "claude") -> Dict[str, Any]:
    """
    Process all notes in a directory.

    Args:
        directory: Directory to process (default: vault/notes/)
        model: LLM model to use

    Returns:
        Batch processing results
    """
    if directory is None:
        directory = VAULT_NOTES

    note_paths = sorted(directory.glob("*.md"))
    processor = NoteProcessor(model=model)
    return processor.process_batch(note_paths)
