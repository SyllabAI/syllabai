"""Taxonomy tests: the 95-artifact / 12-family contract."""
from __future__ import annotations

import unittest

from tools.sib import taxonomy


class TestTaxonomy(unittest.TestCase):
    def test_total_is_95(self):
        self.assertEqual(taxonomy.TAXONOMY_SIZE, 95)

    def test_family_counts(self):
        expected = {"CUR": 8, "EXP": 8, "MIS": 9, "ASM": 10, "MS": 8, "EXM": 6,
                    "PED": 9, "PRA": 5, "PRO": 7, "HIS": 7, "TUT": 10, "GAP": 8}
        counts = {code: sum(1 for a in taxonomy.ARTIFACTS.values()
                            if a.family_code == code)
                  for code in expected}
        self.assertEqual(counts, expected)

    def test_all_ids_shape_valid(self):
        for aid in taxonomy.all_artifact_ids():
            self.assertTrue(taxonomy.is_valid_artifact_id(aid), aid)

    def test_family_slugs_unique(self):
        slugs = [f.slug for f in taxonomy.FAMILIES.values()]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_family_membership(self):
        self.assertEqual(taxonomy.expected_family_slug("MIS-01"),
                         "misconception_intelligence")
        self.assertEqual(taxonomy.expected_family_slug("MS-07"),
                         "mark_scheme_intelligence")
        self.assertEqual(taxonomy.expected_family_slug("PRA-03"),
                         "practical_procedural_intelligence")

    def test_canonical_filename_matches_schema_example(self):
        # exact example from SIB_ARTIFACT_SCHEMA_V1.md section 1
        self.assertEqual(
            taxonomy.canonical_filename("Chemistry", "4CH1", "MIS-01"),
            "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")

    def test_canonical_filename_template_is_specification_based(self):
        # SIB_ARTIFACT_SCHEMA_V1.md §1 (PROPOSED/DEFINED 2026-10-01):
        # <SUBJECT>_<SPECIFICATION>_<ARTIFACT_ID>_<SLUG>.md — slot 2 is the
        # specification code, and the qualification NEVER participates in
        # the filename (it stays a front-matter metadata field).
        canonical = taxonomy.canonical_filename("Chemistry", "4CH1", "MIS-01")
        self.assertEqual(canonical,
                         "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")
        self.assertNotIn("INTERNATIONAL_GCSE", canonical)
        # deterministic: same inputs -> same filename, no environment input
        self.assertEqual(
            canonical,
            taxonomy.canonical_filename("Chemistry", "4CH1", "MIS-01"))
        # every taxonomy artifact yields a canonical name for the same
        # subject/specification context (95-slot invariant)
        for aid in taxonomy.all_artifact_ids():
            fn = taxonomy.canonical_filename("Chemistry", "4CH1", aid)
            self.assertTrue(fn.startswith("CHEMISTRY_4CH1_"), fn)
            self.assertTrue(fn.endswith(".md"), fn)

    def test_record_vs_artifact_id_shape(self):
        self.assertTrue(taxonomy.is_valid_record_id("MIS-001"))
        self.assertFalse(taxonomy.is_valid_record_id("MIS-01"))
        self.assertFalse(taxonomy.is_valid_artifact_id("MIS-001"))
        self.assertTrue(taxonomy.is_valid_artifact_id("MIS-01"))

    def test_invalid_shapes(self):
        for bad in ("mis-01", "MIS-1", "MIS-001", "XX00-01", "MIS-", "", "-01"):
            self.assertFalse(taxonomy.is_valid_artifact_id(bad), bad)


if __name__ == "__main__":
    unittest.main()
