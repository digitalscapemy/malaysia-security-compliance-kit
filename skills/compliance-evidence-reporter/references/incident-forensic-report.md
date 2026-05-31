# Incident / Forensic Report

For a **data-breach or security-incident report** — the timeline-driven account of what happened,
what data was affected, how it was contained, and whether the **PDPA breach-notification duties** were
met. It serves both the **regulator** (Personal Data Protection Commissioner / JPDP) and, if the
matter is litigated, the **court**. Built on the same forensic engine.

## When to use

- After a confirmed or suspected personal-data breach, to document the incident defensibly.
- To evidence that the **breach-notification timeline** was met (the most common compliance failure).

## PDPA breach-notification duties (mirror the kit)

If a breach **causes or is likely to cause significant harm**:

- **Notify the Commissioner (JPDP)** as soon as practicable, **no later than 72 hours** from the breach.
- **Notify affected data subjects** without undue delay, **within 7 days** after notifying the
  Commissioner.

Record the exact times you became aware, contained, and notified — these are the facts a regulator
checks first. See `malaysia-security-compliance/references/01-malaysian-law.md` and
`templates/breach-response-runbook.md`.

> Engineering guidance, not legal advice. The "significant harm" threshold and exact prescribed
> period are legal determinations — confirm with counsel and the current JPDP guidance. Cite the
> version you relied on and the date it was in force.

## Forensic timeline discipline

The timeline is the spine of this report and the first thing scrutinised. Every entry should carry a
timestamp (ISO-8601, MYT) and, where possible, a hashed exhibit (a log line, an alert, an email). A
timeline backed by hashed, reproducible exhibits survives challenge; a narrative one does not.

## Required sections

1. **Summary** — one paragraph: what happened, when detected, scale, current status.
2. **Incident timeline** — chronological table: detection → triage → containment → investigation →
   notification → remediation. Each row timestamped, citing an exhibit where possible.
3. **Scope and affected data** — systems affected, categories and volume of personal data, number of
   data subjects, whether **sensitive personal data** was involved (raises the stakes and thresholds).
4. **Root cause** — the technical cause, evidenced.
5. **Containment and remediation** — actions taken and dates; what stops recurrence.
6. **Notification record** — who was notified, the deadline, when actually notified, and how — the
   compliance proof for the 72h / 7-day duties.
7. **Evidence register (exhibits)** — hashed exhibits (`build_register.py` block output).
8. **Declaration and statement of truth** — the preparer attests the account and exhibits are true.

Fill `assets/templates/incident-forensic-report.md.tmpl` exactly as the other templates
(see `workflow.md`); the engine is identical.
