# 06 — Critical Runtime CVE Response

Use when a review finds the language runtime (PHP, Node, Python, …) on a version with a known
**CRITICAL** remote CVE, or when the user asks about one. A critical unauthenticated RCE in the
runtime is release-blocking and a PDPA Security Principle exposure (`01` §A.2): patching it,
with dated proof, is the "practical step" a regulator expects.

**Ground rules:** report findings first and **get approval before changing, deploying, or pushing
anything**. Re-verify every version number against the vendor's own advisory or changelog at the
time of use. Do not rely on AI search summaries or on this file alone.

---

## A. Generic procedure

1. **Find where production actually runs the runtime.** Check whichever apply:
   - `Dockerfile*`: the `FROM` image and tag (`php:*`, `serversideup/php`, `bitnami/php-fpm`, Sail, …)
   - `docker-compose*.yml`, Forge/Vapor/Ploi config, deploy scripts, k8s manifests
   - App servers: Laravel Octane, FrankenPHP, RoadRunner, Swoole
   - `composer.json` `"php"` constraint and the CI runtime version (`.github/workflows/*`, `setup-php`)

   Report the **minor version** prod runs, the **SAPI** (FPM / mod_php / FrankenPHP / Octane / LSAPI),
   and the **file and line where that version is set**. A CI or composer version is not proof of prod.
2. **Confirm a patched build exists for that setup.**
   - **Docker:** confirm the exact patched tag exists on Docker Hub. Read the image's release notes
     for a **major version bump behind a floating tag** and list any breaking changes that touch this setup.
   - **Host-installed** (Forge, VPS, ondrej/php PPA, distro packages): name the package version that
     contains the fix. `apt upgrade` on the host does nothing if the runtime runs inside a container.
   - **Managed / shared hosting:** list what to ask the provider: patched version, date, and whether the mitigation INI is set.
3. **Propose the smallest fix:**
   - **Pin the exact patched version** (`FROM php:8.4.27-fpm`), not a floating tag, so a cached
     old base layer can't be reused. Note that the pin needs a **manual bump at each new patch release**.
   - Apply the vendor's config mitigation via a dedicated ini file that loads last (e.g.
     `conf.d/zz-security.ini`). Check first that the app doesn't depend on the feature you're disabling.
   - **Never** apply a mitigation that weakens other protections (e.g. `memory_limit=-1`) without asking.
4. **After approval:** make the change, run the test suite, commit. **Do not deploy or push** unless
   told to. Before pushing, list everything else on the branch a deploy would also ship
   (`git log origin/main..HEAD`, new migrations).
5. **Post-deploy checklist.** Run every check **where production runs** (inside the container, not on the host):
   - [ ] `php -v` (or equivalent) shows the patched version
   - [ ] The mitigation setting reads as expected (`php -i | grep <setting>`)
   - [ ] Health check passes
   - [ ] Migrations ran
   - [ ] **Every process on the old binary was rebuilt/restarted**: queue workers, schedulers, Horizon, Octane workers, cron containers
   - [ ] One real request exercising the affected path (e.g. a large upload / request body) succeeds
   - [ ] Archive the outputs, dated, as evidence (`02` §5)

---

## B. Known critical: PHP2Shell (CVE-2026-109618 / CVE-2026-109619)

Verified 2026-10-29 against php-src GitHub advisories. Re-verify before use.

| | CVE-2026-109618 ([GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w)) | CVE-2026-109619 ([GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp)) |
|---|---|---|
| Title | RCE via OOM corruption | RCE via stale global state |
| Severity | Critical, CVSS v4 9.2, unauthenticated, remote | Critical, CVSS v4 9.2, unauthenticated, remote |
| mod_php | RCE validated over HTTP | RCE confirmed |
| PHP-FPM | Susceptible by source analysis; no full exploit shown | Conditionally exposed; **session upload-progress path validated** |
| FrankenPHP / LSAPI | Likely susceptible | LSAPI conditional; FrankenPHP default not established, **not immune** |

**Affected:** every PHP below **8.2.35 / 8.3.36 / 8.4.27 / 8.5.12**. **Fixed in exactly those versions.**
PHP ≤ 8.1 is end-of-life and gets no fix, so upgrade to a supported minor.
**Upgrading is the only complete fix.** Both advisories state that config alone does not mitigate.

### Detect

```bash
grep -rnE '^\s*FROM\s+\S*php' --include='Dockerfile*' .            # base image + tag
grep -rnE 'php-version|php:' .github/ 2>/dev/null                    # CI runtime
grep -n '"php"' composer.json                                         # constraint (not proof of prod)
docker compose exec <app> php -v                                      # the real answer, where prod runs
docker compose exec <app> php -i | grep -E 'upload_progress.enabled|Server API'
```

**CRITICAL finding** if the production version is below the fixed patch for its minor, or can't
be determined (floating tag, unpinned host package). Then follow §A.

### Fix (proposal shape: discuss before applying)

```dockerfile
FROM php:8.4.27-fpm          # exact patched pin, bump manually at each PHP patch
COPY docker/php/zz-security.ini /usr/local/etc/php/conf.d/zz-security.ini
```

```ini
; zz-security.ini: loads last. Mitigation for CVE-2026-109619, kept after patching if unused.
session.upload_progress.enabled = 0
```

- Disable `session.upload_progress` only after checking the app doesn't use it. Grep for
  `session.upload_progress` / `PHP_SESSION_UPLOAD_PROGRESS`. Laravel's own session driver does
  **not** need it, but a native `session_start()` upload-progress bar does.
- `serversideup/php`: floating tags reportedly moved to **v5 on 2026-10-08** (verify on their release notes). Pin an exact tag and read the v5 breaking changes before bumping.
- Interim only, if patching must wait: the advisories also list `memory_limit=-1`, tighter
  `post_max_size` / input limits, and on 8.5 `fatal_error_backtraces=0`. All are **partial**.
  **Ask before** setting `memory_limit=-1`. Never use `RLIMIT_AS` / `RLIMIT_DATA`, which trigger the vulnerable path.
- Restart **every** PHP worker after the change (FPM pools, Octane, queue/Horizon, scheduler).

### Sources

- [GHSA-w8hw-w9fx-j79w](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) · [GHSA-6wmf-4rv5-p3rp](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) · [PHP 8 ChangeLog](https://www.php.net/ChangeLog-8.php)
