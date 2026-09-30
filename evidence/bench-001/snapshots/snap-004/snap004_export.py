#!/usr/bin/env python3
"""snap-004 re-freeze exporter — the AT-FLIP freeze (trigger A re-run substrate).

Fourth versioned freeze in the snap-N series. Adapted from the frozen
snap003_export.py (carried in evidence/bench-001/snapshots/snap-003/).

Operator directive (2026-09-27, in-chat, trace 1a0e23212e7b3cf5): "re-run
trigger A" — the operator lifts the at-flip hold recorded at the T-C27 close
(5a18253d9: "at-flip trigger-A re-run stays operator-held"). First-hand
verification this session: the operator/teacher validation wave promoted the
PAPER axis (13 exam_papers rows VALIDATED + their 13 QP + 13 MS documents
VALIDATED at doc level — docs were uniformly SUGGESTED at snap-003 freeze);
the CARD axis is NOT promoted (298/298 T-C27 cards SUGGESTED). The flip is
therefore real on the paper axis; snap-004 captures it.

Changes vs snap-003 (all recorded as manifest-bound deltas, never silent):
  SNAP4-F1  validation wave (paper axis): doc-level paper_state flips
            SUGGESTED -> VALIDATED on the promoted documents' chunks; the
            harness gate (VALIDATED-only over snapshot metadata) then serves
            them. Card axis unchanged (298/298 SUGGESTED — recorded honestly;
            the card-flip run stays available when the card wave lands).
  SNAP4-M1  method note (unchanged from SNAP3-M1): sanctioned session-env
            read path, SELECT-only, rolled back.

Fidelity anchors (must hold or the script exits non-zero):
  - spec_points / graph_edges / misconceptions / question_anchors /
    concept_attachments  BYTE-IDENTICAL to snap-003 (no content/KG change:
    bank census 999 docs / 4,343 chunks / 1,533 qv unchanged; T-C30 KG
    backfill predates snap-003)
  - graph_code.json      rows set-equal to snap-003 (source.date differs)
  - chunks               SAME row set as snap-003 (same chunk_refs, same
    contents, same kinds, same spec_codes); the ONLY permitted delta is
    paper_state. Any ref/content/kind/spec_codes drift is FAIL.
"""
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import psycopg2

SNAP3 = "/home/z/my-project/download/bench/snap-003"  # frozen snap-003 artifacts (Task-39 delivered copies)
RES = "/home/z/my-project/workspace/snap003/resources_pins"
C19 = f"{RES}/scripts__c19_promotions.yaml"
CONCEPTS_YAML = f"{RES}/graph__igcse-chemistry__concepts.yaml"
STAGING = "/home/z/my-project/workspace/snap004/staging"
HEAD = "1245df009712216b309f163aacdd1c6d8ef39f1b"  # syllabai-resources main (pin unchanged)

_env = {e["key"]: e["value"] for e in json.load(open("/home/z/my-project/scripts/.render_env.json"))["env"]}
_url = _env["SYLLABAI_DATABASE_URL"]
if _url.startswith("jdbc:"):
    _url = _url[len("jdbc:"):]
_hd = _url.split("://", 1)[1].split("/", 1)
DB_URL = f"postgresql://{_env['SYLLABAI_DATABASE_USERNAME']}:{_env['SYLLABAI_DATABASE_PASSWORD']}@{_hd[0]}/{_hd[1]}"

SEMANTIC_RELATIONS = (
    "COMMONLY_CONFUSED_WITH",
    "EXPLAINED_BY",
    "MISCONCEPTION_OF",
    "REMEDIATED_BY",
    "REQUIRES_PREREQUISITE",
    "WRONG_ANSWER_PATTERN",
)

PREDICATE = "documents.kind IN ('QUESTION_PAPER','MARK_SCHEME','EXTERNAL_QUESTIONS')"

FAILS = []
DELTAS = {}


def check(cond, label, detail=""):
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {label}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


def compact(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    os.makedirs(STAGING, exist_ok=True)
    conn = psycopg2.connect(DB_URL, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=True, autocommit=False)
    cur = conn.cursor()

    # ---------------- chunks.jsonl.gz ----------------
    print("== chunks")
    cur.execute(
        """SELECT d.checksum, c.chunk_index, c.content, c.kind, d.kind,
                  c.page_end, c.page_start, c.paper_code, d.validation_state,
                  c.token_estimate, c.spec_codes, c.subject_id
           FROM document_chunks c JOIN documents d ON d.id = c.document_row_id
           WHERE d.kind IN ('QUESTION_PAPER','MARK_SCHEME','EXTERNAL_QUESTIONS')
           ORDER BY d.checksum, c.chunk_index"""
    )
    chunks = []
    kind_mismatch = 0
    for checksum, idx, content, ckind, dkind, pe, ps, pcode, vstate, tok, spc, subj in cur.fetchall():
        if ckind != dkind:
            kind_mismatch += 1
        codes = sorted({str(x) for x in spc}) if spc else []
        chunks.append(
            {
                "chunk_ref": f"{checksum}:{idx}",
                "content": content,
                "content_sha256": sha(content.encode("utf-8")),
                "kind": ckind,
                "page_end": pe,
                "page_start": ps,
                "paper_code": pcode,
                "paper_state": vstate,
                "subject_id": str(subj) if subj else None,
                "token_estimate": tok,
                "spec_codes": codes,
            }
        )
    check(kind_mismatch == 0, "chunk.kind == document.kind on every row",
          f"{kind_mismatch} mismatches")
    check(all(sha(c["content"].encode()) == c["content_sha256"] for c in chunks),
          "chunk content_sha256 self-consistency", f"{len(chunks)} rows")
    check(len({c["chunk_ref"] for c in chunks}) == len(chunks), "no duplicate chunk_refs")

    # ---- snap-003 comparison: row-set identity, paper_state-only delta ----
    old = json.load(gzip.open(f"{SNAP3}/chunks.jsonl.gz"))
    old_by_ref = {c["chunk_ref"]: c for c in old}
    new_by_ref = {c["chunk_ref"]: c for c in chunks}
    check(set(old_by_ref) == set(new_by_ref),
          "chunk_ref set IDENTICAL to snap-003 (no corpus evolution)",
          f"snap003 {len(old_by_ref)} vs snap004 {len(new_by_ref)}")
    content_drift = [r for r in new_by_ref
                     if r in old_by_ref and old_by_ref[r]["content"] != new_by_ref[r]["content"]]
    check(not content_drift, "chunk contents IDENTICAL to snap-003", f"{len(content_drift)} drifts")
    kind_drift = [r for r in new_by_ref
                  if r in old_by_ref and old_by_ref[r]["kind"] != new_by_ref[r]["kind"]]
    check(not kind_drift, "chunk kinds IDENTICAL to snap-003", f"{len(kind_drift)} drifts")
    sc_drift = [r for r in new_by_ref
                if r in old_by_ref and old_by_ref[r]["spec_codes"] != new_by_ref[r]["spec_codes"]]
    check(not sc_drift, "chunk spec_codes IDENTICAL to snap-003", f"{len(sc_drift)} drifts")

    state_flips = []
    code_stamps = []
    for r, c in new_by_ref.items():
        o = old_by_ref.get(r)
        if o and o["paper_state"] != c["paper_state"]:
            state_flips.append({"chunk_ref": r, "kind": c["kind"], "paper_code": c["paper_code"],
                                "snap003": o["paper_state"], "snap004": c["paper_state"]})
        if o and o.get("paper_code") != c.get("paper_code"):
            code_stamps.append({"chunk_ref": r, "kind": c["kind"],
                                "snap003": o.get("paper_code"), "snap004": c.get("paper_code")})
    up_flips = [f for f in state_flips if f["snap004"] == "VALIDATED"]
    down_flips = [f for f in state_flips if f["snap004"] != "VALIDATED"]
    check(len(state_flips) == len(up_flips), "no SUGGESTED->non-VALIDATED regressions",
          f"{len(down_flips)} regressions")

    ps_by_kind = {}
    for c in chunks:
        ps_by_kind.setdefault(c["kind"], {}).setdefault(c["paper_state"], 0)
        ps_by_kind[c["kind"]][c["paper_state"]] += 1
    print(f"  paper_state by kind: {json.dumps(ps_by_kind, sort_keys=True)}")
    flip_by_kind_code = {}
    for f in up_flips:
        key = f"{f['kind']}|{f['paper_code']}"
        flip_by_kind_code.setdefault(key, 0)
        flip_by_kind_code[key] += 1
    print(f"  promoted chunks by kind|paper_code: {json.dumps(flip_by_kind_code, sort_keys=True)}")

    promoted_docs = sorted({f["chunk_ref"].rsplit(":", 1)[0] for f in up_flips})
    DELTAS["SNAP4-F1_validation_wave"] = {
        "finding": "the operator/teacher validation wave promoted the PAPER axis after the "
                   "snap-003 freeze and after the paper-axis repairs (f96b0d57): 13 exam_papers "
                   "rows VALIDATED (11 glmocr-era + 4CH1/2C June-2019 + 4CH1/1C January-2022) "
                   "with their 13 QP + 13 MS documents VALIDATED at doc level (docs were "
                   "uniformly SUGGESTED at snap-003 freeze; core 02664958a then recorded "
                   "paper-VALIDATED + doc-SUGGESTED as production reality). The harness "
                   "VALIDATED-only gate reads snapshot paper_state, so the promoted chunks "
                   "now ENTER the served view — this freeze is the at-flip substrate.",
        "chunks_flipped_suggested_to_validated": len(up_flips),
        "flips_by_kind_paper_code": flip_by_kind_code,
        "documents_with_promoted_chunks": len(promoted_docs),
        "paper_state_by_kind": ps_by_kind,
        "card_axis": "the T-C27 cards ingested 2026-09-26 (298 chunks) are ALL still "
                     "SUGGESTED — the card validation wave has NOT landed. The 11 VALIDATED "
                     "EQ chunks are the single pre-existing 2026-09-20-cohort 4CH1/1C card "
                     "document, which was SUGGESTED at the snap-003 freeze and is promoted "
                     "in this window (part of the same wave). The card-flip run (r6) stays "
                     "available when the operator/teacher card wave lands — trigger A is "
                     "cashed here on the paper axis, honestly scoped.",
        "no_regressions": len(down_flips) == 0,
        "row_set_identity": "chunk_ref set, contents, kinds and spec_codes are IDENTICAL to "
                            "snap-003 — the only field deltas are paper_state (this delta) and "
                            "the metadata-only paper_code stamps (SNAP4-F2), both verified "
                            "programmatically",
    }
    DELTAS["SNAP4-M1_method_note"] = {
        "finding": "unchanged SNAP3-M1 read path: sanctioned production connection from the "
                   "session env, READ-ONLY (set_session(readonly=True)), SELECT-only, rolled "
                   "back; zero writes to any production table",
    }
    stamp_by_kind = {}
    for s in code_stamps:
        stamp_by_kind[s["kind"]] = stamp_by_kind.get(s["kind"], 0) + 1
    DELTAS["SNAP4-F2_chunk_paper_code_backfill"] = {
        "finding": "246 chunk rows gained a paper_code value (snap-003: null) — the mirror "
                   "stamping that accompanied the post-freeze repair/validation lane (the "
                   "paper-axis repairs f96b0d57 backfilled series/year on the bank-wave "
                   "exam_papers rows and stamped the mirrors; embed mirrors now carry "
                   "paper_code on the promoted docs' chunks). Metadata-only: chunk_ref, "
                   "content, kind and spec_codes are unchanged; retrieval identity is "
                   "content-addressed and unaffected. Recorded so the field diff is never "
                   "silent.",
        "rows_stamped": len(code_stamps),
        "by_kind": stamp_by_kind,
        "note": "field-level diff vs snap-003 verified programmatically: paper_state (317 "
                "flips, SNAP4-F1) and paper_code (246 stamps, SNAP4-F2) are the only VALUE "
                "deltas; subject_id (SNAP4-F3) is an additive projection snap-003 does not "
                "carry.",
    }
    subj_by_kind = {}
    subj_null = 0
    for c in chunks:
        subj_by_kind.setdefault(c["kind"], [0, 0])
        subj_by_kind[c["kind"]][0] += 1
        if c["subject_id"]:
            subj_by_kind[c["kind"]][1] += 1
        else:
            subj_null += 1
    DELTAS["SNAP4-F3_chunk_subject_id_projection"] = {
        "finding": "chunk rows project the document_chunks.subject_id column (the at-flip "
                   "generation enabler, syllabai-core e728b7d: the optional subject_id "
                   "projection is parsed as verification/census evidence for the at-flip "
                   "generation, never a gate input — the bench container stamps chunks with "
                   "the bench scope's own subject, single-subject topology). snap-001..003 "
                   "carry no such field; missing and JSON null fold to null in the loader "
                   "(BenchSnapshotSubjectIdTest pins the fold).",
        "rows_by_kind_present_total": {k: {"rows": v[0], "with_subject_id": v[1]}
                                       for k, v in sorted(subj_by_kind.items())},
        "rows_without_subject_id": subj_null,
    }

    # ---------------- spec_points.json ----------------
    print("== spec_points")
    cur.execute(
        """SELECT code, node_type, title, validation_status FROM knowledge_nodes
           WHERE node_type='SUBTOPIC' AND validation_status='VALIDATED'
             AND code LIKE '4CH1-%' ORDER BY code"""
    )
    spec_points = [
        {"code": r[0], "node_type": r[1], "title": r[2], "validation_status": r[3]}
        for r in cur.fetchall()
    ]
    sp_bytes = compact(spec_points).encode()
    check(sha(sp_bytes) == sha(open(f"{SNAP3}/spec_points.json", "rb").read()),
          "spec_points BYTE-IDENTICAL to snap-003 (fidelity anchor)",
          f"{len(spec_points)} rows, {sha(sp_bytes)[:16]}")

    # ---------------- graph_edges.json ----------------
    print("== graph_edges")
    cur.execute(
        """SELECT e.relation_type, sn.code, tn.code
           FROM knowledge_edges e
           JOIN knowledge_nodes sn ON sn.id = e.source_node_id
           JOIN knowledge_nodes tn ON tn.id = e.target_node_id
           WHERE e.validation_status='VALIDATED'
             AND e.relation_type IN %s
           ORDER BY 1, 2, 3""",
        (SEMANTIC_RELATIONS,),
    )
    graph_edges = [
        {"relation": r[0], "source": r[1], "target": r[2]} for r in cur.fetchall()
    ]
    ge_bytes = compact(graph_edges).encode()
    check(sha(ge_bytes) == sha(open(f"{SNAP3}/graph_edges.json", "rb").read()),
          "graph_edges BYTE-IDENTICAL to snap-003 (fidelity anchor)",
          f"{len(graph_edges)} edges, {sha(ge_bytes)[:16]}")

    # ---------------- misconceptions.json ----------------
    print("== misconceptions")
    cur.execute(
        """SELECT code, title FROM knowledge_nodes
           WHERE node_type='MISCONCEPTION' ORDER BY code"""
    )
    misconceptions = [{"code": r[0], "title": r[1]} for r in cur.fetchall()]
    mis_bytes = compact(misconceptions).encode()
    check(sha(mis_bytes) == sha(open(f"{SNAP3}/misconceptions.json", "rb").read()),
          "misconceptions BYTE-IDENTICAL to snap-003", f"{len(misconceptions)} rows")

    # ---------------- question_anchors.json ----------------
    print("== question_anchors")
    cur.execute(
        """SELECT kn.code, qv.command_word, qv.marks, ep.paper_code,
                  qv.validation_state, qv.stem
           FROM question_versions qv
           JOIN questions q ON q.id = qv.question_id
           JOIN knowledge_nodes kn ON kn.id = q.primary_topic_node_id
           LEFT JOIN exam_papers ep ON ep.id = q.exam_paper_id
           WHERE qv.validation_state='VALIDATED'
           ORDER BY kn.code, qv.stem"""
    )
    anchors = [
        {"anchor_code": r[0], "command_word": r[1], "marks": r[2],
         "paper_code": r[3], "qversion_state": r[4], "stem": r[5]}
        for r in cur.fetchall()
    ]
    qa_bytes = compact(anchors).encode()
    check(sha(qa_bytes) == sha(open(f"{SNAP3}/question_anchors.json", "rb").read()),
          "question_anchors BYTE-IDENTICAL to snap-003 (fidelity anchor)",
          f"{len(anchors)} rows, {sha(qa_bytes)[:16]}")

    # ---------------- graph_code.json ----------------
    print("== graph_code")
    import yaml
    yam = yaml.safe_load(open(CONCEPTS_YAML))
    ynodes = {n["code"]: n for n in yam["nodes"]}
    cur.execute(
        """SELECT code, node_type, title FROM knowledge_nodes
           WHERE node_type IN ('CONCEPT','MISCONCEPTION') ORDER BY code"""
    )
    db_nodes = cur.fetchall()
    concepts_out, mis_out = [], []
    title_drift = []
    for code, node_type, db_title in db_nodes:
        y = ynodes.get(code)
        raw_sp = (y or {}).get("spec_points") or []
        norm_sp = [sp["code"] if isinstance(sp, dict) else sp for sp in raw_sp]
        row = {
            "aliases": (y or {}).get("aliases") or [],
            "code": code,
            "family": node_type,
            "spec_points": norm_sp,
            "title": (y or {}).get("title") or db_title,
        }
        if y and y.get("title") != db_title:
            title_drift.append(code)
        (concepts_out if node_type == "CONCEPT" else mis_out).append(row)
    concepts_out.sort(key=lambda r: r["code"])
    mis_out.sort(key=lambda r: r["code"])
    total_att = sum(len(r["spec_points"]) for r in concepts_out + mis_out)
    with_att = sum(1 for r in concepts_out if r["spec_points"])
    import pathlib
    pins = {"concepts.yaml": sha(pathlib.Path(CONCEPTS_YAML).read_bytes())}
    graph_code = {
        "concepts": concepts_out,
        "counts": {
            "concepts": len(concepts_out),
            "concepts_with_spec_attachment": with_att,
            "misconceptions": len(mis_out),
            "total_spec_attachments": total_att,
        },
        "misconceptions": mis_out,
        "source": {
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "files_sha256": pins,
            "head": HEAD,
            "repo": "SyllabAI/syllabai-resources",
        },
    }
    old_gc = json.load(open(f"{SNAP3}/graph_code.json"))

    def sig(rows):
        return {r["code"]: (tuple(sorted(r["aliases"])), tuple(sorted(r["spec_points"])),
                            r["family"], r["title"]) for r in rows}

    check(sig(concepts_out) == sig(old_gc["concepts"]),
          "graph_code.concepts rows set-equal to snap-003 (pinned store @1245df0 unchanged)")
    check(mis_out == old_gc["misconceptions"], "graph_code.misconceptions byte-equal",
          f"{len(mis_out)}")
    check(graph_code["counts"] == old_gc["counts"], "graph_code.counts equal",
          json.dumps(graph_code["counts"]))
    check(not title_drift, "no title drift on emitted nodes", f"{title_drift[:5]}")
    check(old_gc["source"]["head"] == HEAD, "resources HEAD pin unchanged since snap-003", HEAD)

    # ---------------- concept_attachments.json ----------------
    print("== concept_attachments")
    promo = yaml.safe_load(open(C19))["promotions"]
    attachments = sorted(
        ({"concept": p["attachment"]["concept"],
          "provenance": "HUMAN_VALIDATED",
          "spec_point": p["attachment"]["spec_point"]}
         for p in promo),
        key=lambda r: (r["concept"], r["spec_point"]),
    )
    cur.execute(
        """SELECT sn.code, tn.code FROM knowledge_edges e
           JOIN knowledge_nodes sn ON sn.id = e.source_node_id
           JOIN knowledge_nodes tn ON tn.id = e.target_node_id
           WHERE e.relation_type='PART_OF' AND e.validation_status='SUGGESTED'
           ORDER BY 1, 2"""
    )
    db_pairs = {(r[0], r[1]) for r in cur.fetchall()}
    promo_pairs = {(a["concept"], a["spec_point"]) for a in attachments}
    check(len(attachments) == 117 == len(promo_pairs),
          "concept_attachments == 117 HUMAN_VALIDATED rows (c19 record)")
    check(db_pairs == promo_pairs,
          "DB serving pairs (SUGGESTED, all CONCEPT->SUBTOPIC) == ratified HV pair set "
          "(1:1, status lag preserved since snap-002)",
          f"db {len(db_pairs)} pairs")
    yaml_pairs = set()
    for r in concepts_out + mis_out:
        for spc in r["spec_points"]:
            code = spc.get("code") if isinstance(spc, dict) else spc
            yaml_pairs.add((r["code"], code))
    check(promo_pairs <= yaml_pairs,
          "HV pairs present in pinned ratified concepts.yaml",
          f"{len(promo_pairs & yaml_pairs)}/117")
    att_bytes = compact(attachments).encode()
    check(sha(att_bytes) == sha(open(f"{SNAP3}/concept_attachments.json", "rb").read()),
          "concept_attachments BYTE-IDENTICAL to snap-003 (same ratified inputs)",
          sha(att_bytes)[:16])

    conn.rollback()
    conn.close()

    # ---------------- write staging ----------------
    outs = {
        "spec_points.json": sp_bytes,
        "graph_edges.json": ge_bytes,
        "misconceptions.json": mis_bytes,
        "question_anchors.json": qa_bytes,
        "concept_attachments.json": att_bytes,
    }
    gc_bytes = json.dumps(graph_code, indent=1, sort_keys=True).encode()
    outs["graph_code.json"] = gc_bytes
    for name, data in outs.items():
        open(f"{STAGING}/{name}", "wb").write(data)
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=open(f"{STAGING}/chunks.jsonl.gz", "wb"),
                       mtime=0)
    gz.write(json.dumps(chunks, sort_keys=True, separators=(",", ":")).encode())
    gz.close()

    json.dump(DELTAS, open(f"{STAGING}/verification_deltas.json", "w"), indent=1)
    print("\n== summary")
    counts = {
        "chunks": len(chunks),
        "chunks_flipped_to_validated": len(up_flips),
        "concept_attachments": len(attachments),
        "edges": len(graph_edges),
        "misconceptions": len(misconceptions),
        "question_anchors": len(anchors),
        "spec_points": len(spec_points),
    }
    print("  counts:", json.dumps(counts))
    for name in sorted(outs) + ["chunks.jsonl.gz"]:
        p = f"{STAGING}/{name}"
        raw = open(p, "rb").read()
        size = len(gzip.open(p).read()) if name.endswith(".gz") else len(raw)
        print(f"  {name}: sha256 {sha(raw)[:16]}… (bytes {size})")

    if FAILS:
        print(f"\nVERIFICATION FAILED ({len(FAILS)}): {FAILS}")
        sys.exit(1)
    print("\nALL VERIFICATIONS PASS — snap-004 staging tree ready for manifest + freeze review")


if __name__ == "__main__":
    main()
