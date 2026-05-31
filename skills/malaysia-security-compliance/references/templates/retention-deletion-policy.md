# Data Retention & Deletion Policy — TEMPLATE

> Satisfies the PDPA **Retention Principle** (don't keep data longer than necessary). Fill `[BRACKETS]`.

**Owner:** `[DPO/ROLE]` · **Last reviewed:** `[DATE]` · **Review cadence:** annual

---

## 1. Principle
Personal data is retained only as long as necessary for the purpose it was collected, or as required
by law, then securely deleted or anonymised.

## 2. Retention schedule

| Data category | Purpose | Retention period | Trigger to delete |
|---|---|---|---|
| `[Account / profile]` | `[service delivery]` | `[e.g. life of account + 90 days]` | `[account closure]` |
| `[Transaction records]` | `[legal/accounting]` | `[e.g. 7 years]` | `[end of statutory period]` |
| `[Support tickets / logs]` | `[ops/security]` | `[e.g. 12–24 months]` | `[age]` |
| `[Marketing data]` | `[consent-based]` | `[until consent withdrawn]` | `[withdrawal]` |
| `[Backups]` | `[recovery]` | `[e.g. 30–90 day rolling]` | `[rotation]` |
| `[Sensitive / biometric]` | `[ ]` | `[minimise — shortest viable]` | `[ ]` |

## 3. Deletion method
- Production: hard-delete or irreversibly anonymise (not just soft-delete flags) `[describe mechanism]`
- Backups: data ages out of the rolling window within `[N]` days; documented, not manually purged per-record
- Object storage / files: deleted with the parent record
- Confirm deletion cascades across all stores (DB, search index, cache, logs, sub-processors)

## 4. Data-subject deletion requests
- [ ] Verify requester identity
- [ ] Locate all stores holding their data (use the data map)
- [ ] Delete/anonymise within `[N]` days; honour legal-hold exceptions
- [ ] Confirm to the subject; log the request + action

## 5. Tenant/customer offboarding
On contract end: per the DPA, **delete or return** all of that customer's data within `[N]` days;
issue a deletion confirmation. `[Reference the purge mechanism.]`

## 6. Evidence
Log deletions (what, when, by what process) — proof of compliance without storing the deleted data itself.
