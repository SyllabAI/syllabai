#!/usr/bin/env python3
"""snap-003 re-freeze exporter — T-C13 corpus snapshot discipline (spec §4).

Third versioned freeze in the snap-N series. Adapted from the frozen
snap-002 exporter (evidence/bench-001/snapshots/snap-002/snap002_export.py),
which reconstructed the snap-001 predicates from first principles.

Operator directive (2026-09-26, in-chat): "Proceed with retrieval bench
(snap-003 re-freeze + gold-v2)" — lifts the operator hold recorded in the
T-C27 blocked list ("recorded T-C13 bench (snap-003 re-freeze + gold-v2) —
operator-held per the snap-002 FREEZE_RECORD").

Changes vs snap-002 (all recorded as manifest-bound deltas, never silent):
  SNAP3-F1  predicate extension: documents.kind adds 'EXTERNAL_QUESTIONS'
            (the T-C27 question cards, 298 new 2026-09-26 + 81 pre-existing
            2026-09-20; all SUGGESTED / serving-inert at freeze time). The
            extension is what makes the snap-003 pair usable for the
            serving-flip recorded run the T-C27 debt names.
            EXTERNAL_NOTES + SYLLABUS stay EXCLUDED (T-C06/C13 lane
            governance; counts recorded).
  SNAP3-F2  corpus evolution vs snap-002 (rw-9b v2 re-ingest, bank wave,
            T-C23 repair, card ingest) — survival arithmetic recorded.
  SNAP3-F3  chunk rows gain `spec_codes` (V33 GIN column, jsonb projected to
            a sorted unique list of code strings). Loader-safe: the harness
            reads known fields via path accessors and ignores unknown ones.

Method delta (recorded): read path is the sanctioned production connection
from the session env (the same read path the ops lanes' state probes use)
opened READ-ONLY (set_session(readonly=True), SELECT-only, rolled back);
snap-002's isolated-branch method required the Neon management credential,
which is not present in this session. Zero writes to any production table.

Fidelity anchors (must hold or the script exits non-zero):
  - graph_edges.json        byte-identical to snap-002 (== snap-001 chain)
  - misconceptions.json     byte-identical to snap-002 (== snap-001 chain)
  - spec_points.json        byte-identical to snap-002 expected; any drift
                            is FAIL unless recorded as a named delta
  - concept_attachments     1:1 with c19_promotions.yaml AND with the DB
                            SUGGESTED PART_OF pair set (CONCEPT->SUBTOPIC)
  - graph_code.json         rows set-equal to snap-002 (source.date differs
                            by construction)
  - chunk kind==doc kind    per-row consistency check (chunk.kind column vs
                            parent document.kind)
"""
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

import psycopg2

SNAP2 = "/home/z/my-project/workspace/snap003/snap002_reference"
RES = "/home/z/my-project/workspace/snap003/resources_pins"
C19 = f"{RES}/scripts__c19_promotions.yaml"
CONCEPTS_YAML = f"{RES}/graph__igcse-chemistry__concepts.yaml"
STAGING = "/home/z/my-project/workspace/snap003/staging"
HEAD = "1245df009712216b309f163aacdd1c6d8ef39f1b"  # syllabai-resources main (unchanged since snap-002's pin)

# --- production read-only connection (method delta SNAP3-M1, recorded) ---
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
                  c.token_estimate, c.spec_codes
           FROM document_chunks c JOIN documents d ON d.id = c.document_row_id
           WHERE d.kind IN ('QUESTION_PAPER','MARK_SCHEME','EXTERNAL_QUESTIONS')
           ORDER BY d.checksum, c.chunk_index"""
    )
    chunks = []
    kind_mismatch = 0
    for checksum, idx, content, ckind, dkind, pe, ps, pcode, vstate, tok, spc in cur.fetchall():
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
                "token_estimate": tok,
                "spec_codes": codes,
            }
        )
    check(kind_mismatch == 0, "chunk.kind == document.kind on every row",
          f"{kind_mismatch} mismatches")
    check(all(sha(c["content"].encode()) == c["content_sha256"] for c in chunks),
          "chunk content_sha256 self-consistency", f"{len(chunks)} rows")
    check(len({c["chunk_ref"] for c in chunks}) == len(chunks), "no duplicate chunk_refs")

    old = json.load(gzip.open(f"{SNAP2}/chunks.jsonl.gz"))
    old_refs = {c["chunk_ref"] for c in old}
    new_refs = {c["chunk_ref"] for c in chunks}
    old_md5 = {hashlib.md5(c["content"].encode()).hexdigest() for c in old}
    new_md5 = {hashlib.md5(c["content"].encode()).hexdigest() for c in chunks}
    # apples-to-apples: QP/MS-only survival against the snap-002 universe
    old_qpms_refs = {c["chunk_ref"] for c in old}
    cur_qpms_refs = {c["chunk_ref"] for c in chunks if c["kind"] in ("QUESTION_PAPER", "MARK_SCHEME")}
    surv_refs = len(old_qpms_refs & cur_qpms_refs)
    surv_content = len(old_md5 & {hashlib.md5(c["content"].encode()).hexdigest()
                                  for c in chunks if c["kind"] in ("QUESTION_PAPER", "MARK_SCHEME")})
    old_kinds = {}
    for c in old:
        old_kinds[c["kind"]] = old_kinds.get(c["kind"], 0) + 1
    new_kinds = {}
    for c in chunks:
        new_kinds[c["kind"]] = new_kinds.get(c["kind"], 0) + 1
    old_docs = len({c["chunk_ref"].rsplit(":", 1)[0] for c in old})
    new_docs = len({c["chunk_ref"].rsplit(":", 1)[0] for c in chunks})
    DELTAS["SNAP3-F1_predicate_extension"] = {
        "finding": "predicate extended with documents.kind='EXTERNAL_QUESTIONS' "
                   "(T-C27 question cards: 298 ingested 2026-09-26 + 81 pre-existing "
                   "2026-09-20; all SUGGESTED, serving-inert at freeze time — the "
                   "extension is what makes this pair usable for the serving-flip "
                   "recorded run named by the T-C27 debt)",
        "predicate_t0_and_snap002": "documents.kind IN ('QUESTION_PAPER','MARK_SCHEME')",
        "predicate_snap003": PREDICATE,
        "excluded_kinds": {"EXTERNAL_NOTES": "350 chunks (T-C06/C13 lane governance)",
                           "SYLLABUS": "162 chunks (reference substrate, out of arm scope)"},
        "chunk_rows_by_kind": {"snap002": old_kinds, "snap003": new_kinds},
        "documents_with_chunks": {"snap002": old_docs, "snap003": new_docs},
        "note": "paper_state (documents.validation_state) is uniformly SUGGESTED in "
                "snap-002 AND snap-003 — doc-level state; paper-level VALIDATED lives "
                "on exam_papers (11) and question_versions axes, unchanged discipline",
    }
    DELTAS["SNAP3-F2_corpus_evolution"] = {
        "finding": "QP/MS corpus re-ingested again between snap-002 (2026-09-25) and "
                   "snap-003 (rw-9b v2 supersession of the 13 clear pairs, bank-wave "
                   "repoint, T-C23 guarded repair); card axis is purely additive",
        "qpms_chunks": {"snap002": len(old), "snap003": len(cur_qpms_refs)},
        "total_chunks": {"snap002": len(old), "snap003": len(chunks)},
        "chunk_refs_surviving_qpms_to_qpms": surv_refs,
        "unique_contents_surviving_qpms_to_qpms": surv_content,
        "t0_unique_contents_snap002": len(old_md5),
        "consequence": "gold-v1 AND gold-v2 stay SHA-paired to their own snapshots; "
                       "snap-002 keeps gold-v1-freeze semantics (its anchors never "
                       "resolved post-SNAP2-F1); snap-003 pairs with gold-v2 (built "
                       "in the same freeze)",
    }
    DELTAS["SNAP3-F3_chunk_spec_codes_field"] = {
        "finding": "chunk rows carry the V33 spec_codes GIN column (T-C27 deterministic "
                   "join), projected jsonb -> sorted unique code strings",
        "rows_with_codes_by_kind": {},
    }
    sc_by_kind = {}
    for c in chunks:
        k = c["kind"]
        sc_by_kind.setdefault(k, [0, 0])
        sc_by_kind[k][0] += 1
        if c["spec_codes"]:
            sc_by_kind[k][1] += 1
    DELTAS["SNAP3-F3_chunk_spec_codes_field"]["rows_with_codes_by_kind"] = {
        k: {"rows": v[0], "with_codes": v[1]} for k, v in sorted(sc_by_kind.items())}
    print(f"  kinds: {new_kinds} | docs: {new_docs}")

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
    old_sp_sha = sha(open(f"{SNAP2}/spec_points.json", "rb").read())
    check(sha(sp_bytes) == old_sp_sha,
          "spec_points BYTE-IDENTICAL to snap-002 (fidelity anchor)",
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
    old_ge_sha = sha(open(f"{SNAP2}/graph_edges.json", "rb").read())
    check(sha(ge_bytes) == old_ge_sha,
          "graph_edges BYTE-IDENTICAL to snap-002 (== snap-001 chain anchor)",
          f"{len(graph_edges)} edges, {sha(ge_bytes)[:16]}")

    # ---------------- misconceptions.json ----------------
    print("== misconceptions")
    cur.execute(
        """SELECT code, title FROM knowledge_nodes
           WHERE node_type='MISCONCEPTION' ORDER BY code"""
    )
    misconceptions = [{"code": r[0], "title": r[1]} for r in cur.fetchall()]
    mis_bytes = compact(misconceptions).encode()
    check(sha(mis_bytes) == sha(open(f"{SNAP2}/misconceptions.json", "rb").read()),
          "misconceptions BYTE-IDENTICAL to snap-002", f"{len(misconceptions)} rows")

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
    old_qa_sha = sha(open(f"{SNAP2}/question_anchors.json", "rb").read())
    check(sha(qa_bytes) == old_qa_sha,
          "question_anchors BYTE-IDENTICAL to snap-002 (fidelity anchor)",
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
    pins = {}
    import pathlib
    for label, path in [("concepts.yaml", CONCEPTS_YAML)]:
        pins[label] = sha(pathlib.Path(path).read_bytes())
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
    old_gc = json.load(open(f"{SNAP2}/graph_code.json"))

    def sig(rows):
        return {r["code"]: (tuple(sorted(r["aliases"])), tuple(sorted(r["spec_points"])),
                            r["family"], r["title"]) for r in rows}

    check(sig(concepts_out) == sig(old_gc["concepts"]),
          "graph_code.concepts rows set-equal to snap-002 (pinned store @1245df0 unchanged)")
    check(mis_out == old_gc["misconceptions"], "graph_code.misconceptions byte-equal",
          f"{len(mis_out)}")
    check(graph_code["counts"] == old_gc["counts"], "graph_code.counts equal",
          json.dumps(graph_code["counts"]))
    check(not title_drift, "no title drift on emitted nodes", f"{title_drift[:5]}")
    check(old_gc["source"]["head"] == HEAD, "resources HEAD pin unchanged since snap-002", HEAD)

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
    old_att_sha = sha(open(f"{SNAP2}/concept_attachments.json", "rb").read())
    check(sha(att_bytes) == old_att_sha,
          "concept_attachments BYTE-IDENTICAL to snap-002 (same ratified inputs)",
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
    print("\nALL VERIFICATIONS PASS — staging tree ready for manifest + freeze review")


if __name__ == "__main__":
    main()
