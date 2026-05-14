"""Smart search engine - provides semantic note search with related notes and suggestions."""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any

from brain_system.paths import VAULT_NOTES
from brain_system.rag import search

logger = logging.getLogger(__name__)


class SmartSearch:
    """Provides intelligent note search with related notes and suggestions."""

    def __init__(self, vault_path: Path | None = None):
        """Initialize search engine."""
        self.vault_path = vault_path or VAULT_NOTES
        self._build_note_index()

    def _build_note_index(self):
        """Build in-memory index of notes for quick access."""
        self.notes_index: Dict[str, Dict[str, Any]] = {}
        for note_file in self.vault_path.glob("*.md"):
            try:
                content = note_file.read_text(encoding="utf-8")
                # Extract title from filename
                title = note_file.stem.replace("_", " ")

                # Extract first line as summary if no heading
                lines = content.split("\n")
                summary = ""
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        summary = line[:100].strip()
                        break

                # Extract tags from frontmatter or content
                tags = re.findall(r"tags:\s*\[([^\]]+)\]", content)
                tags = (
                    [t.strip().strip("'\"") for t in tags[0].split(",")] if tags else []
                )

                # Extract links
                links = re.findall(r"\[\[([^\]]+)\]\]", content)

                self.notes_index[note_file.stem] = {
                    "title": title,
                    "path": note_file,
                    "summary": summary,
                    "tags": tags,
                    "links": links,
                    "size": len(content),
                }
            except Exception as e:
                logger.warning(f"Failed to index {note_file}: {e}")

    def search(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Smart search with related notes and suggestions.

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            Dict with {
                "query": str,
                "top_notes": list[{title, path, summary, relevance}],
                "related_notes": list[{title, reason}],
                "suggested_links": list[{from, to, reason}],
                "total_results": int
            }
        """
        result = {
            "query": query,
            "top_notes": [],
            "related_notes": [],
            "suggested_links": [],
            "total_results": 0,
        }

        try:
            # Perform RAG search for top matches
            try:
                rag_results = search(query)
            except:
                # Graceful fallback if search fails
                rag_results = []

            if not rag_results:
                return result

            # Map RAG results to our note index
            rag_scores: Dict[str, float] = {}
            for rag_result in rag_results:
                # 1) Prefer direct mapping by source metadata from vector store.
                source = rag_result.get("source")
                if source:
                    note_id = Path(str(source)).stem
                    if note_id in self.notes_index:
                        rag_scores[note_id] = max(
                            rag_scores.get(note_id, 0.0),
                            float(rag_result.get("score", 0.0) or 0.0),
                        )
                        continue

                # 2) Fallback to content overlap.
                # Try to find matching note
                for note_id, note_info in self.notes_index.items():
                    if "content" in rag_result and len(str(rag_result["content"])) > 20:
                        note_content = note_info["path"].read_text(encoding="utf-8")[:120]
                        if note_content and note_content in str(rag_result["content"]):
                            rag_scores[note_id] = max(
                                rag_scores.get(note_id, 0.0),
                                float(rag_result.get("score", 0.0) or 0.0),
                            )
                            break

            # 3) Combine semantic + lexical score and order globally.
            ranked: list[tuple[float, str, Dict[str, Any]]] = []
            for note_id, note_info in self.notes_index.items():
                lexical_score = self._lexical_score(note_info, query)
                rag_score = rag_scores.get(note_id, 0.0)

                # Keep notes found semantically or with meaningful lexical signal.
                if rag_score <= 0 and lexical_score <= 0:
                    continue

                if rag_score > 0 and lexical_score > 0:
                    relevance = (0.45 * rag_score) + (0.55 * lexical_score)
                elif lexical_score > 0:
                    relevance = lexical_score
                else:
                    relevance = rag_score * 0.75

                ranked.append((min(0.99, relevance), note_id, note_info))

            ranked.sort(key=lambda item: item[0], reverse=True)

            for relevance, note_id, note_info in ranked[:top_k]:
                result["top_notes"].append(
                    {
                        "title": note_info["title"],
                        "path": str(note_info["path"]),
                        "summary": note_info["summary"],
                        "relevance": relevance,
                        "tags": note_info["tags"],
                    }
                )

            result["total_results"] = len(result["top_notes"])
            processed_notes = {
                Path(note["path"]).stem for note in result["top_notes"] if "path" in note
            }

            # Find related notes based on tags and links
            if result["top_notes"]:
                top_note_id = None
                for note_id, note_info in self.notes_index.items():
                    if note_info["title"] == result["top_notes"][0]["title"]:
                        top_note_id = note_id
                        break

                if top_note_id:
                    related = self._find_related_notes(
                        top_note_id, exclude=processed_notes
                    )
                    result["related_notes"] = related[:3]

                    # Suggest new links
                    suggested = self._suggest_links(
                        top_note_id, exclude=processed_notes
                    )
                    result["suggested_links"] = suggested[:3]

        except Exception as e:
            logger.error(f"Search failed: {e}")

        return result

    def _find_related_notes(
        self, note_id: str, exclude: set | None = None
    ) -> List[Dict[str, str]]:
        """Find notes related by tags or existing links."""
        if exclude is None:
            exclude = set()

        note_info = self.notes_index.get(note_id)
        if not note_info:
            return []

        related = []
        query_tags = set(note_info["tags"])
        query_links = set(note_info["links"])

        for other_id, other_info in self.notes_index.items():
            if other_id == note_id or other_id in exclude:
                continue

            # Score by tag match
            tag_match = len(query_tags & set(other_info["tags"])) / max(
                len(query_tags), 1
            )

            # Score by link match
            link_match = 1.0 if other_id in query_links else 0.0

            if tag_match > 0 or link_match > 0:
                related.append(
                    {
                        "title": other_info["title"],
                        "reason": self._get_relation_reason(tag_match, link_match),
                    }
                )

        return sorted(related, key=lambda x: x.get("score", 0), reverse=True)

    def _suggest_links(
        self, note_id: str, exclude: set | None = None
    ) -> List[Dict[str, str]]:
        """Suggest new [[links]] for a note."""
        if exclude is None:
            exclude = set()

        note_info = self.notes_index.get(note_id)
        if not note_info:
            return []

        suggested = []
        existing_links = set(note_info["links"])

        # Suggest notes with high tag overlap
        for other_id, other_info in self.notes_index.items():
            if other_id == note_id or other_id in exclude or other_id in existing_links:
                continue

            tag_match = len(set(note_info["tags"]) & set(other_info["tags"]))

            if tag_match >= 1:
                suggested.append(
                    {
                        "from": note_info["title"],
                        "to": other_info["title"],
                        "reason": f"shared {tag_match} tag(s)",
                    }
                )

        return sorted(suggested, key=lambda x: x.get("strength", 0), reverse=True)[:5]

    @staticmethod
    def _get_relation_reason(tag_match: float, link_match: float) -> str:
        """Generate human-readable relation reason."""
        reasons = []
        if link_match > 0:
            reasons.append("linked")
        if tag_match > 0.5:
            reasons.append("shared tags")
        return ", ".join(reasons) or "related"

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        match = re.match(r"(?ms)^---\s*\n.*?\n---\s*\n?", content)
        if match:
            return content[match.end() :]
        return content

    def _lexical_score(self, note_info: Dict[str, Any], query: str) -> float:
        query_lower = (query or "").strip().lower()
        if not query_lower:
            return 0.0

        title = str(note_info.get("title", "")).lower()
        tags = [str(t).lower() for t in note_info.get("tags", [])]
        content_full = note_info["path"].read_text(encoding="utf-8")
        body = self._strip_frontmatter(content_full).lower()

        score = 0.0
        if query_lower in title:
            score += 0.65
        if query_lower in tags:
            score += 0.20

        occurrences = body.count(query_lower)
        if occurrences > 0:
            score += min(0.60, 0.25 + (occurrences * 0.08))

        return min(0.99, score)


def smart_search(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Standalone function for smart note search.

    Args:
        query: Search query
        top_k: Number of results

    Returns:
        Search results with related notes and suggestions
    """
    engine = SmartSearch()
    return engine.search(query, top_k=top_k)
