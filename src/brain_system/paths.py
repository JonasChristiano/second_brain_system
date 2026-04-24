from __future__ import annotations

import os
from pathlib import Path


def resolve_root() -> Path:
    default_root = Path(__file__).resolve().parents[2]
    return Path(
        os.environ.get("BRAIN_ROOT") or os.environ.get("PWD") or str(default_root)
    )


ROOT = resolve_root()
SKILLS_DIR = ROOT / "skills"
CONTEXT_FILE = ROOT / ".codex" / "context.md"
VAULT_DIR = ROOT / "vault"
NOTES_DIR = VAULT_DIR / "notes"
VAULT_GIT_DIR = VAULT_DIR / ".git"
