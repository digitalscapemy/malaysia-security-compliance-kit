<div align="center">

# Malaysia Security & Compliance Kit

### Ship software in Malaysia that survives both attackers *and* regulators.

A [Claude Code](https://claude.com/claude-code) plugin that bakes Malaysian law (**PDPA 2024**,
**Cyber Security Act 2024**) and security practice (**OWASP** web / API / mobile, secure SDLC,
infra & ops) directly into your build — and gives you the **documents to prove it.**

<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-8A63D2)](https://claude.com/claude-code)
[![PDPA 2024](https://img.shields.io/badge/PDPA-Amendment%202024-success)](skills/malaysia-security-compliance/references/01-malaysian-law.md)
[![Cyber Security Act 2024](https://img.shields.io/badge/Cyber%20Security%20Act-2024-success)](skills/malaysia-security-compliance/references/01-malaysian-law.md)
[![Jurisdiction: Malaysia](https://img.shields.io/badge/Jurisdiction-Malaysia-red)](#)

</div>

---

> ### ⚖️ Core principle: **evidence beats code.**
> Regulators and courts don't punish imperfect code alone — they punish the inability to **prove**
> due diligence. Every control in this kit has a matching artifact to keep, dated. Apply the controls
> **and** produce the documents. Code without paperwork still loses in court.

---

## Why this exists

Most security guides are written for the US/EU. Malaysian builders face a **different legal reality**:

- The **PDPA Amendment 2024** (full force **1 June 2025**) made **data processors directly liable** for
  the Security Principle — most dev shops, SaaS, and hosting providers. *You cannot contract this away.*
- The **Cyber Security Act 2024** (in force **26 August 2024**) adds duties for entities tied to
  National Critical Information Infrastructure.
- Breach notification, DPO thresholds, and cross-border transfer rules now carry **real penalties.**

This kit turns those obligations into concrete engineering controls and ready-to-file documents —
without you needing to reverse-engineer the statutes yourself.

## Who it's for

| You are… | This kit gives you… |
|---|---|
| 👩‍💻 A developer / dev shop | A pre-go-live gate and OWASP controls mapped to Malaysian law |
| 🏢 A SaaS / hosting operator | Your data-processor duties, spelled out, with the documents to satisfy them |
| 🔍 A security auditor | Control tables with a *"how to verify"* column for every item |
| ⚖️ An expert witness / legal advisor | The legal framework, penalties, and sources — plus *(coming soon)* a forensic-grade report engine |

---

## ✨ What's inside

The **`malaysia-security-compliance`** skill auto-activates on security reviews, PDPA / Cyber
Security Act questions, OWASP assessments, pre-go-live gates, and compliance-document drafting. It
routes to **only** the reference a task needs — never dumping everything at once.

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

## 🚀 Install

### Via plugin marketplace (recommended)

```bash
/plugin marketplace add digitalscapemy/malaysia-security-compliance-kit
/plugin install malaysia-security-compliance
```

### Manual

Copy the skill into your skills directory:

```bash
# Every project (user-level)
cp -r skills/malaysia-security-compliance ~/.claude/skills/

# A single project
cp -r skills/malaysia-security-compliance <project>/.claude/skills/
```

---

## 💬 Usage

Once installed, just work as normal — the skill activates itself. Try:

> *"Is this codebase PDPA compliant?"*
> *"Run a pre-go-live security gate on this repo."*
> *"Scan for hardcoded credentials and secrets in git history."*
> *"Draft a breach-response runbook for a SaaS handling 50,000 users."*
> *"Do I need to appoint a DPO?"*

It reads only the reference(s) the task needs, applies the controls, and points you at the matching
evidence artifact to keep.

---

## 🔧 Recommended scanning & pentest tools

The kit tells you *what* to check; these tools *prove* it. Run them, keep the output — each report is
a dated evidence artifact that defends the PDPA Security Principle (and feeds the forthcoming
evidence-reporter as a hashed exhibit). All four are free / open-source or have a free tier.

| Tool | Type | Use it to |
|---|---|---|
| [**OWASP ZAP**](https://www.zaproxy.org/) | DAST (dynamic) | Actively scan a *running* web app / API for injection, XSS, auth flaws, misconfig — the hands-on pentest proxy. Maps to `03-application-security.md`. |
| [**HostedScan**](https://hostedscan.com/) | Hosted vuln scanning | Run external, scheduled scans (OWASP ZAP / OpenVAS / Nmap) from outside your network and get shareable reports — good for *recurring* evidence and a third-party-looking artifact. |
| [**Nuclei**](https://github.com/projectdiscovery/nuclei) | Template-based scanner | Fast, CI-friendly checks against thousands of community templates (CVEs, exposures, misconfig). Drop it in your pipeline for continuous coverage. |
| [**Trivy**](https://trivy.dev/) | SCA / container / IaC / secrets | Scan dependencies, container images, IaC, and the filesystem for vulnerabilities **and secrets** — and generate an **SBOM**. Maps to `02-secure-build-playbook.md` (SCA + SBOM + hardcoded-credential scan). |

> **Coverage at a glance:** Trivy + Nuclei in CI for *continuous* build-time evidence; OWASP ZAP for
> *deep* manual web/API pentests; HostedScan for *scheduled external* scans. Keep every report, dated.

---

## 🗺️ Roadmap

The kit is evolving from a *knowledge* plugin into a full **compliance evidence & litigation toolkit**.

| Status | Capability |
|---|---|
| ✅ **Shipped** | `malaysia-security-compliance` skill — law + OWASP controls + document templates |
| 🚧 **In development** | `compliance-evidence-reporter` — forensic-grade engine that turns an assessment into **hashed evidence (SHA-256 + reproducible commands)** and a **court-ready `.docx` + `.pdf` Defensive Due-Diligence Report** |
| 📋 **Planned** | Expert-witness report (impartiality declaration) · Offensive gap-analysis · Incident / forensic report (72h/7d notification timeline) |

> Design spec: [`docs/specs/2026-05-31-evidence-reporter-design.md`](docs/specs/2026-05-31-evidence-reporter-design.md)

---

## 📚 Legal coverage

| Law | Status | In the kit |
|---|---|---|
| **PDPA 2010**, as amended by **Act A1727 (2024)** | Full force **1 June 2025** | Roles, 7 principles, DPO thresholds, breach notification, cross-border, penalties |
| **Cyber Security Act 2024** | In force **26 August 2024** | NCII duties, incident reporting |
| **Copyright Act 1987** | — | License/SBOM exposure (GPL, dependency provenance) |
| **Contracts Act 1950** | — | SOW, liability caps, DPA clauses |
| **Penal Code / Computer Crimes Act 1997** | — | Unauthorised access framing |

*Sources are cited at the bottom of each reference file.*

---

## ⚠️ Disclaimer

This is an **engineering kit, not legal advice.** It helps you build and document defensibly; it does
**not** replace a qualified Malaysian lawyer. Penalties, notification timelines, and DPO thresholds
must be confirmed with counsel before you rely on them.

**Last verified against Malaysian law:** PDPA (Amendment) Act 2024 in full force **1 June 2025**;
Cyber Security Act 2024 in force **26 August 2024**. Laws change — re-verify the cited sources in each
reference file before each engagement.

---

## 🤝 Contributing

Issues and pull requests welcome — especially:

- Updates when Malaysian law changes (with an official source).
- New control checks with a *"how to verify"* step.
- Additional fill-in document templates.

Keep the kit **portable and project-agnostic** — no client names, no stack-specific assumptions.

---

## 📄 License

[MIT](LICENSE) © [Digitalscape](https://github.com/digitalscapemy)

<div align="center">
<br>
<sub>Built for Malaysian builders who'd rather prove their diligence than explain its absence.</sub>
</div>
