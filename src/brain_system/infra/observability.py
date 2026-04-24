from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

from ..paths import ROOT


class Observability:
    def __init__(self, log_file: Path | None = None):
        if log_file is None:
            log_file = ROOT / "logs" / "observability.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = log_file

    def log_execution(
        self,
        run_id: str,
        skill: str,
        duration: float,
        tokens: int | None,
        success: bool,
        metadata: dict[str, Any] | None = None,
    ):
        entry = {
            "timestamp": time.time(),
            "run_id": run_id,
            "skill": skill,
            "duration_seconds": duration,
            "tokens": tokens,
            "success": success,
            "metadata": metadata or {},
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_run_id(self) -> str:
        return str(uuid.uuid4())


# Global instance
observer = Observability()
