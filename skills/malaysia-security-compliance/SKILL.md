---
name: malaysia-security-compliance
description: Use when building, reviewing, or launching any software, system, web app, mobile app, or API that handles user data in Malaysia — including security reviews and audits, PDPA 2024 or Cyber Security Act 2024 compliance checks, pre-go-live gates, OWASP web/API/mobile assessments, SQL-injection/path-traversal/secrets/access-control concerns, or drafting data-processing/breach/retention/sub-processor/security-policy documents.
---

# Malaysia Security & Compliance

## Overview

A reference kit for shipping software in Malaysia that survives both attackers and regulators. It
covers Malaysian law (PDPA Amendment 2024, Cyber Security Act 2024, Copyright, Contracts, Penal
Code) and security practice (OWASP web/API/mobile, secure SDLC, infra/ops).

**Core principle: _evidence beats code_.** Regulators and courts don't punish imperfect code alone —
they punish the inability to **prove** due diligence. Every control here has a matching artifact to
keep, dated. Apply the controls AND produce the documents.

## When to use

- Starting a new system / web app / mobile app / API that touches personal data
- Doing a security review or audit (someone asks "is this secure / compliant?")
- Questions about PDPA 2024, DPO appointment, data-breach notification, Cyber Security Act 2024
- Concerns about SQL injection, path traversal, secrets in repos, access control, file uploads, multi-tenant isolation
- Pre-go-live readiness check
- Drafting a DPA, breach runbook, retention policy, sub-processor register, or security policy

**When NOT to use:** pure local scripts with no user data, or non-Malaysia jurisdictions (the OWASP parts still apply; the legal parts don't).

## How to use — route to the right reference

Read **only** the reference file(s) the task needs (do not load all of them upfront):

| Task / question | Read |
|---|---|
| Legal duties, penalties, PDPA role, DPO threshold, breach timeline, cross-border | `references/01-malaysian-law.md` |
| Project setup, secrets, CI scanning, SBOM/license, testing, **pre-go-live gate** | `references/02-secure-build-playbook.md` |
| Web app or API controls (injection, access control, crypto, uploads, etc.) | `references/03-application-security.md` |
| Mobile app (iOS/Android/React Native/Flutter), MASVS, App Store/Play Store | `references/04-mobile-app-security.md` |
| Hosting, encryption-at-rest, backups, monitoring, incident response | `references/05-infrastructure-ops-security.md` |
| Need to produce a compliance document | `references/templates/` (fill the bracketed template) |

For an **audit**, verify against the control tables in `03`/`04` (each row has a "How to verify"),
then check the organisational duties in `01` §A.3 and the evidence register in `02` §7.

## The non-negotiables (fast check)

1. Parameterised queries only; whitelist any dynamic column/sort — never concat input into SQL.
2. Authorize every write server-side, **passing the resource** (not just "is logged in").
3. **No hardcoded credentials — MANDATORY scan every review.** Zero passwords, API keys, app keys, JWT/DB secrets, or default admin logins in source, seeders, config fallbacks, docs, or git history. Also confirm no DB dumps / `.env` / `*.pem` / `*.key` / backup files sit in (or are committable from) the working tree — `.env` and every dump/backup/scratch dir gitignored. This is the single dumbest, most common, most damaging finding; run the scan in `02` §2 on **every** build and review, not just at go-live.
4. Serve files via a storage abstraction keyed on a stored id — never a raw request path.
5. Encryption at rest (DB + storage + backups); TLS in transit; passwords bcrypt/argon2.
6. Audit trail on sensitive actions; never log PII/secrets.
7. SCA + SBOM/license scan in CI (defends dependency + GPL/copyright exposure).
8. Have the documents: DPA, breach runbook (72h/7d), retention policy, sub-processor register, DPO if over 20k/10k.

## Reminder

This is an engineering kit, not legal advice — confirm legal specifics with a qualified Malaysian
lawyer. Sources are cited at the bottom of `01-malaysian-law.md` and each reference file.
