"""Deterministic artifact/manifest fixtures for the SIB test suite.

All builders are pure functions of their arguments -- no clocks, no random.
"""
from __future__ import annotations

from typing import Dict, List, Optional


def artifact_text(
    artifact_id: str = "MIS-01",
    subject: str = "Chemistry",
    qualification: str = "International GCSE",
    specification: str = "4CH1",
    curriculum_version: str = "2017",
    research_family: Optional[str] = None,
    applicability: str = "REQUIRED",
    temporal_current: bool = True,
    temporal_legacy: bool = True,
    source_scope: Optional[Dict[str, bool]] = None,
    status: str = "GENERATED",
    generated_by: str = "notebooklm",
    generated_at: str = "2026-10-01",
    notebook: str = "nb-chem-4ch1",
    source_manifest: str = "src-man-4ch1-2017",
    extra_metadata: str = "",
    sections: str = "_default_",
    records: str = "_default_",
    evidence_lines: Optional[List[str]] = None,
) -> str:
    """Build a SIB artifact markdown string. Deterministic."""
    if research_family is None:
        from tools.sib import taxonomy
        research_family = taxonomy.expected_family_slug(artifact_id)
    if source_scope is None:
        source_scope = {
            "specification": True, "textbook": True, "question_papers": True,
            "mark_schemes": True, "examiner_reports": False,
            "supplementary": False,
        }
    if sections == "_default_":
        sections = (
            "## Purpose\n\nResearch the misconception landscape.\n"
            "## Scope\n\nCovers the full specification.\n"
            "## Executive Summary\n\nKey findings summarized here.\n"
            "## Main Analysis\n\nDetailed analysis follows.\n"
            "## Evidence / Source Basis\n\n" +
            ("\n".join(evidence_lines) + "\n" if evidence_lines else
             "Evidence: QP/MS corpus and examiner reports.\n") +
            "## Limitations / Coverage Gaps\n\nSome gaps remain.\n"
            "## Research Status\n\nGENERATED; not educational truth.\n")
    if records == "_default_":
        fam = artifact_id.split("-")[0]
        records = (
            f"### {fam}-001 — Boiling point of alkali metals\n\n"
            "**Concepts:** group 1 trends\n"
            "**Specification Points:** 1.4, 1.5\n"
            "**Temporal scope:** CURRENT — AUTHORITATIVE\n"
            "**Evidence:** Jan 2020 4CH1/1C Q3; MS marks 2/2.\n\n"
            f"### {fam}-002 — Electrolysis of aqueous salts\n\n"
            "**Concepts:** electrolysis\n"
            "**Specification Points:** 2.30\n"
            "**Temporal scope:** CURRENT — AUTHORITATIVE\n"
            "**Evidence:** Jun 2019 4CH1/2C Q7.\n")
    ts = (f"temporal_scope:\n  current: {str(temporal_current).lower()}\n"
          f"  legacy: {str(temporal_legacy).lower()}\n")
    ss = "source_scope:\n" + "".join(
        f"  {k}: {str(v).lower()}\n" for k, v in source_scope.items())
    return (
        "---\n"
        "sib_protocol: SIB-1.0\n"
        f"artifact_id: {artifact_id}\n"
        "artifact_version: 1.0\n"
        f"subject: {subject}\n"
        f"qualification: {qualification}\n"
        f"specification: {specification}\n"
        f"curriculum_version: \"{curriculum_version}\"\n"
        "\n"
        f"research_family: {research_family}\n"
        f"applicability: {applicability}\n"
        "\n"
        f"{ts}"
        "\n"
        f"{ss}"
        "\n"
        f"status: {status}\n"
        f"generated_by: {generated_by}\n"
        f"generated_at: {generated_at}\n"
        "\n"
        "provenance:\n"
        f"  notebook: \"{notebook}\"\n"
        f"  source_manifest: \"{source_manifest}\"\n"
        f"{extra_metadata}"
        "---\n"
        f"# {artifact_id} — Misconception Atlas\n\n"
        f"{sections}\n"
        f"{records}\n")


def minimal_manifest(
    rows: Optional[List[Dict]] = None,
    subject: str = "Chemistry",
    specification: str = "4CH1",
    qualification: str = "International GCSE",
    curriculum_version: str = "2017",
    notebook: str = "nb-chem-4ch1",
    source_manifest: str = "src-man-4ch1-2017",
    source_gaps: Optional[List[Dict]] = None,
    backlog: Optional[List[Dict]] = None,
) -> str:
    import yaml
    data = {
        "sib_protocol": "SIB-1.0",
        "manifest_version": "1.0",
        "subject": subject,
        "qualification": qualification,
        "specification": specification,
        "curriculum_version": curriculum_version,
        "notebook": notebook,
        "source_manifest": source_manifest,
        "artifacts": rows if rows is not None else [
            {"artifact_id": "MIS-01", "applicability": "REQUIRED",
             "status": "GENERATED",
             "filename": "CHEMISTRY_4CH1_MIS-01_MISCONCEPTION_ATLAS.md"},
        ],
    }
    if source_gaps:
        data["source_gaps"] = source_gaps
    if backlog:
        data["backlog"] = backlog
    return yaml.safe_dump(data, sort_keys=False)


def registry_yaml(ids: Optional[List[str]] = None) -> str:
    import yaml
    ids = ids if ids is not None else ["1.4", "1.5", "2.30"]
    return yaml.safe_dump({"specification_points": ids}, sort_keys=False)
