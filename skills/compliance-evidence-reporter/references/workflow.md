# Workflow — assessment to court-ready document

End-to-end procedure for the Defensive Due-Diligence Report. Run all commands from the directory
holding your working evidence (create a per-matter folder, e.g. `matter-acme/`).

## 1. Assess
Use the `malaysia-security-compliance` skill to run the controls against the codebase/system. For
each control, decide: implemented / partial / gap. Capture the *proof* of each as a file in
`evidence/` (a command output, a config excerpt, a policy PDF).

## 2. Hash each exhibit
For every artifact, record it with the exact command that produced it:

    python <skill>/assets/scripts/hash_evidence.py \
      --file evidence/nginx-tls.conf \
      --description "Nginx TLS configuration (TLS 1.3 only)" \
      --command "openssl s_client -connect host:443 | tee evidence/nginx-tls.conf"

Repeat for every exhibit. The register `evidence-register.jsonl` grows append-only.

## 3. Build the register
    python <skill>/assets/scripts/build_register.py \
      --register evidence-register.jsonl \
      --out-summary exhibits.md \
      --out-validated register-numbered.jsonl

This assigns exhibit numbers (A-1, A-2 ...) and writes the Markdown table to `exhibits.md`.

## 4. Fill the template
Copy `assets/templates/defensive-due-diligence.md.tmpl` to `filled.md` and replace every
`{{PLACEHOLDER}}`. Paste the `exhibits.md` table into `{{EXHIBIT_TABLE}}`. Build the
`{{CONTROLS_TABLE_ROWS}}` so each control cites its exhibit (e.g. "see Exhibit A-3").

## 5. Render
    python <skill>/assets/scripts/render_document.py \
      --input filled.md --outdir out \
      --reference-docx <skill>/assets/templates/reference.docx \
      --register register-numbered.jsonl

Outputs `out/report.docx` and `out/report.pdf`. The `--register` flag makes the renderer refuse to
proceed if any cited exhibit file is missing.

## 6. Bundle
Deliver: `out/report.docx`, `out/report.pdf`, `evidence-register.jsonl`, and the `evidence/` folder.
Keep the bundle dated and unaltered.
