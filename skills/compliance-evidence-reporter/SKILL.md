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
- The PDF template sets `mainfont: "Inter"` (a clean modern sans). Install Inter, or change the
  `mainfont` line in `assets/templates/defensive-due-diligence.md.tmpl` to a font you have
  (e.g. `Open Sans`, `Arial`) — xelatex errors if the named font is missing.

## Workflow (summary — full detail in references/workflow.md)

1. **Assess** with the `malaysia-security-compliance` controls → write findings.
2. **Collect & hash** each evidence artifact:
   `python assets/scripts/hash_evidence.py --file <artifact> --description "..." --command "<cmd>"`
3. **Build the register:**
   `python assets/scripts/build_register.py --register evidence-register.jsonl --out-summary exhibits.md --out-validated register-numbered.jsonl`
4. **Fill** a template from the findings + `exhibits.md` (paste the table into `{{EXHIBIT_TABLE}}`):
   - `assets/templates/defensive-due-diligence.md.tmpl` — a party proving reasonable measures, or
   - `assets/templates/expert-witness-report.md.tmpl` — an independent expert report (Evidence Act
     1950 s.45; impartiality declaration), or
   - `assets/templates/offensive-gap-analysis.md.tmpl` — a plaintiff-side gap analysis showing the
     other party fell below the standard, or
   - `assets/templates/incident-forensic-report.md.tmpl` — a data-breach / incident report (timeline,
     scope, 72h/7d notification record). See `references/document-types.md` and the matching
     `references/*.md` for each type.
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
