# 03 — Application Security (Web + API)

Control reference for server-side applications and APIs, mapped to the **OWASP Top 10** and
**OWASP API Security Top 10**. The "How to verify" column is what a reviewer or forensic examiner
actually checks.

---

## Web application controls (OWASP Top 10)

| Risk | Required control | How to verify |
|---|---|---|
| **Injection (SQL/NoSQL/command)** | ORM / parameterised queries with `?` bindings. Never concatenate user input into raw SQL/shell. Dynamic column/sort must be **whitelisted**, never raw. | Grep raw query builders; confirm each uses bindings or a static/whitelisted string |
| **Broken Access Control** | Authorize **every** request server-side, **deny by default**. Always pass the *resource* to the check so per-object rules apply. Never rely on hiding UI. | Pick 5 write endpoints; confirm each authorizes with the object, not just "is logged in" |
| **Path Traversal** | Serve files only via a storage abstraction keyed on a **stored DB id/path**, never a raw request path. If you must touch the FS: `basename()` + allowlist the directory. | Confirm no `request input` flows into a filesystem path |
| **Cryptographic Failures** | TLS 1.2+ everywhere + HSTS. **Encryption at rest** (DB + storage + backups). Passwords hashed with **bcrypt/argon2** (never MD5/SHA1/plaintext). Encrypt sensitive columns. | Check TLS, at-rest flags, password hash algorithm |
| **Insecure Design / Mass Assignment** | Explicit allow-list of mass-assignable fields; guard privilege fields (role, approved/verified flags, balances) — set only via explicit code. | Review model fillable lists; confirm privilege fields guarded |
| **Security Misconfiguration** | `APP_DEBUG=false` in prod; security headers (CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, HSTS); no directory listing; default creds removed; verbose errors off. | Curl prod; inspect headers; confirm debug off |
| **Vulnerable Components** | SCA in CI (see `02` §3); patch cadence; CVE feed subscription. | Confirm audit jobs block on HIGH/CRITICAL |
| **Identification & Auth Failures** | Rate-limit + lockout on login/reset; strong password policy; **MFA** for privileged accounts; session fixation prevention; invalidate sessions on logout/deactivation. | Rapid-login test → throttled; confirm MFA on admin |
| **Software/Data Integrity Failures** | Verify integrity of updates/CI artifacts; signed packages; no deserialisation of untrusted data. | Review update + deserialisation paths |
| **Logging & Monitoring Failures** | Audit trail for **sensitive actions** (auth, privilege change, data export, admin, impersonation). Centralised, tamper-resistant. **Never log PII, passwords, tokens, full PAN.** Alert on anomalies. | Confirm audit mechanism called from sensitive paths; grep logs for leaked secrets |
| **SSRF** | Allow-list any URL the server fetches on user input; block internal IP ranges + metadata endpoints. | Review every "fetch URL"/webhook/image-proxy feature |
| **CSRF** | CSRF tokens on all state-changing posts (framework default — don't disable). | Confirm CSRF middleware enabled |
| **File Upload Abuse** | Validate type/size; store outside webroot or on object storage; disable script execution in the upload dir; force `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff`; randomise filenames. | Upload a `.php`/`.svg`; confirm no execution, downloads as attachment |
| **Race Conditions** | Wrap multi-row writes in DB transactions; use `lockForUpdate()` / atomic locks for counters, balances, sequential IDs, quota spend. | Review money/quota/sequence code for locking |
| **Multi-Tenancy Isolation** | Hard isolation (separate DB/schema, or rigorously scoped queries). Tokens/sessions scoped per tenant. | Use tenant A's valid token against tenant B → must fail |
| **XSS** | Output-encode by default (templating auto-escape on); sanitise rich text; CSP as defence-in-depth. | Inject `<script>` in a text field → rendered inert |

---

## API-specific controls (OWASP API Security Top 10)

| Risk | Required control |
|---|---|
| **BOLA (Broken Object Level Auth)** | Check the caller owns/may access **this specific object id** on every request — the #1 API breach cause |
| **Broken Authentication** | Strong token issuance/validation; short-lived access tokens; rotate/revoke; no auth in query string |
| **BOPLA (Property-Level Auth)** | Don't over-return fields (mass disclosure) or accept fields the caller shouldn't set (mass assignment). Use explicit resource serializers |
| **Unrestricted Resource Consumption** | Rate limits + pagination caps + payload size limits + query complexity limits |
| **BFLA (Function-Level Auth)** | Enforce role/permission per endpoint, not just authentication |
| **Unrestricted Access to Business Flows** | Throttle/abuse-protect sensitive flows (signup, purchase, OTP) |
| **SSRF** | As above — APIs are common SSRF sinks via webhook/callback URLs |
| **Security Misconfiguration** | Disable unused verbs/endpoints; lock CORS to known origins; consistent error format that doesn't leak internals |
| **Improper Inventory Management** | Document every API version/host; retire/deprecate old versions deliberately (don't break customers silently — version it) |
| **Unsafe Consumption of 3rd-party APIs** | Validate and sanitise data you receive from upstream APIs as if it were user input |

**Contract stability:** treat a public API as a contract. Renaming/removing a field silently breaks
every integration. Pin the field list with snapshot/contract tests, keep an OpenAPI spec as the
source of truth, and ship breaking changes under a new version with a deprecation timeline.

---

## Sources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) · [OWASP API Security Top 10](https://owasp.org/API-Security/) · [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
