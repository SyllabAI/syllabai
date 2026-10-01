#!/usr/bin/env python3
"""SIB v1 validator / ingestion CLI.

Deterministic commands over a subject research library:

    python3 -m tools.sib.cli validate-artifact <file.md> [--library DIR]
    python3 -m tools.sib.cli validate-manifest  <library-dir>
    python3 -m tools.sib.cli qa           <library-dir> artifacts/<file.md>
    python3 -m tools.sib.cli stage        <library-dir> artifacts/<file.md>
    python3 -m tools.sib.cli publish      <library-dir> staged/<file.md>
    python3 -m tools.sib.cli chunks       <library-dir> artifacts/<file.md>
    python3 -m tools.sib.cli report       <library-dir>

Exit codes: 0 = QA passed / action ok; 1 = QA failed / error.
Output is JSON (sorted keys, no timestamps) -- byte-stable for identical input.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional

if __package__ in (None, ""):  # direct script execution support
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools.sib import taxonomy, lifecycle
from tools.sib.manifest_model import (load_manifest, manifest_counts,
                                      validate_manifest)
from tools.sib.ingest import SibLibrary


def _registry_ids(library_dir: str) -> Optional[List[str]]:
    """Optional curriculum registry at <library>/curriculum_registry.yaml."""
    path = os.path.join(library_dir, "curriculum_registry.yaml")
    if not os.path.isfile(path):
        return None
    from tools.sib.yamlmini import load_yaml
    with open(path, "r", encoding="utf-8") as fh:
        data = load_yaml(fh.read()) or {}
    ids = data.get("specification_points") or data.get("identifiers") or []
    return [str(i) for i in ids]


def _load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def cmd_validate_artifact(args: argparse.Namespace) -> int:
    from tools.sib.artifact_validator import validate_artifact
    from tools.sib.anchors import build_registry
    text = _load_text(args.artifact)
    reg = build_registry(_registry_ids(args.library) if args.library else None)
    known = None
    if args.library:
        landing = os.path.join(args.library, "artifacts")
        if os.path.isdir(landing):
            known = _known_ids(landing, exclude_filename=os.path.basename(args.artifact))
    rep = validate_artifact(text, filename=os.path.basename(args.artifact),
                            known_artifact_ids=known, registry=reg)
    print(rep.to_json())
    return 0 if rep.qa_passed else 1


def _known_ids(landing: str, exclude_filename: str = "") -> List[str]:
    from tools.sib.frontmatter import parse_front_matter
    ids = []
    for f in sorted(os.listdir(landing)):
        if f.endswith(".md") and f != exclude_filename:
            meta = parse_front_matter(_load_text(os.path.join(landing, f))).metadata
            aid = str(meta.get("artifact_id") or "")
            if aid:
                ids.append(aid)
    return ids


def cmd_validate_manifest(args: argparse.Namespace) -> int:
    manifest, err = load_manifest(args.library_dir and
                                  os.path.join(args.library_dir, "manifest.yaml") or "")
    rep = validate_manifest(manifest, err, artifacts_dir=os.path.join(args.library_dir, "artifacts"),
                            qa_report_dir=os.path.join(args.library_dir, "qa-reports"))
    payload = rep.to_dict()
    if manifest is not None:
        payload["counts"] = manifest_counts(manifest)
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if rep.qa_passed else 1


def _library_action(args: argparse.Namespace, action: str) -> int:
    lib = SibLibrary(args.library_dir, registry_ids=_registry_ids(args.library_dir))
    if action == "qa":
        text = _load_text(args.artifact)
        landing = os.path.join(args.library_dir, "artifacts")
        known = (_known_ids(landing, exclude_filename=os.path.basename(args.artifact))
                 if os.path.isdir(landing) else None)
        result = lib.qa_artifact(os.path.basename(args.artifact), text, known)
    elif action == "stage":
        result = lib.stage_artifact(os.path.basename(args.artifact))
    elif action == "publish":
        result = lib.publish_artifact(os.path.basename(args.artifact))
    elif action == "chunks":
        text = _load_text(args.artifact)
        out = lib.write_chunks(os.path.basename(args.artifact), text)
        print(json.dumps({"chunks_file": out, "artifact_id":
                          os.path.basename(args.artifact).split("_")[2] if "_" in os.path.basename(args.artifact) else ""},
                         indent=2, sort_keys=True))
        return 0
    else:  # pragma: no cover
        raise ValueError(action)
    payload = result.summary()
    payload["report"] = result.report.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if result.qa_passed else 1


def cmd_report(args: argparse.Namespace) -> int:
    manifest, err = load_manifest(os.path.join(args.library_dir, "manifest.yaml"))
    rep = validate_manifest(manifest, err,
                            artifacts_dir=os.path.join(args.library_dir, "artifacts"),
                            qa_report_dir=os.path.join(args.library_dir, "qa-reports"))
    payload = {
        "library": os.path.abspath(args.library_dir),
        "sib_protocol": taxonomy.SIB_PROTOCOL if manifest is None else manifest.sib_protocol,
        "manifest_qa_passed": rep.qa_passed,
        "manifest_issues": rep.to_dict()["issues"],
        "counts": manifest_counts(manifest) if manifest else {},
        "lifecycle": {s: list(lifecycle.TRANSITIONS[s]) for s in lifecycle.ALL_STATUSES},
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if rep.qa_passed else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="sib", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("validate-artifact", help="validate one artifact file")
    p.add_argument("artifact")
    p.add_argument("--library", default="", help="library dir for optional registry/duplicates")
    p.set_defaults(fn=cmd_validate_artifact)

    p = sub.add_parser("validate-manifest", help="validate library manifest")
    p.add_argument("library_dir")
    p.set_defaults(fn=cmd_validate_manifest)

    for action in ("qa", "stage", "publish", "chunks"):
        p = sub.add_parser(action, help=f"{action} an artifact")
        p.add_argument("library_dir")
        p.add_argument("artifact")
        p.set_defaults(fn=lambda a, _ac=action: _library_action(a, _ac))

    p = sub.add_parser("report", help="library completion metrics")
    p.add_argument("library_dir")
    p.set_defaults(fn=cmd_report)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
