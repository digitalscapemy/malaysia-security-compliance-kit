<div align="center">

# Malaysia Security & Compliance Kit

### Ship software in Malaysia that survives both attackers *and* regulators — then prove it in court.

A [Claude Code](https://claude.com/claude-code) plugin that bakes Malaysian law (**PDPA 2024**,
**Cyber Security Act 2024**) and security practice (**OWASP** web / API / mobile, secure SDLC,
infra & ops) into your build — and turns an assessment into **hashed evidence and court-ready
`.docx` + `.pdf` reports.**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.4.0-blue)](#️-roadmap)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-8A63D2)](https://claude.com/claude-code)
[![PDPA 2024](https://img.shields.io/badge/PDPA-Amendment%202024-success)](skills/malaysia-security-compliance/references/01-malaysian-law.md)
[![Cyber Security Act 2024](https://img.shields.io/badge/Cyber%20Security%20Act-2024-success)](skills/malaysia-security-compliance/references/01-malaysian-law.md)
[![Jurisdiction: Malaysia](https://img.shields.io/badge/Jurisdiction-Malaysia-red)](#)

</div>

---

> ### ⚖️ Core principle: **evidence beats code.**
> Regulators and courts don't punish imperfect code alone — they punish the inability to **prove**
> due diligence. Every control here has a matching artifact to keep, dated and hashed. Apply the
> controls **and** produce the documents. Code without paperwork still loses in court.

---

## Why this exists

Most security guides are written for the US/EU. Malaysian builders face a **different legal reality**:

- The **PDPA Amendment 2024** (full force **1 June 2025**) made **data processors directly liable**
  for the Security Principle — most dev shops, SaaS, and hosting providers. *You cannot contract this
  away.*
- The **Cyber Security Act 2024** (in force **26 August 2024**) adds duties for entities tied to
  National Critical Information Infrastructure.
- Breach notification, DPO thresholds, and cross-border transfer rules now carry **real penalties.**

This kit turns those obligations into concrete engineering controls **and** the dated, hashed
evidence you need to defend — or prove — a case.

## The two skills

The plugin ships two skills that work together: one tells you *what* to do, the other *proves* you did it.

| Skill | What it is |
|---|---|
| 🛡️ **`malaysia-security-compliance`** | The **knowledge kit** — Malaysian law + OWASP web/API/mobile controls + secure-SDLC + fill-in compliance documents. Auto-activates on security reviews, PDPA questions, OWASP assessments, and pre-go-live gates. |
| 📑 **`compliance-evidence-reporter`** | The **evidence engine** — turns an assessment into a SHA-256 chain-of-custody register and a **court-ready `.docx` + `.pdf`** report, in four document types. |

## Who it's for

| You are… | This kit gives you… |
|---|---|
| 👩‍💻 A developer / dev shop | A pre-go-live gate and OWASP controls mapped to Malaysian law |
| 🏢 A SaaS / hosting operator | Your data-processor duties, spelled out, with the documents to satisfy them |
| 🔍 A security auditor | Control tables with a *"how to verify"* column, plus a hashed evidence register |
| ⚖️ An expert witness / legal advisor | The legal framework **and** a forensic engine that produces court-ready expert, defence, plaintiff, and breach reports |

---

## 🛡️ The knowledge skill — what's inside

`malaysia-security-compliance` routes to **only** the reference a task needs — never dumping
everything at once.

| 📄 Reference | Covers |
|---|---|
| [`01-malaysian-law.md`](skills/malaysia-security-compliance/references/01-malaysian-law.md) | Legal duties, penalties, PDPA role, DPO threshold, breach timeline, cross-border transfer, sources |
| [`02-secure-build-playbook.md`](skills/malaysia-security-compliance/references/02-secure-build-playbook.md) | Secure SDLC: secrets, **hardcoded-credential scan**, CI scanning, SBOM/license, testing, evidence register, pre-go-live gate |
| [`03-application-security.md`](skills/malaysia-security-compliance/references/03-application-security.md) | OWASP **Web + API** Top 10 — control table with *how to verify* |
| [`04-mobile-app-security.md`](skills/malaysia-security-compliance/references/04-mobile-app-security.md) | OWASP **Mobile** Top 10 + MASVS + iOS / Android + App Store / Play Store compliance |
| [`05-infrastructure-ops-security.md`](skills/malaysia-security-compliance/references/05-infrastructure-ops-security.md) | Encryption-at-rest, backups, hardening, monitoring, incident response |
| 📁 [`templates/`](skills/malaysia-security-compliance/references/templates) | Fill-in documents: **DPA**, **breach runbook**, **retention policy**, **sub-processor register**, **security policy** |

### The non-negotiables (fast check)

1. **Parameterised queries only** — whitelist any dynamic column/sort; never concat input into SQL.
2. **Authorize every write server-side**, passing the resource — not just *"is logged in"*.
3. **No hardcoded credentials** — scan every build & review (the single most common, most damaging finding).
4. **Serve files via a storage abstraction** keyed on a stored id — never a raw request path.
5. **Encryption at rest** (DB + storage + backups); **TLS** in transit; passwords bcrypt/argon2.
6. **Audit trail** on sensitive actions; never log PII/secrets.
7. **SCA + SBOM/license scan** in CI.
8. **Have the documents** — DPA, breach runbook (72h/7d), retention policy, sub-processor register, DPO if over the threshold.

---

## 📑 The evidence engine — court-ready reports

`compliance-evidence-reporter` turns an assessment into **provable evidence** and a **court-ready
document**. It is forensic by design: every exhibit is SHA-256 hashed at collection and recorded with
the exact command that produced it, so the report survives cross-examination.

**How it works** — three standard-library Python scripts do the deterministic work; Claude does the
assessment and legal mapping:

```
hash_evidence.py   →   build_register.py   →   render_document.py
SHA-256 + MYT          validate + number       Markdown template
timestamp + the        exhibits (A-1, A-2)      → .docx + .pdf
exact command          + exhibit blocks         via pandoc + xelatex
```

**Four document types, one engine** — pick the template for your posture:

| Document | Posture | Hallmark |
|---|---|---|
| **Defensive Due-Diligence** | Defendant | "reasonable security measures were taken" (PDPA Security Principle) |
| **Expert-Witness Report** | Independent | duty-to-court declaration + statement of truth (**Evidence Act 1950 s.45**) |
| **Offensive Gap-Analysis** | Plaintiff | graded gap table (Critical/High/Medium/Low) vs PDPA/OWASP |
| **Incident / Forensic Report** | Either | breach timeline + scope + **72h / 7-day notification record** |

Each report carries a cover, table of contents, the relevant analysis, a **hashed exhibit register**,
and a signed declaration — typeset in a clean modern font with a header/footer on every page. Full
procedure: [`workflow.md`](skills/compliance-evidence-reporter/references/workflow.md); document
specifics: [`document-types.md`](skills/compliance-evidence-reporter/references/document-types.md).

**Render prerequisites:** Python 3.10+, [pandoc](https://pandoc.org/installing.html) + a LaTeX engine
with **xelatex** (TeX Live / MiKTeX) for PDF, and the **Inter** font (or change `mainfont` in the
template). The scripts fail loudly with install guidance if a tool is missing.

---

## 🚀 Install

### Via plugin marketplace (recommended)

```bash
/plugin marketplace add digitalscapemy/malaysia-security-compliance-kit
/plugin install malaysia-security-compliance
```

This installs both skills. For PDF/DOCX rendering, also install pandoc + xelatex + Inter (see above).

### Manual

```bash
# Every project (user-level) — copy both skills
cp -r skills/malaysia-security-compliance skills/compliance-evidence-reporter ~/.claude/skills/

# A single project
cp -r skills/malaysia-security-compliance skills/compliance-evidence-reporter <project>/.claude/skills/
```

---

## 💬 Usage

Once installed, just work as normal — the skills activate themselves. Try:

> *"Is this codebase PDPA compliant?"*
> *"Run a pre-go-live security gate on this repo."*
> *"Scan for hardcoded credentials and secrets in git history."*
> *"Draft a breach-response runbook for a SaaS handling 50,000 users."*
> *"Produce a court-ready due-diligence report with hashed evidence for this codebase."*
> *"Write an expert-witness report on whether this system met the PDPA Security Principle."*

The knowledge skill reads only the reference a task needs and points you at the evidence artifact to
keep; the engine hashes that evidence and renders the report.

---

## 🔧 Recommended scanning & pentest tools

The kit tells you *what* to check; these tools *prove* it. Run them, keep the output — each report is
a dated evidence artifact that defends the PDPA Security Principle (and feeds the
`compliance-evidence-reporter` as a hashed exhibit). All four are free / open-source or have a free tier.

| Tool | Type | Use it to |
|---|---|---|
| [**OWASP ZAP**](https://www.zaproxy.org/) | DAST (dynamic) | Actively scan a *running* web app / API for injection, XSS, auth flaws, misconfig — the hands-on pentest proxy. Maps to `03-application-security.md`. |
| [**HostedScan**](https://hostedscan.com/) | Hosted vuln scanning | Run external, scheduled scans (OWASP ZAP / OpenVAS / Nmap) from outside your network and get shareable reports — good for *recurring* evidence and a third-party-looking artifact. |
| [**Nuclei**](https://github.com/projectdiscovery/nuclei) | Template-based scanner | Fast, CI-friendly checks against thousands of community templates (CVEs, exposures, misconfig). Drop it in your pipeline for continuous coverage. |
| [**Trivy**](https://trivy.dev/) | SCA / container / IaC / secrets | Scan dependencies, container images, IaC, and the filesystem for vulnerabilities **and secrets** — and generate an **SBOM**. Maps to `02-secure-build-playbook.md`. |

> **Coverage at a glance:** Trivy + Nuclei in CI for *continuous* build-time evidence; OWASP ZAP for
> *deep* manual web/API pentests; HostedScan for *scheduled external* scans. Keep every report, dated.

---

## 🗺️ Roadmap

| Status | Capability |
|---|---|
| ✅ **Shipped** | `malaysia-security-compliance` — law + OWASP controls + fill-in document templates |
| ✅ **Shipped** | `compliance-evidence-reporter` — forensic engine: hashed evidence (SHA-256 + reproducible commands) → court-ready `.docx` + `.pdf` |
| ✅ **Shipped** | **All four document types** — Defensive Due-Diligence · Expert-Witness · Offensive Gap-Analysis · Incident / Forensic |
| 🔭 **Next** | Cryptographic PDF signing · per-document polish · the same engine for new jurisdictions |

> Design spec & plan live in [`docs/`](docs/).

---

## 📚 Legal coverage

| Law | Status | In the kit |
|---|---|---|
| **PDPA 2010**, as amended by **Act A1727 (2024)** | Full force **1 June 2025** | Roles, 7 principles, DPO thresholds, breach notification (72h/7d), cross-border, penalties |
| **Cyber Security Act 2024** | In force **26 August 2024** | NCII duties, incident reporting |
| **Evidence Act 1950 (s. 45)** | — | Basis for expert opinion in the Expert-Witness & Gap-Analysis reports |
| **Copyright Act 1987** | — | License/SBOM exposure (GPL, dependency provenance) |
| **Contracts Act 1950** | — | SOW, liability caps, DPA clauses |
| **Penal Code / Computer Crimes Act 1997** | — | Unauthorised access framing |

*Sources are cited at the bottom of each reference file.*

---

## ⚠️ Disclaimer

This is an **engineering kit, not legal advice.** It helps you build and document defensibly; it does
**not** replace a qualified Malaysian lawyer. Penalties, notification timelines, DPO thresholds, the
"significant harm" breach threshold, and the exact wording of expert declarations must be confirmed
with counsel before you rely on them.

**Last verified against Malaysian law:** PDPA (Amendment) Act 2024 in full force **1 June 2025**;
Cyber Security Act 2024 in force **26 August 2024**. Laws change — re-verify the cited sources in each
reference file before each engagement, and cite the version and date you relied on in every report.

---

## 🤝 Contributing

Issues and pull requests welcome — especially:

- Updates when Malaysian law changes (with an official source).
- New control checks with a *"how to verify"* step.
- Additional document templates on the shared engine.

Keep the kit **portable and project-agnostic** — no client names, no stack-specific assumptions.

---

## 📄 License

[MIT](LICENSE) © [Digitalscape](https://github.com/digitalscapemy)

<div align="center">
<br>
<sub>Built for Malaysian builders who'd rather prove their diligence than explain its absence.</sub>
</div>
