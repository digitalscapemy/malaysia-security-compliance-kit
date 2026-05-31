import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_register as br  # noqa: E402
import hash_evidence as he  # noqa: E402
import render_document as rd  # noqa: E402


class GoldenPipelineTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.evidence = self.dir / "evidence"
        self.evidence.mkdir()
        (self.evidence / "nginx.conf").write_text("ssl_protocols TLSv1.3;\n", encoding="utf-8")
        self.register = self.dir / "evidence-register.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_hash_to_table_pipeline(self):
        rec = he.build_record(
            self.evidence / "nginx.conf",
            "Nginx TLS configuration",
            "cp /etc/nginx/nginx.conf evidence/nginx.conf",
            "2026-05-31T14:00:00+08:00",
        )
        he.append_record(rec, self.register)

        records = br.load_register(self.register)
        br.validate(records)
        numbered = br.assign_exhibits(records)
        table = br.summary_table(numbered)

        self.assertEqual(numbered[0]["exhibit"], "A-1")
        self.assertIn("Nginx TLS configuration", table)
        self.assertIn(rec["sha256"], table)

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
    def test_render_produces_docx(self):
        filled = self.dir / "filled.md"
        filled.write_text(
            "# Defensive Due-Diligence Report\n\n## Exhibits\n\n"
            "| Exhibit | Description |\n|---|---|\n| A-1 | Nginx TLS configuration |\n",
            encoding="utf-8",
        )
        out = self.dir / "report.docx"
        rd.run_pandoc_docx(filled, out, None)
        self.assertTrue(out.is_file() and out.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
