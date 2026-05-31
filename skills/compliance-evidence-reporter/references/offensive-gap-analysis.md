# Offensive Gap-Analysis Report

For the **plaintiff / claimant side** — a structured analysis showing that another party's system or
conduct **fell below** the applicable security standard. The same forensic engine underpins it, but
the framing is adversarial: every finding is a **gap** between what the standard required and what was
observed, mapped to the law and supported by a hashed exhibit.

## When to use

- Acting for a data subject, regulator, or business asserting that a defendant failed the **PDPA 2010
  Security Principle** (as amended 2024) or fell below reasonable OWASP-aligned practice.
- You need to demonstrate, control by control, the deficiencies and their severity — and, where the
  instructions ask, how those deficiencies caused or contributed to the harm complained of.

## Independence still applies

Even on the plaintiff side, if this report is tendered as expert evidence the author owes the same
**overriding duty to the court** (Evidence Act 1950 s. 45; see `expert-witness.md`). Do not become an
advocate. State each gap factually, grade severity honestly, and disclose anything that cuts against
your client's case. An overstated gap analysis is discredited on the first contrary exhibit.

> Engineering guidance, not legal advice. **Causation** is ultimately for the court — confine any
> causation opinion to the technical contribution of the identified gaps, and confirm framing with the
> instructing solicitors.

## The core: the gap

Each row is one gap, measured against the standard:

| Field | Meaning |
|---|---|
| **Area** | The control area (e.g. transport security, access control, secrets handling) |
| **Required standard** | What the PDPA Security Principle / OWASP required, cited and dated |
| **Observed** | What was actually found, citing the hashed exhibit |
| **Gap & severity** | The deficiency and its grading (Critical / High / Medium / Low) |

## Required sections

1. **Introduction** — who instructs you, the system/conduct assessed, the standard applied.
2. **Applicable standard** — the benchmark (PDPA Security Principle + OWASP), as in force on a stated
   date, against which each control is measured.
3. **Methodology** — how assessed, materials examined, forensic-integrity statement (SHA-256, repro).
4. **Gap analysis** — the table above, one row per gap, each citing an exhibit.
5. **Severity and impact** — how the gaps expose personal data / breach the Security Principle.
6. **Causation / contribution** — the technical contribution of the gaps to the harm (carefully).
7. **Conclusion** — a plain summary: the system fell below the reasonable standard in N respects.
8. **Evidence register (exhibits)** — hashed exhibits (`build_register.py` block output).
9. **Declaration and statement of truth** — duty to the court, impartiality, statement of truth.

Fill `assets/templates/offensive-gap-analysis.md.tmpl` exactly as the other templates (see
`workflow.md`); the engine is identical.
