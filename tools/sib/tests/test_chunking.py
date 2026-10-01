"""Deterministic SIB chunking tests."""
from __future__ import annotations

import unittest

from tools.sib.chunking import chunk_artifact, chunk_envelope_fields
from tools.sib.tests.fixtures import artifact_text


class TestChunking(unittest.TestCase):
    def setUp(self):
        self.chunks = chunk_artifact(artifact_text())

    def test_record_chunks_present_with_ids(self):
        recs = [c for c in self.chunks if c.kind == "record"]
        self.assertEqual([r.record_id for r in recs], ["MIS-001", "MIS-002"])
        self.assertEqual(recs[0].chunk_id, "MIS-01:rec:MIS-001")

    def test_section_chunks_present(self):
        secs = [c for c in self.chunks if c.kind == "section"]
        headings = [s.heading for s in secs]
        self.assertIn("Purpose", headings)
        self.assertIn("Main Analysis", headings)
        self.assertIn("Evidence / Source Basis", headings)

    def test_records_not_duplicated_in_section_chunks(self):
        sec = next(c for c in self.chunks
                   if c.heading == "Research Status" or
                   c.heading == "Evidence / Source Basis")
        for c in self.chunks:
            if c.kind == "section":
                self.assertNotIn("### MIS-001", c.text)

    def test_envelope_fields_preserved(self):
        required = chunk_envelope_fields()
        for c in self.chunks:
            for field_name in required:
                self.assertIn(field_name, c.metadata,
                              f"{c.chunk_id} missing {field_name}")
        c0 = self.chunks[0]
        self.assertEqual(c0.metadata["artifact_id"], "MIS-01")
        self.assertEqual(c0.metadata["subject"], "Chemistry")
        self.assertEqual(c0.metadata["specification"], "4CH1")
        self.assertEqual(c0.metadata["curriculum_version"], "2017")
        self.assertEqual(c0.metadata["research_family"],
                         "misconception_intelligence")
        self.assertEqual(c0.metadata["status"], "GENERATED")
        self.assertEqual(c0.metadata["curriculum_anchor_refs"],
                         ["1.4", "1.5", "2.30"])
        self.assertEqual(c0.metadata["provenance"]["notebook"], "nb-chem-4ch1")

    def test_chunk_identity_deterministic_shape(self):
        for c in self.chunks:
            self.assertRegex(c.chunk_id, r"^MIS-01:(sec|rec):[A-Z0-9_\-]+$")
            self.assertRegex(c.content_sha256, r"^[0-9a-f]{64}$")

    def test_content_hash_binds_text(self):
        for c in self.chunks:
            import hashlib
            self.assertEqual(
                hashlib.sha256(c.text.encode("utf-8")).hexdigest(),
                c.content_sha256)


if __name__ == "__main__":
    unittest.main()
