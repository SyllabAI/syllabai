"""Curriculum-anchor validation for SIB artifacts.

Boundary rules (task §5):
* validate identifier SHAPE;
* resolve against an OPTIONAL curriculum registry when one is supplied;
* distinguish: structurally valid / resolvable-existing / unresolved /
  invented-invalid;
* NEVER create SpecificationPoints, KG nodes/edges, or mutate curriculum
  truth. Unresolved references are reported, not repaired.

Specification-point ID shape follows the specification-point convention used
across SyllabAI (e.g. Edexcel numbered objectives ``1.1``, ``3.24``):
    <unit 1-2 digits>.<point 1-3 digits>[.<sub-point 1-2 digits>]

The registry file (optional, operator-supplied) is a YAML/JSON list of
identifier strings, e.g. a pinned copy of syllabai-resources
``graph/specification_points.yaml`` ids.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional

from .errors import Codes, SEVERITY_ERROR, SEVERITY_INFO, SEVERITY_WARNING, ValidationReport

# Edexcel-style numbered specification point: 1.1 / 2.35 / 4.3.2
SPEC_POINT_RE = re.compile(r"^\d{1,2}\.\d{1,3}(?:\.\d{1,2})?$")

# prose field labels that carry anchors in SIB records/artifacts
ANCHOR_FIELD_LABELS = (
    "Specification Points:",
    "Specification Points",
    "Specification Point:",
    "Specification anchors:",
    "Curriculum anchors:",
)

# a free "Specification Points: 1.1, 2.3; 3.4/1.5" tail -> candidates.
# Lookarounds keep the match from being a substring of a longer dotted
# number ("999.999.999" must NOT yield the plausible-looking "99.999").
_CANDIDATE_RE = re.compile(
    r"(?<![\d.])(\d{1,2}\.\d{1,3}(?:\.\d{1,2})?)(?![\d.])")
# any dotted-numeric token inside an anchor field (for malformed detection)
_DOTTED_TOKEN_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)+)(?![\w.])")


@dataclass(frozen=True)
class AnchorRef:
    """One curriculum-anchor reference extracted from artifact content."""

    raw: str                 # matched text
    record_id: str           # owning record ('' = artifact-level)
    kind: str                # 'spec_point' | 'malformed'


def valid_identifier_shape(identifier: str) -> bool:
    """Structural (shape) validity only."""
    return bool(SPEC_POINT_RE.fullmatch(identifier or ""))


def extract_anchor_refs(artifact_text: str) -> List[AnchorRef]:
    """Extract specification-point candidates from anchor-bearing fields.

    Deterministic: scan order is line order; candidate order is match order;
    duplicates removed keeping first occurrence. Dotted tokens inside anchor
    fields that fail the identifier shape are returned as 'malformed' refs
    so the validator can flag invented/invalid identifiers (they are never
    silently dropped).
    """
    refs: List[AnchorRef] = []
    seen: set = set()
    current_record = ""
    for line in artifact_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("### "):
            current_record = stripped[4:].split(" ")[0].strip()
            continue
        for label in ANCHOR_FIELD_LABELS:
            idx = line.find(label)
            if idx < 0:
                continue
            tail = line[idx + len(label):]
            valid_in_tail = set()
            for m in _CANDIDATE_RE.finditer(tail):
                raw = m.group(1)
                key = (raw, current_record)
                if key not in seen:
                    seen.add(key)
                    refs.append(AnchorRef(raw=raw, record_id=current_record,
                                          kind="spec_point"))
                valid_in_tail.add(m.group(1))
            for m in _DOTTED_TOKEN_RE.finditer(tail):
                tok = m.group(1)
                if tok in valid_in_tail or valid_identifier_shape(tok):
                    continue
                key = (tok, current_record)
                if key not in seen:
                    seen.add(key)
                    refs.append(AnchorRef(raw=tok, record_id=current_record,
                                          kind="malformed"))
    return refs


class AnchorRegistry:
    """Optional resolution layer over an operator-supplied identifier set.

    Absent registry -> validation reports ANCHOR_REGISTRY_ABSENT (INFO) and
    every structurally-valid anchor is UNRESOLVED (WARNING), not an error:
    shape correctness is still evidence; existence is reported honestly.
    """

    def __init__(self, identifiers: Optional[FrozenSet[str]] = None):
        self._ids = frozenset(identifiers) if identifiers else None

    @property
    def present(self) -> bool:
        return self._ids is not None

    def resolve(self, identifier: str) -> str:
        """'resolved' | 'unresolved' | 'no_registry'."""
        if self._ids is None:
            return "no_registry"
        return "resolved" if identifier in self._ids else "unresolved"


def validate_anchors(artifact_text: str, artifact_id: str,
                     registry: Optional[AnchorRegistry] = None,
                     report: Optional[ValidationReport] = None
                     ) -> ValidationReport:
    """Validate all anchor references in ``artifact_text``.

    Never mutates anything. Issues:
      SIB-ANCH-001 ERROR   invented/invalid identifier shape
      SIB-ANCH-002 WARNING unresolved (registry present, id absent)
      SIB-ANCH-003 INFO    registry absent (resolution not attempted)
      SIB-ANCH-004 INFO    resolved (registry hit) -- provenance of resolution
    """
    rep = report or ValidationReport(subject_unit=artifact_id)
    reg = registry or AnchorRegistry(None)
    if not reg.present:
        rep.add(Codes.ANCHOR_REGISTRY_ABSENT, SEVERITY_INFO,
                "no curriculum registry supplied; anchor existence not checked",
                artifact_id=artifact_id, field="curriculum_anchor_refs")
    for ref in extract_anchor_refs(artifact_text):
        if not valid_identifier_shape(ref.raw):
            rep.add(Codes.ANCHOR_INVALID, SEVERITY_ERROR,
                    f"invalid curriculum identifier shape: {ref.raw!r}",
                    artifact_id=artifact_id, record_id=ref.record_id,
                    field=f"curriculum_anchor_refs[{ref.raw}]")
            continue
        state = reg.resolve(ref.raw)
        if state == "resolved":
            rep.add(Codes.ANCHOR_RESOLVED, SEVERITY_INFO,
                    f"anchor {ref.raw} resolves to registry entry",
                    artifact_id=artifact_id, record_id=ref.record_id,
                    field=f"curriculum_anchor_refs[{ref.raw}]")
        elif state == "unresolved":
            rep.add(Codes.ANCHOR_UNRESOLVED, SEVERITY_WARNING,
                    f"anchor {ref.raw} not present in curriculum registry; "
                    "reported, not repaired",
                    artifact_id=artifact_id, record_id=ref.record_id,
                    field=f"curriculum_anchor_refs[{ref.raw}]")
        else:  # no_registry: shape-valid, existence unknown
            rep.add(Codes.ANCHOR_UNRESOLVED, SEVERITY_WARNING,
                    f"anchor {ref.raw} is structurally valid but unresolvable "
                    "(no registry); reported, not repaired",
                    artifact_id=artifact_id, record_id=ref.record_id,
                    field=f"curriculum_anchor_refs[{ref.raw}]")
    return rep


def build_registry(identifiers: Optional[List[str]]) -> AnchorRegistry:
    """Convenience constructor used by the CLI/ingest layer."""
    if not identifiers:
        return AnchorRegistry(None)
    return AnchorRegistry(frozenset(identifiers))
