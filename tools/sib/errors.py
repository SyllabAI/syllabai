"""SIB structured validation error model.

Machine-readable, deterministic. Every issue carries:
  code        -- stable registry code (e.g. SIB-META-001)
  severity    -- ERROR | WARNING | INFO
  artifact_id -- artifact the issue belongs to (may be '' for manifest-level)
  record_id   -- record-level issue target, when applicable ('' otherwise)
  field       -- dotted field path the issue refers to ('' when not field-bound)
  message     -- human explanation (deterministic for identical input)

Correctness failures are NEVER downgraded to WARNING merely to allow
ingestion: any ERROR severity fails QA.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"
SEVERITIES = (SEVERITY_ERROR, SEVERITY_WARNING, SEVERITY_INFO)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: str
    artifact_id: str
    record_id: str
    field: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "artifact_id": self.artifact_id,
            "record_id": self.record_id,
            "field": self.field,
            "message": self.message,
        }


@dataclass
class ValidationReport:
    """Ordered, deterministic validation result for one validation unit."""

    subject_unit: str                      # e.g. artifact id or manifest name
    issues: List[ValidationIssue] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    # -- mutation ------------------------------------------------------------
    def add(self, code: str, severity: str, message: str, *,
            artifact_id: str = "", record_id: str = "", field: str = "") -> None:
        if severity not in SEVERITIES:
            raise ValueError(f"unknown severity: {severity}")
        self.issues.append(ValidationIssue(code, severity, artifact_id,
                                           record_id, field, message))

    def extend(self, other: "ValidationReport") -> None:
        self.issues.extend(other.issues)

    # -- queries -------------------------------------------------------------
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_ERROR]

    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_WARNING]

    def infos(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == SEVERITY_INFO]

    @property
    def qa_passed(self) -> bool:
        """Structural QA verdict: no ERROR-severity issues."""
        return not self.errors()

    def codes(self) -> List[str]:
        """Sorted unique issue codes (stable)."""
        return sorted({i.code for i in self.issues})

    # -- deterministic serialization ------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        issues = sorted(
            self.issues,
            key=lambda i: (i.code, i.artifact_id, i.record_id, i.field, i.message),
        )
        return {
            "unit": self.subject_unit,
            "qa_passed": self.qa_passed,
            "counts": {
                "ERROR": len(self.errors()),
                "WARNING": len(self.warnings()),
                "INFO": len(self.infos()),
            },
            "issues": [i.to_dict() for i in issues],
            "context": _sorted_context(self.context),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False,
                          sort_keys=True) + "\n"

    def __iter__(self) -> Iterator[ValidationIssue]:
        return iter(self.issues)

    def __len__(self) -> int:
        return len(self.issues)


def _sorted_context(ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively sort dict keys for deterministic output; leave lists as-is
    (callers must already build lists deterministically)."""
    if isinstance(ctx, dict):
        return {k: _sorted_context(v) for k, v in sorted(ctx.items())}
    if isinstance(ctx, list):
        return [_sorted_context(v) for v in ctx]
    return ctx


# --------------------------------------------------------------------------
# Issue-code registry. Codes are stable identifiers; never repurpose a code.
# --------------------------------------------------------------------------

class Codes:
    # front matter / metadata
    META_MISSING = "SIB-META-001"          # required front-matter field missing
    META_INVALID = "SIB-META-002"          # field present but malformed
    META_PROTOCOL = "SIB-META-003"         # sib_protocol mismatch
    META_FRONTMATTER = "SIB-META-004"      # no/unparsable YAML front matter
    # identity
    IDENT_ARTIFACT_ID = "SIB-IDENT-001"    # artifact_id shape invalid
    IDENT_UNKNOWN = "SIB-IDENT-002"        # artifact_id not in the 95 taxonomy
    IDENT_FAMILY = "SIB-IDENT-003"         # research_family != family of artifact_id
    IDENT_FILENAME = "SIB-IDENT-004"       # filename contradicts metadata identity
    IDENT_FILENAME_CANON = "SIB-IDENT-005" # filename not canonical (INFO)
    IDENT_APPLICABILITY = "SIB-IDENT-006"  # invalid applicability value
    IDENT_DUP_ARTIFACT = "SIB-IDENT-007"   # duplicate artifact id (manifest scope)
    IDENT_DUP_RECORD = "SIB-IDENT-008"     # duplicate record id within artifact
    IDENT_RECORD_ID = "SIB-IDENT-009"      # record id shape invalid
    IDENT_RECORD_FAMILY = "SIB-IDENT-010"  # record id family != artifact family
    IDENT_VERSION = "SIB-IDENT-011"        # artifact_version missing/invalid
    # sections
    SECTION_MISSING = "SIB-SECT-001"       # required universal section missing
    # lifecycle
    STATUS_INVALID = "SIB-STATUS-001"      # unknown status value
    STATUS_TRANSITION = "SIB-STATUS-002"   # invalid lifecycle transition
    STATUS_PUBLICATION = "SIB-STATUS-003"  # unsupported publication state
    # temporal / source semantics
    TEMPORAL_MISSING = "SIB-TEMP-001"      # temporal scope absent/empty
    TEMPORAL_CONTRADICTION = "SIB-TEMP-002"  # current/legacy contradiction
    TEMPORAL_LABEL = "SIB-TEMP-003"        # label outside the 4 canonical labels
    TEMPORAL_MIXING = "SIB-TEMP-004"       # current/legacy mixing w/o explicit label
    SOURCE_SCOPE_MISSING = "SIB-SRC-001"   # no source basis declared
    # provenance
    PROV_MISSING = "SIB-PROV-001"          # required provenance field missing
    PROV_UNKNOWN = "SIB-PROV-002"          # provenance reference unresolvable
    PROV_UNDATEABLE = "SIB-PROV-003"       # generated_at missing/malformed
    # curriculum anchors
    ANCHOR_INVALID = "SIB-ANCH-001"        # invented/invalid identifier shape
    ANCHOR_UNRESOLVED = "SIB-ANCH-002"     # structurally valid but not resolvable
    ANCHOR_REGISTRY_ABSENT = "SIB-ANCH-003"  # no registry supplied (INFO)
    ANCHOR_RESOLVED = "SIB-ANCH-004"       # resolvable existing identifier (INFO)
    # manifest
    MANIFEST_MALFORMED = "SIB-MANI-001"    # unparsable/missing manifest
    MANIFEST_FIELD = "SIB-MANI-002"        # required manifest field missing/invalid
    MANIFEST_DUP = "SIB-MANI-003"          # duplicate artifact id in manifest
    MANIFEST_UNKNOWN_ID = "SIB-MANI-004"   # artifact id outside taxonomy
    MANIFEST_STATUS = "SIB-MANI-005"       # invalid manifest status value
    MANIFEST_COMBINATION = "SIB-MANI-006"  # impossible status/applicability combo
    MANIFEST_MISSING_REQ = "SIB-MANI-007"  # REQUIRED artifact absent from disk
    MANIFEST_DISAGREE = "SIB-MANI-008"     # manifest/artifact status disagreement
    MANIFEST_PUBLISH = "SIB-MANI-009"      # unsupported publication in manifest
    MANIFEST_FAMILY = "SIB-MANI-010"       # invalid family/artifact combination
    MANIFEST_GAP = "SIB-MANI-011"          # declared source gap (WARNING)
    MANIFEST_BACKLOG = "SIB-MANI-012"      # backlog entry present (INFO)
    # ingestion / runtime boundary
    INGEST_PATH = "SIB-ING-001"            # write attempted outside library root
    INGEST_ORDER = "SIB-ING-002"           # staging/publication precondition failed
