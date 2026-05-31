# Design: Cryptographic signing for the evidence reporter

**Date:** 2026-05-31
**Skill:** `compliance-evidence-reporter`
**Status:** Approved (brainstorm) — pending spec review

## Problem

The chain of custody today ends at "SHA-256 hashes printed inside the rendered
document." Those hashes prove each *exhibit* is reproducible, but nothing binds the
**final rendered artifacts** (`report.pdf`, `report.docx`, `register-numbered.jsonl`)
to an identity. Anyone could generate a PDF containing the same hashes. There is no
way for the opposing side to confirm *who* produced the bundle, or that it is
*unchanged since it was produced*.

## Goal

Add a final tamper-evident seal that binds the rendered artifacts to the holder of a
signing key, and a verification path the opposing side can run independently.

Non-goals (YAGNI): embedded PAdES PDF signatures; integration with a licensed CA's
issuance API; key escrow/HSM; timestamping authorities. The design leaves room for
embedded PAdES later but does not build it now.

## Decisions (from brainstorm)

1. **Detached manifest + signature**, not embedded PDF signature. Signs *all*
   artifacts uniformly (PDF, DOCX, register), not just the PDF.
2. **OpenSSL + X.509**, shelling out exactly like `render_document.py` shells out to
   pandoc. Keeps the zero-Python-dependency rule (stdlib + external tool). The X.509
   cert carries signer identity in its subject (CN).
3. **Separate `sign_report.py` + `verify_report.py` scripts**, not a flag on
   `render_document.py`. Single-purpose convention; the manifest can only be built
   *after* render produces the outputs.
4. **Self-signed cert supported, with honest disclosure** of the legal distinction.
   A helper mints one for out-of-the-box use; the tool also accepts a CA-issued cert.

## Data flow

```
render_document.py
   → report.pdf + report.docx + register-numbered.jsonl
sign_report.py  --artifacts report.pdf report.docx register-numbered.jsonl
                --key signing.key --cert signing.crt --out out/
   → signing-manifest.json          (canonical JSON, sorted keys)
   → signing-manifest.json.sig       (detached openssl signature over the manifest bytes)
verify_report.py --manifest signing-manifest.json --sig signing-manifest.json.sig
                 --cert signing.crt --artifacts-dir out/
   → per-file ✓/✗ table + overall PASS / FAIL (non-zero exit on FAIL)
```

## Components

### 1. `assets/scripts/sign_report.py`

- **Does:** builds a canonical manifest of the rendered artifacts and signs it.
- **Inputs:** `--artifacts <file> [<file> ...]`, `--key <pem>`, `--cert <pem>`,
  `--out <dir>` (default `.`), `--now <iso8601>` (optional; for deterministic tests —
  if omitted, read the system clock).
- **Manifest fields:**
  - `version`: schema version string (e.g. `"1"`).
  - `signed_at`: ISO-8601 with `+08:00`.
  - `signer_cn`: Common Name extracted from the cert subject (via
    `openssl x509 -noout -subject`).
  - `cert_sha256`: SHA-256 fingerprint of the DER cert (via
    `openssl x509 -fingerprint -sha256`), so a verifier can match it out-of-band.
  - `artifacts`: array of `{name, sha256, size_bytes}`, sorted by `name` for
    determinism. `name` is the **basename** of each artifact (no directory
    component), so verification resolves it against `--artifacts-dir`. Two artifacts
    with the same basename → fail loudly at sign time.
- **Canonicalization:** `json.dumps(manifest, sort_keys=True, separators=(",", ":"),
  ensure_ascii=False)` then UTF-8 encode. The exact bytes written to
  `signing-manifest.json` are the bytes signed — no separate canonical form to drift.
- **Signing:** `openssl dgst -sha256 -sign <key> -out <sig> <manifest>`.
- **Errors:** missing openssl → fail loudly with install guidance (reuse the
  `require_tool` pattern from `render_document.py`); missing artifact / key / cert →
  clear error, non-zero exit.

### 2. `assets/scripts/verify_report.py`

- **Does:** independent verification — what the opposing side runs.
- **Inputs:** `--manifest`, `--sig`, `--cert`, `--artifacts-dir` (default `.`).
- **Steps:**
  1. `openssl dgst -sha256 -verify <pubkey-from-cert> -signature <sig> <manifest>`.
     Extract the public key from the cert first (`openssl x509 -pubkey -noout`).
     Signature mismatch → FAIL.
  2. For each manifest artifact: recompute SHA-256 from `<artifacts-dir>/<name>`,
     compare to the manifest. Print `✓`/`✗` per file. Any mismatch / missing → FAIL.
  3. Print the cert fingerprint and signer CN so the verifier can match them against
     the report cover.
- **Output:** a per-file table, then `PASS` (exit 0) or `FAIL` (exit 1).

### 3. `assets/scripts/make_signing_cert.py` (helper)

- **Does:** convenience minting of a self-signed key+cert.
- **Inputs:** `--subject "/CN=<firm or expert name>/O=<org>"`, `--out-key`,
  `--out-cert`, `--days` (default 825).
- **Wraps:** `openssl req -x509 -newkey rsa:4096 -sha256 -nodes -keyout <key>
  -out <cert> -days <n> -subj <subject>`.
- Prints the resulting cert SHA-256 fingerprint for the user to paste onto the cover.

### 4. Trust model (documented, not enforced)

A self-signed signature proves **"unchanged since signing by the holder of this
key."** It is **not** a legally *recognized* digital signature under the **Digital
Signature Act 1997** unless the cert is issued by a Malaysian licensed CA (Pos
Digicert, MSC Trustgate, etc.). The tool accepts either kind of cert and behaves
identically. The trust anchor for a self-signed cert is its SHA-256 fingerprint,
which the author prints on the report cover and the verifier matches out-of-band.

## Tests (`assets/tests/test_sign_verify.py`)

Follow the existing stdlib `unittest` pattern. Each test generates an ephemeral
self-signed cert via `make_signing_cert.py` (or openssl directly) in a temp dir, so
no fixture keys live in the repo.

1. **Round-trip:** sign then verify → `PASS`, exit 0.
2. **Tampered artifact:** flip a byte in an artifact after signing → verify `FAIL`,
   exit 1, the right file shows `✗`.
3. **Tampered manifest:** edit the manifest after signing → signature check fails →
   `FAIL`.
4. **Wrong cert:** verify with a different cert → signature check fails → `FAIL`.
5. **Determinism:** signing the same artifacts with a fixed `--now` produces an
   identical manifest (byte-for-byte).
6. **Missing openssl:** simulate absence (PATH manipulation) → loud, actionable error.

All tests skip cleanly with a clear message if `openssl` is not on PATH (mirrors how
render tests treat pandoc).

## Documentation

- **`references/signing.md`** (new): the signing/verification workflow, key & cert
  handling, the DSA 1997 distinction, and how a verifier checks the bundle.
- **`SKILL.md`:** add workflow step 6 ("Seal the bundle") and list openssl under
  prerequisites.
- **`references/forensic-integrity.md`:** add a "Seal the rendered bundle" rule and a
  note that the cert fingerprint belongs on the cover.

## Out of scope / future

- Embedded PAdES signature inside the PDF (the manifest design does not preclude it).
- RFC 3161 trusted timestamping.
- Automated CA issuance.
