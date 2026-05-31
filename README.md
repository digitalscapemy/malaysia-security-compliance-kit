# Malaysia Security & Compliance Kit

A [Claude Code](https://claude.com/claude-code) skill for shipping software in **Malaysia** that
survives both attackers and regulators. It covers Malaysian law (PDPA Amendment 2024, Cyber Security
Act 2024, Copyright, Contracts, Penal Code) and security practice (OWASP web/API/mobile, secure SDLC,
infra/ops) — plus ready-to-fill compliance documents.

**Core principle: _evidence beats code_.** Regulators and courts don't punish imperfect code alone —
they punish the inability to **prove** due diligence. Every control here has a matching artifact to
keep, dated. Apply the controls AND produce the documents.

## What's inside

The skill auto-triggers on security reviews, PDPA / Cyber Security Act questions, OWASP assessments,
pre-go-live gates, and compliance-document drafting. It routes to:

| Reference | Covers |
|---|---|
| `01-malaysian-law.md` | Legal duties, penalties, PDPA role, DPO threshold, breach timeline, cross-border |
| `02-secure-build-playbook.md` | Secure SDLC: secrets, hardcoded-credential scan, CI scanning, SBOM, testing, pre-go-live gate |
| `03-application-security.md` | OWASP Web + API Top 10 — control table with "how to verify" |
| `04-mobile-app-security.md` | OWASP Mobile Top 10 + MASVS + iOS/Android + App Store / Play Store |
| `05-infrastructure-ops-security.md` | Encryption-at-rest, backups, hardening, monitoring, incident response |
| `templates/` | Fill-in documents: DPA, breach runbook, retention policy, sub-processor register, security policy |

## Install

### Via plugin marketplace (recommended)

```
/plugin marketplace add digitalscapemy/malaysia-security-compliance-kit
/plugin install malaysia-security-compliance
```

### Manual

Copy `skills/malaysia-security-compliance/` into your skills directory:

- `~/.claude/skills/` — available in every project
- `<project>/.claude/skills/` — that project only

## Usage

Once installed, just work as normal. Ask things like *"is this secure / PDPA compliant?"*, *"run a
pre-go-live gate"*, or *"draft a breach runbook"* — the skill activates and routes to the right
reference. It reads only the file(s) a task needs, not all of them.

## Disclaimer

This is an **engineering kit, not legal advice.** It helps you build and document defensibly; it does
not replace a qualified Malaysian lawyer. Confirm legal specifics — penalties, notification timelines,
DPO thresholds — with counsel before relying on them.

**Last verified against Malaysian law:** PDPA (Amendment) Act 2024 in full force 1 June 2025; Cyber
Security Act 2024 in force 26 August 2024. Laws change — re-verify the cited sources in each reference
file before each engagement.

## License

[MIT](LICENSE) © Digitalscape
