"""Auto-linking engine - automatically detects and inserts semantic [[references]].

The linker analyzes note content to find related notes and inserts [[wiki-style links]]
for better navigation in the Second Brain system.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

from brain_system.paths import VAULT_NOTES
from brain_system.rag import search as rag_search

logger = logging.getLogger(__name__)


class NoteLinkEngine:
    """Automatically detects and creates links between notes."""

    def __init__(self, vault_path: Path = None, min_similarity: float = 0.3):
        """Initialize the link engine."""
        self.vault_path = vault_path or VAULT_NOTES
        self.min_similarity = min_similarity
        self.link_graph: Dict[str, Set[str]] = defaultdict(set)
        self._load_note_registry()

    def _load_note_registry(self):
        """Build registry of note titles and aliases."""
        self.note_registry: Dict[str, str] = {}  # alias/title -> file_path
        for note_file in self.vault_path.glob("*.md"):
            # Use filename without .md as primary key
            clean_name = note_file.stem.lower().replace("_", " ")
            self.note_registry[clean_name] = note_file

    def find_links_for_note(self, note_path: Path, top_k: int = 5) -> List[str]:
        """
        Find semantically related notes using RAG search.

        Args:
            note_path: Path to the note
            top_k: Maximum number of related notes to return

        Returns:
            List of related note filenames (without .md)
        """
        try:
            content = note_path.read_text(encoding="utf-8")
            # Extract first 500 chars as query
            query = content[:500].split("\n")[0]

            if not query or len(query) < 10:
                return []

            # Search for related notes
            results = rag_search(query)

            related = []
            for result in results[:top_k]:
                if "content" in result:
                    # Try to find source file from content
                    for note_file in self.vault_path.glob("*.md"):
                        if result["content"][:100] in note_file.read_text(
                            encoding="utf-8"
                        ):
                            if note_file != note_path:
                                related.append(note_file.stem)
                                break

            return related

        except Exception as e:
            logger.warning(f"Failed to find links for {note_path}: {e}")
            return []

    def insert_links(self, note_path: Path) -> Dict[str, any]:
        """
        Insert [[links]] into a note.

        Args:
            note_path: Path to the note

        Returns:
            Dict with {
                "links_added": int,
                "links": list[str],
                "modified": bool
            }
        """
        result = {"links_added": 0, "links": [], "modified": False}

        try:
            content = note_path.read_text(encoding="utf-8")
            original_content = content

            # Find related notes
            related_notes = self.find_links_for_note(note_path)

            if not related_notes:
                return result

            # Extract existing links to avoid duplicates
            existing_links = set(re.findall(r"\[\[([^\]]+)\]\]", content))

            # Add new links
            new_links = [n for n in related_notes if n not in existing_links]

            if new_links:
                # Insert links section if not exists
                if "## Related Notes" not in content:
                    content = content.rstrip() + "\n\n## Related Notes\n\n"
                else:
                    # Find the related notes section
                    section_start = content.find("## Related Notes")
                    section_content = content[section_start:]

                    # Check if already has links
                    if "[[" not in section_content.split("\n")[1]:
                        # Insert after the heading
                        insert_pos = section_start + len("## Related Notes\n")
                        content = (
                            content[:insert_pos]
                            + "\n"
                            + content[insert_pos:]
                        )

                # Add link lines
                link_lines = "\n".join(f"- [[{link}]]" for link in new_links)
                content = content.rstrip() + "\n" + link_lines + "\n"

                # Write back
                note_path.write_text(content, encoding="utf-8")

                result["links_added"] = len(new_links)
                result["links"] = new_links
                result["modified"] = True

                logger.info(
                    f"Added {len(new_links)} links to {note_path.name}: {new_links}"
                )

        except Exception as e:
            logger.error(f"Error inserting links into {note_path}: {e}")

        return result

    def link_all_notes(self) -> Dict[str, any]:
        """
        Process all notes in vault to add links.

        Returns:
            Summary of linking results
        """
        results = []
        total_links_added = 0

        for note_file in sorted(self.vault_path.glob("*.md")):
            result = self.insert_links(note_file)
            results.append(result)
            total_links_added += result["links_added"]

        return {
            "notes_processed": len(results),
            "total_links_added": total_links_added,
            "notes_modified": sum(1 for r in results if r["modified"]),
            "results": results,
        }

    def get_link_graph(self) -> Dict[str, List[str]]:
        """Get the complete link graph of all notes."""
        graph = {}
        for note_file in self.vault_path.glob("*.md"):
            content = note_file.read_text(encoding="utf-8")
            links = re.findall(r"\[\[([^\]]+)\]\]", content)
            if links:
                graph[note_file.stem] = links

        return graph


def auto_link_note(note_path: Path, top_k: int = 5) -> Dict[str, any]:
    """
    Standalone function to auto-link a single note.

    Args:
        note_path: Path to the note
        top_k: Maximum related notes to link

    Returns:
        Linking result
    """
    engine = NoteLinkEngine()
    return engine.insert_links(note_path)


def auto_link_all(vault_path: Path = None) -> Dict[str, any]:
    """
    Auto-link all notes in the vault.

    Args:
        vault_path: Path to vault (default: VAULT_NOTES)

    Returns:
        Summary of all linking operations
    """
    engine = NoteLinkEngine(vault_path=vault_path)
    return engine.link_all_notes()
