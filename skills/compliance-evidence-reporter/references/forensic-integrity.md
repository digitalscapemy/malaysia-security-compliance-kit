# Forensic integrity rules

What makes this report survive cross-examination. Apply all of these.

1. **Hash at collection.** Compute SHA-256 the moment you capture an artifact, before any editing.
   The hash in the report must match the file in the bundle.
2. **Record the command.** Every exhibit stores the exact command that produced it. If the other
   side runs it and gets the same output, your evidence stands.
3. **Timestamps with zone.** ISO-8601 + `+08:00` (MYT). Never bare dates.
4. **Append-only register.** Never edit or reorder `evidence-register.jsonl`. Add new lines only.
   Re-running `build_register.py` re-derives exhibit numbers deterministically.
5. **Dated law.** Cite each obligation with its version and "as in force on <date>" plus a source
   URL. Laws change; pin the version you relied on.
6. **No tampering.** If you must redact PII inside an exhibit, do it visibly, record the redaction as
   its own step with its own command, and hash the redacted version as a separate exhibit.
7. **Impartiality.** State your limitations and what was *not* assessed. Overclaiming destroys
   credibility faster than a gap.

A claim without a hashed, reproducible exhibit is an assertion, not evidence.
