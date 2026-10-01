"""Anchor extraction/registry resolution tests."""
from __future__ import annotations

import unittest

from tools.sib.anchors import (AnchorRegistry, build_registry,
                               extract_anchor_refs, valid_identifier_shape,
                               validate_anchors)
from tools.sib.errors import Codes
from tools.sib.tests.fixtures import artifact_text, registry_yaml
from tools.sib.yamlmini import load_yaml


class TestAnchorShape(unittest.TestCase):
    def test_valid_shapes(self):
        for good in ("1.1", "2.35", "4.3.2", "10.123"):
            self.assertTrue(valid_identifier_shape(good), good)

    def test_invalid_shapes(self):
        for bad in ("999.999.999", "1", "a.1", "1.1.1.1", "1.", ".1", ""):
            self.assertFalse(valid_identifier_shape(bad), bad)


class TestAnchorExtraction(unittest.TestCase):
    def test_extracts_from_spec_fields(self):
        refs = extract_anchor_refs(artifact_text())
        raws = sorted({r.raw for r in refs})
        self.assertEqual(raws, ["1.4", "1.5", "2.30"])
        recs = {r.raw: r.record_id for r in refs}
        self.assertEqual(recs["1.4"], "MIS-001")
        self.assertEqual(recs["2.30"], "MIS-002")

    def test_deduplicated(self):
        text = artifact_text(records=(
            "### MIS-001 — a\n**Specification Points:** 1.4\n"
            "### MIS-002 — b\n**Specification Points:** 1.4\n"))
        refs = extract_anchor_refs(text)
        self.assertEqual(len(refs), 2)  # per-record occurrences kept


class TestAnchorResolution(unittest.TestCase):
    def test_no_registry_is_info(self):
        rep = validate_anchors("**Specification Points:** 1.4", "MIS-01")
        self.assertIn(Codes.ANCHOR_REGISTRY_ABSENT, rep.codes())
        self.assertFalse(any(i.severity == "ERROR" for i in rep))

    def test_resolved_and_unresolved(self):
        reg = AnchorRegistry(frozenset({"1.4"}))
        rep = validate_anchors(
            "**Specification Points:** 1.4, 7.7", "MIS-01")
        rep = validate_anchors("**Specification Points:** 1.4, 7.7",
                               "MIS-01", registry=reg)
        resolved = [i for i in rep.issues if i.code == Codes.ANCHOR_RESOLVED]
        unresolved = [i for i in rep.issues
                      if i.code == Codes.ANCHOR_UNRESOLVED]
        self.assertEqual(len(resolved), 1)
        self.assertEqual(len(unresolved), 1)
        self.assertIn("7.7", unresolved[0].field)
        self.assertIn("reported, not repaired", unresolved[0].message)

    def test_invalid_shape_is_error(self):
        reg = AnchorRegistry(frozenset({"1.4"}))
        rep = validate_anchors("**Specification Points:** 999.999.999",
                               "MIS-01", registry=reg)
        self.assertTrue(any(i.code == Codes.ANCHOR_INVALID and
                            i.severity == "ERROR" for i in rep))

    def test_never_repairs(self):
        """Unresolved anchors must appear verbatim in output and nowhere be
        rewritten; the validator returns issues, not modified text."""
        text = "**Specification Points:** 7.7\n"
        rep = validate_anchors(text, "MIS-01",
                               registry=AnchorRegistry(frozenset({"1.4"})))
        self.assertTrue(rep.issues)
        self.assertIn("7.7", text)


class TestRegistryConstruction(unittest.TestCase):
    def test_quoted_ids_survive_yaml_typing(self):
        """Canonical registry convention: ids are QUOTED ("- \"2.30\"")
        so the identifier '2.30' survives verbatim (never becomes 2.3)."""
        data = load_yaml(registry_yaml(["1.4", "1.5", "2.30"]))
        reg = build_registry(data["specification_points"])
        self.assertEqual(reg.resolve("2.30"), "resolved")
        self.assertEqual(reg.resolve("2.3"), "unresolved")  # distinct ids

    def test_float_ids_fail_closed(self):
        """An unquoted '- 2.30' arrives as the float 2.3. The tooling must
        refuse it loudly, never silently mint the different identifier
        \"2.3\"."""
        with self.assertRaises(ValueError) as ctx:
            build_registry(["1.4", 2.30])
        self.assertIn("2.3", str(ctx.exception))
        self.assertIn("Quote registry ids", str(ctx.exception))

    def test_unquoted_registry_yaml_fails_closed_end_to_end(self):
        """End-to-end: registry YAML with an unquoted id -> load_yaml (YAML
        float semantics) -> build_registry raises ValueError."""
        data = load_yaml("specification_points:\n  - 1.4\n  - 2.30\n")
        self.assertEqual(data["specification_points"][0], 1.4)  # float
        with self.assertRaises(ValueError):
            build_registry(data["specification_points"])

    def test_integer_ids_are_losslessly_stringified(self):
        reg = build_registry([1, 12])
        self.assertEqual(reg.resolve("1"), "resolved")
        self.assertEqual(reg.resolve("12"), "resolved")


if __name__ == "__main__":
    unittest.main()
