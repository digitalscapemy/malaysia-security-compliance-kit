import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_register as br  # noqa: E402


def make_record(sha, description="d", command="c"):
    return {
        "id": sha[:12], "description": description, "source_file": "evidence/x",
        "sha256": sha, "size_bytes": 1, "collected_at": "2026-05-31T14:00:00+08:00",
        "command": command,
    }


class LoadRegisterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "reg.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_rejects_malformed_line(self):
        self.path.write_text('{"ok": 1}\nNOT JSON\n', encoding="utf-8")
        with self.assertRaises(br.RegisterError):
            br.load_register(self.path)

    def test_load_skips_blank_lines(self):
        self.path.write_text('{"a":1}\n\n{"b":2}\n', encoding="utf-8")
        self.assertEqual(len(br.load_register(self.path)), 2)


class ValidateTest(unittest.TestCase):
    def test_rejects_missing_field(self):
        with self.assertRaises(br.RegisterError):
            br.validate([{"sha256": "a" * 64}])

    def test_rejects_duplicate_sha256(self):
        sha = "a" * 64
        with self.assertRaises(br.RegisterError):
            br.validate([make_record(sha), make_record(sha)])

    def test_accepts_distinct_valid_records(self):
        br.validate([make_record("a" * 64), make_record("b" * 64)])  # must not raise


class ExhibitTest(unittest.TestCase):
    def test_assigns_numbers_in_order(self):
        numbered = br.assign_exhibits([make_record("a" * 64), make_record("b" * 64)])
        self.assertEqual(numbered[0]["exhibit"], "A-1")
        self.assertEqual(numbered[1]["exhibit"], "A-2")

    def test_summary_table_contains_exhibit_and_hash(self):
        numbered = br.assign_exhibits([make_record("a" * 64, description="Nginx TLS")])
        table = br.summary_table(numbered)
        self.assertIn("A-1", table)
        self.assertIn("Nginx TLS", table)
        self.assertIn("a" * 64, table)

    def test_summary_table_escapes_pipes_in_cells(self):
        rec = br.assign_exhibits([make_record(
            "a" * 64, description="cmd with | pipe", command="openssl x | tee out",
        )])
        table = br.summary_table(rec)
        # the raw unescaped sequences must not appear; escaped form must
        self.assertNotIn("with | pipe", table)
        self.assertIn(r"with \| pipe", table)
        self.assertIn(r"openssl x \| tee out", table)


if __name__ == "__main__":
    unittest.main()
