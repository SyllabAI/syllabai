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

    def test_fallback_path_matches_pyyaml(self):
        """Both parse paths yield identical metadata (v1 + v2 shapes).

        The fallback under test is the REAL one (yamlmini-backed since the
        SIB-GEN r0 CI defect): parse_front_matter is called with PyYAML
        masked, exactly as on stdlib-only CI runners.
        """
        from tools.sib.tests.fixtures import no_pyyaml, v2_provenance
        v1_text = artifact_text()
        v2_text = artifact_text(generated_by="zai_agent",
                                provenance_block=v2_provenance())
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML unavailable; fallback is the only path")
        for text in (v1_text, v2_text):
            with no_pyyaml():
                via_fallback = parse_front_matter(text)
            via_yaml = parse_front_matter(text)
            self.assertIsNone(via_fallback.parse_error)
            self.assertIsNone(via_yaml.parse_error)
            self.assertEqual(via_fallback.parse_mode, "builtin")
            self.assertEqual(via_yaml.parse_mode, "pyyaml")
            self.assertEqual(via_fallback.metadata, via_yaml.metadata)

    def test_fallback_preserves_nested_v2_provenance(self):
        """Regression (SIB-GEN r0 CI, run 40191937682): the stdlib fallback
        must preserve the two-level nested v2 provenance block
        (provenance.generator.{provider, model, agent_version}) instead of
        silently flattening it away -- the old one-level builtin parser
        reduced it to generator: None and failed every v2 artifact with
        SIB-PROV-001 in stdlib-only environments."""
        from tools.sib.tests.fixtures import no_pyyaml, v2_provenance
        text = artifact_text(generated_by="zai_agent",
                             provenance_block=v2_provenance())
        with no_pyyaml():
            res = parse_front_matter(text)
        self.assertIsNone(res.parse_error)
        prov = res.metadata["provenance"]
        self.assertEqual(prov["generator"],
                         {"provider": "z.ai", "model": "glm-test-model",
                          "agent_version": "SIB-GEN-r0"})
        self.assertEqual(prov["source_revisions"]["syllabai_resources"],
                         "ba7815576c4e7f116f06ced7635596159585d245")
        self.assertEqual(prov["source_revisions"]["syllabai_pastpapers"],
                         "3632b0e6aaaa1111222233334444555566667777")

    def test_parse_error_surfaces(self):
        res = parse_front_matter("---\n: bad line\n---\nbody")
        self.assertIsNotNone(res.parse_error)


if __name__ == "__main__":
    unittest.main()
