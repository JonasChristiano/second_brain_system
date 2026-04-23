from __future__ import annotations

import os
import shutil
from pathlib import Path


BASE = Path("./vault")
NOTES = BASE / "notes"
ATTACHMENTS = BASE / "attachments"


def reorganize_vault(base: Path = BASE) -> None:
    notes = base / "notes"
    attachments = base / "attachments"

    notes.mkdir(parents=True, exist_ok=True)
    attachments.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(base):
        root_path = Path(root)

        if root_path in {notes, attachments}:
            continue

        for filename in files:
            path = root_path / filename

            if filename.endswith(".md"):
                shutil.move(str(path), str(notes / filename))
            elif not filename.endswith(".py"):
                shutil.move(str(path), str(attachments / filename))


def main() -> None:
    reorganize_vault()
    print("Vault reorganizado.")


if __name__ == "__main__":
    main()
