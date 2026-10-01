"""Research-library ingestion scaffolding for SIB artifacts.

Implements the governed pipeline boundary (task §7):

    NotebookLM / external research
        -> SIB Markdown artifacts      (artifacts/  landing zone)
        -> artifact parser             (frontmatter.parse_front_matter)
        -> schema validation           (artifact_validator.validate_artifact)
        -> provenance validation       (artifact_validator + source manifest)
        -> curriculum-anchor validation (anchors.validate_anchors)
        -> QA result                   (qa-reports/<ARTIFACT_ID>.qa.json)
        -> STAGED                      (staged/)
        -> PUBLISHED research library  (published/)

Hard runtime boundary (task §8). SIB ingestion MUST NOT:
  * mutate canonical KG,
  * mutate learner mastery or learner evidence,
  * create SpecificationPoints,
  * bypass assessment validation,
  * replace canonical curriculum content,
  * override provenance,
  * become the sole source of educational truth.

Enforcement model:
  * validation functions are pure (no filesystem writes); the pure layer is
    ``artifact_validator.validate_artifact``; only the explicit QA/stage/
    publish/chunk actions write, and only inside the library root;
  * mutating helpers (stage/publish) write ONLY under the library root,
    enforced by ``_confined`` path checks (SIB-ING-001 on violation);
  * transitions strictly follow lifecycle.py: a PASSING QA report bound to
    the exact landing content is a precondition for staging, and a PASSING
    QA report is ALSO re-verified at publication time (SIB-ING-002) -- a
    file dropped directly into staged/ cannot be published without QA
    evidence;
  * NOT_APPLICABLE artifacts are valid inventory but never advance to
    QA_PASSED/STAGED/PUBLISHED through this pipeline;
  * no Subject Tutor integration is implemented here.

Library layout (all under the library root, e.g. research/sib/CHEMISTRY_4CH1/):

    manifest.yaml            operator-owned inventory
    source_manifest.yaml     operator-owned source provenance
    artifacts/               landing zone (GENERATED / QA_FAILED)
    staged/                  validated, awaiting publication decision
    published/               published research library
    qa-reports/              deterministic QA results
    chunks/                  deterministic chunk JSONL per artifact
"""
from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from . import lifecycle
from .anchors import AnchorRegistry, build_registry
from .artifact_validator import VALID_APPLICABILITY, content_fingerprint, validate_artifact
from .errors import Codes, SEVERITY_ERROR, ValidationReport
from .frontmatter import parse_front_matter
from .yamlmini import load_yaml

_LIBRARY_SUBDIRS = ("artifacts", "staged", "published", "qa-reports", "chunks")

_FORBIDDEN_PLACEHOLDERS = {
    "<subject notebook identifier>", "<source manifest identifier>",
}


@dataclass
class IngestResult:
    artifact_id: str
    action: str                       # "qa" | "stage" | "publish"
    qa_passed: bool
    report: ValidationReport
    moved_to: str = ""                # destination path for stage/publish

    def summary(self) -> Dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "action": self.action,
            "qa_passed": self.qa_passed,
            "errors": len(self.report.errors()),
            "warnings": len(self.report.warnings()),
            "infos": len(self.report.infos()),
            "moved_to": self.moved_to,
        }


class SibLibrary:
    """Filesystem boundary of one subject's research library.

    All writes are confined to ``root``; canonical curriculum/KG/learner
    state is simply not addressable from this class.
    """

    def __init__(self, root: str, registry_ids: Optional[List[str]] = None):
        self.root = os.path.abspath(root)
        self.registry: AnchorRegistry = build_registry(registry_ids)

    # -- paths -----------------------------------------------------------------
    def _dir(self, name: str) -> str:
        return os.path.join(self.root, name)

    def ensure_layout(self) -> None:
        for name in _LIBRARY_SUBDIRS:
            os.makedirs(self._dir(name), exist_ok=True)

    def _confined(self, path: str) -> str:
        """Refuse any path escaping the library root (SIB-ING-001)."""
        resolved = os.path.abspath(path)
        if not (resolved == self.root or resolved.startswith(self.root + os.sep)):
            raise PermissionError(
                f"SIB-ING-001: path {resolved!r} escapes the research-library "
                f"root {self.root!r}; the research library cannot mutate "
                "canonical truth")
        return resolved

    # -- source manifest ----------------------------------------------------------
    def source_manifest_ids(self) -> Optional[List[str]]:
        """Identifiers declared by the operator's source_manifest.yaml.

        Expected shape: ``sources: [<id>, ...]`` or a mapping with ``id:``
        fields. Returns None when no source manifest is provided
        (provenance cross-check then degrades to shape checks).
        """
        path = self._dir("source_manifest.yaml")
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = load_yaml(fh.read()) or {}
        except Exception:
            return []
        ids: List[str] = []
        for entry in data.get("sources") or []:
            if isinstance(entry, str):
                ids.append(entry)
            elif isinstance(entry, dict) and entry.get("id"):
                ids.append(str(entry["id"]))
        return ids

    # -- QA (pure evidence + deterministic report file) ---------------------------
    def qa_artifact(self, filename: str, text: str,
                    known_artifact_ids: Optional[List[str]] = None
                    ) -> IngestResult:
        """Validate one artifact and write its deterministic QA report.

        The QA step NEVER changes the artifact's status. A GENERATED
        artifact that passes stays GENERATED until an explicit staging
        action transitions it via the lifecycle.
        """
        meta = parse_front_matter(text).metadata
        aid = str(meta.get("artifact_id") or "") or _aid_from(filename)
        rep = validate_artifact(
            text, filename=filename,
            known_artifact_ids=known_artifact_ids,
            registry=self.registry,
            source_manifest_ids=self.source_manifest_ids(),
        )
        qa = {
            "artifact_id": aid,
            "filename": filename,
            "sib_protocol": "SIB-1.0",
            "qa_passed": rep.qa_passed,
            "content_sha256": content_fingerprint(text),
            "report": rep.to_dict(),
        }
        self.ensure_layout()
        out = self._confined(os.path.join(self._dir("qa-reports"),
                                          f"{aid}.qa.json"))
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(rep_to_json(qa))
        return IngestResult(aid, "qa", rep.qa_passed, rep, out)

    # -- staging --------------------------------------------------------------------
    def stage_artifact(self, filename: str, *, apply_status: bool = True
                       ) -> IngestResult:
        """Move a QA-passed artifact from artifacts/ to staged/ (GENERATED ->
        QA_PASSED -> STAGED), updating the artifact's front-matter status.

        Preconditions (all machine-checked, SIB-ING-002 otherwise):
          * QA report exists, passes, and is bound to the EXACT current
            landing content (``content_sha256`` match) -- QA-then-edit is
            detected and refused;
          * the QA report is keyed by the artifact's front-matter
            ``artifact_id`` (not by filename segment);
          * artifact front-matter status is GENERATED or QA_PASSED (both
            legal lifecycle predecessors of STAGED); re-staging an already
            STAGED artifact is idempotent;
          * applicability is not NOT_APPLICABLE (NOT_APPLICABLE artifacts
            are inventory; they never advance through the pipeline).
        """
        src = self._confined(os.path.join(self._dir("artifacts"), filename))
        if not os.path.isfile(src):
            rep = ValidationReport(subject_unit=filename)
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    f"artifact not found in landing zone: artifacts/{filename}")
            return IngestResult(_aid_from(filename), "stage", False, rep)
        text = open(src, "r", encoding="utf-8").read()
        meta = parse_front_matter(text).metadata
        aid = str(meta.get("artifact_id") or "") or _aid_from(filename)
        rep = ValidationReport(subject_unit=aid)

        qa_path = self._confined(os.path.join(self._dir("qa-reports"),
                                              f"{aid}.qa.json"))
        if not os.path.isfile(qa_path):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "no QA report; run the qa action before staging")
            return IngestResult(aid, "stage", False, rep)
        with open(qa_path, "r", encoding="utf-8") as fh:
            qa = json.load(fh)
        if not qa.get("qa_passed"):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "QA report does not pass; staging refused (errors are "
                    "never downgraded to allow ingestion)")
            return IngestResult(aid, "stage", False, rep)
        recorded = str(qa.get("content_sha256") or "")
        if recorded and recorded != content_fingerprint(text):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "QA report content_sha256 does not match the current "
                    "landing content; the artifact changed after QA -- "
                    "re-run the qa action (evidence is content-bound)")
            return IngestResult(aid, "stage", False, rep)

        status = str(meta.get("status") or "")
        applicability = str(meta.get("applicability") or "")
        if applicability == "NOT_APPLICABLE":
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "NOT_APPLICABLE artifacts never advance to "
                    "QA_PASSED/STAGED/PUBLISHED; they are inventory, not "
                    "pipeline candidates")
            return IngestResult(aid, "stage", False, rep)
        if status == lifecycle.STATUS_GENERATED and apply_status:
            # GENERATED -> QA_PASSED -> STAGED (two legal transitions)
            text = _set_status(text, lifecycle.STATUS_STAGED,
                               via=lifecycle.STATUS_QA_PASSED)
        elif status == lifecycle.STATUS_QA_PASSED and apply_status:
            # QA_PASSED -> STAGED (single legal transition)
            text = _set_status(text, lifecycle.STATUS_STAGED)
        elif status != lifecycle.STATUS_STAGED:
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    f"artifact status {status!r} cannot be staged (lifecycle "
                    "GENERATED -> QA_PASSED -> STAGED)")
            return IngestResult(aid, "stage", False, rep)

        dst = self._confined(os.path.join(self._dir("staged"), filename))
        shutil.move(src, dst)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
        return IngestResult(aid, "stage", rep.qa_passed, rep, dst)

    # -- publication -----------------------------------------------------------------
    def publish_artifact(self, filename: str, *, apply_status: bool = True
                         ) -> IngestResult:
        """STAGED -> PUBLISHED. Writes to published/.

        Preconditions (all machine-checked, SIB-ING-002 otherwise):
          * the artifact file exists in staged/;
          * a PASSING QA report exists for the artifact (re-verified here so
            a file dropped directly into staged/ cannot bypass QA evidence);
          * front-matter status is STAGED -- checked regardless of
            ``apply_status`` (the flag controls whether the status line is
            rewritten, never whether preconditions hold).
        """
        src = self._confined(os.path.join(self._dir("staged"), filename))
        rep = ValidationReport(subject_unit=_aid_from(filename))
        if not os.path.isfile(src):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    f"artifact not staged: staged/{filename}")
            return IngestResult(_aid_from(filename), "publish", False, rep)
        text = open(src, "r", encoding="utf-8").read()
        meta = parse_front_matter(text).metadata
        status = str(meta.get("status") or "")
        aid = str(meta.get("artifact_id") or "") or _aid_from(filename)
        qa_path = self._confined(os.path.join(self._dir("qa-reports"),
                                              f"{aid}.qa.json"))
        if not os.path.isfile(qa_path):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "no QA report; publication requires QA evidence "
                    "(SIB-ING-002)")
            return IngestResult(aid, "publish", False, rep)
        with open(qa_path, "r", encoding="utf-8") as fh:
            qa = json.load(fh)
        if not qa.get("qa_passed"):
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    "QA report does not pass; publication refused "
                    "(no publication without QA evidence)")
            return IngestResult(aid, "publish", False, rep)
        if status != lifecycle.STATUS_STAGED:
            rep.add(Codes.INGEST_ORDER, SEVERITY_ERROR,
                    f"artifact status {status!r} cannot be published directly; "
                    "STAGED is required (no GENERATED/QA_PASSED shortcut)")
            return IngestResult(aid, "publish", False, rep)
        if apply_status:
            text = _set_status(text, lifecycle.STATUS_PUBLISHED)
        dst = self._confined(os.path.join(self._dir("published"), filename))
        shutil.move(src, dst)
        with open(dst, "w", encoding="utf-8") as fh:
            fh.write(text)
        return IngestResult(aid, "publish", rep.qa_passed, rep, dst)

    # -- chunking ----------------------------------------------------------------------
    def write_chunks(self, filename: str, text: str) -> str:
        """Write deterministic chunk JSONL for one artifact under chunks/.

        Chunk identity is deterministic (no timestamps/randomness); a
        re-run over identical input is byte-identical.
        """
        from .chunking import chunk_artifact
        aid = _aid_from(filename) or str(parse_front_matter(text).metadata.get("artifact_id") or "")
        out = self._confined(os.path.join(self._dir("chunks"),
                                          f"{aid}.chunks.jsonl"))
        chunks = chunk_artifact(text)
        with open(out, "w", encoding="utf-8") as fh:
            for ch in chunks:
                fh.write(json.dumps(ch.to_dict(), ensure_ascii=False,
                                    sort_keys=True) + "\n")
        return out


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _aid_from(filename: str) -> str:
    m = re.match(r".*_([A-Z]{2,3}-\d{2})_.*\.md$", filename)
    return m.group(1) if m else ""


def _set_status(text: str, new_status: str, *, via: Optional[str] = None) -> str:
    """Rewrite the front-matter ``status:`` line.

    ``via`` records the intermediate lifecycle stop in a comment line so the
    two-step transition (GENERATED -> QA_PASSED -> STAGED) is observable in
    the artifact itself. Deterministic; touches nothing else.
    """
    lines = text.split("\n")
    out: List[str] = []
    in_fm = False
    fm_closed = False
    for line in lines:
        if line.strip() == "---" and not fm_closed:
            if in_fm:
                fm_closed = True
                in_fm = False
            else:
                in_fm = True
            out.append(line)
            continue
        if in_fm and re.match(r"^status\s*:", line):
            if via:
                out.append(f"# lifecycle: {line.split(':', 1)[1].strip()} -> {via} -> {new_status}")
            out.append(f"status: {new_status}")
            continue
        out.append(line)
    return "\n".join(out)


def rep_to_json(qa: Dict[str, object]) -> str:
    return json.dumps(qa, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
