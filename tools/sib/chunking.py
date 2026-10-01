"""Deterministic semantic chunking for SIB artifacts (SIB-specific).

Not a generic RAG chunker. Chunk boundaries follow schema §9:
  * one machine-readable record (### <FAM>-NNN — ...) -> one chunk;
  * top-level universal sections -> one chunk each (records excluded from
    their parent section chunk);
  * preface (front-matter-following content before the first ## heading) is
    attached to the Purpose section chunk (or becomes its own chunk).

Every chunk preserves the full provenance envelope:

    artifact_id, record_id, subject, qualification, specification,
    curriculum_version, research_family, temporal_scope, source_scope,
    status, curriculum_anchor_refs, provenance

Chunk identity is deterministic:
    chunk_id = <artifact_id>:sec:<HEADING_SLUG>
             | <artifact_id>:rec:<RECORD_ID>
    content_sha256 over the chunk's exact text.

No timestamps, no random UUIDs, anywhere in chunk identity.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .artifact_validator import ArtifactModel, parse_artifact
from .anchors import extract_anchor_refs

_RECORD_HEADER_RE = re.compile(r"^(###\s+[A-Z]{2,3}-\d{3}\s+—.*)$")
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")


@dataclass
class SibChunk:
    chunk_id: str
    kind: str                       # "section" | "record"
    heading: str
    artifact_id: str
    record_id: str                  # "" for section chunks
    text: str
    content_sha256: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "kind": self.kind,
            "heading": self.heading,
            "artifact_id": self.artifact_id,
            "record_id": self.record_id,
            "content_sha256": self.content_sha256,
            "metadata": self.metadata,
            "text": self.text,
        }


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(heading: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", heading).strip("_").upper()
    return slug or "UNTITLED"


def chunk_artifact(text: str) -> List[SibChunk]:
    """Split a SIB artifact into provenance-preserving semantic chunks.

    Deterministic: identical artifact text -> identical chunk list
    (ids, order, content hashes).
    """
    model: ArtifactModel = parse_artifact(text)
    meta = model.metadata if model.front_matter.parse_error is None else {}
    aid = str(meta.get("artifact_id") or "")

    envelope: Dict[str, Any] = {
        "artifact_id": aid,
        "subject": meta.get("subject", ""),
        "qualification": meta.get("qualification", ""),
        "specification": meta.get("specification", ""),
        "curriculum_version": meta.get("curriculum_version", ""),
        "research_family": meta.get("research_family", ""),
        "temporal_scope": meta.get("temporal_scope", {}),
        "source_scope": meta.get("source_scope", {}),
        "status": meta.get("status", ""),
        "artifact_version": meta.get("artifact_version", ""),
        "curriculum_anchor_refs": sorted(
            {r.raw for r in extract_anchor_refs(model.body)}),
        "provenance": meta.get("provenance", {}),
    }

    # -- split body into segments ------------------------------------------
    lines = model.body.split("\n")
    preface: List[str] = []
    sections: List[Dict[str, Any]] = []       # {heading, lines, record_chunks}
    records: List[Dict[str, Any]] = []        # {record_id, lines}
    current_section: Optional[Dict[str, Any]] = None
    current_record: Optional[Dict[str, Any]] = None

    for line in lines:
        m_rec = _RECORD_HEADER_RE.match(line.strip())
        if m_rec and m_rec.group(1):
            # record header line is "### MIS-001 — name"
            rid = line.strip().split()[1]
            current_record = {"record_id": rid, "lines": [line]}
            records.append(current_record)
            if current_section is not None:
                current_section = None  # record chunks stand alone
            continue
        if current_record is not None:
            m_h = _HEADING_RE.match(line.strip())
            if m_h:  # a record ends at the next ## heading
                current_record = None
            else:
                current_record["lines"].append(line)
                continue
        m_h = _HEADING_RE.match(line.strip())
        if m_h:
            current_section = {"heading": m_h.group(1), "lines": [line]}
            sections.append(current_section)
            continue
        if current_section is not None:
            current_section["lines"].append(line)
        else:
            preface.append(line)

    # -- build chunks ---------------------------------------------------------
    chunks: List[SibChunk] = []

    def _mk(chunk_id: str, kind: str, heading: str, record_id: str,
            text: str) -> SibChunk:
        md = dict(envelope)
        md["record_id"] = record_id
        return SibChunk(chunk_id=chunk_id, kind=kind, heading=heading,
                        artifact_id=aid, record_id=record_id,
                        text=text.rstrip("\n"), content_sha256=_sha256(text.rstrip("\n")),
                        metadata=md)

    preface_text = "\n".join(preface).strip()
    if preface_text:
        # attach preface to the first section (typically Purpose), or standalone
        target = sections[0]["heading"] if sections else "PREFACE"
        cid = f"{aid}:sec:{_slug(target)}" if sections else f"{aid}:sec:PREFACE"
        chunks.append(_mk(cid, "section", target, "", preface_text))

    for sec in sections:
        text = "\n".join(sec["lines"]).strip("\n")
        if not text.strip():
            continue
        # drop record lines from the section chunk (records are their own chunks)
        section_only_lines = [ln for ln in sec["lines"]
                              if not _RECORD_HEADER_RE.match(ln.strip())]
        text = "\n".join(section_only_lines).strip("\n")
        chunks.append(_mk(f"{aid}:sec:{_slug(sec['heading'])}", "section",
                          sec["heading"], "", text))

    for rec in records:
        text = "\n".join(rec["lines"]).strip("\n")
        chunks.append(_mk(f"{aid}:rec:{rec['record_id']}", "record",
                          rec["record_id"], rec["record_id"], text))

    return chunks


def chunk_envelope_fields() -> List[str]:
    """The provenance fields every chunk preserves (task §9 contract)."""
    return [
        "artifact_id", "record_id", "subject", "qualification",
        "specification", "curriculum_version", "research_family",
        "temporal_scope", "source_scope", "status",
        "curriculum_anchor_refs", "provenance",
    ]
