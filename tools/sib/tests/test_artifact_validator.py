"""Artifact validator tests: valid artifacts first, then every rejection path."""
from __future__ import annotations

import unittest

from tools.sib.anchors import build_registry
from tools.sib.artifact_validator import validate_artifact
from tools.sib.errors import Codes
from tools.sib.tests.fixtures import artifact_text

REGISTRY = ["1.4", "1.5", "2.30"]


def _codes(rep):
    return rep.codes()


class TestValidArtifacts(unittest.TestCase):
    def assertClean(self, rep):
        self.assertTrue(rep.qa_passed,
                        f"expected clean QA, got: {rep.to_json()}")

    def test_fully_valid_artifact(self):
        rep = validate_artifact(artifact_text(),
                                filename="CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md",
                                registry=build_registry(REGISTRY))
        self.assertClean(rep)
        self.assertNotIn(Codes.ANCHOR_REGISTRY_ABSENT,
                         {i.code for i in rep.infos()} | {i.code for i in rep.errors()})

    def test_valid_optional_artifact(self):
        rep = validate_artifact(artifact_text(artifact_id="CUR-06",
                                              applicability="OPTIONAL"))
        self.assertClean(rep)

    def test_valid_not_applicable_artifact(self):
        # a NOT_APPLICABLE artifact is a placeholder record of inapplicability
        rep = validate_artifact(artifact_text(artifact_id="PRA-03",
                                              applicability="NOT_APPLICABLE",
                                              records=""))
        self.assertClean(rep)

    def test_valid_current_authoritative_only(self):
        rep = validate_artifact(artifact_text(
            temporal_legacy=False,
            evidence_lines=[
                "CURRENT — AUTHORITATIVE: group 1 melting points decrease down the group."]))
        self.assertClean(rep)

    def test_valid_legacy_historical_artifact(self):
        rep = validate_artifact(artifact_text(
            temporal_current=False, temporal_legacy=True,
            records=("### MIS-001 — Pre-2017 nomenclature confusion\n\n"
                     "**Temporal scope:** LEGACY — HISTORICAL\n"
                     "**Evidence:** legacy 2011 spec QP corpus.\n"),
            evidence_lines=[
                "LEGACY — HISTORICAL: the 2011 specification phrased this as ..."]))
        self.assertClean(rep)


class TestInvalidArtifacts(unittest.TestCase):
    def _expect(self, rep, code, severity=None):
        hits = [i for i in rep.issues if i.code == code]
        self.assertTrue(hits, f"expected {code}, got: {rep.to_json()}")
        if severity:
            self.assertTrue(all(i.severity == severity for i in hits),
                            f"{code} severity mismatch: {rep.to_json()}")
        self.assertFalse(rep.qa_passed)

    def test_missing_required_metadata(self):
        text = artifact_text().replace("applicability: REQUIRED\n", "")
        self._expect(validate_artifact(text), Codes.META_MISSING)

    def test_missing_provenance_block(self):
        text = artifact_text().replace(
            "provenance:\n  notebook: \"nb-chem-4ch1\"\n"
            "  source_manifest: \"src-man-4ch1-2017\"\n", "")
        self._expect(validate_artifact(text), Codes.META_MISSING)

    def test_missing_required_section(self):
        text = artifact_text().replace("## Executive Summary\n\nKey findings summarized here.\n", "")
        self._expect(validate_artifact(text), Codes.SECTION_MISSING)

    def test_invalid_artifact_id_shape(self):
        text = artifact_text(artifact_id="MIS-1")
        self._expect(validate_artifact(text, artifact_id_override=""),
                     Codes.IDENT_ARTIFACT_ID)

    def test_unknown_artifact_id(self):
        text = artifact_text(artifact_id="ZZ-99")
        self._expect(validate_artifact(text, artifact_id_override="ZZ-99"),
                     Codes.IDENT_UNKNOWN)

    def test_duplicate_artifact_id(self):
        rep = validate_artifact(
            artifact_text(), known_artifact_ids=["MIS-01", "CUR-01"])
        self._expect(rep, Codes.IDENT_DUP_ARTIFACT)

    def test_duplicate_record_id(self):
        dup = ("### MIS-001 — duplicate record\n\n**Evidence:** again.\n")
        text = artifact_text(records=dup + dup)
        self._expect(validate_artifact(text), Codes.IDENT_DUP_RECORD)

    def test_invalid_record_family(self):
        text = artifact_text(records="### CUR-001 — wrong family\n\nEvidence.\n")
        self._expect(validate_artifact(text), Codes.IDENT_RECORD_FAMILY)

    def test_invalid_family_membership(self):
        text = artifact_text(research_family="curriculum_intelligence")
        self._expect(validate_artifact(text), Codes.IDENT_FAMILY)

    def test_invalid_applicability(self):
        text = artifact_text(applicability="OPTIONAL_BUT_NICE")
        self._expect(validate_artifact(text), Codes.IDENT_APPLICABILITY)

    def test_invalid_status_value(self):
        text = artifact_text(status="ACCEPTED")
        self._expect(validate_artifact(text), Codes.STATUS_INVALID)

    def test_invalid_status_transition_recorded(self):
        # a QA_FAILED artifact must not present itself as STAGED without the
        # lifecycle: the validator flags impossible self-declared states via
        # transition checks in the ingest layer; here the manifest layer is
        # exercised (see manifest tests). This test pins the lifecycle table
        # behind artifact identity.
        from tools.sib.lifecycle import can_transition
        self.assertFalse(can_transition("QA_FAILED", "STAGED"))
        self.assertFalse(can_transition("GENERATED", "STAGED"))

    def test_missing_provenance_fields(self):
        text = artifact_text(notebook="", source_manifest="")
        self._expect(validate_artifact(text), Codes.PROV_MISSING)

    def test_placeholder_provenance_rejected(self):
        text = artifact_text(notebook="<subject notebook identifier>")
        self._expect(validate_artifact(text), Codes.PROV_MISSING)

    def test_unresolvable_source_manifest_reference(self):
        rep = validate_artifact(artifact_text(),
                                source_manifest_ids=["other-manifest"])
        self._expect(rep, Codes.PROV_UNKNOWN)

    def test_unresolved_curriculum_anchor(self):
        rep = validate_artifact(artifact_text(), registry=build_registry(["1.4"]))
        hits = [i for i in rep.issues if i.code == Codes.ANCHOR_UNRESOLVED]
        self.assertTrue(hits)
        self.assertTrue(all(i.severity == "WARNING" for i in hits))
        # unresolved does not fail QA: existence is reported, not guessed
        self.assertTrue(rep.qa_passed)

    def test_invalid_curriculum_anchor_shape(self):
        text = artifact_text(records=(
            "### MIS-003 — invented anchor\n\n"
            "**Specification Points:** 999.999.999\n"))
        self._expect(validate_artifact(text), Codes.ANCHOR_INVALID)

    def test_current_legacy_contradiction(self):
        # metadata: legacy-only; content claims CURRENT — AUTHORITATIVE
        text = artifact_text(temporal_current=False)
        self._expect(validate_artifact(text), Codes.TEMPORAL_CONTRADICTION)

    def test_legacy_claim_in_current_only(self):
        text = artifact_text(
            temporal_legacy=False,
            evidence_lines=["LEGACY — HISTORICAL: 2011 spec said ..."])
        self._expect(validate_artifact(text), Codes.TEMPORAL_CONTRADICTION)

    def test_empty_temporal_scope(self):
        text = artifact_text(temporal_current=False, temporal_legacy=False)
        self._expect(validate_artifact(text), Codes.TEMPORAL_MISSING)

    def test_mixed_scope_without_labels(self):
        text = artifact_text(records="", evidence_lines=None)
        # valid artifact has CURRENT — AUTHORITATIVE labels; strip them
        text = text.replace("**Temporal scope:** CURRENT — AUTHORITATIVE",
                            "**Temporal scope:** unspecified")
        rep = validate_artifact(text)
        hits = [i for i in rep.issues if i.code == Codes.TEMPORAL_MIXING]
        self.assertTrue(hits)
        self.assertTrue(all(i.severity == "WARNING" for i in hits))

    def test_no_source_basis(self):
        empty_scope = {"specification": False, "textbook": False,
                       "question_papers": False, "mark_schemes": False,
                       "examiner_reports": False, "supplementary": False}
        text = artifact_text(source_scope=empty_scope)
        self._expect(validate_artifact(text), Codes.SOURCE_SCOPE_MISSING)

    def test_filename_identity_mismatch(self):
        rep = validate_artifact(artifact_text(),
                                filename="CHEMISTRY_4CH1_CUR-01_WRONG.md")
        self._expect(rep, Codes.IDENT_FILENAME)

    def test_filename_noncanonical_is_info_only(self):
        rep = validate_artifact(artifact_text(),
                                filename="CHEMISTRY_4CH1_MIS-01_ATLAS.md")
        self.assertTrue(rep.qa_passed)
        self.assertIn(Codes.IDENT_FILENAME_CANON, rep.codes())

    def test_canonical_filename_agrees_with_specification_slot(self):
        # SIB_ARTIFACT_SCHEMA_V1.md §1 (PROPOSED/DEFINED 2026-10-01): slot 2
        # is the SPECIFICATION (4CH1); the qualification (International
        # GCSE) is metadata only. A canonical filename therefore produces
        # ZERO filename issues even though qualification != filename slot 2.
        from tools.sib.taxonomy import canonical_filename
        canonical = canonical_filename("Chemistry", "4CH1", "MIS-01")
        self.assertEqual(canonical,
                         "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")
        rep = validate_artifact(artifact_text(), filename=canonical)
        self.assertTrue(rep.qa_passed, rep.to_json())
        self.assertNotIn(Codes.IDENT_FILENAME, rep.codes())
        self.assertNotIn(Codes.IDENT_FILENAME_CANON, rep.codes())

    def test_bad_protocol_version(self):
        text = artifact_text().replace("sib_protocol: SIB-1.0",
                                       "sib_protocol: SIB-0.9")
        self._expect(validate_artifact(text), Codes.META_PROTOCOL)

    def test_bad_generated_at(self):
        text = artifact_text(generated_at="10/01/2026")
        self._expect(validate_artifact(text), Codes.PROV_UNDATEABLE)


class TestProvenanceOneOfV2(unittest.TestCase):
    """Schema v2 provenance one-of (SIB_ARTIFACT_SCHEMA_V2 §3): v1 notebook-shape
    stays valid; v2 generator-shape valid; mixing/neither/provider-mismatch fail."""

    def _expect(self, rep, code, severity=None):
        hits = [i for i in rep.issues if i.code == code]
        self.assertTrue(hits, f"expected {code}, got: {rep.to_json()}")
        if severity:
            self.assertTrue(all(i.severity == severity for i in hits),
                            f"{code} severity mismatch: {rep.to_json()}")
        self.assertFalse(rep.qa_passed)

    def _v2_text(self, **kw):
        from tools.sib.tests.fixtures import v2_provenance
        kw.setdefault("generated_by", "zai_agent")
        kw["provenance_block"] = kw.pop("prov", v2_provenance())
        return artifact_text(**kw)

    def test_valid_v2_generator_shape(self):
        rep = validate_artifact(self._v2_text(),
                                filename="CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")
        self.assertTrue(rep.qa_passed, f"expected clean QA, got: {rep.to_json()}")

    def test_valid_v2_without_source_revisions(self):
        from tools.sib.tests.fixtures import v2_provenance
        rep = validate_artifact(
            self._v2_text(prov=v2_provenance(source_revisions="")))
        self.assertTrue(rep.qa_passed, f"expected clean QA, got: {rep.to_json()}")

    def test_zai_agent_in_vocabulary(self):
        # zai_agent + v2 shape is the canonical new-run combination
        rep = validate_artifact(self._v2_text())
        self.assertNotIn(Codes.META_INVALID, _codes(rep))

    def test_v2_missing_generator(self):
        from tools.sib.tests.fixtures import v2_provenance
        block = v2_provenance().replace(
            '  generator:\n    provider: "z.ai"\n    model: "glm-test-model"\n'
            '    agent_version: "SIB-GEN-r0"\n', "")
        self._expect(validate_artifact(self._v2_text(prov=block)), Codes.PROV_MISSING)

    def test_v2_placeholder_model_rejected(self):
        from tools.sib.tests.fixtures import v2_provenance
        rep = validate_artifact(
            self._v2_text(prov=v2_provenance(model="<actual model identifier>")))
        self._expect(rep, Codes.PROV_MISSING)

    def test_v2_bad_source_revision_sha(self):
        from tools.sib.tests.fixtures import v2_provenance
        rep = validate_artifact(
            self._v2_text(prov=v2_provenance(
                source_revisions='  source_revisions:\n'
                                 '    syllabai_resources: "not-a-sha"\n')))
        self._expect(rep, Codes.PROV_MISSING)

    def test_zai_agent_with_v1_shape_rejected(self):
        # provider/shape mismatch: zai_agent requires the v2 generator-shape
        rep = validate_artifact(artifact_text(generated_by="zai_agent"))
        self._expect(rep, Codes.PROV_MISSING)

    def test_mixed_shapes_rejected(self):
        text = artifact_text(generated_by="zai_agent",
                             provenance_block=(
                                 '  notebook: "nb-chem-4ch1"\n'
                                 '  source_manifest: "src-man-4ch1-2017"\n'
                                 '  generation_run_id: "SIB-CHEMISTRY_4CH1-RUN-001"\n'
                                 '  generator:\n'
                                 '    provider: "z.ai"\n'
                                 '    model: "glm-test-model"\n'
                                 '    agent_version: "SIB-GEN-r0"\n'))
        self._expect(validate_artifact(text), Codes.PROV_MISSING)

    def test_neither_shape_rejected(self):
        text = artifact_text(provenance_block='  source_manifest: "src-man-4ch1-2017"\n')
        self._expect(validate_artifact(text), Codes.PROV_MISSING)

    def test_v1_notebooklm_still_valid(self):
        # the historical shape is untouched by v2
        rep = validate_artifact(artifact_text())
        self.assertTrue(rep.qa_passed, f"legacy v1 shape must stay valid: {rep.to_json()}")

    def test_v2_source_manifest_crosscheck_still_applies(self):
        rep = validate_artifact(self._v2_text(),
                                source_manifest_ids=["other-manifest"])
        self._expect(rep, Codes.PROV_UNKNOWN)


class TestAnchorReportIntegration(unittest.TestCase):
    """Regression: an empty shared ValidationReport is falsy (__len__==0); the
    anchor validator must not silently discard findings for clean artifacts."""

    def test_anchor_findings_survive_clean_shared_report(self):
        from tools.sib.anchors import validate_anchors, build_registry
        from tools.sib.errors import ValidationReport
        text = artifact_text()  # contains '**Specification Points:** 1.4, 1.5' records
        shared = ValidationReport('MIS-01')
        ret = validate_anchors(text, 'MIS-01', registry=build_registry(["9.99"]), report=shared)
        self.assertIs(ret, shared)
        self.assertTrue(any(i.code == Codes.ANCHOR_UNRESOLVED for i in shared.issues),
                        "anchor findings must not be dropped for clean artifacts")

    def test_anchor_findings_surfaced_by_validate_artifact(self):
        from tools.sib.anchors import build_registry
        rep = validate_artifact(artifact_text(), registry=build_registry(["9.99"]))
        self.assertTrue(any(i.code == Codes.ANCHOR_UNRESOLVED for i in rep.issues),
                        "validate_artifact must surface anchor findings")


class TestStdlibOnlyParseParity(unittest.TestCase):
    """The validator must QA identically with and without PyYAML -- CI
    runners (setup-python images) are stdlib-only, so the yamlmini fallback
    in frontmatter.parse_front_matter is the PRIMARY parser there.

    Regression for the SIB-GEN r0 CI failure (runs 40191937682 /
    40191981272): the previous one-level builtin fallback silently
    flattened the nested v2 ``provenance.generator`` mapping, failing both
    pilot artifacts with SIB-PROV-001 in CI while the PyYAML path stayed
    green locally.
    """

    def test_v2_generator_shape_qa_passes_without_pyyaml(self):
        from tools.sib.tests.fixtures import no_pyyaml, v2_provenance
        text = artifact_text(generated_by="zai_agent",
                             provenance_block=v2_provenance())
        with no_pyyaml():
            rep = validate_artifact(
                text, filename="CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md")
        self.assertTrue(rep.qa_passed, f"stdlib-only QA failed: {rep.to_json()}")
        self.assertNotIn(Codes.PROV_MISSING, _codes(rep))

    def test_v2_shape_rejections_intact_without_pyyaml(self):
        # the one-of law must hold on the fallback path too
        from tools.sib.tests.fixtures import no_pyyaml
        with no_pyyaml():
            mixed = validate_artifact(artifact_text(
                generated_by="zai_agent",
                provenance_block=('  notebook: "nb-chem-4ch1"\n'
                                  '  source_manifest: "src-man-4ch1-2017"\n'
                                  '  generation_run_id: "SIB-CHEMISTRY_4CH1-RUN-001"\n'
                                  '  generator:\n'
                                  '    provider: "z.ai"\n'
                                  '    model: "glm-test-model"\n'
                                  '    agent_version: "SIB-GEN-r0"\n')))
            neither = validate_artifact(
                artifact_text(provenance_block='  source_manifest: "src-man-4ch1-2017"\n'))
        self._expect_code(mixed, Codes.PROV_MISSING)
        self._expect_code(neither, Codes.PROV_MISSING)

    def test_v1_notebook_shape_qa_passes_without_pyyaml(self):
        from tools.sib.tests.fixtures import no_pyyaml
        text = artifact_text()
        with no_pyyaml():
            rep = validate_artifact(text)
        self.assertTrue(rep.qa_passed, f"stdlib-only QA failed: {rep.to_json()}")

    @staticmethod
    def _expect_code(rep, code):
        hits = [i for i in rep.issues if i.code == code]
        assert hits, f"expected {code}, got: {rep.to_json()}"
        assert not rep.qa_passed, rep.to_json()


if __name__ == "__main__":
    unittest.main()
