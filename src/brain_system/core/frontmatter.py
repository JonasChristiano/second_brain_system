from __future__ import annotations

import re
from datetime import date
from typing import Any


_FRONTMATTER_RE = re.compile(r"(?ms)^---\s*\n(.*?)\n---\s*\n?")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter, body). Frontmatter does not include --- markers."""
    source = text or ""
    m = _FRONTMATTER_RE.match(source.lstrip())
    if not m:
        return None, source
    frontmatter = m.group(1)
    body = source.lstrip()[m.end() :]
    return frontmatter, body


def _has_key(frontmatter: str, key: str) -> bool:
    return re.search(rf"(?m)^\s*{re.escape(key)}\s*:\s*.+$", frontmatter) is not None


def infer_title(text: str) -> str:
    """Infer a human-friendly title from frontmatter, heading, or first content line."""
    content = (text or "").strip()
    if not content:
        return "nota"

    # Drop stray language tag lines (common from some LLMs)
    lines = content.splitlines()
    if len(lines) >= 2 and lines[0].strip().lower() in {"yaml", "markdown"}:
        content = "\n".join(lines[1:]).lstrip()

    frontmatter, body = split_frontmatter(content)
    if frontmatter:
        m = re.search(r"(?m)^\s*title:\s*(.+?)\s*$", frontmatter)
        if m:
            return m.group(1).strip().strip("'\"")

    heading = re.search(r"(?m)^\s*#\s+(.+?)\s*$", body)
    if heading:
        return heading.group(1).strip()

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"---", "yaml", "markdown"}:
            continue
        if stripped.startswith("```"):
            continue
        return stripped

    words = body.split()
    return " ".join(words[:6]) if words else "nota"


def ensure_minimum_frontmatter(
    text: str,
    *,
    defaults: dict[str, Any] | None = None,
    ensure_title: bool = True,
) -> str:
    """Ensure note has YAML frontmatter with minimum keys, without overwriting existing values."""
    defaults = defaults or {}
    content = text or ""
    fm, body = split_frontmatter(content)

    # Remove a trailing standalone '---' (often used as prompt separator)
    body_lines = body.rstrip().splitlines()
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    if body_lines and body_lines[-1].strip() == "---":
        body = "\n".join(body_lines[:-1]).rstrip() + "\n"

    if fm is None:
        title = infer_title(content) if ensure_title else None
        created = defaults.get("created_at") or date.today().isoformat()
        updated = defaults.get("last_updated") or date.today().isoformat()
        type_value = defaults.get("type") or "note"
        status_value = defaults.get("status") or "active"

        lines: list[str] = []
        if ensure_title and title:
            lines.append(f"title: {title}")
        lines.append(f"type: {type_value}")
        lines.append(f"status: {status_value}")
        lines.append(f"created_at: {created}")
        lines.append(f"last_updated: {updated}")
        fm = "\n".join(lines)
    else:
        fm_lines = fm.splitlines()
        title = infer_title(content)
        if ensure_title and not _has_key(fm, "title"):
            fm_lines.insert(0, f"title: {title}")

        for key in ("type", "status", "created_at", "last_updated"):
            if not _has_key("\n".join(fm_lines), key):
                value = defaults.get(key)
                if value is None:
                    if key in {"created_at", "last_updated"}:
                        value = date.today().isoformat()
                    elif key == "type":
                        value = "note"
                    elif key == "status":
                        value = "active"
                fm_lines.append(f"{key}: {value}")

        fm = "\n".join(fm_lines).rstrip()

    return f"---\n{fm}\n---\n{body.lstrip()}"

