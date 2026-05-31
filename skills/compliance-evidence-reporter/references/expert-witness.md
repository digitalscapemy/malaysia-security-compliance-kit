# Expert-Witness Report

For an **independent expert report** tendered to a Malaysian court — distinct from the
defensive due-diligence report, which is a party's own evidence. Here the author is an *independent
expert* whose overriding duty is to the **court**, not to the party who instructs or pays them.

## Legal basis (Malaysia)

- **Evidence Act 1950, s. 45** — the opinion of a person "specially skilled" in a relevant field
  (here, information security / data protection) is a relevant fact. Your report is the vehicle for
  that opinion.
- The expert's **overriding duty is to assist the court** and to be **independent and impartial**,
  regardless of who instructed or pays. Malaysian practice (and persuasive English authority, e.g.
  the duties summarised in *The Ikarian Reefer* / CPR Part 35) requires the expert to state findings
  and opinions honestly, disclose the basis and any limitations, and not become an advocate for a
  party. Overclaiming or partisanship is the fastest way to have the opinion rejected.

> This is engineering guidance, not legal advice. Confirm the exact declaration wording and any
> court-specific practice directions with the instructing solicitors.

## What makes this report different from the due-diligence report

| | Defensive Due-Diligence | Expert-Witness |
|---|---|---|
| Author's role | The party (defendant) | Independent expert |
| Duty owed to | The party | **The court** (overriding) |
| Hallmark section | Posture statement | **Declaration of impartiality + duty to the court + statement of truth** |
| Tone | "we took reasonable measures" | "in my independent opinion…" |
| Privilege footer | Prepared in contemplation of litigation | None — an expert report is disclosed, not privileged |

## Required sections

1. **Title / introduction** — "Expert Report of [name]" in the matter, the court, who instructed.
2. **Qualifications** — credentials and experience establishing you as "specially skilled" (s. 45).
3. **Instructions and scope** — who instructed you, the questions you were asked, materials examined.
4. **Methodology** — how the assessment was done, tools and versions, the forensic-integrity
   statement (SHA-256, reproducible commands). Reuse the engine.
5. **Findings** — the factual technical findings.
6. **Opinion** — your independent opinion, grounded in the findings (the s. 45 opinion).
7. **Basis and limitations** — assumptions, what was and was not examined, the limits of the opinion.
8. **Evidence register (exhibits)** — hashed exhibits (`build_register.py` block output).
9. **Declaration and statement of truth** — duty to the court, impartiality, statement of truth,
   signature. This section is mandatory and load-bearing — see the template.

The shared engine (`hash_evidence.py` → `build_register.py` → `render_document.py`) is identical; only
the template and this framing change. Fill `assets/templates/expert-witness-report.md.tmpl` exactly as
you fill the due-diligence template (see `workflow.md`).
