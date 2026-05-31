# Compliance Evidence Reporter — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `compliance-evidence-reporter` skill — a forensic-grade engine that turns a security/compliance assessment into a hashed, chain-of-custody evidence register and a court-ready `.docx` + `.pdf` **Defensive Due-Diligence Report**.

**Architecture:** Approach A — the skill (Markdown) orchestrates Claude's *judgment* (running controls, writing findings, mapping to law); three standard-library Python scripts own the *deterministic, court-critical* parts: `hash_evidence.py` (SHA-256 + timestamp + provenance), `build_register.py` (validate + assign exhibit numbers + summary table), `render_document.py` (Markdown → `.docx` + `.pdf` via pandoc). A Markdown document template carries placeholders Claude fills.

**Tech Stack:** Python 3.10 (standard library only — no pip deps); `unittest` for tests; **pandoc** + **xelatex** as external render tools (declared prerequisites, scripts fail loudly if absent). Lives in the `digitalscapemy/malaysia-security-compliance-kit` repo alongside the existing `malaysia-security-compliance` skill.

**Spec:** `docs/specs/2026-05-31-evidence-reporter-design.md`

**Deliberate deviation from spec (documented):** The spec named a standalone `court-document.latex` template fork. This plan instead puts PDF styling in the document template's YAML `header-includes` (fancyhdr header/footer with party, doc-ref, "Page X of Y", privilege footer) rendered by xelatex, plus a generated `reference.docx` for Word. Same court-grade output, far less fragile than maintaining a forked pandoc template. Flag to the user at review.

**Working directory:** all paths are relative to the repo root `C:\xampp\htdocs\malaysia-security-compliance-kit`. Run every command from there.

---

## File Structure

```
skills/compliance-evidence-reporter/
    SKILL.md                                  ← routing + when-to-use + workflow (Task 1)
    references/
        workflow.md                           ← end-to-end procedure (Task 6)
        forensic-integrity.md                 ← hashing / chain-of-custody / reproducibility rules (Task 6)
        document-types.md                     ← the 4 doc types; sections required for each (Task 6)
    assets/
        templates/
            defensive-due-diligence.md.tmpl   ← Phase 1 document body + YAML styling (Task 5)
            reference.docx                    ← Word styling baseline, generated (Task 5)
        scripts/
            hash_evidence.py                  ← Task 2
            build_register.py                 ← Task 3
            render_document.py                ← Task 4
        tests/
            test_hash_evidence.py             ← Task 2
            test_build_register.py            ← Task 3
            test_render_document.py           ← Task 4
            test_golden_e2e.py                ← Task 7
```

**Test command (run from repo root):**
```bash
python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_*.py" -v
```

---

## Task 1: Scaffold the skill (SKILL.md)

**Files:**
- Create: `skills/compliance-evidence-reporter/SKILL.md`

- [ ] **Step 1: Create the skill directory and SKILL.md**

Create `skills/compliance-evidence-reporter/SKILL.md` with exactly:

```markdown
---
name: compliance-evidence-reporter
description: Use when producing a forensic-grade security or compliance evidence report, or a court-ready document for Malaysian litigation or regulator submission — assessing a codebase, hashing evidence artifacts (SHA-256 + reproducible commands) into a chain-of-custody register, and rendering a Defensive Due-Diligence Report to court-ready .docx and .pdf. Pairs with the malaysia-security-compliance skill.
---

# Compliance Evidence Reporter

## Overview

Turns a security/compliance assessment into **provable** evidence and a court-ready document.
Knowledge of *what* to check lives in the `malaysia-security-compliance` skill; this skill is the
**evidence + document engine** built on top of it.

**Core principle: _evidence beats code_.** Every finding is mapped to law; every exhibit is hashed
(SHA-256) with the exact command that produced it, so the opposing side can reproduce it.

## When to use

- Someone needs a **due-diligence / "we took reasonable measures" report** for a PDPA matter, a
  breach investigation, a customer audit, or litigation.
- You need a **chain-of-custody evidence register** (hashed exhibits) from a codebase assessment.
- You need court-ready `.docx` + `.pdf`, not just notes.

**When NOT to use:** quick "is this secure?" questions with no document deliverable — use
`malaysia-security-compliance` directly.

## Prerequisites

- Python 3.10+ (scripts use the standard library only).
- **pandoc** (https://pandoc.org/installing.html) and a LaTeX engine with **xelatex** (TeX Live or
  MiKTeX) for PDF output. The render script fails loudly with install guidance if either is absent.

## Workflow (summary — full detail in references/workflow.md)

1. **Assess** with the `malaysia-security-compliance` controls → write findings.
2. **Collect & hash** each evidence artifact:
   `python assets/scripts/hash_evidence.py --file <artifact> --description "..." --command "<cmd>"`
3. **Build the register:**
   `python assets/scripts/build_register.py --register evidence-register.jsonl --out-summary exhibits.md --out-validated register-numbered.jsonl`
4. **Fill** `assets/templates/defensive-due-diligence.md.tmpl` from the findings + `exhibits.md`.
5. **Render:**
   `python assets/scripts/render_document.py --input filled.md --outdir out --reference-docx assets/templates/reference.docx --register register-numbered.jsonl`

## Forensic rules (full detail in references/forensic-integrity.md)

- Hash every exhibit at collection; print the hash beside it in the report.
- Record the exact command per exhibit (reproducible).
- ISO-8601 timestamps with timezone (MYT, +08:00).
- Cite laws with version + "as in force on <date>" + source URL.
- The register is append-only; altering a file changes its hash (tamper-evident).

## Reminder

This is an engineering kit, not legal advice. Confirm legal specifics with a qualified Malaysian
lawyer. See `references/document-types.md` for the other report types (expert-witness, offensive,
incident) planned on this same engine.
```

- [ ] **Step 2: Verify the file exists and is well-formed**

Run: `python -c "import pathlib,sys; p=pathlib.Path('skills/compliance-evidence-reporter/SKILL.md'); sys.exit(0 if p.is_file() and p.read_text(encoding='utf-8').startswith('---') else 1)"`
Expected: exit 0 (no output).

- [ ] **Step 3: Commit**

```bash
git add skills/compliance-evidence-reporter/SKILL.md
git commit -m "feat(reporter): scaffold compliance-evidence-reporter skill"
```

---

## Task 2: `hash_evidence.py` — hash an artifact into the register

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/hash_evidence.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_hash_evidence.py`

- [ ] **Step 1: Write the failing test**

Create `skills/compliance-evidence-reporter/assets/tests/test_hash_evidence.py`:

```python
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import hash_evidence as he  # noqa: E402


class HashEvidenceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.artifact = self.dir / "artifact.txt"
        self.artifact.write_text("nginx tls config\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_sha256_is_deterministic_and_correct(self):
        expected = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.assertEqual(he.sha256_file(self.artifact), expected)
        self.assertEqual(he.sha256_file(self.artifact), he.sha256_file(self.artifact))

    def test_build_record_shape(self):
        rec = he.build_record(self.artifact, "Nginx TLS", "cp x y", "2026-05-31T14:00:00+08:00")
        for field in he.REQUIRED_FIELDS:
            self.assertIn(field, rec)
        self.assertEqual(rec["id"], rec["sha256"][:12])
        self.assertEqual(rec["size_bytes"], self.artifact.stat().st_size)
        self.assertEqual(rec["collected_at"], "2026-05-31T14:00:00+08:00")

    def test_append_writes_one_json_line_each_call(self):
        register = self.dir / "reg.jsonl"
        rec = he.build_record(self.artifact, "d", "c", "2026-05-31T14:00:00+08:00")
        he.append_record(rec, register)
        he.append_record(rec, register)
        lines = register.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["sha256"], rec["sha256"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_hash_evidence.py" -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'hash_evidence'`.

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/hash_evidence.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_hash_evidence.py" -v`
Expected: PASS (3 tests OK).

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/hash_evidence.py skills/compliance-evidence-reporter/assets/tests/test_hash_evidence.py
git commit -m "feat(reporter): hash_evidence.py — SHA-256 chain-of-custody records"
```

---

## Task 3: `build_register.py` — validate + number exhibits + summary table

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/build_register.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_build_register.py`

- [ ] **Step 1: Write the failing test**

Create `skills/compliance-evidence-reporter/assets/tests/test_build_register.py`:

```python
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_register as br  # noqa: E402


def make_record(sha, description="d", command="c"):
    return {
        "id": sha[:12], "description": description, "source_file": "evidence/x",
        "sha256": sha, "size_bytes": 1, "collected_at": "2026-05-31T14:00:00+08:00",
        "command": command,
    }


class LoadRegisterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "reg.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_rejects_malformed_line(self):
        self.path.write_text('{"ok": 1}\nNOT JSON\n', encoding="utf-8")
        with self.assertRaises(br.RegisterError):
            br.load_register(self.path)

    def test_load_skips_blank_lines(self):
        self.path.write_text('{"a":1}\n\n{"b":2}\n', encoding="utf-8")
        self.assertEqual(len(br.load_register(self.path)), 2)


class ValidateTest(unittest.TestCase):
    def test_rejects_missing_field(self):
        with self.assertRaises(br.RegisterError):
            br.validate([{"sha256": "a" * 64}])

    def test_rejects_duplicate_sha256(self):
        sha = "a" * 64
        with self.assertRaises(br.RegisterError):
            br.validate([make_record(sha), make_record(sha)])

    def test_accepts_distinct_valid_records(self):
        br.validate([make_record("a" * 64), make_record("b" * 64)])  # must not raise


class ExhibitTest(unittest.TestCase):
    def test_assigns_numbers_in_order(self):
        numbered = br.assign_exhibits([make_record("a" * 64), make_record("b" * 64)])
        self.assertEqual(numbered[0]["exhibit"], "A-1")
        self.assertEqual(numbered[1]["exhibit"], "A-2")

    def test_summary_table_contains_exhibit_and_hash(self):
        numbered = br.assign_exhibits([make_record("a" * 64, description="Nginx TLS")])
        table = br.summary_table(numbered)
        self.assertIn("A-1", table)
        self.assertIn("Nginx TLS", table)
        self.assertIn("a" * 64, table)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_build_register.py" -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_register'`.

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/build_register.py`:

```python
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


def summary_table(records: list) -> str:
    """Render a Markdown exhibit table from records that already carry an 'exhibit' label."""
    lines = [
        "| Exhibit | Description | SHA-256 | Collected (MYT) | Source command |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| {rec['exhibit']} | {rec['description']} | `{rec['sha256']}` | "
            f"{rec['collected_at']} | `{rec['command']}` |"
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_build_register.py" -v`
Expected: PASS (7 tests OK).

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/build_register.py skills/compliance-evidence-reporter/assets/tests/test_build_register.py
git commit -m "feat(reporter): build_register.py — validate + number exhibits + summary table"
```

---

## Task 4: `render_document.py` — Markdown → .docx + .pdf via pandoc

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/render_document.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_render_document.py`

- [ ] **Step 1: Write the failing test**

Create `skills/compliance-evidence-reporter/assets/tests/test_render_document.py`:

```python
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import render_document as rd  # noqa: E402


class RequireToolTest(unittest.TestCase):
    def test_missing_tool_raises(self):
        with self.assertRaises(rd.RenderError):
            rd.require_tool("definitely-not-a-real-tool-xyz")


class VerifyExhibitsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.evidence = self.dir / "evidence"
        self.evidence.mkdir()
        self.register = self.dir / "reg.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_raises_when_exhibit_file_absent(self):
        self.register.write_text(
            '{"source_file": "evidence/missing.conf", "id": "x"}\n', encoding="utf-8"
        )
        with self.assertRaises(rd.RenderError):
            rd.verify_exhibits(self.register, self.evidence)

    def test_passes_when_exhibit_present(self):
        (self.evidence / "present.conf").write_text("ok", encoding="utf-8")
        self.register.write_text(
            '{"source_file": "evidence/present.conf", "id": "x"}\n', encoding="utf-8"
        )
        rd.verify_exhibits(self.register, self.evidence)  # must not raise


@unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
class PandocSmokeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.md = self.dir / "doc.md"
        self.md.write_text("# Title\n\nHello **world**.\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_docx_is_produced(self):
        out = self.dir / "report.docx"
        rd.run_pandoc_docx(self.md, out, None)
        self.assertTrue(out.is_file() and out.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_render_document.py" -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'render_document'`.

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/render_document.py`:

```python
#!/usr/bin/env python3
"""Render a filled Markdown report into court-ready .docx and .pdf via pandoc.

Deterministic: same Markdown in, same documents out. Fails loudly if pandoc or the PDF engine is
missing, or if a cited evidence file is absent. Standard library only (shells out to pandoc).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


class RenderError(Exception):
    """Raised when a prerequisite tool or a cited exhibit is missing, or pandoc fails."""


def require_tool(name: str) -> str:
    """Return the path to a required executable or raise RenderError with install guidance."""
    found = shutil.which(name)
    if not found:
        raise RenderError(
            f"required tool '{name}' not found on PATH. Install it:\n"
            f"  pandoc  -> https://pandoc.org/installing.html\n"
            f"  xelatex -> TeX Live (Linux/macOS) or MiKTeX (Windows)"
        )
    return found


def verify_exhibits(register_path: Path, evidence_dir: Path) -> None:
    """Raise RenderError if any record's source_file is missing — can't cite an absent exhibit."""
    for raw in register_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        rec = json.loads(line)
        named = Path(rec["source_file"])
        if not named.is_file() and not (evidence_dir / named.name).is_file():
            label = rec.get("exhibit", rec.get("id", "?"))
            raise RenderError(f"cited exhibit missing: {rec['source_file']} ({label})")


def _run(cmd: list) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RenderError(f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr}")


def run_pandoc_docx(input_md: Path, out_docx: Path, reference_docx: Path | None) -> None:
    """Render Markdown → .docx, applying the Word styling template if provided."""
    cmd = [require_tool("pandoc"), str(input_md), "-o", str(out_docx)]
    if reference_docx and reference_docx.is_file():
        cmd += ["--reference-doc", str(reference_docx)]
    _run(cmd)


def run_pandoc_pdf(input_md: Path, out_pdf: Path, engine: str = "xelatex") -> None:
    """Render Markdown → .pdf using the given LaTeX engine (styling comes from the doc's YAML)."""
    require_tool(engine)
    cmd = [require_tool("pandoc"), str(input_md), "-o", str(out_pdf), f"--pdf-engine={engine}"]
    _run(cmd)


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a filled report to .docx + .pdf.")
    parser.add_argument("--input", required=True, help="Filled Markdown report.")
    parser.add_argument("--outdir", default="out", help="Output directory.")
    parser.add_argument("--reference-docx", default=None, help="Word styling template (.docx).")
    parser.add_argument("--register", default=None, help="If set, verify each exhibit file exists.")
    parser.add_argument("--evidence-dir", default="evidence", help="Where exhibit files live.")
    parser.add_argument("--pdf-engine", default="xelatex")
    parser.add_argument("--skip-pdf", action="store_true", help="Render only .docx.")
    args = parser.parse_args(argv)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    input_md = Path(args.input)

    try:
        if args.register:
            verify_exhibits(Path(args.register), Path(args.evidence_dir))
        ref = Path(args.reference_docx) if args.reference_docx else None
        run_pandoc_docx(input_md, outdir / "report.docx", ref)
        if not args.skip_pdf:
            run_pandoc_pdf(input_md, outdir / "report.pdf", args.pdf_engine)
    except RenderError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    tail = "" if args.skip_pdf else f" + {outdir / 'report.pdf'}"
    print(f"rendered → {outdir / 'report.docx'}{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_render_document.py" -v`
Expected: PASS — `RequireToolTest` + `VerifyExhibitsTest` run (3 tests); `PandocSmokeTest` runs if pandoc is installed, otherwise reports `skipped 'pandoc not installed'`. Either way: no failures.

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/render_document.py skills/compliance-evidence-reporter/assets/tests/test_render_document.py
git commit -m "feat(reporter): render_document.py — Markdown to court-ready .docx/.pdf via pandoc"
```

---

## Task 5: Document template + Word styling baseline

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/templates/defensive-due-diligence.md.tmpl`
- Create: `skills/compliance-evidence-reporter/assets/templates/reference.docx` (generated)

- [ ] **Step 1: Create the document template**

Create `skills/compliance-evidence-reporter/assets/templates/defensive-due-diligence.md.tmpl`.
Placeholders are `{{UPPER_SNAKE}}` — Claude replaces every one when filling. The YAML block carries
the PDF styling (header/footer via fancyhdr + xelatex):

```markdown
---
title: "Defensive Due-Diligence Report"
subtitle: "Reasonable Security Measures under the PDPA 2010 (as amended by Act A1727, 2024) Security Principle"
author: "{{PREPARER_NAME}}, {{PREPARER_TITLE}}"
date: "{{REPORT_DATE}}"
documentclass: report
geometry: margin=1in
fontsize: 11pt
mainfont: "Times New Roman"
toc: true
numbersections: true
header-includes: |
  \usepackage{fancyhdr}
  \usepackage{lastpage}
  \pagestyle{fancy}
  \fancyhf{}
  \fancyhead[L]{\small {{PARTY_NAME}}}
  \fancyhead[R]{\small Doc Ref: {{DOC_REF}}}
  \fancyfoot[C]{\footnotesize CONFIDENTIAL — Prepared in Contemplation of Litigation}
  \fancyfoot[R]{\small Page \thepage\ of \pageref{LastPage}}
  \renewcommand{\headrulewidth}{0.4pt}
  \renewcommand{\footrulewidth}{0.4pt}
---

\thispagestyle{empty}

**CONFIDENTIAL — PREPARED IN CONTEMPLATION OF LITIGATION**

**Party:** {{PARTY_NAME}}
**Document reference:** {{DOC_REF}} (version {{DOC_VERSION}})
**Prepared by:** {{PREPARER_NAME}}, {{PREPARER_TITLE}}
**Date:** {{REPORT_DATE}}

\newpage

# 1. Executive summary

{{EXECUTIVE_SUMMARY}}

This report sets out the security measures implemented by {{PARTY_NAME}} in respect of
{{SYSTEM_NAME}}, and the evidence supporting each, to demonstrate that reasonable steps were taken to
protect personal data in accordance with the PDPA Security Principle.

# 2. Scope and methodology

**Scope of assessment:** {{SCOPE_DESCRIPTION}}

**Assessment window:** {{ASSESSMENT_START}} to {{ASSESSMENT_END}} (MYT).

**Tools and versions:** {{TOOLS_AND_VERSIONS}}

**Forensic integrity:** Every item of evidence in this report was hashed with SHA-256 at the time of
collection and recorded with the exact command that produced it, enabling independent reproduction.
Timestamps are ISO-8601 with Malaysian time zone (+08:00). The evidence register is append-only; any
alteration to an exhibit changes its hash and is therefore detectable. See §6 (Evidence Register).

**Limitations and impartiality:** {{LIMITATIONS_STATEMENT}}

# 3. Legal framework

The applicable obligations are summarised below and assessed as in force on {{LAW_AS_OF_DATE}}.

{{LEGAL_FRAMEWORK}}

> Sources: see the cited references in the accompanying assessment. This report is engineering
> evidence and does not constitute legal advice.

# 4. Controls implemented

| Control | Evidence (exhibit) | Date | Status |
|---|---|---|---|
{{CONTROLS_TABLE_ROWS}}

# 5. Findings and remediation

{{FINDINGS_AND_REMEDIATION}}

# 6. Evidence register (exhibits)

The following exhibits are referenced above. Each is hashed (SHA-256) and reproducible via the stated
command.

{{EXHIBIT_TABLE}}

# 7. Declaration

I, {{PREPARER_NAME}}, confirm that the assessment described in this report was carried out as stated,
that the exhibits listed in §6 are true copies of the artifacts collected, and that the SHA-256
hashes recorded were computed from those artifacts at the time of collection.

\vspace{2cm}

Signed: ______________________________

Name: {{PREPARER_NAME}}

Title: {{PREPARER_TITLE}}

Date: {{REPORT_DATE}}

# Appendix A — Raw exhibit contents

{{APPENDIX_RAW_EXHIBITS}}
```

- [ ] **Step 2: Generate the Word styling baseline (reference.docx)**

This produces a valid baseline `.docx` style that a lawyer can later refine in Word. Requires pandoc;
if pandoc is not yet installed, install it first (the file must be committed for the renderer's
`--reference-docx` flag to work).

Run: `pandoc --print-default-data-file reference.docx > skills/compliance-evidence-reporter/assets/templates/reference.docx`

- [ ] **Step 3: Verify both template files exist**

Run: `python -c "import pathlib,sys; d=pathlib.Path('skills/compliance-evidence-reporter/assets/templates'); sys.exit(0 if (d/'defensive-due-diligence.md.tmpl').is_file() and (d/'reference.docx').stat().st_size>0 else 1)"`
Expected: exit 0.

- [ ] **Step 4: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/templates/
git commit -m "feat(reporter): defensive due-diligence template + Word styling baseline"
```

---

## Task 6: Reference docs (workflow, forensic-integrity, document-types)

**Files:**
- Create: `skills/compliance-evidence-reporter/references/workflow.md`
- Create: `skills/compliance-evidence-reporter/references/forensic-integrity.md`
- Create: `skills/compliance-evidence-reporter/references/document-types.md`

- [ ] **Step 1: Create `references/workflow.md`**

```markdown
# Workflow — assessment to court-ready document

End-to-end procedure for the Defensive Due-Diligence Report. Run all commands from the directory
holding your working evidence (create a per-matter folder, e.g. `matter-acme/`).

## 1. Assess
Use the `malaysia-security-compliance` skill to run the controls against the codebase/system. For
each control, decide: implemented / partial / gap. Capture the *proof* of each as a file in
`evidence/` (a command output, a config excerpt, a policy PDF).

## 2. Hash each exhibit
For every artifact, record it with the exact command that produced it:

    python <skill>/assets/scripts/hash_evidence.py \
      --file evidence/nginx-tls.conf \
      --description "Nginx TLS configuration (TLS 1.3 only)" \
      --command "openssl s_client -connect host:443 | tee evidence/nginx-tls.conf"

Repeat for every exhibit. The register `evidence-register.jsonl` grows append-only.

## 3. Build the register
    python <skill>/assets/scripts/build_register.py \
      --register evidence-register.jsonl \
      --out-summary exhibits.md \
      --out-validated register-numbered.jsonl

This assigns exhibit numbers (A-1, A-2 ...) and writes the Markdown table to `exhibits.md`.

## 4. Fill the template
Copy `assets/templates/defensive-due-diligence.md.tmpl` to `filled.md` and replace every
`{{PLACEHOLDER}}`. Paste the `exhibits.md` table into `{{EXHIBIT_TABLE}}`. Build the
`{{CONTROLS_TABLE_ROWS}}` so each control cites its exhibit (e.g. "see Exhibit A-3").

## 5. Render
    python <skill>/assets/scripts/render_document.py \
      --input filled.md --outdir out \
      --reference-docx <skill>/assets/templates/reference.docx \
      --register register-numbered.jsonl

Outputs `out/report.docx` and `out/report.pdf`. The `--register` flag makes the renderer refuse to
proceed if any cited exhibit file is missing.

## 6. Bundle
Deliver: `out/report.docx`, `out/report.pdf`, `evidence-register.jsonl`, and the `evidence/` folder.
Keep the bundle dated and unaltered.
```

- [ ] **Step 2: Create `references/forensic-integrity.md`**

```markdown
# Forensic integrity rules

What makes this report survive cross-examination. Apply all of these.

1. **Hash at collection.** Compute SHA-256 the moment you capture an artifact, before any editing.
   The hash in the report must match the file in the bundle.
2. **Record the command.** Every exhibit stores the exact command that produced it. If the other
   side runs it and gets the same output, your evidence stands.
3. **Timestamps with zone.** ISO-8601 + `+08:00` (MYT). Never bare dates.
4. **Append-only register.** Never edit or reorder `evidence-register.jsonl`. Add new lines only.
   Re-running `build_register.py` re-derives exhibit numbers deterministically.
5. **Dated law.** Cite each obligation with its version and "as in force on <date>" plus a source
   URL. Laws change; pin the version you relied on.
6. **No tampering.** If you must redact PII inside an exhibit, do it visibly, record the redaction as
   its own step with its own command, and hash the redacted version as a separate exhibit.
7. **Impartiality.** State your limitations and what was *not* assessed. Overclaiming destroys
   credibility faster than a gap.

A claim without a hashed, reproducible exhibit is an assertion, not evidence.
```

- [ ] **Step 3: Create `references/document-types.md`**

```markdown
# Document types

The engine (hash → register → render) is shared; each document type is a different template and a
different framing. Phase 1 ships the first; the rest are planned on the same spine.

| Type | Posture | Purpose | Status |
|---|---|---|---|
| **Defensive Due-Diligence Report** | Defendant | Prove reasonable security measures were taken (PDPA Security Principle) | Phase 1 — shipped |
| **Expert-Witness Report** | Independent | Technical findings + methodology + impartiality declaration + expert's duty to the court | Planned |
| **Offensive Gap-Analysis** | Plaintiff | Show the other side fell below the PDPA/OWASP standard | Planned |
| **Incident / Forensic Report** | Either | Timeline, breach scope, affected data, 72h/7d notification record, remediation | Planned |

All four reuse `hash_evidence.py`, `build_register.py`, and `render_document.py`. Adding a type =
adding a template + (where needed) a reference describing its required sections.
```

- [ ] **Step 4: Verify the three files exist**

Run: `python -c "import pathlib,sys; d=pathlib.Path('skills/compliance-evidence-reporter/references'); sys.exit(0 if all((d/f).is_file() for f in ['workflow.md','forensic-integrity.md','document-types.md']) else 1)"`
Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/references/
git commit -m "docs(reporter): workflow, forensic-integrity, and document-types references"
```

---

## Task 7: Golden end-to-end test

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/tests/test_golden_e2e.py`

- [ ] **Step 1: Write the test**

Create `skills/compliance-evidence-reporter/assets/tests/test_golden_e2e.py`. It exercises the whole
data pipeline (hash → load → validate → number → table) without external tools, then does a guarded
pandoc render:

```python
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_register as br  # noqa: E402
import hash_evidence as he  # noqa: E402
import render_document as rd  # noqa: E402


class GoldenPipelineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.evidence = self.dir / "evidence"
        self.evidence.mkdir()
        (self.evidence / "nginx.conf").write_text("ssl_protocols TLSv1.3;\n", encoding="utf-8")
        self.register = self.dir / "evidence-register.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_hash_to_table_pipeline(self):
        rec = he.build_record(
            self.evidence / "nginx.conf",
            "Nginx TLS configuration",
            "cp /etc/nginx/nginx.conf evidence/nginx.conf",
            "2026-05-31T14:00:00+08:00",
        )
        he.append_record(rec, self.register)

        records = br.load_register(self.register)
        br.validate(records)
        numbered = br.assign_exhibits(records)
        table = br.summary_table(numbered)

        self.assertEqual(numbered[0]["exhibit"], "A-1")
        self.assertIn("Nginx TLS configuration", table)
        self.assertIn(rec["sha256"], table)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
    def test_render_produces_docx(self):
        filled = self.dir / "filled.md"
        filled.write_text(
            "# Defensive Due-Diligence Report\n\n## Exhibits\n\n"
            "| Exhibit | Description |\n|---|---|\n| A-1 | Nginx TLS configuration |\n",
            encoding="utf-8",
        )
        out = self.dir / "report.docx"
        rd.run_pandoc_docx(filled, out, None)
        self.assertTrue(out.is_file() and out.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the full test suite**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_*.py" -v`
Expected: all tests PASS; pandoc-dependent tests show `skipped` if pandoc is absent. Zero failures, zero errors.

- [ ] **Step 3: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/tests/test_golden_e2e.py
git commit -m "test(reporter): golden end-to-end pipeline test"
```

---

## Task 8: Wire into the plugin + prove it works + flip the roadmap

**Files:**
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`

- [ ] **Step 1: Bump the marketplace version and mention both skills**

In `.claude-plugin/marketplace.json`, change the top-level `metadata.version` and the plugin entry's
`version` from `"1.0.0"` to `"1.1.0"`, and append to the plugin entry's `description` so it reads:

```
"description": "Build, review, and launch software in Malaysia that survives both attackers and regulators. Includes the malaysia-security-compliance knowledge skill and the compliance-evidence-reporter forensic evidence + court-ready document engine.",
```

- [ ] **Step 2: Verify the marketplace JSON is valid and both skills are discoverable**

Run: `python -c "import json; json.load(open('.claude-plugin/marketplace.json', encoding='utf-8')); print('json ok')"`
Run: `python -c "import pathlib,sys; s=pathlib.Path('skills'); names=sorted(p.name for p in s.iterdir() if p.is_dir()); print(names); sys.exit(0 if 'compliance-evidence-reporter' in names and 'malaysia-security-compliance' in names else 1)"`
Expected: `json ok`, then a list containing both skill names, exit 0.

- [ ] **Step 3: Produce a real sample report as proof (requires pandoc + xelatex)**

This is the verification-before-completion gate. If pandoc/xelatex are not installed, install them
first — do not skip and do not claim "shipped" without a rendered artifact.

```bash
mkdir -p /tmp/ddr-proof/evidence
printf 'ssl_protocols TLSv1.3;\n' > /tmp/ddr-proof/evidence/nginx.conf
cd /tmp/ddr-proof
python "$OLDPWD/skills/compliance-evidence-reporter/assets/scripts/hash_evidence.py" \
  --file evidence/nginx.conf --description "Nginx TLS configuration" \
  --command "cp /etc/nginx/nginx.conf evidence/nginx.conf"
python "$OLDPWD/skills/compliance-evidence-reporter/assets/scripts/build_register.py" \
  --register evidence-register.jsonl --out-summary exhibits.md --out-validated register-numbered.jsonl
```

Then build a minimal `filled.md` from the template (replace placeholders with sample text, paste
`exhibits.md` into the exhibit table), and render:

```bash
python "$OLDPWD/skills/compliance-evidence-reporter/assets/scripts/render_document.py" \
  --input filled.md --outdir out \
  --reference-docx "$OLDPWD/skills/compliance-evidence-reporter/assets/templates/reference.docx" \
  --register register-numbered.jsonl
```

Confirm `out/report.docx` and `out/report.pdf` both exist and open. Do not commit the proof bundle.

- [ ] **Step 4: Flip the roadmap row to shipped**

In `README.md`, in the Roadmap table, move `compliance-evidence-reporter` from the `🚧 In development`
row to a `✅ Shipped` row:

```
| ✅ **Shipped** | `compliance-evidence-reporter` — forensic-grade engine: assessment → hashed evidence (SHA-256 + reproducible commands) → court-ready `.docx` + `.pdf` Defensive Due-Diligence Report |
```

Leave the `📋 Planned` row (expert-witness, offensive, incident) unchanged.

- [ ] **Step 5: Run the full suite one last time, then commit and push**

Run: `python -m unittest discover -s skills/compliance-evidence-reporter/assets/tests -p "test_*.py" -v`
Expected: zero failures, zero errors.

```bash
git add .claude-plugin/marketplace.json README.md
git commit -m "feat(reporter): ship compliance-evidence-reporter — bump to 1.1.0, update roadmap"
git push
```

---

## Self-review notes

- **Spec coverage:** assessment engine (Task 1 SKILL + Task 6 workflow); `hash_evidence.py` (Task 2);
  `build_register.py` (Task 3); `render_document.py` (Task 4); templates incl. forensic header/footer
  (Task 5); forensic rules (Task 6); error handling (loud-fail in Task 4, duplicate/malformed reject
  in Task 3, missing-exhibit reject in Task 4); unit + golden tests (Tasks 2–4, 7); phasing &
  doc-types (Task 6 document-types.md); plugin wiring + proof (Task 8). Phases 2–4 are explicitly out
  of scope per the spec.
- **Deviation:** PDF styling via the template's YAML `header-includes` + xelatex instead of a forked
  `court-document.latex` — documented at the top and in Task 5.
- **Type/name consistency:** `RegisterError`, `RenderError`, `sha256_file`,
  `build_record`, `append_record`, `load_register`, `validate`, `assign_exhibits`, `summary_table`,
  `require_tool`, `verify_exhibits`, `run_pandoc_docx`, `run_pandoc_pdf` — used identically across
  scripts and tests. `REQUIRED_FIELDS` defined in both `hash_evidence` and `build_register` (same
  tuple, intentional — each script is independently runnable with no shared import).
```
