import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import render_document as rd  # noqa: E402


class RequireToolTest(unittest.TestCase):
    def test_missing_tool_raises(self):
        with self.assertRaises(rd.RenderError):
            rd.require_tool("definitely-not-a-real-tool-xyz")


class VerifyExhibitsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.evidence = self.dir / "evidence"
        self.evidence.mkdir()
        self.register = self.dir / "reg.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_raises_when_exhibit_file_absent(self):
        self.register.write_text(
            '{"source_file": "evidence/missing.conf", "id": "x"}\n', encoding="utf-8"
        )
        with self.assertRaises(rd.RenderError):
            rd.verify_exhibits(self.register, self.evidence)

    def test_passes_when_exhibit_present(self):
        (self.evidence / "present.conf").write_text("ok", encoding="utf-8")
        self.register.write_text(
            '{"source_file": "evidence/present.conf", "id": "x"}\n', encoding="utf-8"
        )
        rd.verify_exhibits(self.register, self.evidence)  # must not raise


@unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
class PandocSmokeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.md = self.dir / "doc.md"
        self.md.write_text("# Title\n\nHello **world**.\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_docx_is_produced(self):
        out = self.dir / "report.docx"
        rd.run_pandoc_docx(self.md, out, None)
        self.assertTrue(out.is_file() and out.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
