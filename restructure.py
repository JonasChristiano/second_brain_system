from __future__ import annotations

import os
import shutil
from pathlib import Path


BASE = Path("./vault")
NOTES = BASE / "notes"
ATTACHMENTS = BASE / "attachments"
TEMPLATES = BASE / "templates"
INBOX = BASE / "inbox"
ARCHIVE = BASE / "archive"
STANDARD_DIR_NAMES = {
    "notes",
    "attachments",
    "templates",
    "inbox",
    "archive",
    ".git",
}


def reorganize_vault(base: Path = BASE) -> dict[str, int]:
    notes = base / "notes"
    attachments = base / "attachments"
    templates = base / "templates"
    inbox = base / "inbox"
    archive = base / "archive"

    notes.mkdir(parents=True, exist_ok=True)
    attachments.mkdir(parents=True, exist_ok=True)
    templates.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)

    moved_notes = 0
    moved_attachments = 0

    for root, dirs, files in os.walk(base):
        root_path = Path(root)

        dirs[:] = [name for name in dirs if name not in {".git", "__pycache__"}]

        if root_path in {notes, attachments, templates, inbox, archive}:
            continue

        for filename in files:
            path = root_path / filename

            if path.parent.name in STANDARD_DIR_NAMES:
                continue

            if filename.endswith(".md"):
                shutil.move(str(path), str(notes / filename))
                moved_notes += 1
            elif not filename.endswith(".py"):
                shutil.move(str(path), str(attachments / filename))
                moved_attachments += 1

    return {
        "notes_moved": moved_notes,
        "attachments_moved": moved_attachments,
    }


def main() -> None:
    result = reorganize_vault()
    print(
        "Vault reorganizado. "
        f"Notas movidas: {result['notes_moved']}. "
        f"Anexos movidos: {result['attachments_moved']}."
    )


if __name__ == "__main__":
    main()
