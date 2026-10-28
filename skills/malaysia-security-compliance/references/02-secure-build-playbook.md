# 02 — Secure Build Playbook (Secure SDLC)

The *process* you follow when building any software. Defends against the most damaging forensic
findings: "no evidence of testing", "no vulnerability screening", "secrets in the repo". For the
*laws* behind this, see [`01-malaysian-law.md`](01-malaysian-law.md).

---

## 1. Legal & contractual foundation (BEFORE writing code)

The strongest predictor of surviving a claim is paperwork signed *before* the project starts.

- [ ] Identify your **PDPA role** (Controller vs Processor — see `01` §A.1)
- [ ] **Scope of Work (SOW)** — exactly what you will/won't deliver
- [ ] **Limitation of Liability** clause (caps damages, e.g. to fees paid)
- [ ] **Data Processing Agreement** signed with the client (`templates/data-processing-agreement.md`)
- [ ] **Acceptance / UAT sign-off** in writing before go-live (defeats fraud claims)
- [ ] **Professional Indemnity (PI) insurance** active
- [ ] Don't overclaim competence in proposals (Penal Code s.417/419)
- [ ] If you sell security services → confirm **CSP licence** (Cyber Security Act 2024)

## 2. Secrets management

- [ ] `.env` and every secret file gitignored from commit #1 (`.env.*` except `.example`, `auth.json`, `*.key`, `*.pem`)
- [ ] Secrets injected at runtime (env / secrets manager / vault), never in source, images, or client bundles (a public JS/mobile bundle is **not secret**)
- [ ] **Secret scanning in CI** (Gitleaks) over the **full git history**; on a leak, **rotate**, don't just delete the commit

### 2a. Hardcoded-credential scan — MANDATORY on every build & review

A leaked secret or a committed DB dump is the dumbest, most damaging, and most *common*
forensic finding. **Run this every time you review or ship — never skip it.** Treat any hit as
release-blocking until triaged.

```bash
# 1. Is .env (and only .env.example) actually ignored & untracked?
git check-ignore .env && git ls-files | grep -E '^\.env' | grep -v '\.example$'   # 2nd grep should be EMPTY

# 2. Full-history secret scan (a deleted secret is still leaked). Prefer Gitleaks.
gitleaks detect --no-banner --redact          # or: docker run -v "$PWD:/r" zricethezav/gitleaks detect -s /r

# 3. Fallback grep when Gitleaks isn't installed — source + seeders + config + docs.
grep -rniE "(password|passwd|secret|api[_-]?key|token|private[_-]?key|access[_-]?key)[\"' ]*[:=>]+[\"' ]*[^\"' ]{6,}" \
  --include='*.php' --include='*.js' --include='*.ts' --include='*.env*' --include='*.yml' --include='*.yaml' \
  --exclude-dir=vendor --exclude-dir=node_modules .
grep -rnE "(Hash::make|bcrypt)\(['\"][^'\"]{4,}" database/ app/   # default/seeded passwords baked into seeders
grep -rnE "(sk_live|pk_live|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY)" --exclude-dir=vendor .

# 4. Stray dumps / secret files sitting in the tree AND committable (not gitignored).
git status --porcelain | grep -iE '\.(sql|sqlite|dump|bak|pem|key|p12|pfx)$|backup|db_backups|\.env'
```

What to flag (each is a finding, not "just a default"):
- [ ] Default/seeded **admin or DB password** in source or docs (e.g. a `Hash::make('...')` in a seeder, an `IDENTIFIED BY '...'` in an init SQL, a "log in with X / Y" line in deploy docs). Even a "change it later" default is a known reused credential until proven changed in prod — **confirm the live value differs**.
- [ ] Any **production DB dump / SQL export** (real emails, password hashes, remember-tokens, PII) in the working tree — a single `git add .` from being pushed public, and a PDPA personal-data exposure even if never pushed. Move it out of the repo or gitignore + delete when done; if the source app is live, treat leaked session/remember tokens as needing rotation.
- [ ] Scratch/backup/screenshot dirs (`db_backups/`, `*.bak`, browser-capture folders) **not** in `.gitignore`.
- [ ] Config `env('X', 'default')` fallbacks that ship a *real* secret as the default (a non-secret default like a hostname is fine).

Remediation: gitignore + remove the file → **rotate the exposed secret** (deleting the commit is not enough) → replace seeded/default passwords with env-injected or random-generated-and-printed-once values.

## 3. Dependency & supply-chain security

- [ ] Use only reputable, maintained packages — vet before adding (downloads, last release, maintainer, open CVEs)
- [ ] Lock files committed (`composer.lock`, `package-lock.json`); reproducible installs (`npm ci`)
- [ ] **SCA in CI**: `composer audit` + `npm audit` + Trivy/Snyk; fail the build on HIGH/CRITICAL
- [ ] **Scheduled weekly scan** — catches newly-disclosed CVEs in already-locked deps
- [ ] **SBOM + license report** generated and committed (`composer licenses` / `license-checker` / Syft → `THIRD_PARTY_LICENSES`) — your defence against GPL-contamination/copyright claims
- [ ] Be skeptical of AI-suggested packages — confirm the package actually exists, is the real one (typo-squatting), and is reputable

- [ ] **Runtime pinned to an exact, patched version** (Docker `FROM`, host package) and on the CVE watch list; a critical runtime CVE → `06`

## 4. Quality & security gates in CI

- [ ] **SAST** (PHPStan/Psalm/Semgrep, ESLint security rules) + lint
- [ ] **Security tests**: unauthorised access → 403/404, injection neutralised, cross-tenant blocked, upload can't execute. Never silently skip a failing auth test
- [ ] **DAST / pentest**: at minimum a scanner sweep; an **external pentest** before launching anything handling PII (strongest due-diligence evidence)
- [ ] Branch protection on `main`: green CI + code review (reviewer checks the `03`–`05` controls, not just functionality), no direct pushes
- [ ] **Archive CI run output** (scan + test reports), dated: your "tested before go-live" proof

## 5. Evidence & documentation register (keep these, dated)

| Artifact | Defends against |
|---|---|
| Privacy notice (bilingual) | PDPA Notice & Choice |
| DPA per client | Contracts s.74; PDPA processor duty |
| SOW + liability cap + UAT sign-off | s.74 damages; Penal Code s.417/419 |
| DPO appointment + Commissioner notification | PDPA 2024 |
| Breach response runbook (72h/7d) | PDPA 2024 |
| Retention & deletion policy | PDPA Retention |
| Sub-processor register | PDPA 2024 |
| Security policy (access/crypto/backup/IR) | PDPA Security Principle |
| Threat model (1-page data-flow + trust boundaries) | "no security design" finding |
| Archived CI scan + test reports | "no testing / screening" finding |
| External pentest report | due-diligence proof |
| SBOM + THIRD_PARTY_LICENSES | copyright / GPL claims |
| Tagged releases / change log | breach-of-contract scope disputes |
| PI insurance policy | financial backstop |

Templates for the documents above are in [`templates/`](templates/).

## 6. Pre-go-live one-page gate

Do **not** launch a system handling personal data with any of these unchecked:

```
LEGAL          [ ] PDPA role documented  [ ] DPA + SOW + liability cap signed
               [ ] UAT sign-off  [ ] DPO appointed if over 20k/10k  [ ] PI insurance

PRIVACY        [ ] Bilingual privacy notice live  [ ] Retention/deletion policy + working delete
               [ ] Sub-processor register disclosed  [ ] Breach runbook written (72h/7d)

SECRETS/SUPPLY [ ] Hardcoded-credential scan clean (§2a) — no secrets/default admin pw/DB dumps
               [ ] No secrets in source or git history  [ ] SCA green (no HIGH/CRITICAL)
               [ ] SBOM + license report stored  [ ] Runtime on patched version, no critical CVE (06)

APP SECURITY   [ ] Queries parameterised; dynamic identifiers whitelisted (03)
               [ ] Authz enforced server-side on every write, resource passed (03)
               [ ] File serving via storage abstraction; uploads can't execute (03)
               [ ] Passwords hashed (bcrypt/argon2); TLS on; debug OFF
               [ ] Security headers + CSRF + rate limiting (03)
               [ ] Tenant isolation verified by cross-tenant test (03)
               [ ] Audit trail on sensitive actions; no PII/secrets in logs (03/05)
               [ ] (Mobile) MASVS storage/crypto/network/auth checks pass (04)

INFRA/OPS      [ ] Encryption at rest (DB + storage + backups) (05)
               [ ] Backups automated AND restore rehearsed (05)
               [ ] MFA on all prod/cloud/CI/registrar access (05)
               [ ] Monitoring + alerting live  [ ] IR runbook written (05)

EVIDENCE       [ ] CI scan + test reports archived, dated  [ ] All §5 docs filed
```
