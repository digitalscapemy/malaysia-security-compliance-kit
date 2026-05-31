#!/usr/bin/env python3
"""Hash an evidence artifact and append it to the evidence register (forensic chain of custody).

Each record is one exhibit: SHA-256 of the file, when it was collected (ISO-8601 MYT), and the exact
command that produced it — so the opposing side can reproduce it. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MYT = timezone(timedelta(hours=8))
REQUIRED_FIELDS = (
    "id", "description", "source_file", "sha256", "size_bytes", "collected_at", "command",
)


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in chunks so large files don't exhaust memory."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_myt() -> str:
    """Current Malaysia time (UTC+8) as an ISO-8601 string to the second."""
    return datetime.now(MYT).isoformat(timespec="seconds")


def build_record(path: Path, description: str, command: str, timestamp: str) -> dict:
    """Build one evidence-register record (one exhibit) for the given artifact."""
    digest = sha256_file(path)
    return {
        "id": digest[:12],
        "description": description,
        "source_file": str(path).replace("\\", "/"),
        "sha256": digest,
        "size_bytes": path.stat().st_size,
        "collected_at": timestamp,
        "command": command,
    }


def append_record(record: dict, register_path: Path) -> None:
    """Append one record as a JSON line to the append-only register."""
    register_path.parent.mkdir(parents=True, exist_ok=True)
    with open(register_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hash an evidence artifact into the register.")
    parser.add_argument("--file", required=True, help="Path to the evidence artifact.")
    parser.add_argument("--description", required=True, help="What this exhibit is.")
    parser.add_argument("--command", required=True, help="The exact command that produced it.")
    parser.add_argument("--register", default="evidence-register.jsonl", help="Register path.")
    parser.add_argument("--timestamp", default=None, help="ISO-8601 override (default: now MYT).")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error: evidence file not found: {path}", file=sys.stderr)
        return 1

    record = build_record(path, args.description, args.command, args.timestamp or now_myt())
    append_record(record, Path(args.register))
    print(f"recorded {record['id']}  {record['sha256']}  {record['source_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
