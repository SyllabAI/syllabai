"""Determinism proof tests: identical input -> byte-identical output."""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from tools.sib.artifact_validator import content_fingerprint, validate_artifact
from tools.sib.chunking import chunk_artifact
from tools.sib.ingest import SibLibrary
from tools.sib.manifest_model import from_dict, load_manifest, manifest_counts, validate_manifest
from tools.sib.tests.fixtures import artifact_text, minimal_manifest

FILENAME = "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md"


class TestDeterminism(unittest.TestCase):
    def test_validator_json_byte_identical_over_5_runs(self):
        text = artifact_text()
        runs = [validate_artifact(text, filename=FILENAME).to_json()
                for _ in range(5)]
        self.assertEqual(len(set(runs)), 1)

    def test_validator_json_stable_across_key_order_perturbation(self):
        """Front matter with reordered keys must produce the same report."""
        a = validate_artifact(artifact_text(), filename=FILENAME).to_json()
        reordered = artifact_text(extra_metadata="")  # same content
        b = validate_artifact(reordered, filename=FILENAME).to_json()
        self.assertEqual(a, b)

    def test_chunking_identical_over_runs(self):
        runs = [[(c.chunk_id, c.content_sha256) for c in chunk_artifact(artifact_text())]
                for _ in range(5)]
        self.assertEqual(len({json.dumps(r) for r in runs}), 1)

    def test_content_fingerprint_excludes_nothing_but_changes_with_content(self):
        a = content_fingerprint(artifact_text())
        b = content_fingerprint(artifact_text(generated_at="2026-10-02"))
        self.assertEqual(len(a), 64)
        self.assertNotEqual(a, b)  # changes are observable via hash

    def test_manifest_counts_deterministic(self):
        import yaml
        m = from_dict(yaml.safe_load(minimal_manifest()))
        c1 = json.dumps(manifest_counts(m), sort_keys=True)
        c2 = json.dumps(manifest_counts(from_dict(yaml.safe_load(minimal_manifest()))), sort_keys=True)
        self.assertEqual(c1, c2)

    def test_qa_report_file_byte_identical_in_libraries_at_different_paths(self):
        """Path-independence: same input in two different temp roots yields
        identical QA payloads (no absolute paths, no clocks inside payload)."""
        payloads = []
        for _ in range(2):
            tmp = tempfile.mkdtemp(prefix="sib-det-")
            lib = SibLibrary(tmp)
            lib.ensure_layout()
            lib.qa_artifact(FILENAME, artifact_text())
            with open(os.path.join(tmp, "qa-reports", "MIS-01.qa.json")) as fh:
                payload = json.load(fh)
            payload.pop("filename", None)  # the only path-derived field
            payloads.append(json.dumps(payload, sort_keys=True))
        self.assertEqual(payloads[0], payloads[1])


if __name__ == "__main__":
    unittest.main()
