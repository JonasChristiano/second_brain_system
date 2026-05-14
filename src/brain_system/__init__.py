"""Brain System package."""

from __future__ import annotations

import os
from importlib import metadata
from pathlib import Path

from .logging_config import get_logger, setup_logging

PROJECT_NAME = "SECOND BRAIN SYSTEM"
PROJECT_SHORT = "SBS"
__author__ = os.environ.get("SBS_AUTHOR", "Jonas")

try:
    __version__ = metadata.version("brain-system")
except Exception:
    try:
        pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
        import tomllib

        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        __version__ = str(data.get("project", {}).get("version", "0.0.0"))
    except Exception:
        __version__ = "0.0.0"

__all__ = [
    "PROJECT_NAME",
    "PROJECT_SHORT",
    "__author__",
    "__version__",
    "setup_logging",
    "get_logger",
]
