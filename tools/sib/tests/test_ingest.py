"""Ingestion scaffolding tests: QA -> stage -> publish governance."""
from __future__ import annotations

import os
import tempfile
import unittest

from tools.sib.errors import Codes
from tools.sib.frontmatter import parse_front_matter
from tools.sib.ingest import SibLibrary
from tools.sib.tests.fixtures import artifact_text, minimal_manifest

FILENAME = "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md"


class IngestBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sib-ingest-")
        self.lib = SibLibrary(self.tmp)
        self.lib.ensure_layout()
        with open(os.path.join(self.tmp, "manifest.yaml"), "w") as fh:
            fh.write(minimal_manifest())


class TestQaStage(IngestBase):
    def test_qa_pass_writes_deterministic_report_without_status_change(self):
        path = os.path.join(self.tmp, "artifacts", FILENAME)
        with open(path, "w") as fh:
            fh.write(artifact_text())
        r1 = self.lib.qa_artifact(FILENAME, artifact_text())
        self.assertTrue(r1.qa_passed)
        # artifact status untouched: validation is evidence, not transition
        status = parse_front_matter(open(path).read()).metadata["status"]
        self.assertEqual(status, "GENERATED")
        qa_file = os.path.join(self.tmp, "qa-reports", "MIS-01.qa.json")
        self.assertTrue(os.path.isfile(qa_file))
        first = open(qa_file).read()
        self.lib.qa_artifact(FILENAME, artifact_text())
        self.assertEqual(first, open(qa_file).read())  # byte-stable

    def test_qa_fail_blocks_staging(self):
        broken = artifact_text().replace(
            "## Executive Summary\n\nKey findings summarized here.\n", "")
        with open(os.path.join(self.tmp, "artifacts", FILENAME), "w") as fh:
            fh.write(broken)
        res = self.lib.qa_artifact(FILENAME, broken)
        self.assertFalse(res.qa_passed)
        staged = self.lib.stage_artifact(FILENAME)
        self.assertFalse(staged.qa_passed)
        self.assertIn(Codes.INGEST_ORDER, staged.report.codes())

    def test_stage_requires_qa_report(self):
        with open(os.path.join(self.tmp, "artifacts", FILENAME), "w") as fh:
            fh.write(artifact_text())
        staged = self.lib.stage_artifact(FILENAME)
        self.assertFalse(staged.qa_passed)
        self.assertIn("no QA report", staged.report.issues[0].message)

    def test_full_landing_to_staged_to_published(self):
        text = artifact_text()
        with open(os.path.join(self.tmp, "artifacts", FILENAME), "w") as fh:
            fh.write(text)
        self.lib.qa_artifact(FILENAME, text)
        staged = self.lib.stage_artifact(FILENAME)
        self.assertTrue(staged.qa_passed, staged.report.to_json())
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "staged", FILENAME)))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "artifacts", FILENAME)))
        # status advanced through the legal two-step transition
        st = parse_front_matter(open(staged.moved_to).read()).metadata["status"]
        self.assertEqual(st, "STAGED")

        published = self.lib.publish_artifact(FILENAME)
        self.assertTrue(published.qa_passed, published.report.to_json())
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "published", FILENAME)))
        st = parse_front_matter(open(published.moved_to).read()).metadata["status"]
        self.assertEqual(st, "PUBLISHED")

    def test_publish_requires_staged(self):
        with open(os.path.join(self.tmp, "artifacts", FILENAME), "w") as fh:
            fh.write(artifact_text())
        res = self.lib.publish_artifact(FILENAME)
        self.assertFalse(res.qa_passed)
        self.assertIn("not staged", res.report.issues[0].message)

    def test_staged_file_publish_requires_status(self):
        # a STAGED-lifecycle file placed manually without status -> refused
        with open(os.path.join(self.tmp, "staged", FILENAME), "w") as fh:
            fh.write(artifact_text(status="GENERATED"))
        res = self.lib.publish_artifact(FILENAME)
        self.assertFalse(res.qa_passed)


class TestChunkWriting(IngestBase):
    def test_chunks_jsonl_deterministic(self):
        out1 = self.lib.write_chunks(FILENAME, artifact_text())
        first = open(out1).read()
        out2 = self.lib.write_chunks(FILENAME, artifact_text())
        self.assertEqual(first, open(out2).read())
        self.assertIn("chunks", out1)


class TestSourceManifestCrossCheck(IngestBase):
    def test_source_manifest_ids_used(self):
        with open(os.path.join(self.tmp, "source_manifest.yaml"), "w") as fh:
            fh.write("sources:\n  - src-man-4ch1-2017\n")
        res = self.lib.qa_artifact(FILENAME, artifact_text())
        self.assertTrue(res.qa_passed)

    def test_unknown_source_manifest_fails(self):
        with open(os.path.join(self.tmp, "source_manifest.yaml"), "w") as fh:
            fh.write("sources:\n  - different-manifest\n")
        res = self.lib.qa_artifact(FILENAME, artifact_text())
        self.assertFalse(res.qa_passed)
        self.assertIn(Codes.PROV_UNKNOWN, res.report.codes())


if __name__ == "__main__":
    unittest.main()
