# 05 — Infrastructure & Operations Security

The runtime + operational controls. Application code (`03`/`04`) can be perfect and still fail the
PDPA Security Principle if the infrastructure leaks, the backups are untested, or there's no
incident response.

---

## Encryption

- [ ] **TLS 1.2+** on every public endpoint; HSTS; auto-renewing certs; redirect HTTP→HTTPS
- [ ] **Encryption at rest** — database volume, object storage buckets, **and backups** all encrypted
- [ ] Sensitive columns (tokens, secrets) encrypted at the application layer
- [ ] Keys managed in a KMS / secrets manager, rotated, never in source

## Backups & disaster recovery

- [ ] Automated, scheduled backups (DB + uploaded files)
- [ ] Backups **encrypted** and access-controlled
- [ ] **Restore actually rehearsed** — an untested backup is not a backup
- [ ] Documented **RPO** (max data loss) and **RTO** (max downtime)
- [ ] Off-site / separate-account copy (ransomware/region-failure resilience)
- [ ] Written DR plan: who does what, in what order

## Hardening & access control

- [ ] **Least privilege** — DB users scoped to only needed schemas/grants; no app running as root; minimal container capabilities
- [ ] **MFA on ALL production access** — servers, cloud console, DB, CI/CD, domain registrar, DNS
- [ ] Separate admin credentials from app credentials; separate environments (dev/stage/prod)
- [ ] SSH key-based only (no password auth); bastion/jump host for prod
- [ ] Secrets injected at runtime, not in images; rotate on staff offboarding
- [ ] Disable unused ports/services; keep the attack surface minimal

## Network

- [ ] **WAF** in front of public apps
- [ ] **DDoS protection** at the edge (CDN/edge provider)
- [ ] Network segmentation — DB not publicly reachable; private subnets for data tier
- [ ] Restrict egress where feasible (limits exfiltration + SSRF blast radius)

## Patch & vulnerability management

- [ ] Documented patch cadence for OS, runtime, framework, dependencies
- [ ] Subscribe to CVE feeds for your stack; the CI SCA job (`02` §3) runs weekly
- [ ] Track and remediate findings with SLAs (e.g. CRITICAL ≤ 7 days)

## Monitoring, logging & alerting

- [ ] Centralised logs; **tamper-resistant audit trail** for sensitive actions
- [ ] **Never log** PII, passwords, tokens, full card numbers, session ids
- [ ] Alerts on: auth anomalies (brute force, impossible travel), error spikes, resource exhaustion, backup failures, cert expiry
- [ ] Retention of security logs long enough to investigate an incident (and consistent with your retention policy)

## Incident response

- [ ] Written **IR runbook**: detect → contain → eradicate → recover → **notify** → post-mortem
- [ ] Wired to the **PDPA breach timeline**: Commissioner ≤ **72 hours**, data subjects ≤ **7 days** after, when significant harm is likely (see `01` §A.3 and `templates/breach-response-runbook.md`)
- [ ] If serving an **NCII** client: also the Cyber Security Act timeline (6 hours via NC4S, 14-day supplementary — `01` §B)
- [ ] Contact tree + roles defined **before** an incident; rehearse it
- [ ] Evidence preservation steps (don't destroy logs you'll need)

## Sub-processors & cloud

- [ ] Maintain a **Sub-Processor Register** (`templates/sub-processor-register.md`) — every third party that touches data: cloud host, object storage, email/SMS, analytics, payment, AI APIs
- [ ] Record **where** each stores data (cross-border → document the legal basis, `01` §A.3)
- [ ] Confirm each sub-processor's own security posture (DPA / certifications)
- [ ] Disclose sub-processors to clients in your DPA
