"""KAI public safe trace logger.

Purpose:
    Demonstrates append only event tracing for auditability.
    Free text can be hashed when privacy mode is enabled.
"""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class KAITraceLogger:
    """Append only JSONL trace logger for KAI audit events."""

    def __init__(self, directory: str | Path, filename: str = "kai_trace.jsonl", privacy_mode: bool = True) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.filename = filename
        self.privacy_mode = privacy_mode
        self._lock = threading.Lock()

    def _path_for_today(self) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.directory / self.filename.replace(".jsonl", f".{stamp}.jsonl")

    def _safe_text(self, value: str) -> str:
        if not self.privacy_mode:
            return value
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
        return f"sha256:{digest}"

    def event(self, kind: str, **fields: Any) -> None:
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "kind": kind,
        }

        for key, value in fields.items():
            if key in {"query", "response", "user_text"} and isinstance(value, str):
                record[key] = self._safe_text(value)
            else:
                record[key] = value

        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with self._lock:
            with self._path_for_today().open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")


if __name__ == "__main__":
    logger = KAITraceLogger("./kai_logs")
    logger.event(
        "decision_trace_created",
        query="example user request",
        primary_role="KAI-R01",
        risk_level="low",
        final_response_classification="allowed",
    )
    print("KAI trace event written.")
