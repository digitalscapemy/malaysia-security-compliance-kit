# Information Security Policy — TEMPLATE

> A short, real policy is worth more than a long unused one. This evidences the PDPA Security
> Principle (organisational measures). Fill `[BRACKETS]`. Keep it to a few pages.

**Organisation:** `[NAME]` · **Owner:** `[DPO/CTO]` · **Last reviewed:** `[DATE]` · **Cadence:** annual

---

## 1. Purpose & scope
Defines how `[ORG]` protects personal and confidential data across all systems, apps, and staff.

## 2. Roles
- **DPO:** `[NAME]` — accountable for PDPA compliance (appointed where over the 20k/10k threshold).
- **Security owner:** `[NAME]` — owns controls + incident response.
- **All staff/contractors:** bound by confidentiality; complete `[annual]` security awareness.

## 3. Access control
- Least privilege; access granted by role, reviewed `[quarterly]`.
- **MFA** on all production, cloud, CI/CD, DB, and registrar access.
- Access revoked within `[24h]` of offboarding; secrets rotated.

## 4. Data protection
- Encryption in transit (TLS 1.2+) and **at rest** (DB, storage, backups).
- Secrets in a manager/vault, never in source.
- Data classified `[public / internal / confidential / sensitive]`; sensitive (incl. biometric) gets the strictest handling.
- Retention & deletion per the Retention Policy.

## 5. Secure development
- Follow the Secure Build Playbook (`02`): code review, SAST, SCA, secret scanning, SBOM/license scan, tests.
- No secrets in repos; CI blocks on HIGH/CRITICAL findings.
- External pentest before major releases of PII-handling systems.

## 6. Operations
- Patch cadence: `[OS/runtime/deps]`; CRITICAL ≤ `[7]` days.
- Backups automated, encrypted, **restore-tested** `[quarterly]`.
- Centralised logging + alerting; **no PII/secrets in logs**.

## 7. Incident & breach response
- Per the Breach Response Runbook: Commissioner ≤ 72h, data subjects ≤ 7d (significant harm).
- Report suspected incidents to `[CONTACT]` immediately.

## 8. Third parties
- Sub-processors listed + disclosed (Sub-Processor Register); each bound by a DPA.

## 9. Compliance & review
- Aligned to PDPA 2010 (Amd. 2024) and, where applicable, Cyber Security Act 2024.
- Policy reviewed annually and after any major incident.
- Non-compliance handled via `[disciplinary process]`.
