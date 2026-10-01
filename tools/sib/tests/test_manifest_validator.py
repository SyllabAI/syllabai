"""Manifest validation tests: taxonomy coverage, states, disk cross-checks."""
from __future__ import annotations

import os
import tempfile
import unittest

from tools.sib.errors import Codes
from tools.sib.manifest_model import (from_dict, load_manifest,
                                      manifest_counts, validate_manifest)
from tools.sib.tests.fixtures import artifact_text, minimal_manifest

VALID_ROW = {"artifact_id": "MIS-01", "applicability": "REQUIRED",
             "status": "GENERATED",
             "filename": "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md"}


def _write(tmp, relpath, content):
    path = os.path.join(tmp, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return path


class _ManifestTestBase(unittest.TestCase):
    def _expect(self, rep, code, substring=""):
        hits = [i for i in rep.issues if i.code == code and
                substring in i.field]
        self.assertTrue(hits, f"expected {code} ({substring}); got {rep.to_json()}")
        self.assertFalse(rep.qa_passed)


class TestManifestStructure(_ManifestTestBase):
    def test_valid_minimal_manifest(self):
        import yaml
        manifest = from_dict(yaml.safe_load(minimal_manifest()))
        rep = validate_manifest(manifest, None)
        self.assertTrue(rep.qa_passed, rep.to_json())

    def test_missing_manifest(self):
        rep = validate_manifest(None, "manifest file not found: x")
        self.assertFalse(rep.qa_passed)
        self.assertIn(Codes.MANIFEST_MALFORMED, rep.codes())

    def test_missing_required_field(self):
        import yaml
        data = yaml.safe_load(minimal_manifest())
        del data["specification"]
        rep = validate_manifest(from_dict(data), None)
        self._expect(rep, Codes.MANIFEST_FIELD, "specification")

    def test_missing_provenance_fields(self):
        import yaml
        data = yaml.safe_load(minimal_manifest(notebook="TBD"))
        rep = validate_manifest(from_dict(data), None)
        self._expect(rep, Codes.MANIFEST_FIELD, "notebook")

    def test_duplicate_artifact_rows(self):
        import yaml
        rows = [VALID_ROW, dict(VALID_ROW)]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self._expect(rep, Codes.MANIFEST_DUP)

    def test_unknown_artifact_id(self):
        import yaml
        rows = [dict(VALID_ROW, artifact_id="ZZ-99")]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self._expect(rep, Codes.MANIFEST_UNKNOWN_ID)

    def test_invalid_applicability(self):
        import yaml
        rows = [dict(VALID_ROW, applicability="MAYBE")]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self._expect(rep, Codes.MANIFEST_FIELD, "applicability")

    def test_invalid_status(self):
        import yaml
        rows = [dict(VALID_ROW, status="ACCEPTED")]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self._expect(rep, Codes.MANIFEST_STATUS)

    def test_not_applicable_cannot_be_published(self):
        import yaml
        rows = [dict(VALID_ROW, applicability="NOT_APPLICABLE",
                     status="PUBLISHED")]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self._expect(rep, Codes.MANIFEST_COMBINATION)

    def test_optional_and_not_applicable_are_first_class(self):
        import yaml
        rows = [
            dict(VALID_ROW),
            {"artifact_id": "CUR-06", "applicability": "OPTIONAL",
             "status": ""},
            {"artifact_id": "PRA-03", "applicability": "NOT_APPLICABLE",
             "status": ""},
        ]
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest(rows))), None)
        self.assertTrue(rep.qa_passed, rep.to_json())

    def test_all_95_not_required(self):
        """A manifest with one row must pass disk-less validation: the 95
        taxonomy slots are inventory, not obligations."""
        import yaml
        rep = validate_manifest(from_dict(yaml.safe_load(minimal_manifest())), None)
        self.assertTrue(rep.qa_passed)


class TestManifestAgainstDisk(_ManifestTestBase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sib-manifest-")
        self.lib = self.tmp

    def test_required_missing_from_disk(self):
        manifest, err = load_manifest(
            _write(self.tmp, "manifest.yaml", minimal_manifest()))
        self.assertIsNone(err)
        rep = validate_manifest(manifest, err,
                                artifacts_dir=os.path.join(self.lib, "artifacts"))
        self._expect(rep, Codes.MANIFEST_MISSING_REQ)

    def test_required_present_passes(self):
        _write(self.tmp, "manifest.yaml", minimal_manifest())
        _write(self.tmp, "artifacts/CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md",
               artifact_text())
        manifest, err = load_manifest(os.path.join(self.tmp, "manifest.yaml"))
        rep = validate_manifest(manifest, err,
                                artifacts_dir=os.path.join(self.tmp, "artifacts"))
        self.assertTrue(rep.qa_passed, rep.to_json())

    def test_manifest_artifact_status_disagreement(self):
        _write(self.tmp, "manifest.yaml", minimal_manifest())
        _write(self.tmp, "artifacts/CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md",
               artifact_text(status="STAGED"))
        manifest, err = load_manifest(os.path.join(self.tmp, "manifest.yaml"))
        rep = validate_manifest(manifest, err,
                                artifacts_dir=os.path.join(self.tmp, "artifacts"))
        self._expect(rep, Codes.MANIFEST_DISAGREE)

    def test_unmanifested_file_detected(self):
        _write(self.tmp, "manifest.yaml", minimal_manifest())
        _write(self.tmp, "artifacts/CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md",
               artifact_text())
        _write(self.tmp, "artifacts/CHEMISTRY_4CH1_CUR-01_CURRICULUM_OVERVIEW.md",
               artifact_text(artifact_id="CUR-01",
                             status="GENERATED"))
        manifest, err = load_manifest(os.path.join(self.tmp, "manifest.yaml"))
        rep = validate_manifest(manifest, err,
                                artifacts_dir=os.path.join(self.tmp, "artifacts"))
        hits = [i for i in rep.issues if i.code == Codes.MANIFEST_DISAGREE
                and "CUR-01" in i.message]
        self.assertTrue(hits)

    def test_unsupported_publication_requires_qa_evidence(self):
        import yaml
        rows = [dict(VALID_ROW, status="PUBLISHED")]
        _write(self.tmp, "manifest.yaml", minimal_manifest(rows))
        manifest, err = load_manifest(os.path.join(self.tmp, "manifest.yaml"))
        rep = validate_manifest(manifest, err,
                                artifacts_dir=os.path.join(self.tmp, "artifacts"))
        self._expect(rep, Codes.MANIFEST_PUBLISH)

    def test_source_gaps_and_backlog_reported(self):
        import yaml
        data = yaml.safe_load(minimal_manifest(
            source_gaps=[{"id": "GAP-SRC-001",
                          "description": "examiner reports missing"}],
            backlog=[{"id": "BL-001", "description": "legacy mapping"}]))
        rep = validate_manifest(from_dict(data), None)
        self.assertIn(Codes.MANIFEST_GAP, rep.codes())
        self.assertIn(Codes.MANIFEST_BACKLOG, rep.codes())
        # gaps/backlog are warnings/info, not failures
        self.assertTrue(rep.qa_passed)


class TestManifestCounts(unittest.TestCase):
    def test_counts_shape(self):
        import yaml
        m = from_dict(yaml.safe_load(minimal_manifest()))
        counts = manifest_counts(m)
        self.assertEqual(counts["artifacts_defined"], 95)
        self.assertEqual(counts["REQUIRED"], 1)
        self.assertEqual(counts["OPTIONAL"], 0)
        self.assertEqual(counts["NOT_APPLICABLE"], 0)
        self.assertEqual(counts["GENERATED"], 1)
        self.assertEqual(counts["UNMANIFESTED"], 94)


if __name__ == "__main__":
    unittest.main()
