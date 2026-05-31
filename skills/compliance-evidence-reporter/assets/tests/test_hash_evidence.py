import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import hash_evidence as he  # noqa: E402


class HashEvidenceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.artifact = self.dir / "artifact.txt"
        self.artifact.write_text("nginx tls config\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_sha256_is_deterministic_and_correct(self):
        expected = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.assertEqual(he.sha256_file(self.artifact), expected)
        self.assertEqual(he.sha256_file(self.artifact), he.sha256_file(self.artifact))

    def test_build_record_shape(self):
        rec = he.build_record(self.artifact, "Nginx TLS", "cp x y", "2026-05-31T14:00:00+08:00")
        for field in he.REQUIRED_FIELDS:
            self.assertIn(field, rec)
        self.assertEqual(rec["id"], rec["sha256"][:12])
        self.assertEqual(rec["size_bytes"], self.artifact.stat().st_size)
        self.assertEqual(rec["collected_at"], "2026-05-31T14:00:00+08:00")

    def test_append_writes_one_json_line_each_call(self):
        register = self.dir / "reg.jsonl"
        rec = he.build_record(self.artifact, "d", "c", "2026-05-31T14:00:00+08:00")
        he.append_record(rec, register)
        he.append_record(rec, register)
        lines = register.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["sha256"], rec["sha256"])


if __name__ == "__main__":
    unittest.main()
