# Sub-Processor Register — TEMPLATE

> Every third party that touches personal data. Required disclosure under the PDPA 2024 + your DPA.
> Keep current; notify clients of changes per the DPA. Fill `[BRACKETS]`.

**Owner:** `[DPO/ROLE]` · **Last updated:** `[DATE]`

| Sub-processor | Service / purpose | Data categories accessed | Data location (country) | Cross-border basis | DPA / security ref |
|---|---|---|---|---|---|
| `[Cloud host, e.g. provider]` | `[compute / hosting]` | `[all app data]` | `[e.g. Singapore]` | `[comparable protection / contract]` | `[link]` |
| `[Object storage, e.g. R2/S3]` | `[file storage]` | `[uploaded files]` | `[region]` | `[ ]` | `[ ]` |
| `[Email/SMS provider]` | `[transactional mail/OTP]` | `[name, email, phone]` | `[ ]` | `[ ]` | `[ ]` |
| `[Payment gateway]` | `[payments]` | `[billing data]` | `[ ]` | `[ ]` | `[PCI/DPA]` |
| `[Analytics / monitoring]` | `[ops/usage]` | `[pseudonymous ids]` | `[ ]` | `[ ]` | `[ ]` |
| `[AI / LLM API, if used]` | `[feature]` | `[prompt content — avoid PII]` | `[ ]` | `[ ]` | `[ ]` |

## Notes
- A vendor that only stores **encrypted** data you control the keys to may still be a sub-processor — list it.
- For each cross-border entry, record the **legal basis** (PDPA 2024 comparable-protection test) in the data map.
- Review whenever you add/remove a vendor, and at least `[annually]`.
- AI/LLM APIs: do not send personal/sensitive data to a third-party model unless covered by a DPA and disclosed here.
