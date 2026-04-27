"""Note optimization engine - bulk improvement and maintenance of the vault.

The optimizer runs background tasks to improve note quality:
- note_refinement on all notes
- metadata enrichment updates
- re-linking detection and fixing
- archive old notes
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta

from brain_system.core.processor import NoteProcessor
from brain_system.core.linker import auto_link_all
from brain_system.paths import VAULT_NOTES, VAULT_ARCHIVE
from brain_system.rag import build_index as rag_build_index

logger = logging.getLogger(__name__)


class NoteOptimizer:
    """Optimizes and maintains the vault through background processes."""

    def __init__(self, vault_path: Path = None, model: str = "claude"):
        """Initialize optimizer."""
        self.vault_path = vault_path or VAULT_NOTES
        self.model = model
        self.processor = NoteProcessor(model=model)

    def optimize_all(self, relink: bool = True, reindex: bool = True) -> Dict[str, Any]:
        """
        Run complete optimization pass on vault.

        Args:
            relink: Re-detect and update all links
            reindex: Rebuild RAG index after optimization

        Returns:
            Summary of optimization results
        """
        result = {
            "start_time": datetime.now().isoformat(),
            "refinement": {"processed": 0, "errors": 0},
            "relinking": {"links_added": 0, "notes_modified": 0},
            "reindex": {"success": False, "error": None},
            "total_notes": 0,
        }

        try:
            # Count total notes
            note_files = list(self.vault_path.glob("*.md"))
            result["total_notes"] = len(note_files)

            logger.info(f"Starting optimization pass on {len(note_files)} notes")

            # Step 1: Refine all notes
            for note_file in note_files:
                try:
                    # Run note_refinement skill
                    refine_result = self.processor.process_note(note_file)
                    if refine_result["success"]:
                        result["refinement"]["processed"] += 1
                    else:
                        result["refinement"]["errors"] += 1
                except Exception as e:
                    logger.warning(f"Failed to refine {note_file}: {e}")
                    result["refinement"]["errors"] += 1

            logger.info(
                f"✓ Refinement complete: {result['refinement']['processed']} notes"
            )

            # Step 2: Re-link all notes
            if relink:
                link_result = auto_link_all(self.vault_path)
                result["relinking"] = {
                    "links_added": link_result.get("total_links_added", 0),
                    "notes_modified": link_result.get("notes_modified", 0),
                }
                logger.info(
                    f"✓ Relinking complete: {result['relinking']['links_added']} links added"
                )

            # Step 3: Reindex vault
            if reindex:
                try:
                    rag_build_index()
                    result["reindex"]["success"] = True
                    logger.info("✓ Vault reindexed")
                except Exception as e:
                    result["reindex"]["success"] = False
                    result["reindex"]["error"] = str(e)
                    logger.error(f"Reindexing failed: {e}")

            result["end_time"] = datetime.now().isoformat()
            logger.info("✅ Optimization complete")

        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            result["error"] = str(e)

        return result

    def cleanup_old_notes(self, days: int = 90) -> Dict[str, Any]:
        """
        Archive notes not modified in N days.

        Args:
            days: Days of inactivity before archiving

        Returns:
            Cleanup results
        """
        result = {
            "archived": [],
            "total": 0,
            "error": None,
        }

        try:
            cutoff = datetime.now() - timedelta(days=days)
            VAULT_ARCHIVE.mkdir(parents=True, exist_ok=True)

            for note_file in self.vault_path.glob("*.md"):
                mod_time = datetime.fromtimestamp(note_file.stat().st_mtime)

                if mod_time < cutoff:
                    try:
                        archive_file = VAULT_ARCHIVE / note_file.name
                        note_file.rename(archive_file)
                        result["archived"].append(note_file.name)
                        logger.info(f"Archived: {note_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to archive {note_file}: {e}")

            result["total"] = len(result["archived"])
            logger.info(f"✓ Cleanup complete: {result['total']} notes archived")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Cleanup failed: {e}")

        return result

    def get_vault_stats(self) -> Dict[str, Any]:
        """Get current vault statistics."""
        note_files = list(self.vault_path.glob("*.md"))
        total_size = sum(f.stat().st_size for f in note_files)
        total_words = 0

        for note_file in note_files:
            try:
                content = note_file.read_text(encoding="utf-8")
                total_words += len(content.split())
            except:
                pass

        # Count tags and links
        all_tags = set()
        all_links = 0
        import re

        for note_file in note_files:
            try:
                content = note_file.read_text(encoding="utf-8")
                tags = re.findall(r"tags:\s*\[([^\]]+)\]", content)
                links = len(re.findall(r"\[\[([^\]]+)\]\]", content))
                if tags:
                    all_tags.update(tags[0].split(","))
                all_links += links
            except:
                pass

        return {
            "total_notes": len(note_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "total_words": total_words,
            "unique_tags": len(all_tags),
            "total_links": all_links,
            "avg_words_per_note": round(total_words / len(note_files), 0)
            if note_files
            else 0,
        }


def optimize_vault(relink: bool = True, reindex: bool = True) -> Dict[str, Any]:
    """
    Standalone function to optimize vault.

    Args:
        relink: Re-detect and update all links
        reindex: Rebuild RAG index

    Returns:
        Optimization results
    """
    optimizer = NoteOptimizer()
    return optimizer.optimize_all(relink=relink, reindex=reindex)


def cleanup_vault(days: int = 90) -> Dict[str, Any]:
    """
    Standalone function to cleanup old notes.

    Args:
        days: Days before archiving

    Returns:
        Cleanup results
    """
    optimizer = NoteOptimizer()
    return optimizer.cleanup_old_notes(days=days)
