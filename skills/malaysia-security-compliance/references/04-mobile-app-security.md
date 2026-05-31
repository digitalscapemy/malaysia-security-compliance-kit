# 04 — Mobile App Security (iOS / Android)

For native and cross-platform apps (Swift, Kotlin, React Native, Flutter). A mobile app is a
**client running on a device you don't control** — assume the device is hostile, rooted, and the
binary is decompiled. The backend API it calls must *separately* meet [`03`](03-application-security.md);
never trust the client.

Mapped to the **OWASP Mobile Top 10 (2024)** — the first major revision since 2016 — and the
**OWASP MASVS v2** control groups.

---

## OWASP Mobile Top 10 (2024) + required controls

| # | Risk (2024) | Required control |
|---|---|---|
| **M1** | **Improper Credential Usage** | No hardcoded credentials/API keys in the binary or resources. Use short-lived tokens; don't ship long-lived secrets to the client |
| **M2** | **Inadequate Supply Chain Security** | Vet SDKs/libraries; pin versions; SCA on mobile deps; verify SDK signatures (Apple privacy manifests / signed SDKs) |
| **M3** | **Insecure Authentication/Authorization** | OAuth 2.1 / OIDC with **PKCE**; enforce authz **server-side** (the app UI is not a security boundary); biometric unlock gates local access only |
| **M4** | **Insufficient Input/Output Validation** | Validate all input on the server; sanitise data rendered in WebViews; avoid SQL injection in local SQLite |
| **M5** | **Insecure Communication** | TLS 1.2+ only; **certificate/public-key pinning** with backup pins + rotation plan; iOS App Transport Security (no exceptions); Android Network Security Config (no cleartext, debug-only overrides) |
| **M6** | **Inadequate Privacy Controls** | Collect minimum data; honour consent; match store privacy disclosures to reality (see store section) |
| **M7** | **Insufficient Binary Protections** | Code obfuscation (R8/ProGuard, etc.); anti-tampering; root/jailbreak detection for high-risk apps; remove debug symbols/logs from release builds |
| **M8** | **Security Misconfiguration** | No debug flags in release; `android:allowBackup=false` for sensitive apps; lock exported components (activities/services/providers); no verbose logging |
| **M9** | **Insecure Data Storage** | Store secrets in **Keychain (iOS) / Keystore (Android)**. Use EncryptedSharedPreferences / EncryptedFile on Android. **Never** plaintext prefs, embedded resources, or unencrypted SQLite for sensitive data |
| **M10** | **Insufficient Cryptography** | Strong, current algorithms (AES-GCM, etc.); keys in the secure enclave/Keystore; never roll your own crypto; no hardcoded keys |

## MASVS v2 control groups (use as your test checklist)

- **MASVS-STORAGE** — sensitive data at rest is protected / minimised
- **MASVS-CRYPTO** — correct, modern cryptography & key management
- **MASVS-AUTH** — authentication & authorization done right (server-enforced)
- **MASVS-NETWORK** — secure transport (TLS, pinning)
- **MASVS-PLATFORM** — safe use of platform APIs, IPC, WebViews, exported components
- **MASVS-CODE** — secure coding, dependency hygiene, input handling
- **MASVS-RESILIENCE** — anti-tamper / reverse-engineering resistance (for high-risk apps)
- **MASVS-PRIVACY** — minimise & protect user data, honour consent

> Note: the old verification levels (L1/L2/R) were replaced in MASVS v2 by **MAS Testing Profiles** in the OWASP MASWE weakness enumeration.

## Practical implementation defaults

- [ ] Secrets → **Keychain/Keystore**, never code or plaintext prefs
- [ ] Transport → **TLS 1.2+ + certificate pinning** (with backup pins + a rotation plan so a cert swap doesn't brick the app)
- [ ] iOS → App Transport Security enabled, no exceptions; **Privacy Manifest** + signed third-party SDKs
- [ ] Android → Network Security Config (no cleartext; debug overrides only in debug builds); `allowBackup=false` for sensitive data; lock exported components
- [ ] Auth → OAuth 2.1/OIDC + PKCE; **short-lived access token (15–60 min)** + protected refresh token in the secure enclave; never long-lived secrets on device
- [ ] Release builds → obfuscated, no debug logs, no debug symbols; consider root/jailbreak detection for finance/health apps
- [ ] WebViews → disable JS unless required; never load untrusted content; no `file://` access to app data
- [ ] Local DB (SQLite/Realm) → encrypt if it holds personal/sensitive data

---

## App Store / Play Store compliance (also a PDPA Notice obligation)

Your store privacy disclosures are **legally binding** and must **match** your actual behaviour and
your privacy policy — mismatches trigger store enforcement *and* PDPA Notice & Choice issues.

**Google Play**
- [ ] Complete the **Data Safety form** (what you collect, why, sharing, retention, security) and keep it updated
- [ ] Linked **privacy policy** that matches the form and the requested permissions
- [ ] Disclose third-party / AI / external-service data sharing (tightened in the Nov 2025 update)

**Apple App Store**
- [ ] **Privacy Nutrition Labels** (App Privacy details) accurate
- [ ] **Privacy Manifests** for your app + bundled SDKs; **signed third-party SDKs**
- [ ] **App Tracking Transparency** prompt before any cross-app tracking
- [ ] Privacy policy aligns with the labels and the permission prompts

**Both**
- [ ] Request the **minimum** permissions; justify each
- [ ] Bilingual (BM + English) privacy notice for Malaysian users
- [ ] If you process > 20k users' personal data (or > 10k sensitive), the PDPA **DPO** duty applies (see `01` §A.3)

---

## Sources

- [OWASP Mobile Application Security (MAS) project](https://mas.owasp.org/) · [OWASP MASVS](https://mas.owasp.org/MASVS/)
- [OWASP Mobile Top 10 2024 update (Cobalt)](https://www.cobalt.io/blog/owasp-mobile-top-10-2024-update)
- [Google Play Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en) · [Apple App Privacy details](https://developer.apple.com/app-store/app-privacy-details/)
