# Compliance Evidence & Court-Document Reporter — Design

**Date:** 2026-05-31
**Status:** Approved design (Phase 1 to build)
**Repo:** `digitalscapemy/malaysia-security-compliance-kit`

## Purpose

Extend the kit from a *knowledge* plugin (controls + law) into one that also **produces
forensic-grade evidence and court-ready documents** to support Malaysian litigation. The
existing `malaysia-security-compliance` skill stays the knowledge base; a new
`compliance-evidence-reporter` skill turns an assessment into hashed evidence and a filed-quality
`.docx` + `.pdf`.

Core principle carried over: **evidence beats code.** The plugin's job is to make due diligence
*provable* — every finding mapped to law, every exhibit hashed, every command reproducible.

## Decisions locked during brainstorming

| Question | Decision |
|---|---|
| Court postures supported | All four (defensive, expert-witness, offensive, incident) — **built in phases** |
| Output format | Court-ready `.docx` **and** `.pdf` |
| Evidence input | Auto-assess the codebase/system **plus** manual evidence intake |
| Evidentiary rigor | **Forensic-grade**: SHA-256 + timestamp + reproducible command per exhibit; methodology + impartiality declaration; dated law versions; append-only register |
| Architecture | **Approach A** — skill orchestrates judgment; bundled Python scripts own the deterministic, court-critical parts (hash, register, render) |
| Render engine | **Pandoc** single pipeline: PDF via a bespoke **LaTeX** template; DOCX via a styled **reference.docx** |
| Build scope | **Phased** — engine + one document (Defensive Due-Diligence) first |

## Architecture (Approach A)

Deterministic where a court can challenge it (hashing, formatting, reproducibility); Claude's
judgment where reasoning is required (finding the issues, mapping to law, writing the narrative).

```
skills/malaysia-security-compliance/      ← existing knowledge skill — UNCHANGED
skills/compliance-evidence-reporter/      ← NEW
    SKILL.md                              ← routing, when-to-use, short workflow
    references/
        workflow.md                       ← end-to-end: assess → hash → fill → render
        forensic-integrity.md             ← hashing, timestamps, chain of custody, reproducibility rules
        document-types.md                 ← the 4 document types; when each applies; required sections
    assets/
        templates/
            defensive-due-diligence.md.tmpl   ← Phase 1 document body (placeholdered Markdown)
            reference.docx                    ← Word styling (numbered headings, fonts, table styles)
            court-document.latex              ← LaTeX template for the PDF (typography, numbering, headers)
        scripts/
            hash_evidence.py                  ← SHA-256 + timestamp + provenance → evidence-register.jsonl
            build_register.py                 ← validate register, assign exhibit numbers, emit summary table
            render_document.py                ← filled .md → .docx + .pdf via pandoc
        tests/
            test_hash_evidence.py
            test_build_register.py
            test_render_smoke.py
            fixtures/                         ← tiny fake "system" + expected register for the golden test
```

### Component responsibilities

| Component | Responsibility | Type |
|---|---|---|
| Assessment engine | Claude runs the existing skill's controls against the codebase → `findings.jsonl` (id, title, severity, OWASP/PDPA mapping, evidence ref, status) | Claude judgment |
| `hash_evidence.py` | Given a file (or stdin) + the command that produced it, compute SHA-256, stamp ISO-8601 MYT time, append one record to `evidence-register.jsonl` | Deterministic script |
| `build_register.py` | Validate the register (reject malformed/duplicate exhibit ids), assign exhibit numbers (A-1, A-2…), emit a summary table for the report | Deterministic script |
| `render_document.py` | Convert filled `.md` → `.docx` (pandoc + `reference.docx`) and `.pdf` (pandoc + `court-document.latex`); fail loudly if a cited exhibit file is missing or a renderer is absent | Deterministic script |
| Templates | Placeholdered Markdown + the two styling templates | Data |

## Phase 1 document: Defensive Due-Diligence Report

Proves "reasonable security measures were taken" under the PDPA 2024 Security Principle. Sections:

1. **Cover page** — title, party, document ref/version, date, privilege marker (*"CONFIDENTIAL —
   Prepared in Contemplation of Litigation"*), prepared by.
2. **Executive summary** — posture statement: reasonable measures taken.
3. **Scope & methodology** — what was assessed, when, tools + versions, the forensic-integrity
   statement (reproducible commands, hashing).
4. **Legal framework** — PDPA 2024 Security Principle + Cyber Security Act 2024 duties, mapped
   (cites `malaysia-security-compliance/references/01-malaysian-law.md`).
5. **Controls implemented** — table: control → evidence (exhibit ref) → date → status.
6. **Findings & remediation** — gaps found + remediation + dates (shows continuing diligence).
7. **Evidence register / exhibits** — hashed exhibit table (A-1…): description, SHA-256, timestamp,
   source command.
8. **Declaration** — preparer statement, signature block, date.
9. **Appendices** — raw command outputs as exhibits.

## Forensic integrity rules (the differentiator)

- Every exhibit is SHA-256 hashed at collection; the hash is printed beside the exhibit in the report.
- Every exhibit records the exact command that produced it → opposing side can reproduce it.
- Timestamps are ISO-8601 with timezone (MYT).
- Law citations carry the version + *"as in force on <date>"* + source URL.
- The register is append-only JSONL; altering a file changes its hash (tamper-evident).
- The methodology section declares tools, versions, and an impartiality / limitations statement.

## Data flow

```
1. Claude assesses (existing skill controls)         → findings.jsonl
2. Each evidence artifact → hash_evidence.py          → evidence-register.jsonl (sha256, ts, cmd, exhibit#)
3. build_register.py     → validated register + exhibit numbers + summary table
4. Claude fills defensive-due-diligence.md.tmpl from findings + register
5. render_document.py filled.md                       → report.docx + report.pdf
6. Output bundle: /evidence/ (raw artifacts) + evidence-register.jsonl + report.docx + report.pdf
```

## Error handling

- Missing pandoc / LaTeX → `render_document.py` exits non-zero with install instructions; never
  emits a half-formed document.
- Evidence file cited but missing at render time → hard error (cannot cite an exhibit that is absent).
- Re-verification hash mismatch → flagged, not silently accepted.
- `build_register.py` rejects duplicate exhibit ids or malformed JSONL lines rather than renumbering silently.

## Testing

- **Unit:** `hash_evidence.py` — same input → same SHA-256 (determinism); record shape correct.
  `build_register.py` — rejects malformed/duplicate ids, assigns exhibit numbers in order.
- **Smoke:** `render_document.py` — produces a valid `.docx` and `.pdf` from a fixture filled `.md`.
  (Skips with a clear message if pandoc/LaTeX absent, so the suite is informative on bare machines.)
- **Golden end-to-end:** a tiny fixture "system" → run the workflow → assert the report contains the
  exhibit table with the expected hashes.

Tests use Python's `unittest` (stdlib) so they run without extra dependencies; rendering tests guard
on tool availability.

## Phasing

- **Phase 1 (now):** engine (`hash_evidence`, `build_register`) + `render_document` + the two render
  templates + Defensive Due-Diligence template + tests + wire the skill into the plugin marketplace.
- **Phase 2:** expert-witness report template + `references/expert-witness.md` (impartiality
  declaration, expert's duty to the court).
- **Phase 3:** offensive gap-analysis template (proving the other side fell below the standard).
- **Phase 4:** incident/forensic report template (timeline, breach scope, 72h/7d notification).

## Out of scope (YAGNI for Phase 1)

- The three later document types (Phases 2–4).
- Remote/manual-only intake mode (primary mode is auto-assess + manual supplement).
- Any CI/automation packaging of the engine.
- Digital signing / PKI of the PDF (signature block is a printed block; cryptographic signing is a
  later consideration if a court requires it).

## Dependencies introduced

- **pandoc** (document conversion) and a LaTeX engine (e.g. TeX Live / MiKTeX) for PDF — declared in
  the skill's prerequisites with install guidance; scripts fail loudly if absent.
- Python 3 standard library only for the scripts and tests (no pip dependencies), keeping the engine
  portable and the hashing path dependency-free.
