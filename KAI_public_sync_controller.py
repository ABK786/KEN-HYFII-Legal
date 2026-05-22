"""KAI public safe sync controller.

Demonstrates a minimal integrity index for KAI knowledge files.
The sample uses only local files and does not expose private content.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class KAIFileRecord:
    path: str
    size_bytes: int
    sha256: str
    modified_utc: str


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_index(root: Path, patterns: tuple[str, ...] = ("*.md", "*.json", "*.py", "*.js", "*.html")) -> list[KAIFileRecord]:
    records: list[KAIFileRecord] = []
    for pattern in patterns:
        for path in sorted(root.rglob(pattern)):
            if not path.is_file():
                continue
            stat = path.stat()
            records.append(
                KAIFileRecord(
                    path=path.relative_to(root).as_posix(),
                    size_bytes=stat.st_size,
                    sha256=hash_file(path),
                    modified_utc=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                )
            )
    return records


def write_index(root: str, output: str = "kai_public_index.json") -> None:
    records = build_index(Path(root).resolve())
    payload = {
        "index_name": "KAI_PUBLIC_SAFE_FILE_INDEX",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "file_count": len(records),
        "files": [asdict(record) for record in records],
    }
    Path(output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"KAI index written: {output} ({len(records)} files)")


if __name__ == "__main__":
    write_index(".")
