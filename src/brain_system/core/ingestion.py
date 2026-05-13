"""Note ingestion system - handles the complete flow of adding notes to Second Brain.

Ingestion pipeline:
1. Save raw note to vault/inbox/ with a generic temporary filename
2. Process through core pipeline (split_ideas, metadata_enrichment, note_refinement, linking)
3. Move to vault/notes/ using a title-based descriptive filename
4. Trigger RAG indexing
"""

import logging
import re
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

    def __init__(self, inbox_path: Path | None = None, notes_path: Path | None = None):
        """Initialize ingestion system."""
        self.inbox_path = inbox_path or VAULT_INBOX
        self.notes_path = notes_path or VAULT_NOTES
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.notes_path.mkdir(parents=True, exist_ok=True)

    def _sanitize_title(self, title: str | None) -> str:
        raw_title = title.strip().splitlines()[0] if title else ""
        raw_title = raw_title.lower()
        raw_title = re.sub(r"[^\w\s-]", "", raw_title)
        raw_title = re.sub(r"[\s-]+", "_", raw_title)
        return raw_title.strip("_")[:64] if raw_title else ""

    def _infer_title_from_content(self, content: str) -> str:
        text = (content or "").strip()
        if not text:
            return "nota"

        # Remove stray language tag some LLMs prepend (e.g., "yaml")
        lines = text.splitlines()
        if len(lines) >= 2 and lines[0].strip().lower() in {"yaml", "markdown"}:
            text = "\n".join(lines[1:]).lstrip()

        # Prefer frontmatter title if present
        if text.startswith("---"):
            m = re.search(r"(?ms)^---\s*\n(.*?)\n---\s*\n", text)
            if m:
                frontmatter = m.group(1)
                t = re.search(r"(?m)^\s*title:\s*(.+?)\s*$", frontmatter)
                if t:
                    return t.group(1).strip().strip("'\"")

        # Prefer first markdown heading
        h = re.search(r"(?m)^\s*#\s+(.+?)\s*$", text)
        if h:
            return h.group(1).strip()

        # Otherwise first meaningful line (skip frontmatter markers)
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped in {"---", "yaml", "markdown"}:
                continue
            if stripped.startswith("```"):
                continue
            return stripped

        words = text.split()
        return " ".join(words[:6]) if words else "nota"

    @staticmethod
    def ensure_frontmatter_title(content: str, title: str) -> str:
        """Ensure frontmatter contains a `title:` field when frontmatter exists."""
        text = (content or "").lstrip()
        if not text.startswith("---"):
            return content

        m = re.search(r"(?ms)^---\s*\n(.*?)\n---\s*\n?", text)
        if not m:
            return content

        frontmatter = m.group(1)
        if re.search(r"(?m)^\s*title:\s*.+$", frontmatter):
            return content

        # Insert title near the top (after id if present, else first line)
        lines = frontmatter.splitlines()
        insert_at = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("id:"):
                insert_at = i + 1
                break
        lines.insert(insert_at, f"title: {title}")
        new_frontmatter = "\n".join(lines)
        rebuilt = re.sub(
            r"(?ms)^---\s*\n(.*?)\n---",
            f"---\n{new_frontmatter}\n---",
            text,
            count=1,
        )
        return rebuilt

    def _build_final_note_path(self, title: str, fallback_name: str) -> Path:
        safe_name = self._sanitize_title(title) or fallback_name
        final_note = self.notes_path / f"{safe_name}.md"
        counter = 1
        while final_note.exists():
            final_note = self.notes_path / f"{safe_name}_{counter}.md"
            counter += 1
        return final_note

    def ingest_note(
        self,
        content: str,
        title: str | None = None,
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
            # Step 1: Save raw note in inbox with a generic temporary filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note_filename = f"note_{timestamp}.md"
            inbox_note = self.inbox_path / note_filename

            counter = 1
            while inbox_note.exists():
                note_filename = f"note_{timestamp}_{counter}.md"
                inbox_note = self.inbox_path / note_filename
                counter += 1

            inbox_note.write_text(content, encoding="utf-8")
            result["steps"].append("saved_to_inbox")
            logger.info(f"✓ Saved note to inbox: {inbox_note}")
            print(f"   ✓ Salvo na inbox: {inbox_note.name}")

            # Step 2: Process through pipeline
            print("   🔄 Processando nota através do pipeline...")
            process_result = process_note(inbox_note, model=model)
            if not process_result["success"]:
                result["success"] = False
                result["error"] = (
                    f"Processamento falhou: {process_result.get('error') or 'erro desconhecido'}"
                )
                result["note_path"] = str(inbox_note)
                logger.error(f"✗ Note processing failed: {result['error']}")
                print(f"   ❌ {result['error']}")
                return result

            result["steps"].extend(process_result["steps_completed"])
            logger.info(f"✓ Processed note: {process_result['steps_completed']}")
            print(
                f"   ✓ Processamento concluído: {len(process_result['steps_completed'])} etapas"
            )

            # Step 3: Move to notes folder with a descriptive filename
            final_title = title or self._infer_title_from_content(content)
            final_note = self._build_final_note_path(
                final_title, note_filename.replace(".md", "")
            )
            print("   📁 Movendo para vault/notes...")
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
    title: str | None = None,
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
