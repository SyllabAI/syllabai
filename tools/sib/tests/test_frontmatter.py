"""Front-matter parsing tests: PyYAML and stdlib fallback parity."""
from __future__ import annotations

import unittest

from tools.sib.frontmatter import parse_front_matter
from tools.sib.tests.fixtures import artifact_text


class TestFrontMatter(unittest.TestCase):
    def test_parses_valid_front_matter(self):
        text = artifact_text()
        res = parse_front_matter(text)
        self.assertIsNone(res.parse_error)
        self.assertEqual(res.metadata["artifact_id"], "MIS-01")
        self.assertEqual(res.metadata["sib_protocol"], "SIB-1.0")
        self.assertEqual(res.metadata["applicability"], "REQUIRED")
        self.assertEqual(res.metadata["temporal_scope"],
                         {"current": True, "legacy": True})
        self.assertTrue(res.metadata["source_scope"]["specification"])
        self.assertEqual(res.metadata["provenance"]["notebook"], "nb-chem-4ch1")
        self.assertIn("## Purpose", res.body)

    def test_missing_delimiters(self):
        res = parse_front_matter("no front matter")
        self.assertIsNotNone(res.parse_error)
        self.assertFalse(res.metadata)

    def test_unclosed_front_matter(self):
        res = parse_front_matter("---\nartifact_id: MIS-01\nbody")
        self.assertIsNotNone(res.parse_error)

    def test_fallback_parser_matches_pyyaml(self):
        text = artifact_text()
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML unavailable; fallback is the only path")
        via_yaml = parse_front_matter(text)
        # simulate fallback: parse with the builtin directly
        from tools.sib.frontmatter import _builtin_parse
        lines = text.split("\n")[1:]
        close = next(i for i, ln in enumerate(lines) if ln.strip() == "---")
        builtin_meta = _builtin_parse(lines[:close])
        self.assertEqual(builtin_meta, via_yaml.metadata)

    def test_parse_error_surfaces(self):
        res = parse_front_matter("---\n: bad line\n---\nbody")
        self.assertIsNotNone(res.parse_error)


if __name__ == "__main__":
    unittest.main()
