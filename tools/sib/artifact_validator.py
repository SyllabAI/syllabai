"""SIB v1 artifact validator -- deterministic structural QA.

Implements validation for:
* required front-matter metadata (schema §2)
* artifact identity: ID format, filename convention, family membership,
  applicability, duplicates (with peer artifacts) (schema §1, task §2)
* required universal sections (schema §3)
* status lifecycle membership (protocol §5)
* temporal/source semantics: CURRENT/LEGACY/SUPPLEMENTARY/RESEARCH labels and
  contradiction detection (schema §5, task §3)
* provenance sufficiency (task §4)
* machine-readable records with stable IDs (schema §6)
* curriculum anchors (task §5)

The validator is PURE: it returns evidence; it never mutates the artifact,
any manifest, or any canonical state. Validation is evidence that structural
requirements are satisfied -- it is NOT educational correctness.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from . import taxonomy
from .anchors import AnchorRegistry, validate_anchors
from .errors import (Codes, SEVERITY_ERROR, SEVERITY_INFO, SEVERITY_WARNING,
                     ValidationReport)
from .frontmatter import FrontMatterResult, parse_front_matter
from .lifecycle import STATUS_GENERATED, is_valid_status

# ---------------------------------------------------------------------------
# schema constants
# ---------------------------------------------------------------------------

REQUIRED_METADATA_FIELDS: Tuple[str, ...] = (
    "sib_protocol", "artifact_id", "artifact_version", "subject",
    "qualification", "specification", "curriculum_version", "research_family",
    "applicability", "temporal_scope", "source_scope", "status",
    "generated_by", "generated_at", "provenance",
)

REQUIRED_PROVENANCE_FIELDS: Tuple[str, ...] = (
    "notebook", "source_manifest",
)

REQUIRED_SECTIONS: Tuple[Tuple[str, str], ...] = (
    # (canonical heading, regex)
    ("Purpose", r"^##\s+Purpose\b"),
    ("Scope", r"^##\s+Scope\b"),
    ("Executive Summary", r"^##\s+Executive Summary\b"),
    ("Main Analysis", r"^##\s+Main Analysis\b"),
    ("Evidence / Source Basis", r"^##\s+Evidence\s*/\s*Source Basis\b"),
    ("Limitations / Coverage Gaps",
     r"^##\s+Limitations\s*/\s*Coverage Gaps\b"),
    ("Research Status", r"^##\s+Research Status\b"),
)

VALID_APPLICABILITY = ("REQUIRED", "OPTIONAL", "NOT_APPLICABLE")

VALID_TEMPORAL_LABELS = (
    "CURRENT — AUTHORITATIVE",
    "LEGACY — HISTORICAL",
    "SUPPLEMENTARY",
    "RESEARCH / INFERRED",
)

_SOURCE_SCOPE_KEYS = (
    "specification", "textbook", "question_papers", "mark_schemes",
    "examiner_reports", "supplementary",
)

_GENERATED_BY_VALUES = ("notebooklm", "operator", "agent", "human")

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_VERSION_RE = re.compile(r"^\d+\.\d+(\.\d+)?$")

_RECORD_HEADER_RE = re.compile(r"^###\s+([A-Z]{2,3}-\d{3})\s+—")

# ---------------------------------------------------------------------------
# parsed artifact model
# ---------------------------------------------------------------------------


@dataclass
class ArtifactModel:
    """Parsed representation of one SIB artifact (no filesystem effects)."""

    raw_text: str
    front_matter: FrontMatterResult
    metadata: Dict[str, Any]
    body: str
    records: List[str] = field(default_factory=list)   # record IDs in order
    parse_mode: str = "builtin"


def parse_artifact(text: str) -> ArtifactModel:
    fm = parse_front_matter(text)
    metadata = fm.metadata if isinstance(fm.metadata, dict) else {}
    records = [m.group(1) for line in fm.body.split("\n")
               if (m := _RECORD_HEADER_RE.match(line.strip()))]
    return ArtifactModel(raw_text=text, front_matter=fm, metadata=metadata,
                         body=fm.body, records=records,
                         parse_mode=fm.parse_mode)


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------


def validate_artifact(text: str, *,
                      filename: str = "",
                      known_artifact_ids: Optional[List[str]] = None,
                      registry: Optional[AnchorRegistry] = None,
                      source_manifest_ids: Optional[List[str]] = None,
                      artifact_id_override: str = "",
                      ) -> ValidationReport:
    """Validate one SIB artifact and return a deterministic report.

    Args:
        text: artifact markdown (front matter + body).
        filename: on-disk filename when known (identity cross-check).
        known_artifact_ids: artifact IDs already present in the manifest /
            landing zone (duplicate detection). The validated artifact's own
            ID is excluded automatically.
        registry: optional curriculum-anchor registry.
        source_manifest_ids: identifiers declared by the operator-provided
            source manifest (provenance cross-check). Absent -> provenance
            references are shape-checked only.
        artifact_id_override: use when the front matter is too broken to
            supply a usable artifact ID (prevents empty artifact_id in
            issues).
    """
    model = parse_artifact(text)
    meta = model.metadata
    aid = str(meta.get("artifact_id") or artifact_id_override or "")
    if not taxonomy.is_valid_artifact_id(aid):
        aid = artifact_id_override or ""
    rep = ValidationReport(subject_unit=aid or "artifact")

    _validate_front_matter_block(model, rep, aid)
    _validate_metadata_fields(meta, rep, aid)
    _validate_identity(meta, rep, aid, filename, known_artifact_ids)
    _validate_sections(model.body, rep, aid)
    _validate_status(meta, rep, aid)
    _validate_temporal_semantics(meta, model.body, rep, aid)
    _validate_source_scope(meta, rep, aid)
    _validate_provenance(meta, rep, aid, source_manifest_ids)
    _validate_records(model, rep, aid)
    validate_anchors(text, aid, registry=registry, report=rep)
    return rep


# -- front matter block ------------------------------------------------------


def _validate_front_matter_block(model: ArtifactModel,
                                 rep: ValidationReport, aid: str) -> None:
    fm = model.front_matter
    if fm.parse_error:
        rep.add(Codes.META_FRONTMATTER, SEVERITY_ERROR,
                f"front matter unusable: {fm.parse_error}",
                artifact_id=aid, field="front_matter")
        return
    if fm.parse_mode == "builtin" and not fm.metadata:
        rep.add(Codes.META_FRONTMATTER, SEVERITY_ERROR,
                "front matter parsed empty; metadata absent",
                artifact_id=aid, field="front_matter")


# -- required metadata --------------------------------------------------------


def _validate_metadata_fields(meta: Dict[str, Any], rep: ValidationReport,
                              aid: str) -> None:
    for field_name in REQUIRED_METADATA_FIELDS:
        if field_name not in meta or meta[field_name] in (None, ""):
            rep.add(Codes.META_MISSING, SEVERITY_ERROR,
                    f"required metadata field missing: {field_name}",
                    artifact_id=aid, field=field_name)
    # value-level checks for present fields
    if meta.get("sib_protocol") not in (None, ""):
        if str(meta.get("sib_protocol")) != "SIB-1.0":
            rep.add(Codes.META_PROTOCOL, SEVERITY_ERROR,
                    f"sib_protocol must be SIB-1.0, got {meta.get('sib_protocol')!r}",
                    artifact_id=aid, field="sib_protocol")
    version = meta.get("artifact_version")
    if version not in (None, "") and not _VERSION_RE.fullmatch(str(version)):
        rep.add(Codes.IDENT_VERSION, SEVERITY_ERROR,
                f"artifact_version must be MAJOR.MINOR[.PATCH], got {version!r}",
                artifact_id=aid, field="artifact_version")
    generated_at = meta.get("generated_at")
    if generated_at not in (None, "") and not _DATE_RE.fullmatch(str(generated_at)):
        rep.add(Codes.PROV_UNDATEABLE, SEVERITY_ERROR,
                f"generated_at must be YYYY-MM-DD, got {generated_at!r}",
                artifact_id=aid, field="generated_at")
    generated_by = meta.get("generated_by")
    if generated_by not in (None, "") and str(generated_by) not in _GENERATED_BY_VALUES:
        rep.add(Codes.META_INVALID, SEVERITY_ERROR,
                f"generated_by {generated_by!r} outside {_GENERATED_BY_VALUES}",
                artifact_id=aid, field="generated_by")


# -- identity ------------------------------------------------------------------


def _validate_identity(meta: Dict[str, Any], rep: ValidationReport, aid: str,
                       filename: str, known_artifact_ids: Optional[List[str]]) -> None:
    # artifact ID shape + taxonomy membership
    raw_id = meta.get("artifact_id")
    if raw_id not in (None, ""):
        if not taxonomy.is_valid_artifact_id(str(raw_id)):
            rep.add(Codes.IDENT_ARTIFACT_ID, SEVERITY_ERROR,
                    f"artifact_id {raw_id!r} violates format {taxonomy.ARTIFACT_ID_PATTERN}",
                    artifact_id=aid, field="artifact_id")
        elif str(raw_id) not in taxonomy.ARTIFACTS:
            rep.add(Codes.IDENT_UNKNOWN, SEVERITY_ERROR,
                    f"artifact_id {raw_id!r} is not one of the 95 taxonomy artifacts",
                    artifact_id=aid, field="artifact_id")

    # family membership
    fam = meta.get("research_family")
    exp_fam = taxonomy.expected_family_slug(aid)
    if fam not in (None, "") and exp_fam and str(fam) != exp_fam:
        rep.add(Codes.IDENT_FAMILY, SEVERITY_ERROR,
                f"research_family {fam!r} does not match artifact family "
                f"{exp_fam!r} for {aid}",
                artifact_id=aid, field="research_family")

    # applicability
    appl = meta.get("applicability")
    if appl not in (None, "") and str(appl) not in VALID_APPLICABILITY:
        rep.add(Codes.IDENT_APPLICABILITY, SEVERITY_ERROR,
                f"applicability {appl!r} outside {VALID_APPLICABILITY}",
                artifact_id=aid, field="applicability")

    # filename convention
    if filename:
        ok, detail = _filename_matches_metadata(filename, meta)
        if not ok:
            severity = SEVERITY_ERROR if detail.startswith("identity") else SEVERITY_INFO
            code = Codes.IDENT_FILENAME if severity == SEVERITY_ERROR else Codes.IDENT_FILENAME_CANON
            rep.add(code, severity, detail, artifact_id=aid, field="filename")

    # duplicates (peer scope): the artifact under validation must not
    # duplicate an ID already present in the scope. Callers scanning a
    # landing zone exclude the file under validation from the list.
    if known_artifact_ids:
        norm = str(raw_id) if raw_id else aid
        if norm and norm in known_artifact_ids:
            rep.add(Codes.IDENT_DUP_ARTIFACT, SEVERITY_ERROR,
                    f"duplicate artifact_id {norm} already present in scope",
                    artifact_id=norm, field="artifact_id")


def _filename_matches_metadata(filename: str,
                               meta: Dict[str, Any]) -> Tuple[bool, str]:
    """Deterministic filename identity check.

    Expected shape: <SUBJECT>_<SPECIFICATION>_<ARTIFACT_ID>_<SLUG>.md where
    SLUG is uppercase letters/digits/underscores. See
    docs/research/SIB_VALIDATOR_IMPLEMENTATION_V1.md for the documented
    template/example divergence.
    """
    subject = str(meta.get("subject") or "").upper().replace(" ", "_")
    spec = str(meta.get("specification") or "").upper().replace(" ", "_")
    aid = str(meta.get("artifact_id") or "")
    if not (subject and spec and aid):
        return False, ("identity metadata incomplete; filename cannot be "
                       "cross-checked")
    if f"_{aid}_" not in filename:
        return False, f"identity mismatch: filename {filename!r} lacks artifact id {aid}"
    prefix_ok = filename.startswith(f"{subject}_{spec}_{aid}_")
    if not prefix_ok:
        return False, (f"identity mismatch: filename {filename!r} does not "
                       f"carry subject/specification prefix {subject}_{spec}_{aid}")
    canonical = taxonomy.canonical_filename(
        str(meta.get("subject") or ""), spec, aid)
    if filename != canonical:
        return False, (f"filename {filename!r} is identity-consistent but not "
                       f"canonical ({canonical})")
    return True, "ok"


# -- sections -------------------------------------------------------------------


def _validate_sections(body: str, rep: ValidationReport, aid: str) -> None:
    for title, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, body, flags=re.MULTILINE):
            rep.add(Codes.SECTION_MISSING, SEVERITY_ERROR,
                    f"required section missing: {title}",
                    artifact_id=aid, field=f"sections[{title}]")


# -- lifecycle --------------------------------------------------------------------


def _validate_status(meta: Dict[str, Any], rep: ValidationReport, aid: str) -> None:
    status = meta.get("status")
    if status in (None, ""):
        return  # META_MISSING already covers absence
    if not is_valid_status(str(status)):
        rep.add(Codes.STATUS_INVALID, SEVERITY_ERROR,
                f"status {status!r} outside lifecycle {('GENERATED', 'QA_PASSED', 'QA_FAILED', 'STAGED', 'PUBLISHED')}",
                artifact_id=aid, field="status")
        return
    # Unsupported publication: NotebookLM-generated output BEGINS as
    # GENERATED (protocol §5). QA_PASSED/STAGED/PUBLISHED are set only by
    # the governed staging path; a landing artifact self-declaring them is
    # bypassing the boundary.
    if str(status) in ("QA_PASSED", "STAGED", "PUBLISHED"):
        rep.add(Codes.STATUS_PUBLICATION, SEVERITY_ERROR,
                f"status {status} is only reachable through governed staging "
                "(GENERATED -> QA_PASSED -> STAGED -> PUBLISHED); a landing "
                "artifact must declare GENERATED (or QA_FAILED)",
                artifact_id=aid, field="status")


# -- temporal / source semantics ------------------------------------------------------


def _validate_temporal_semantics(meta: Dict[str, Any], body: str,
                                 rep: ValidationReport, aid: str) -> None:
    ts = meta.get("temporal_scope")
    if ts in (None, ""):
        return  # META_MISSING covers absence
    if not isinstance(ts, dict):
        rep.add(Codes.TEMPORAL_MISSING, SEVERITY_ERROR,
                "temporal_scope must be a mapping with boolean current/legacy",
                artifact_id=aid, field="temporal_scope")
        return
    current = ts.get("current")
    legacy = ts.get("legacy")
    if not isinstance(current, bool) or not isinstance(legacy, bool):
        rep.add(Codes.TEMPORAL_MISSING, SEVERITY_ERROR,
                "temporal_scope.current/.legacy must be booleans",
                artifact_id=aid, field="temporal_scope")
        return
    if not current and not legacy:
        rep.add(Codes.TEMPORAL_MISSING, SEVERITY_ERROR,
                "temporal_scope is empty (current=false, legacy=false): "
                "every artifact must declare at least one temporal scope",
                artifact_id=aid, field="temporal_scope")

    labels_found = [lab for lab in VALID_TEMPORAL_LABELS if lab in body]
    # contradiction: metadata says legacy-only, content claims CURRENT — AUTHORITATIVE
    if current is False:
        for line in body.split("\n"):
            if "CURRENT — AUTHORITATIVE" in line:
                rep.add(Codes.TEMPORAL_CONTRADICTION, SEVERITY_ERROR,
                        "content asserts 'CURRENT — AUTHORITATIVE' while "
                        "temporal_scope.current is false",
                        artifact_id=aid, field="temporal_scope")
                break
    # contradiction: metadata says current-only, content labels legacy evidence
    if legacy is False:
        for line in body.split("\n"):
            if "LEGACY — HISTORICAL" in line:
                rep.add(Codes.TEMPORAL_CONTRADICTION, SEVERITY_ERROR,
                        "content contains 'LEGACY — HISTORICAL' evidence while "
                        "temporal_scope.legacy is false",
                        artifact_id=aid, field="temporal_scope")
                break
    # mixed scope requires explicit labeling
    if current and legacy and not labels_found:
        rep.add(Codes.TEMPORAL_MIXING, SEVERITY_WARNING,
                "temporal_scope covers current and legacy but no explicit "
                "CURRENT — AUTHORITATIVE / LEGACY — HISTORICAL labels found; "
                "current/legacy separation not demonstrable",
                artifact_id=aid, field="temporal_scope")
    # unknown temporal labels (e.g. free-form "current-ish") near claim fields
    for line in body.split("\n"):
        if re.match(r"^\*\*Temporal scope:\*\*", line.strip()):
            tail = line.split(":", 1)[-1].strip()
            if tail and tail not in VALID_TEMPORAL_LABELS:
                rep.add(Codes.TEMPORAL_LABEL, SEVERITY_WARNING,
                        f"non-canonical temporal label {tail!r}; canonical "
                        f"labels: {VALID_TEMPORAL_LABELS}",
                        artifact_id=aid, field="temporal_labels")


# -- source scope ---------------------------------------------------------------


def _validate_source_scope(meta: Dict[str, Any], rep: ValidationReport,
                           aid: str) -> None:
    ss = meta.get("source_scope")
    if ss in (None, ""):
        return  # META_MISSING covers absence
    if not isinstance(ss, dict):
        rep.add(Codes.SOURCE_SCOPE_MISSING, SEVERITY_ERROR,
                "source_scope must be a mapping of boolean source flags",
                artifact_id=aid, field="source_scope")
        return
    if not any(ss.get(k) is True for k in _SOURCE_SCOPE_KEYS):
        rep.add(Codes.SOURCE_SCOPE_MISSING, SEVERITY_ERROR,
                "source_scope declares no source basis (all flags false/absent)",
                artifact_id=aid, field="source_scope")


# -- provenance --------------------------------------------------------------------


def _validate_provenance(meta: Dict[str, Any], rep: ValidationReport, aid: str,
                         source_manifest_ids: Optional[List[str]]) -> None:
    prov = meta.get("provenance")
    if prov in (None, ""):
        # covered by META_MISSING; nothing further possible
        return
    if not isinstance(prov, dict):
        rep.add(Codes.PROV_MISSING, SEVERITY_ERROR,
                "provenance must be a mapping (notebook, source_manifest)",
                artifact_id=aid, field="provenance")
        return
    for field_name in REQUIRED_PROVENANCE_FIELDS:
        value = prov.get(field_name)
        if value in (None, ""):
            rep.add(Codes.PROV_MISSING, SEVERITY_ERROR,
                    f"required provenance field missing: {field_name}",
                    artifact_id=aid, field=f"provenance.{field_name}")
            continue
        value = str(value)
        if len(value.strip()) < 2 or value.strip().lower() in {"none", "unknown", "tbd", "<subject notebook identifier>", "<source manifest identifier>"}:
            rep.add(Codes.PROV_MISSING, SEVERITY_ERROR,
                    f"provenance.{field_name} is not a concrete reference "
                    f"({value!r}); template placeholders are insufficient",
                    artifact_id=aid, field=f"provenance.{field_name}")
            continue
        if source_manifest_ids is not None and field_name == "source_manifest":
            if value not in source_manifest_ids:
                rep.add(Codes.PROV_UNKNOWN, SEVERITY_ERROR,
                        f"provenance.source_manifest {value!r} is not declared "
                        "by the operator source manifest; refusing to invent "
                        "an identifier",
                        artifact_id=aid, field="provenance.source_manifest")


# -- records --------------------------------------------------------------------------


def _validate_records(model: ArtifactModel, rep: ValidationReport, aid: str) -> None:
    seen: Dict[str, int] = {}
    for line in model.body.split("\n"):
        m = _RECORD_HEADER_RE.match(line.strip())
        if not m:
            continue
        rid = m.group(1)
        if rid in seen:
            rep.add(Codes.IDENT_DUP_RECORD, SEVERITY_ERROR,
                    f"duplicate record id {rid} (first at occurrence {seen[rid]})",
                    artifact_id=aid, record_id=rid, field=f"records[{rid}]")
        seen[rid] = seen.get(rid, 0) + 1
    for rid in sorted(set(model.records)):
        if not taxonomy.is_valid_record_id(rid):
            rep.add(Codes.IDENT_RECORD_ID, SEVERITY_ERROR,
                    f"record id {rid} violates format {taxonomy.RECORD_ID_PATTERN}",
                    artifact_id=aid, record_id=rid, field=f"records[{rid}]")
            continue
        fam = taxonomy.expected_record_family(rid)
        if aid and fam and fam != aid.split("-")[0]:
            rep.add(Codes.IDENT_RECORD_FAMILY, SEVERITY_ERROR,
                    f"record id {rid} belongs to family {fam} but artifact "
                    f"family is {aid.split('-')[0]}",
                    artifact_id=aid, record_id=rid, field=f"records[{rid}]")


# -- determinism helpers --------------------------------------------------------------


def content_fingerprint(text: str) -> str:
    """SHA-256 of the artifact text -- observable change detection (schema §8).

    Timestamps/randomness do not participate: identical input -> identical
    fingerprint.
    """
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
