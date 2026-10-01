"""yamlmini tests: subset coverage + PyYAML parity (when available)."""
from __future__ import annotations

import unittest

from tools.sib.tests.fixtures import (minimal_manifest, registry_yaml,
                                      source_manifest_yaml)
from tools.sib.yamlmini import YamlMiniError, load_yaml, parse


class TestYamlMiniSubset(unittest.TestCase):
    def test_manifest_roundtrip_without_pyyaml(self):
        text = minimal_manifest()
        direct = parse(text)
        self.assertEqual(direct["sib_protocol"], "SIB-1.0")
        self.assertEqual(direct["manifest_version"], "1.0")
        self.assertEqual(direct["subject"], "Chemistry")
        self.assertEqual(direct["curriculum_version"], "2017")
        rows = direct["artifacts"]
        self.assertEqual(rows[0]["artifact_id"], "MIS-01")
        self.assertEqual(rows[0]["applicability"], "REQUIRED")
        self.assertEqual(rows[0]["status"], "GENERATED")
        self.assertEqual(rows[0]["filename"],
                         "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")

    def test_manifest_with_gaps_and_backlog(self):
        text = minimal_manifest(
            source_gaps=[{"id": "GAP-SRC-001",
                          "description": "examiner reports missing"}],
            backlog=[{"id": "BL-001", "description": "legacy mapping"}])
        data = parse(text)
        self.assertEqual(data["source_gaps"][0]["id"], "GAP-SRC-001")
        self.assertEqual(data["backlog"][0]["description"], "legacy mapping")

    def test_scalar_lists(self):
        data = parse(registry_yaml(["1.4", "1.5", "2.30"]))
        self.assertEqual(data["specification_points"], ["1.4", "1.5", "2.30"])

    def test_unquoted_numeric_ids_are_floats_yaml_semantics(self):
        # pins WHY registry ids must be quoted: unquoted 2.30 loses the
        # trailing zero to float typing (PyYAML behaves identically)
        data = parse("specification_points:\n  - 1.4\n  - 2.30\n")
        self.assertEqual(data["specification_points"], [1.4, 2.3])

    def test_scalar_list_of_strings(self):
        data = parse(source_manifest_yaml(["a", "b"]))
        self.assertEqual(data["sources"], ["a", "b"])

    def test_scalars(self):
        data = parse("a: true\nb: false\nc: 42\nd: 1.5\ne:\nf: \"x y\"\n")
        self.assertEqual(data, {"a": True, "b": False, "c": 42, "d": 1.5,
                                "e": None, "f": "x y"})

    def test_comments_and_blanks(self):
        data = parse("# header\na: 1  # trailing\n\nb: \"# not comment\"\n")
        self.assertEqual(data, {"a": 1, "b": "# not comment"})

    def test_empty(self):
        self.assertIsNone(parse(""))
        self.assertIsNone(parse("\n\n"))


class TestParity(unittest.TestCase):
    def test_parity_on_fixtures(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML unavailable; fallback is the only path")
        for text in (minimal_manifest(), registry_yaml(),
                     source_manifest_yaml(["src-man-4ch1-2017"])):
            self.assertEqual(parse(text), load_yaml(text))


if __name__ == "__main__":
    unittest.main()
