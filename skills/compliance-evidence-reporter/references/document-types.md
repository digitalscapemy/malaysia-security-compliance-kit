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
