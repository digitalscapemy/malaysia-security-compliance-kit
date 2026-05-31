# 01 — Malaysian Law You Must Comply With

Reference for any software/system/app handling user data in Malaysia. Penalties and duties are
current as of the 2024 amendments. **Verify with a lawyer before relying on any figure.**

---

## A. Personal Data Protection Act 2010, as amended by Act A1727 (PDPA Amendment 2024)

**Status:** Full implementation **1 June 2025** (phased from 1 Jan 2025). Regulator: Personal Data
Protection Commissioner / Jabatan Perlindungan Data Peribadi (JPDP).

### A.1 Know your role (decide this on day one)

| Role | Definition | Liability after 2024 |
|---|---|---|
| **Data Controller (Data User)** | Decides *why* and *how* data is processed | Always liable |
| **Data Processor** | Processes data **on behalf of** a controller — most dev shops / SaaS / hosting | **Now directly liable** for the Security Principle (NEW in 2024). You cannot contract this away. |

If you build, host, or operate a system touching a client's customer data, **assume you are a Data Processor** with direct statutory duties.

> **Sensitive Personal Data needs the strictest handling.** It covers data on **physical/mental health, biometric & genetic data, religious or other beliefs, political opinions, and the commission of offences**. If your app touches any of these (e.g. a clinic, HR, or fintech app, or biometric login), default to the most cautious controls AND note it hits the **lower DPO threshold of > 10,000 individuals** (see §A.3). **Sector-specific laws may also apply** beyond the PDPA — healthcare (MOH; Private Healthcare Facilities & Services Act 586; Telemedicine Act 1997), finance (Bank Negara Malaysia), telco/online (MCMC) — check your vertical.

### A.2 The 7 Data Protection Principles

| Principle | In practice |
|---|---|
| General | Process only with a lawful basis / consent, for the stated purpose |
| Notice & Choice | Privacy notice (BM + English) at/before collection |
| Disclosure | No disclosure outside the stated purpose |
| **Security** | Take *practical steps* to protect data — this is the whole of sections 02–05 |
| Retention | Don't keep data longer than necessary; delete it |
| Data Integrity | Keep data accurate, complete, current |
| Access | Let subjects access & correct their data |

### A.3 New duties from the 2024 amendment

- **Data Protection Officer (DPO):** mandatory where you process personal data of **> 20,000 individuals** OR sensitive personal data of **> 10,000 individuals**. DPO must be present in Malaysia ≥ 180 days/year (or easily contactable by authorities), proficient in BM + English, understand the PDPA. **Notify the Commissioner** of the appointment.
- **Data Breach Notification:** if a breach causes or is likely to cause **significant harm**, notify the Commissioner **as soon as practicable, no later than 72 hours** from the breach. Notify affected **data subjects without undue delay, within 7 days** after notifying the Commissioner. → You need a written runbook *before* a breach (see `templates/breach-response-runbook.md`).
- **Data portability:** export a subject's data and transfer to another controller on written request.
- **Biometric data is now Sensitive Personal Data** (fingerprint, face template, etc.), joining health, religious/belief, political-opinion and offence data → all require stricter handling and trigger the lower **10,000-individual** DPO threshold (see the callout in §A.1).
- **Cross-border transfer:** the old country "whitelist" is removed; transfers judged on comparable/adequate protection at destination. If you host outside Malaysia (most cloud), document the legal basis.

### A.4 Penalty

Breach of the Data Protection Principles: fine **up to RM1,000,000** and/or imprisonment **up to 3 years** (raised from RM300k / 2 years).

---

## B. Cyber Security Act 2024 (Act 854)

**Status:** In force **26 August 2024**. Regulator: NACSA.

Most ordinary SaaS is **not** directly regulated, but two triggers matter:

- **NCII flow-down.** If your client is a National Critical Information Infrastructure entity (banking, healthcare, energy, telco, government, transport, water, defence, etc.), the Act's duties cascade into your contract: annual cyber-risk assessment, audit at least once every 2 years, and **incident notification** — initial electronic notice immediately, details within **6 hours** via NC4S, supplementary within **14 days**. Build to that bar if you serve those sectors. **NCII status is by official designation** by the sector lead — not self-assessment — so if you serve healthcare/finance/energy/etc., confirm the client's NCII status rather than assuming.
- **Cyber Security Service Provider (CSP) licensing.** No person may **provide** a cyber security service (penetration testing, managed SOC, security risk assessment) or **advertise** as a CSP without a valid licence. Building a SaaS does *not* require this; *selling security services* does. Don't advertise services you aren't licensed for.

---

## C. Copyright Act 1987

- **s.41** — offences for infringing copies and **unauthorised modification / removal of copyright notices**. Penalty: fine **RM2,000–RM20,000 per infringing copy**, or imprisonment up to **5 years**, or both.
- **Engineering implication:** never paste licensed code (e.g. **GPL** / copyleft) into proprietary work, and never strip copyright/licence headers — including AI-generated snippets that may reproduce licensed code. Defend yourself with an **SBOM + license scan** (see `02` §4) and a committed `THIRD_PARTY_LICENSES` file.

---

## D. Contracts Act 1950

- **s.74** — damages for breach of contract: **General Damages** (foreseeable loss) + **Special Damages** (rebuild cost, recovery, reputational harm). Uncapped unless your contract caps it.
- **Engineering implication:** every engagement needs a **Scope of Work**, a **Limitation of Liability** clause, and a **DPA**. Without them, a single breach can expose you to the client's full reconstruction + reputation costs.

---

## E. Penal Code

- **s.417 (cheating)** — up to **5 years** and/or fine. **s.419 (cheating by personation)** — up to **7 years** and/or fine.
- **Engineering implication:** these are charged when a developer **misrepresents competence/qualifications** to win a project. Defence: **honest proposals** (don't overclaim) + **written UAT/acceptance sign-off** proving the client tested and accepted before go-live.

---

## Legal exposure map (quick reference)

| Law | Section | Triggered by | Primary mitigation |
|---|---|---|---|
| PDPA 2010 (Amd. 2024) | s.5 Security Principle | Failing to secure personal data | Controls in `02`–`05` + evidence register |
| PDPA 2010 (Amd. 2024) | DPO / breach duties | No DPO over threshold; late/no breach notice | §A.3 + `templates/breach-response-runbook.md` |
| Cyber Security Act 2024 | NCII / CSP licensing | Serving NCII clients; unlicensed security services | §B |
| Copyright Act 1987 | s.41 | Copying GPL code; stripping notices | SBOM + license scan (`02` §4) |
| Contracts Act 1950 | s.74 | Breach causing client loss | SOW + liability cap + DPA + PI insurance |
| Penal Code | s.417/419 | Misrepresenting competence | Honest proposals + UAT sign-off |

---

## Sources

- [PDPA (Amendment) Act 2024 — pdp.gov.my](https://www.pdp.gov.my/ppdpv1/en/akta/personal-data-protection-amendment-act-2024/) · [Act A1727 full text (PDF)](https://www.pdp.gov.my/ppdpv1/wp-content/uploads/2024/11/Act-A1727.pdf)
- [DPO thresholds & breach 72h (Skrine)](https://www.skrine.com/insights/alerts/february-2025/data-protection-officer-appointment-guidelines-dat) · [Effective 1 June 2025 (One Asia Lawyers)](https://oneasia.legal/en/6322)
- [Guidelines on DBN & DPO (DLA Piper)](https://privacymatters.dlapiper.com/2025/03/malaysia-guidelines-issued-on-data-breach-notification-and-data-protection-officer-appointment/)
- [Cross-border transfer + key amendments (Mayer Brown)](https://www.mayerbrown.com/en/insights/publications/2025/07/from-legislative-reform-to-practical-guidance-key-amendments-to-malaysias-pdpa-and-the-launch-of-cross-border-transfer-guidelines)
- [Cyber Security Act 2024 (Act 854) — NACSA](https://www.nacsa.gov.my/act854.php) · [Act 854 overview (PwC Malaysia, PDF)](https://www.pwc.com/my/en/assets/publications/2024/pwc-my-cyber-security-act-2024-new-era-for-cybersecurity-in-malaysia.pdf)
