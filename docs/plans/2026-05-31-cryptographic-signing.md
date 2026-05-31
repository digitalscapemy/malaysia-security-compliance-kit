# Cryptographic Signing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tamper-evident cryptographic seal to the evidence reporter — sign all rendered artifacts (PDF, DOCX, register) with a detached OpenSSL signature, and ship an independent verifier the opposing side can run.

**Architecture:** Three new stdlib-only scripts that shell out to `openssl` (exactly as `render_document.py` shells out to pandoc): `sign_report.py` builds a canonical JSON manifest of the outputs and signs it; `verify_report.py` re-checks the signature + every artifact hash; `make_signing_cert.py` mints a self-signed cert for out-of-the-box use. No Python dependencies added.

**Tech Stack:** Python 3.10+ standard library, OpenSSL CLI, `unittest`.

**Reference spec:** `docs/specs/2026-05-31-cryptographic-signing-design.md`

**Conventions to follow (from existing scripts):**
- Self-contained scripts (each redefines its own small helpers — the existing scripts do not cross-import; `sha256_file` lives in `hash_evidence.py`, `require_tool` in `render_document.py`, and they don't share).
- Loud failure with install guidance when an external tool is missing.
- ISO-8601 + `+08:00` timestamps via a `MYT` timezone constant.
- **ASCII-only console output** — the codebase explicitly avoids non-ASCII so it never crashes a Windows cp1252 console (see the `MainCliTest` docstring in `test_render_document.py`). Use `[OK]`/`[BAD]`/`PASS`/`FAIL`, never ✓/✗.
- Tests: stdlib `unittest`, `sys.path.insert` to import scripts, `@unittest.skipUnless(shutil.which("openssl"), ...)` for tool-dependent tests, `tempfile.TemporaryDirectory`.

**Paths** (all under `skills/compliance-evidence-reporter/`):
- Create: `assets/scripts/make_signing_cert.py`
- Create: `assets/scripts/sign_report.py`
- Create: `assets/scripts/verify_report.py`
- Create: `assets/tests/test_sign_verify.py`
- Create: `references/signing.md`
- Modify: `SKILL.md`
- Modify: `references/forensic-integrity.md`

---

## Task 1: `make_signing_cert.py` — self-signed cert helper

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/make_signing_cert.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py`

- [ ] **Step 1: Write the failing test**

Create `skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py`:

```python
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import make_signing_cert as mc  # noqa: E402

HAVE_OPENSSL = shutil.which("openssl") is not None


@unittest.skipUnless(HAVE_OPENSSL, "openssl not installed")
class MakeCertTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.key = self.dir / "signing.key"
        self.cert = self.dir / "signing.crt"

    def tearDown(self):
        self._tmp.cleanup()

    def test_creates_key_and_cert(self):
        mc.make_cert("/CN=Test Forensics/O=Test", self.key, self.cert, 1)
        self.assertTrue(self.key.is_file() and self.key.stat().st_size > 0)
        self.assertTrue(self.cert.is_file() and self.cert.stat().st_size > 0)

    def test_fingerprint_is_64_hex(self):
        mc.make_cert("/CN=Test Forensics/O=Test", self.key, self.cert, 1)
        fp = mc.cert_fingerprint(self.cert)
        self.assertEqual(len(fp), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in fp))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'make_signing_cert'` (or skip if openssl absent).

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/make_signing_cert.py`:

```python
#!/usr/bin/env python3
"""Mint a self-signed key + X.509 cert for sealing evidence bundles (convenience helper).

Wraps `openssl req -x509`. A self-signed cert proves integrity + authorship-by-keyholder; it is NOT
a legally recognized digital signature under the Digital Signature Act 1997 unless issued by a
Malaysian licensed CA (Pos Digicert, MSC Trustgate, etc.). Standard library only (shells out to openssl).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class CertError(Exception):
    """Raised when openssl is missing or cert generation fails."""


def require_openssl() -> str:
    """Return the openssl path or raise CertError with install guidance."""
    found = shutil.which("openssl")
    if not found:
        raise CertError(
            "required tool 'openssl' not found on PATH. Install it:\n"
            "  Windows     -> ships with Git for Windows, or https://slproweb.com/products/Win32OpenSSL.html\n"
            "  Linux/macOS -> apt install openssl / brew install openssl"
        )
    return found


def make_cert(subject: str, out_key: Path, out_cert: Path, days: int) -> None:
    """Generate a self-signed RSA-4096 key + cert with the given X.509 subject."""
    openssl = require_openssl()
    cmd = [
        openssl, "req", "-x509", "-newkey", "rsa:4096", "-sha256", "-nodes",
        "-keyout", str(out_key), "-out", str(out_cert), "-days", str(days), "-subj", subject,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise CertError(f"openssl cert generation failed ({result.returncode}): {result.stderr}")


def cert_fingerprint(cert: Path) -> str:
    """Return the cert's SHA-256 fingerprint as lowercase hex with no colons."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "x509", "-in", str(cert), "-noout", "-fingerprint", "-sha256"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise CertError(f"openssl failed reading fingerprint ({result.returncode}): {result.stderr}")
    # output: "sha256 Fingerprint=AB:CD:EF:..."
    return result.stdout.split("=", 1)[1].strip().replace(":", "").lower()


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mint a self-signed signing key + cert.")
    parser.add_argument("--subject", required=True, help='e.g. "/CN=Acme Forensics Sdn Bhd/O=Acme"')
    parser.add_argument("--out-key", default="signing.key")
    parser.add_argument("--out-cert", default="signing.crt")
    parser.add_argument("--days", type=int, default=825)
    args = parser.parse_args(argv)

    try:
        make_cert(args.subject, Path(args.out_key), Path(args.out_cert), args.days)
        fp = cert_fingerprint(Path(args.out_cert))
    except CertError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {args.out_key} + {args.out_cert}")
    print(f"cert SHA-256 fingerprint (print this on the report cover): {fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: PASS (or SKIP if openssl is not installed).

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/make_signing_cert.py skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py
git commit -m "feat(reporter): self-signed cert helper for evidence-bundle signing"
```

---

## Task 2: `sign_report.py` — manifest builder + signer

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/sign_report.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py`

- [ ] **Step 1: Write the failing tests**

Add to the top imports of `test_sign_verify.py` (after the `make_signing_cert` import):

```python
import sign_report as sr  # noqa: E402
```

Append these test classes to `test_sign_verify.py`:

```python
class CanonicalBytesTest(unittest.TestCase):
    """No openssl needed — pure serialization."""

    def test_sorted_keys_and_compact(self):
        manifest = {"version": "1", "artifacts": [], "signed_at": "z"}
        out = sr.canonical_bytes(manifest)
        self.assertIsInstance(out, bytes)
        # keys sorted, no spaces
        self.assertTrue(out.startswith(b'{"artifacts":[]'))
        self.assertNotIn(b", ", out)

    def test_deterministic(self):
        m = {"b": 1, "a": [{"y": 2, "x": 1}]}
        self.assertEqual(sr.canonical_bytes(m), sr.canonical_bytes(dict(m)))


class BuildManifestTest(unittest.TestCase):
    """No openssl needed — file hashing + structure."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.a = self.dir / "report.pdf"
        self.a.write_bytes(b"%PDF fake\n")
        self.b = self.dir / "report.docx"
        self.b.write_bytes(b"docx fake\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_entries_sorted_by_name(self):
        m = sr.build_manifest([str(self.b), str(self.a)], "CN", "deadbeef", "2026-05-31T12:00:00+08:00")
        names = [e["name"] for e in m["artifacts"]]
        self.assertEqual(names, ["report.docx", "report.pdf"])
        self.assertEqual(m["signer_cn"], "CN")
        self.assertEqual(m["cert_sha256"], "deadbeef")

    def test_missing_artifact_raises(self):
        with self.assertRaises(sr.SignError):
            sr.build_manifest([str(self.dir / "nope.pdf")], "CN", "x", "t")

    def test_duplicate_basename_raises(self):
        sub = self.dir / "sub"
        sub.mkdir()
        dup = sub / "report.pdf"
        dup.write_bytes(b"other\n")
        with self.assertRaises(sr.SignError):
            sr.build_manifest([str(self.a), str(dup)], "CN", "x", "t")


class RequireOpensslTest(unittest.TestCase):
    """No openssl needed — monkeypatches shutil.which."""

    def test_raises_when_absent(self):
        original = shutil.which
        shutil.which = lambda name: None
        try:
            with self.assertRaises(sr.SignError):
                sr.require_openssl()
        finally:
            shutil.which = original


@unittest.skipUnless(HAVE_OPENSSL, "openssl not installed")
class SignerCnTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.cert = self.dir / "c.crt"
        mc.make_cert("/CN=Test Forensics/O=Test", self.dir / "c.key", self.cert, 1)

    def tearDown(self):
        self._tmp.cleanup()

    def test_cn_extracted(self):
        self.assertEqual(sr.cert_cn(self.cert), "Test Forensics")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'sign_report'`.

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/sign_report.py`:

```python
#!/usr/bin/env python3
"""Seal a rendered evidence bundle: build a canonical manifest of the outputs and sign it.

The manifest lists each artifact with its SHA-256; openssl signs the exact manifest bytes with the
author's private key. Verification (verify_report.py) is reproducible by the opposing side.
Standard library only (shells out to openssl).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

MYT = timezone(timedelta(hours=8))
MANIFEST_VERSION = "1"


class SignError(Exception):
    """Raised when openssl is missing, an input is absent, or signing fails."""


def require_openssl() -> str:
    """Return the openssl path or raise SignError with install guidance."""
    found = shutil.which("openssl")
    if not found:
        raise SignError(
            "required tool 'openssl' not found on PATH. Install it:\n"
            "  Windows     -> ships with Git for Windows, or https://slproweb.com/products/Win32OpenSSL.html\n"
            "  Linux/macOS -> apt install openssl / brew install openssl"
        )
    return found


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in chunks so large files don't exhaust memory."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def now_myt() -> str:
    """Current Malaysia time (UTC+8) as an ISO-8601 string to the second."""
    return datetime.now(MYT).isoformat(timespec="seconds")


def cert_cn(cert: Path) -> str:
    """Extract the Common Name from the cert subject; '' if none. Handles openssl 1.x and 3.x output."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "x509", "-in", str(cert), "-noout", "-subject"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SignError(f"openssl failed reading subject ({result.returncode}): {result.stderr}")
    text = result.stdout
    # 3.x: "subject=CN = Acme, O = X"   1.x: "subject= /CN=Acme/O=X"
    for sep in ("CN=", "CN ="):
        if sep in text:
            tail = text.split(sep, 1)[1].strip()
            for stop in (",", "/"):
                if stop in tail:
                    tail = tail.split(stop, 1)[0]
            return tail.strip()
    return ""


def cert_fingerprint(cert: Path) -> str:
    """Return the cert's SHA-256 fingerprint as lowercase hex with no colons."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "x509", "-in", str(cert), "-noout", "-fingerprint", "-sha256"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SignError(f"openssl failed reading fingerprint ({result.returncode}): {result.stderr}")
    return result.stdout.split("=", 1)[1].strip().replace(":", "").lower()


def build_manifest(artifacts: list, signer_cn: str, cert_sha256: str, signed_at: str) -> dict:
    """Build the manifest dict. Raise SignError on a missing artifact or duplicate basename."""
    entries = []
    seen = set()
    for raw in artifacts:
        p = Path(raw)
        if not p.is_file():
            raise SignError(f"artifact not found: {p}")
        name = p.name
        if name in seen:
            raise SignError(f"duplicate artifact basename: {name} (basenames must be unique)")
        seen.add(name)
        entries.append({"name": name, "sha256": sha256_file(p), "size_bytes": p.stat().st_size})
    entries.sort(key=lambda e: e["name"])
    return {
        "version": MANIFEST_VERSION,
        "signed_at": signed_at,
        "signer_cn": signer_cn,
        "cert_sha256": cert_sha256,
        "artifacts": entries,
    }


def canonical_bytes(manifest: dict) -> bytes:
    """Deterministic UTF-8 bytes of the manifest — the exact bytes written to disk and signed."""
    return json.dumps(
        manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sign_manifest(manifest_path: Path, key: Path, sig_path: Path) -> None:
    """Produce a detached SHA-256 signature over the manifest file using the private key."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "dgst", "-sha256", "-sign", str(key), "-out", str(sig_path), str(manifest_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SignError(f"openssl signing failed ({result.returncode}): {result.stderr}")


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seal a rendered bundle with a detached signature.")
    parser.add_argument("--artifacts", nargs="+", required=True, help="Rendered output files to seal.")
    parser.add_argument("--key", required=True, help="Signing private key (PEM).")
    parser.add_argument("--cert", required=True, help="Signing X.509 cert (PEM).")
    parser.add_argument("--out", default=".", help="Output directory for manifest + signature.")
    parser.add_argument("--now", default=None, help="ISO-8601 override (default: now MYT). For tests.")
    args = parser.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "signing-manifest.json"
    sig_path = out / "signing-manifest.json.sig"

    try:
        cert = Path(args.cert)
        if not cert.is_file():
            raise SignError(f"cert not found: {cert}")
        if not Path(args.key).is_file():
            raise SignError(f"key not found: {args.key}")
        manifest = build_manifest(
            args.artifacts, cert_cn(cert), cert_fingerprint(cert), args.now or now_myt()
        )
        manifest_path.write_bytes(canonical_bytes(manifest))
        sign_manifest(manifest_path, Path(args.key), sig_path)
    except SignError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"sealed -> {manifest_path} + {sig_path}")
    print(f"signer CN: {manifest['signer_cn']}  cert SHA-256: {manifest['cert_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: PASS (openssl-dependent classes SKIP if openssl absent; `CanonicalBytesTest`, `BuildManifestTest`, `RequireOpensslTest` always run and pass).

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/sign_report.py skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py
git commit -m "feat(reporter): sign_report.py — canonical manifest + detached openssl signature"
```

---

## Task 3: `verify_report.py` — independent verifier + integrity tests

**Files:**
- Create: `skills/compliance-evidence-reporter/assets/scripts/verify_report.py`
- Test: `skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py`

- [ ] **Step 1: Write the failing tests**

Add to imports of `test_sign_verify.py`:

```python
import verify_report as vr  # noqa: E402
```

Append this end-to-end test class to `test_sign_verify.py`:

```python
@unittest.skipUnless(HAVE_OPENSSL, "openssl not installed")
class SignVerifyE2ETest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.key = self.dir / "signing.key"
        self.cert = self.dir / "signing.crt"
        mc.make_cert("/CN=Test Forensics/O=Test", self.key, self.cert, 1)
        self.art_dir = self.dir / "out"
        self.art_dir.mkdir()
        self.pdf = self.art_dir / "report.pdf"
        self.pdf.write_bytes(b"%PDF-1.4 fake pdf\n")
        self.docx = self.art_dir / "report.docx"
        self.docx.write_bytes(b"fake docx\n")

    def tearDown(self):
        self._tmp.cleanup()

    def _sign(self, now="2026-05-31T12:00:00+08:00"):
        return sr.main([
            "--artifacts", str(self.pdf), str(self.docx),
            "--key", str(self.key), "--cert", str(self.cert),
            "--out", str(self.art_dir), "--now", now,
        ])

    def _verify(self, cert=None):
        return vr.main([
            "--manifest", str(self.art_dir / "signing-manifest.json"),
            "--sig", str(self.art_dir / "signing-manifest.json.sig"),
            "--cert", str(cert or self.cert),
            "--artifacts-dir", str(self.art_dir),
        ])

    def test_round_trip_passes(self):
        self.assertEqual(self._sign(), 0)
        self.assertEqual(self._verify(), 0)

    def test_tampered_artifact_fails(self):
        self.assertEqual(self._sign(), 0)
        self.pdf.write_bytes(b"%PDF-1.4 TAMPERED CONTENT\n")
        self.assertEqual(self._verify(), 1)

    def test_tampered_manifest_fails(self):
        self.assertEqual(self._sign(), 0)
        mpath = self.art_dir / "signing-manifest.json"
        mpath.write_bytes(mpath.read_bytes().replace(b"Test Forensics", b"Evil Forensics"))
        self.assertEqual(self._verify(), 1)

    def test_wrong_cert_fails(self):
        self.assertEqual(self._sign(), 0)
        other_cert = self.dir / "other.crt"
        mc.make_cert("/CN=Someone Else/O=X", self.dir / "other.key", other_cert, 1)
        self.assertEqual(self._verify(cert=other_cert), 1)

    def test_manifest_is_deterministic(self):
        self.assertEqual(self._sign(), 0)
        first = (self.art_dir / "signing-manifest.json").read_bytes()
        self.assertEqual(self._sign(), 0)
        second = (self.art_dir / "signing-manifest.json").read_bytes()
        self.assertEqual(first, second)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'verify_report'`.

- [ ] **Step 3: Write the implementation**

Create `skills/compliance-evidence-reporter/assets/scripts/verify_report.py`:

```python
#!/usr/bin/env python3
"""Independently verify a sealed evidence bundle — what the opposing side runs.

Checks (1) the detached signature over the manifest using the public key in the cert, and (2) every
artifact's SHA-256 against the manifest. Prints a per-file table and PASS/FAIL (non-zero exit on
FAIL). Output is ASCII-only so it never crashes a Windows cp1252 console. Stdlib + openssl.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class VerifyError(Exception):
    """Raised when openssl is missing or a required input file is absent."""


def require_openssl() -> str:
    """Return the openssl path or raise VerifyError with install guidance."""
    found = shutil.which("openssl")
    if not found:
        raise VerifyError(
            "required tool 'openssl' not found on PATH. Install it:\n"
            "  Windows     -> ships with Git for Windows, or https://slproweb.com/products/Win32OpenSSL.html\n"
            "  Linux/macOS -> apt install openssl / brew install openssl"
        )
    return found


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pubkey(cert: Path, dest: Path) -> None:
    """Write the cert's public key (PEM) to dest, for openssl dgst -verify."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "x509", "-in", str(cert), "-pubkey", "-noout"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise VerifyError(f"openssl failed extracting pubkey ({result.returncode}): {result.stderr}")
    dest.write_text(result.stdout, encoding="utf-8")


def signature_ok(manifest: Path, sig: Path, pubkey: Path) -> bool:
    """True if the detached signature verifies against the manifest with the given public key."""
    openssl = require_openssl()
    result = subprocess.run(
        [openssl, "dgst", "-sha256", "-verify", str(pubkey), "-signature", str(sig), str(manifest)],
        capture_output=True, text=True,
    )
    return result.returncode == 0  # openssl prints "Verified OK" to stdout, captured (not leaked)


def check_artifacts(manifest_data: dict, artifacts_dir: Path) -> list:
    """Return a list of (name, ok, detail) for each artifact named in the manifest."""
    rows = []
    for entry in manifest_data.get("artifacts", []):
        name = entry["name"]
        path = artifacts_dir / name
        if not path.is_file():
            rows.append((name, False, "missing"))
            continue
        ok = sha256_file(path) == entry["sha256"]
        rows.append((name, ok, "match" if ok else "HASH MISMATCH"))
    return rows


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a sealed evidence bundle.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--sig", required=True)
    parser.add_argument("--cert", required=True)
    parser.add_argument("--artifacts-dir", default=".")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    try:
        for label, p in (
            ("manifest", manifest_path), ("sig", Path(args.sig)), ("cert", Path(args.cert)),
        ):
            if not p.is_file():
                raise VerifyError(f"{label} not found: {p}")
        with tempfile.TemporaryDirectory() as td:
            pub = Path(td) / "pub.pem"
            extract_pubkey(Path(args.cert), pub)
            sig_ok = signature_ok(manifest_path, Path(args.sig), pub)
    except VerifyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = check_artifacts(manifest_data, Path(args.artifacts_dir))

    print(f"signer CN:    {manifest_data.get('signer_cn', '')}")
    print(f"cert SHA-256: {manifest_data.get('cert_sha256', '')}")
    print(f"signed at:    {manifest_data.get('signed_at', '')}")
    print(f"signature:    [{'OK' if sig_ok else 'BAD'}]")
    print("artifacts:")
    for name, ok, detail in rows:
        print(f"  [{'OK' if ok else 'BAD'}] {name}  ({detail})")

    passed = sig_ok and len(rows) > 0 and all(ok for _, ok, _ in rows)
    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py -v`
Expected: PASS (or SKIP for openssl-dependent classes if openssl absent). The round-trip, tamper, wrong-cert, and determinism tests all pass.

- [ ] **Step 5: Commit**

```bash
git add skills/compliance-evidence-reporter/assets/scripts/verify_report.py skills/compliance-evidence-reporter/assets/tests/test_sign_verify.py
git commit -m "feat(reporter): verify_report.py — independent signature + hash verification"
```

---

## Task 4: Documentation — `references/signing.md` + SKILL.md + forensic-integrity.md

**Files:**
- Create: `skills/compliance-evidence-reporter/references/signing.md`
- Modify: `skills/compliance-evidence-reporter/SKILL.md`
- Modify: `skills/compliance-evidence-reporter/references/forensic-integrity.md`

- [ ] **Step 1: Create `references/signing.md`**

Create `skills/compliance-evidence-reporter/references/signing.md`:

```markdown
# Sealing & verifying the bundle (cryptographic signing)

After rendering, **seal** the bundle so the opposing side can confirm two things: that *you* (the
holder of a specific key) produced it, and that it is *unchanged since you produced it*. Sealing is
optional but recommended for any litigation or regulator submission.

## What gets signed

`sign_report.py` builds a canonical JSON manifest (`signing-manifest.json`) listing every output
file with its SHA-256, the signer's Common Name, the signing cert's SHA-256 fingerprint, and an
ISO-8601 (+08:00) timestamp. It then produces a detached signature (`signing-manifest.json.sig`)
over the exact manifest bytes using your private key (`openssl dgst -sha256 -sign`).

Because the manifest pins each artifact's hash, signing the manifest seals the whole bundle —
`report.pdf`, `report.docx`, and `register-numbered.jsonl` alike.

## Steps

1. **Get a key + cert.** Either use one issued by a Malaysian licensed CA, or mint a self-signed
   one for testing/internal use:
   `python assets/scripts/make_signing_cert.py --subject "/CN=Your Firm Sdn Bhd/O=Your Org"`
   Note the printed cert SHA-256 fingerprint.
2. **Seal the rendered outputs:**
   `python assets/scripts/sign_report.py --artifacts out/report.pdf out/report.docx register-numbered.jsonl --key signing.key --cert signing.crt --out out`
3. **Print the cert fingerprint on the report cover** so a verifier can match it out-of-band.
4. **Hand the verifier the bundle + cert.** They run:
   `python assets/scripts/verify_report.py --manifest out/signing-manifest.json --sig out/signing-manifest.json.sig --cert signing.crt --artifacts-dir out`
   Output ends in `PASS` (exit 0) or `FAIL` (exit 1), with a per-file `[OK]`/`[BAD]` line.

## Legal note — Digital Signature Act 1997

A self-signed signature proves **integrity + authorship-by-keyholder**: the bundle has not changed
since it was signed by whoever holds that private key. It is **not** a legally *recognized* digital
signature under the **Digital Signature Act 1997** unless the certificate is issued by a Malaysian
licensed Certification Authority (e.g. Pos Digicert, MSC Trustgate). The tool behaves identically
with either kind of cert — **state in the report which one you used**, and never describe a
self-signed seal as a "recognized digital signature."

## Prerequisites

`openssl` on PATH (ships with Git for Windows; `apt install openssl` / `brew install openssl`).
```

- [ ] **Step 2: Update SKILL.md prerequisites**

In `skills/compliance-evidence-reporter/SKILL.md`, find the Prerequisites bullet list (around line 29-34) and add this bullet after the pandoc/xelatex bullet:

```markdown
- **openssl** (only for the optional signing step) — ships with Git for Windows, or install via your
  package manager. Used by `sign_report.py` / `verify_report.py`.
```

- [ ] **Step 3: Update SKILL.md workflow**

In `skills/compliance-evidence-reporter/SKILL.md`, after the existing step 5 (**Render**, ends around line 53), add a new step 6:

```markdown
6. **Seal the bundle** (optional, recommended for litigation): sign the rendered outputs so the
   opposing side can verify authorship + integrity:
   `python assets/scripts/sign_report.py --artifacts out/report.pdf out/report.docx register-numbered.jsonl --key signing.key --cert signing.crt --out out`
   No key yet? `python assets/scripts/make_signing_cert.py --subject "/CN=Your Firm/O=Your Org"`.
   The other side verifies with `verify_report.py`. Full detail in `references/signing.md`.
```

- [ ] **Step 4: Update forensic-integrity.md**

In `skills/compliance-evidence-reporter/references/forensic-integrity.md`, add rule 8 after rule 7 (Impartiality), before the closing line "A claim without a hashed...":

```markdown
8. **Seal the rendered bundle.** After rendering, sign the outputs (`sign_report.py`) and print the
   signing cert's SHA-256 fingerprint on the cover. A detached signature proves the bundle is
   unchanged since you produced it; the opposing side confirms with `verify_report.py`. A
   self-signed cert proves integrity + authorship-by-keyholder, but is not a *recognized* digital
   signature under the Digital Signature Act 1997 unless issued by a Malaysian licensed CA — state
   which you used. See `signing.md`.
```

- [ ] **Step 5: Verify docs reference real commands**

Run: `python skills/compliance-evidence-reporter/assets/scripts/sign_report.py --help`
Run: `python skills/compliance-evidence-reporter/assets/scripts/verify_report.py --help`
Run: `python skills/compliance-evidence-reporter/assets/scripts/make_signing_cert.py --help`
Expected: each prints its usage without error (exit 0), confirming the flags in the docs match the scripts.

- [ ] **Step 6: Commit**

```bash
git add skills/compliance-evidence-reporter/references/signing.md skills/compliance-evidence-reporter/SKILL.md skills/compliance-evidence-reporter/references/forensic-integrity.md
git commit -m "docs(reporter): document bundle sealing/verification + DSA 1997 note"
```

---

## Task 5: Full suite green + README touch

**Files:**
- Test: run the whole reporter test suite
- Modify: `README.md` (optional — mention signing in the feature list if the four-document line is there)

- [ ] **Step 1: Run the entire reporter test suite**

Run: `python -m pytest skills/compliance-evidence-reporter/assets/tests/ -v`
Expected: all existing tests + new `test_sign_verify.py` tests PASS (openssl-dependent ones SKIP only if openssl is genuinely absent — on this machine openssl ships with XAMPP/Git, so they should run).

- [ ] **Step 2: Confirm openssl is present so the crypto tests actually ran (not just skipped)**

Run: `python -c "import shutil; print('openssl:', shutil.which('openssl'))"`
Expected: prints a path (not `None`). If `None`, install openssl and re-run Step 1 so the round-trip/tamper tests execute rather than skip.

- [ ] **Step 3: Update README.md feature list (if applicable)**

In `README.md`, locate the line describing the reporter's capabilities (the v1.4.0 "two skills, four document types" summary). Add a short phrase that the reporter can cryptographically seal the rendered bundle (detached OpenSSL signature + independent verifier). Keep it to one clause; do not restructure the README.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: note cryptographic bundle sealing in README"
```

---

## Self-review notes (already applied)

- **Spec coverage:** detached manifest+sig (Tasks 2-3), openssl/X.509 (all), separate sign/verify scripts (Tasks 2-3), self-signed helper (Task 1), canonical manifest with basename rule (Task 2 `build_manifest`/`canonical_bytes`), cert fingerprint in manifest + on cover (Task 2 + docs), trust-model docs + DSA 1997 (Task 4), all six spec test scenarios (Tasks 1-3: round-trip, tampered artifact, tampered manifest, wrong cert, determinism, missing openssl).
- **ASCII output:** spec's ✓/✗ replaced with `[OK]`/`[BAD]` per the codebase's Windows cp1252 rule.
- **Type consistency:** `SignError`/`VerifyError`/`CertError` per script; `build_manifest`/`canonical_bytes`/`sign_manifest`/`cert_cn`/`cert_fingerprint`/`sha256_file` names used identically in implementation and tests; manifest keys (`version`, `signed_at`, `signer_cn`, `cert_sha256`, `artifacts[].name/sha256/size_bytes`) consistent across sign, verify, and docs.
```
