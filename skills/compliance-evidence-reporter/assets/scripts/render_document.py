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
    print(f"rendered -> {outdir / 'report.docx'}{tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
