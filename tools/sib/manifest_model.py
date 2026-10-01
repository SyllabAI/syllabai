"""SIB subject manifest model and deterministic validation.

The manifest is the subject-specific applicability + inventory layer over the
universal 95-artifact taxonomy (protocol §3/§6/§9). OPTIONAL and
NOT_APPLICABLE are first-class states: the validator never requires all 95
artifacts to exist.

Manifest file (manifest.yaml) shape -- authoritative for this
implementation, mirrored in docs/research/SIB_VALIDATOR_IMPLEMENTATION_V1.md:

    sib_protocol: SIB-1.0
    manifest_version: "1.0"
    subject: Chemistry
    qualification: International GCSE
    specification: 4CH1
    curriculum_version: "2017"
    notebook: <subject notebook identifier>
    source_manifest: <source manifest identifier>
    artifacts:
      - artifact_id: CUR-01
        applicability: REQUIRED        # REQUIRED | OPTIONAL | NOT_APPLICABLE
        status: GENERATED              # GENERATED|QA_PASSED|QA_FAILED|STAGED|PUBLISHED
        filename: CHEMISTRY_4CH1_CUR-01_CURRICULUM_OVERVIEW.md  # optional
    source_gaps:                       # optional
      - id: GAP-SRC-001
        description: ...
    backlog:                           # optional
      - id: BL-001
        description: ...
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import yaml

from . import taxonomy
from .errors import (Codes, SEVERITY_ERROR, SEVERITY_INFO, SEVERITY_WARNING,
                     ValidationReport)
from .lifecycle import (STATUS_GENERATED, STATUS_PUBLISHED, STATUS_QA_FAILED,
                        STATUS_QA_PASSED, STATUS_STAGED, ALL_STATUSES)
from .artifact_validator import VALID_APPLICABILITY  # single source of truth

# statuses a manifest row may legally carry
_MANIFEST_ROW_STATUSES = frozenset(ALL_STATUSES)


@dataclass
class ManifestRow:
    artifact_id: str
    applicability: str = ""
    status: str = ""
    filename: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"artifact_id": self.artifact_id,
                "applicability": self.applicability,
                "status": self.status,
                "filename": self.filename,
                "notes": self.notes}


@dataclass
class Manifest:
    sib_protocol: str = ""
    manifest_version: str = ""
    subject: str = ""
    qualification: str = ""
    specification: str = ""
    curriculum_version: str = ""
    notebook: str = ""
    source_manifest: str = ""
    rows: List[ManifestRow] = field(default_factory=list)
    source_gaps: List[Dict[str, Any]] = field(default_factory=list)
    backlog: List[Dict[str, Any]] = field(default_factory=list)

    def row(self, artifact_id: str) -> Optional[ManifestRow]:
        for r in self.rows:
            if r.artifact_id == artifact_id:
                return r
        return None


def load_manifest(path: str) -> Tuple[Optional[Manifest], Optional[str]]:
    """Load and parse manifest.yaml. Returns (manifest, None) or (None, error)."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        return None, f"manifest file not found: {path}"
    except Exception as exc:
        return None, f"manifest unparsable: {exc}"
    if not isinstance(data, dict):
        return None, "manifest root must be a mapping"
    return from_dict(data), None


def from_dict(data: Dict[str, Any]) -> Manifest:
    rows: List[ManifestRow] = []
    for raw in data.get("artifacts") or []:
        if isinstance(raw, dict):
            rows.append(ManifestRow(
                artifact_id=str(raw.get("artifact_id") or ""),
                applicability=str(raw.get("applicability") or ""),
                status=str(raw.get("status") or ""),
                filename=str(raw.get("filename") or ""),
                notes=str(raw.get("notes") or ""),
            ))
    return Manifest(
        sib_protocol=str(data.get("sib_protocol") or ""),
        manifest_version=str(data.get("manifest_version") or ""),
        subject=str(data.get("subject") or ""),
        qualification=str(data.get("qualification") or ""),
        specification=str(data.get("specification") or ""),
        curriculum_version=str(data.get("curriculum_version") or ""),
        notebook=str(data.get("notebook") or ""),
        source_manifest=str(data.get("source_manifest") or ""),
        rows=rows,
        source_gaps=list(data.get("source_gaps") or []),
        backlog=list(data.get("backlog") or []),
    )


def validate_manifest(manifest: Optional[Manifest], parse_error: Optional[str],
                      artifacts_dir: Optional[str] = None,
                      qa_report_dir: Optional[str] = None) -> ValidationReport:
    """Validate one subject manifest.

    ``artifacts_dir`` enables disk cross-checks (REQUIRED artifacts present,
    manifest/artifact status agreement via artifact front matter when files
    exist). ``qa_report_dir`` enables publication-evidence checks
    (PUBLISHED requires QA evidence + staged/published presence).

    The validator never creates or deletes artifacts; it reports.
    """
    unit = "manifest"
    rep = ValidationReport(subject_unit=unit)
    if manifest is None:
        rep.add(Codes.MANIFEST_MALFORMED, SEVERITY_ERROR,
                parse_error or "manifest missing")
        return rep

    # -- required manifest-level fields --------------------------------------
    if manifest.sib_protocol != "SIB-1.0":
        rep.add(Codes.MANIFEST_FIELD, SEVERITY_ERROR,
                f"sib_protocol must be SIB-1.0, got {manifest.sib_protocol!r}",
                field="sib_protocol")
    for name in ("manifest_version", "subject", "qualification",
                 "specification", "curriculum_version"):
        if not getattr(manifest, name):
            rep.add(Codes.MANIFEST_FIELD, SEVERITY_ERROR,
                    f"required manifest field missing: {name}", field=name)
    for name in ("notebook", "source_manifest"):
        value = getattr(manifest, name)
        if not value or value.strip().lower() in {"none", "unknown", "tbd"}:
            rep.add(Codes.MANIFEST_FIELD, SEVERITY_ERROR,
                    f"required manifest provenance field missing: {name}",
                    field=name)

    # -- rows -----------------------------------------------------------------
    seen: Dict[str, int] = {}
    unknown_ids: List[str] = []
    for i, row in enumerate(manifest.rows):
        rid = row.artifact_id
        if not taxonomy.is_valid_artifact_id(rid):
            rep.add(Codes.MANIFEST_UNKNOWN_ID, SEVERITY_ERROR,
                    f"row {i}: artifact_id {rid!r} violates taxonomy format",
                    field=f"artifacts[{i}].artifact_id")
            continue
        if rid not in taxonomy.ARTIFACTS:
            rep.add(Codes.MANIFEST_UNKNOWN_ID, SEVERITY_ERROR,
                    f"artifact_id {rid} is not one of the 95 taxonomy artifacts",
                    artifact_id=rid, field=f"artifacts[{i}].artifact_id")
            unknown_ids.append(rid)
            continue
        if rid in seen:
            rep.add(Codes.MANIFEST_DUP, SEVERITY_ERROR,
                    f"duplicate artifact_id {rid} (rows {seen[rid]} and {i})",
                    artifact_id=rid, field=f"artifacts[{i}].artifact_id")
            continue
        seen[rid] = i

        if row.applicability and row.applicability not in VALID_APPLICABILITY:
            rep.add(Codes.MANIFEST_FIELD, SEVERITY_ERROR,
                    f"invalid applicability {row.applicability!r} for {rid} "
                    f"(must be one of {VALID_APPLICABILITY})",
                    artifact_id=rid, field=f"artifacts[{i}].applicability")
        if row.status and row.status not in _MANIFEST_ROW_STATUSES:
            rep.add(Codes.MANIFEST_STATUS, SEVERITY_ERROR,
                    f"invalid status {row.status!r} for {rid}",
                    artifact_id=rid, field=f"artifacts[{i}].status")
        # impossible combinations
        if row.applicability == "NOT_APPLICABLE" and row.status in {
                STATUS_QA_PASSED, STATUS_STAGED, STATUS_PUBLISHED}:
            rep.add(Codes.MANIFEST_COMBINATION, SEVERITY_ERROR,
                    f"NOT_APPLICABLE artifact {rid} cannot be {row.status}",
                    artifact_id=rid, field=f"artifacts[{i}].status")
        # unsupported publication
        if row.status == STATUS_PUBLISHED:
            if not _publication_evidence(rid, qa_report_dir, artifacts_dir):
                rep.add(Codes.MANIFEST_PUBLISH, SEVERITY_ERROR,
                        f"artifact {rid} is PUBLISHED without QA evidence / "
                        "staged boundary pass; unsupported publication",
                        artifact_id=rid, field=f"artifacts[{i}].status")

    # -- coverage / REQUIRED-on-disk -------------------------------------------
    if artifacts_dir:
        _validate_against_disk(manifest, seen, artifacts_dir, rep)

    # -- source gaps / backlog ---------------------------------------------------
    for i, gap in enumerate(manifest.source_gaps):
        gid = str(gap.get("id") or f"source_gaps[{i}]")
        rep.add(Codes.MANIFEST_GAP, SEVERITY_WARNING,
                f"declared source gap {gid}: {gap.get('description') or 'no description'}",
                field=f"source_gaps[{i}]")
    for i, item in enumerate(manifest.backlog):
        rep.add(Codes.MANIFEST_BACKLOG, SEVERITY_INFO,
                f"backlog entry {item.get('id') or i}: "
                f"{item.get('description') or 'no description'}",
                field=f"backlog[{i}]")
    return rep


def _publication_evidence(artifact_id: str, qa_report_dir: Optional[str],
                          artifacts_dir: Optional[str]) -> bool:
    """Publication requires (a) a QA report passing and (b) the artifact file
    present in a staged/ or published/ directory. Evidence is file existence;
    the validator does not move anything."""
    if qa_report_dir:
        qa_path = os.path.join(qa_report_dir, f"{artifact_id}.qa.json")
        if not os.path.isfile(qa_path):
            return False
        try:
            import json
            with open(qa_path, "r", encoding="utf-8") as fh:
                qa = json.load(fh)
            if not qa.get("qa_passed"):
                return False
        except Exception:
            return False
    if artifacts_dir:
        for sub in ("staged", "published"):
            probe = os.path.join(artifacts_dir, "..", sub, artifact_id + "_*.md")
            hits = __import__("glob").glob(probe)
            if hits:
                return True
        return False
    return False


def _validate_against_disk(manifest: Manifest, seen: Dict[str, int],
                           artifacts_dir: str, rep: ValidationReport) -> None:
    """Cross-check REQUIRED rows against the landing zone on disk.

    Checks (deterministic, report-only):
      * REQUIRED artifact without any file in artifacts/ -> MANIFEST_MISSING_REQ
      * file present for a manifest row with front-matter status disagreeing
        with manifest status -> MANIFEST_DISAGREE
      * files on disk whose artifact_id has no manifest row -> MANIFEST_DISAGREE

    A missing/unreadable landing-zone directory is not itself an error: the
    REQUIRED-presence check covers it (every REQUIRED row is then missing).
    """
    from .frontmatter import parse_front_matter

    def _status_of(path: str) -> Tuple[str, str]:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                text = fh.read()
            fm = parse_front_matter(text)
            return str(fm.metadata.get("status") or ""), str(fm.metadata.get("artifact_id") or "")
        except Exception:
            return "", ""

    try:
        files = sorted(f for f in os.listdir(artifacts_dir) if f.endswith(".md"))
    except (FileNotFoundError, NotADirectoryError):
        files = []
    disk_ids: List[str] = []
    for fname in files:
        status, aid = _status_of(os.path.join(artifacts_dir, fname))
        if aid:
            disk_ids.append(aid)
        row = manifest.row(aid) if aid else None
        if row is None:
            rep.add(Codes.MANIFEST_DISAGREE, SEVERITY_ERROR,
                    f"artifact file {fname} (artifact_id {aid or '?'}) has no "
                    "manifest row",
                    artifact_id=aid or "?", field="artifacts")
            continue
        if row.status and status and row.status != status:
            rep.add(Codes.MANIFEST_DISAGREE, SEVERITY_ERROR,
                    f"artifact {aid} front-matter status {status} disagrees "
                    f"with manifest status {row.status}",
                    artifact_id=aid, field="status")
        if row.filename and row.filename != fname:
            rep.add(Codes.IDENT_FILENAME, SEVERITY_ERROR,
                    f"manifest filename {row.filename!r} != on-disk {fname!r} "
                    f"for {aid}",
                    artifact_id=aid, field="filename")

    for rid, idx in sorted(seen.items()):
        row = manifest.rows[idx]
        if row.applicability == "REQUIRED" and rid not in disk_ids:
            rep.add(Codes.MANIFEST_MISSING_REQ, SEVERITY_ERROR,
                    f"REQUIRED artifact {rid} has no file in the landing zone",
                    artifact_id=rid, field="artifacts")


def manifest_counts(manifest: Manifest) -> Dict[str, int]:
    """Deterministic completion metrics (protocol §9)."""
    counts: Dict[str, int] = {
        "artifacts_defined": taxonomy.TAXONOMY_SIZE,
        "rows": len(manifest.rows),
    }
    for appl in VALID_APPLICABILITY:
        counts[appl] = sum(1 for r in manifest.rows if r.applicability == appl)
    for status in ALL_STATUSES:
        counts[status] = sum(1 for r in manifest.rows if r.status == status)
    counts["UNMANIFESTED"] = taxonomy.TAXONOMY_SIZE - len(
        {r.artifact_id for r in manifest.rows if r.artifact_id in taxonomy.ARTIFACTS})
    counts["source_gaps"] = len(manifest.source_gaps)
    counts["backlog"] = len(manifest.backlog)
    return counts
