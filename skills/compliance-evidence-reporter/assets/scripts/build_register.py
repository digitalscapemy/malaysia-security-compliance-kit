#!/usr/bin/env python3
"""Validate the evidence register and assign exhibit numbers (A-1, A-2 ...).

Reads the append-only JSONL register, rejects malformed or duplicate records, assigns exhibit
numbers in collection order, and emits a Markdown summary table for the report. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = (
    "id", "description", "source_file", "sha256", "size_bytes", "collected_at", "command",
)


class RegisterError(Exception):
    """Raised when the register is malformed, incomplete, or has duplicate evidence."""


def load_register(path: Path) -> list:
    """Load JSONL records; raise RegisterError on any malformed line."""
    records = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RegisterError(f"malformed JSON on line {lineno}: {exc}") from exc
    return records


def validate(records: list) -> None:
    """Raise RegisterError on missing fields or duplicate SHA-256 (same evidence recorded twice)."""
    seen: dict = {}
    for index, rec in enumerate(records):
        missing = [f for f in REQUIRED_FIELDS if f not in rec]
        if missing:
            raise RegisterError(f"record {index} missing fields: {', '.join(missing)}")
        sha = rec["sha256"]
        if sha in seen:
            raise RegisterError(
                f"duplicate evidence: record {index} repeats sha256 of record {seen[sha]}"
            )
        seen[sha] = index


def assign_exhibits(records: list, prefix: str = "A") -> list:
    """Return copies of records with an 'exhibit' label assigned in order: A-1, A-2, ..."""
    out = []
    for number, rec in enumerate(records, start=1):
        enriched = dict(rec)
        enriched["exhibit"] = f"{prefix}-{number}"
        out.append(enriched)
    return out


def _escape_cell(value: str) -> str:
    """Escape characters that would break a Markdown table cell."""
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def summary_table(records: list) -> str:
    """Render a Markdown exhibit table from records that already carry an 'exhibit' label."""
    lines = [
        "| Exhibit | Description | SHA-256 | Collected (MYT) | Source command |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| {rec['exhibit']} | {_escape_cell(rec['description'])} | `{rec['sha256']}` | "
            f"{rec['collected_at']} | `{_escape_cell(rec['command'])}` |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the register and build the exhibit table.")
    parser.add_argument("--register", default="evidence-register.jsonl")
    parser.add_argument("--prefix", default="A", help="Exhibit prefix (default A → A-1, A-2 ...).")
    parser.add_argument("--out-summary", default=None, help="Write the Markdown table here.")
    parser.add_argument("--out-validated", default=None, help="Write the numbered register (JSONL) here.")
    args = parser.parse_args(argv)

    try:
        records = load_register(Path(args.register))
        validate(records)
    except RegisterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    numbered = assign_exhibits(records, args.prefix)
    table = summary_table(numbered)

    if args.out_summary:
        Path(args.out_summary).write_text(table, encoding="utf-8")
    else:
        print(table)

    if args.out_validated:
        with open(args.out_validated, "w", encoding="utf-8") as handle:
            for rec in numbered:
                handle.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
