from __future__ import annotations

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def resolve_root() -> Path:
    """Resolve project root from BRAIN_ROOT, PWD, or use default project root."""
    # Try BRAIN_ROOT first (for compatibility with tests)
    if "BRAIN_ROOT" in os.environ:
        return Path(os.environ["BRAIN_ROOT"])
    # Try PWD next
    if "PWD" in os.environ:
        return Path(os.environ["PWD"])
    # Fall back to project root (2 levels up from this file)
    return Path(__file__).resolve().parents[2]


def resolve_project_root() -> Path:
    """Get the actual project root (where this package is located)."""
    return Path(__file__).resolve().parents[2]


def resolve_vault_root(project_root: Path) -> Path:
    """Resolve vault root from BRAIN_VAULT_DIR env var, or use default."""
    vault_env = os.environ.get("BRAIN_VAULT_DIR")
    if vault_env:
        vault_path = Path(vault_env)
    else:
        vault_path = project_root / "vault"

    # Log se a pasta não existe
    if not vault_path.exists():
        logger.debug(f"[PATHS] Pasta do vault não encontrada: {vault_path}")

    return vault_path


ROOT = resolve_root()
SKILLS_DIR = ROOT / "skills"
CONTEXT_FILE = ROOT / ".codex" / "context.md"
VAULT_DIR = resolve_vault_root(ROOT)
NOTES_DIR = VAULT_DIR / "notes"
VAULT_NOTES = VAULT_DIR / "notes"
VAULT_INBOX = VAULT_DIR / "inbox"
VAULT_ARCHIVE = VAULT_DIR / "archive"
VAULT_ATTACHMENTS = VAULT_DIR / "attachments"
VAULT_GIT_DIR = VAULT_DIR / ".git"
