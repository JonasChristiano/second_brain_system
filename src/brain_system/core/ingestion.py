"""Note ingestion system - handles the complete flow of adding notes to Second Brain.

Ingestion pipeline:
1. Save raw note to vault/inbox/
2. Process through core pipeline (split_ideas, metadata_enrichment, note_refinement, linking)
3. Move to vault/notes/
4. Trigger RAG indexing
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from brain_system.core.processor import process_note
from brain_system.core.linker import auto_link_note
from brain_system.paths import VAULT_NOTES, VAULT_INBOX
from brain_system.rag import build_index as rag_build_index

logger = logging.getLogger(__name__)


class NoteIngestion:
    """Manages the complete note ingestion pipeline."""

    def __init__(self, inbox_path: Path = None, notes_path: Path = None):
        """Initialize ingestion system."""
        self.inbox_path = inbox_path or VAULT_INBOX
        self.notes_path = notes_path or VAULT_NOTES
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.notes_path.mkdir(parents=True, exist_ok=True)

    def ingest_note(
        self,
        content: str,
        title: str = None,
        model: str = "claude",
        auto_link: bool = True,
        auto_index: bool = True,
    ) -> Dict[str, Any]:
        """
        Complete ingestion flow for a new note.

        Args:
            content: Raw note content
            title: Note title (auto-generated if None)
            model: LLM model to use
            auto_link: Auto-detect and insert links
            auto_index: Trigger RAG reindexing

        Returns:
            Ingestion result with {
                "success": bool,
                "note_path": str,
                "steps": list[str],
                "error": str | None
            }
        """
        result = {
            "success": True,
            "note_path": None,
            "steps": [],
            "error": None,
        }

        try:
            # Step 1: Create note in inbox with title + timestamp
            if not title:
                title = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            note_filename = f"{title}.md"
            inbox_note = self.inbox_path / note_filename

            # Ensure unique filename
            counter = 1
            while inbox_note.exists():
                safe_title = title.rsplit("_", 1)[0] if "_" in title else title
                note_filename = f"{safe_title}_{counter}.md"
                inbox_note = self.inbox_path / note_filename
                counter += 1

            # Save raw note to inbox
            inbox_note.write_text(content, encoding="utf-8")
            result["steps"].append("saved_to_inbox")
            logger.info(f"✓ Saved note to inbox: {inbox_note}")
            print(f"   ✓ Salvo na inbox: {inbox_note.name}")

            # Step 2: Process through pipeline
            print("   🔄 Processando nota através do pipeline...")
            process_result = process_note(inbox_note, model=model)
            if process_result["success"]:
                result["steps"].extend(process_result["steps_completed"])
                logger.info(f"✓ Processed note: {process_result['steps_completed']}")
                print(f"   ✓ Processamento concluído: {len(process_result['steps_completed'])} etapas")

            # Step 3: Move to notes folder
            print("   📁 Movendo para vault/notes...")
            final_note = self.notes_path / note_filename
            inbox_note.rename(final_note)
            result["note_path"] = str(final_note)
            result["steps"].append("moved_to_notes")
            logger.info(f"✓ Moved note to vault: {final_note}")
            print(f"   ✓ Movido para: {final_note.name}")

            # Step 4: Auto-link if enabled
            if auto_link:
                print("   🔗 Executando auto-linking...")
                link_result = auto_link_note(final_note)
                if link_result["links_added"] > 0:
                    result["steps"].append(f"auto_linked_{link_result['links_added']}")
                    logger.info(
                        f"✓ Auto-linked {link_result['links_added']} references"
                    )
                    print(f"   ✓ {link_result['links_added']} links adicionados")
                else:
                    print("   ✓ Nenhum link novo encontrado")

            # Step 5: Auto-index if enabled
            if auto_index:
                print("   🗂️  Re-indexando vault...")
                try:
                    rag_build_index()
                    result["steps"].append("indexed")
                    logger.info("✓ Re-indexed vault")
                    print("   ✓ Indexação concluída")
                except Exception as e:
                    logger.warning(f"Indexing failed: {e}")
                    print(f"   ⚠️  Indexação falhou: {e}")
                    # Don't fail the whole ingest on index failure

            logger.info(f"✅ Successfully ingested note: {final_note.name}")

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            logger.error(f"Ingestion failed: {e}")

        return result

    def get_inbox_status(self) -> Dict[str, Any]:
        """Get status of notes waiting in inbox."""
        inbox_notes = list(self.inbox_path.glob("*.md"))
        return {
            "pending": len(inbox_notes),
            "notes": [n.name for n in inbox_notes],
        }


def ingest_note(
    content: str,
    title: str = None,
    model: str = "claude",
    auto_link: bool = True,
    auto_index: bool = True,
) -> Dict[str, Any]:
    """
    Standalone function to ingest a note.

    Args:
        content: Raw note content
        title: Note title
        model: LLM model to use
        auto_link: Auto-detect and insert links
        auto_index: Trigger RAG reindexing

    Returns:
        Ingestion result
    """
    ingestion = NoteIngestion()
    return ingestion.ingest_note(
        content,
        title=title,
        model=model,
        auto_link=auto_link,
        auto_index=auto_index,
    )
