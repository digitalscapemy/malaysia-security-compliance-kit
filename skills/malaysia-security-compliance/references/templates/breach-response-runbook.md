# Data Breach Response Runbook — TEMPLATE

> Fill in `[BRACKETS]`. Keep this written and rehearsed **before** an incident. Maps to the PDPA
> (Amendment) 2024 breach-notification duty. **Not legal advice** — confirm timelines with your DPO/lawyer.

**Owner / DPO:** `[NAME, CONTACT, available 24/7?]`
**Last reviewed:** `[DATE]` · **Review cadence:** every `[6]` months

---

## Notification deadlines (PDPA 2024)

| Who | When | Condition |
|---|---|---|
| **Commissioner (JPDP)** | As soon as practicable, **≤ 72 hours** from the breach | If the breach causes or is **likely to cause significant harm** |
| **Affected data subjects** | Without undue delay, **≤ 7 days** after notifying the Commissioner | Same |
| **NCII Sector Lead + NACSA** (only if serving an NCII client) | Initial: immediate · Details: **≤ 6 hours** (NC4S) · Supplementary: **≤ 14 days** | Cyber Security Act 2024 |

> "Significant harm" is judged on data sensitivity, volume, and likelihood of misuse — when in doubt, notify.

---

## Phase 1 — Detect & triage (Hour 0)

- [ ] Record discovery time, reporter, what was observed
- [ ] Assign Incident Lead `[ROLE]`
- [ ] Classify severity `[P1/P2/P3]`
- [ ] **Start the 72-hour clock** — log the breach occurrence time

## Phase 2 — Contain (Hour 0–4)

- [ ] Isolate affected systems (revoke keys/tokens, block access, take offline if needed)
- [ ] **Preserve evidence** — snapshot logs, don't wipe; you'll need them
- [ ] Stop ongoing exfiltration
- [ ] Rotate compromised credentials/secrets

## Phase 3 — Assess (Hour 4–48)

- [ ] What data, how many subjects, what categories (any **sensitive** / biometric?)
- [ ] Root cause
- [ ] Likelihood of **significant harm** → decides notification
- [ ] Document the assessment + decision (and the reasoning) in writing

## Phase 4 — Notify (before Hour 72)

- [ ] **Commissioner** — submit via the JPDP channel: nature of breach, data & subjects affected, likely consequences, measures taken/planned, DPO contact
- [ ] **Data subjects** (≤ 7 days after Commissioner) — plain-language: what happened, what data, what they should do, your contact
- [ ] NCII client / sector lead if applicable
- [ ] Keep copies of every notification, timestamped

## Phase 5 — Recover

- [ ] Eradicate root cause; patch; restore from clean backup
- [ ] Verify integrity before bringing systems back
- [ ] Monitor for recurrence

## Phase 6 — Post-mortem

- [ ] Blameless write-up: timeline, root cause, what worked/didn't
- [ ] Remediation actions with owners + dates
- [ ] Update this runbook + controls
- [ ] File the full record in the evidence register

---

## Contact tree

| Role | Name | Contact |
|---|---|---|
| Incident Lead | `[ ]` | `[ ]` |
| DPO | `[ ]` | `[ ]` |
| Engineering on-call | `[ ]` | `[ ]` |
| Legal counsel | `[ ]` | `[ ]` |
| Client contact(s) | `[ ]` | `[ ]` |
| Commissioner (JPDP) channel | — | `[official submission URL/email]` |
