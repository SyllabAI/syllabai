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
