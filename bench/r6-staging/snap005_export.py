#!/usr/bin/env python3
"""snap-005 exporter — the r6 card-flip freeze substrate (staged pre-flip 2026-09-28).

Fifth versioned freeze in the snap-N series. Adapted from the frozen
snap004_export.py (carried in evidence/bench-001/snapshots/snap-004/) with ALL
producer queries preserved verbatim; comparison base advances snap-003 -> snap-004.

Purpose: the r6 card-flip freeze. The r6 gate is the operator/teacher card
validation wave (298 T-C27 EXTERNAL_QUESTIONS cards; re-probed NOT landed
2026-09-28 four times). This exporter is STAGED PRE-FLIP so the real freeze at
the flip is a single verified run; it captures whatever validation flips exist
AT RUN TIME as manifest-bound deltas — never asserted in advance. A zero-flip
run is legal as a dry-run proof and must NOT be frozen without the operator's
flip confirmation.

Changes vs snap-004 (all recorded as manifest-bound deltas, never silent):
  SNAP5-F1  validation flips captured at run time (expected at the real
            freeze: the card wave SUGGESTED->VALIDATED on the T-C27 card
            docs' chunks; dry-run expects 0)
  SNAP5-H1  additive §8(d) substrate: chunk_spec_hv.json = the
            chunk-sp-substrate-2026-09-27 projection, BYTE-IDENTICAL
            (sha256-pinned to the records-committed artifact), manifest-pinned
            so BenchSnapshot's fail-closed loader verifies it; flips §8(d)
            NOT SCOREABLE -> scoreable-with-coverage at this freeze
  SNAP5-M1  method note: sanctioned session-env read path, SELECT-only,
            rolled back (SNAP3-M1/SNAP4-M1 lineage unchanged)

Fidelity anchors (must hold or the script exits non-zero):
  - chunks               snap-004's 3,831 row set carried IDENTICAL (same chunk_refs,
    contents, kinds, spec_codes); the ONLY permitted value deltas are paper_state
    (SNAP5-F1) and metadata-only paper_code stamps. Any other drift = FAIL.
  - notes-axis inclusion SNAP5-F4: the 350 EXTERNAL_NOTES chunks JOIN the corpus row
    set (additive; they were excluded from snap-001..004 because the §8(d) chunk_ref
    join needs them and the ALL-denominator resolution view scores over the full
    corpus). Their paper_state is SUGGESTED = production truth, so the harness
    VALIDATED-only serving gate excludes them from served views exactly as the
    production T-C07 predicates do; they are reachable ONLY on the ALL-denominator
    view (run-001 B-proxy convention). SYLLABUS stays excluded.
  - spec_points / graph_edges / misconceptions / question_anchors /
    concept_attachments  re-fetched live, BYTE-IDENTICAL to snap-004;
    graph_code re-emitted, rows set-equal (source.date differs by design).
  - DRIFT GATE           every HV mapping re-verified over the FROZEN chunk
    bytes against the pinned resources store: recomputed anchor (kind + hit
    indexes) must equal the recorded projection row; any divergence aborts.
"""
import gzip
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

import psycopg2
import yaml

SNAP4 = "/home/z/my-project/workspace/snap005/snap-004"
HV_SOURCE = "/home/z/my-project/workspace/snap005/chunk_spec_hv_projection.json"
HV_SHA256 = "b5b20ffa96b620bd1d2f27b698eefd325c6f62299f85b15bb16cd141518a32e3"
STORE = "/home/z/my-project/workspace/snap005/store/spec_chunk_mappings.yaml"
STORE_SHA16 = "e8b58a7109104bb7"
RESOURCES_MAIN = "1245df009712216b309f163aacdd1c6d8ef39f1b"
STAGING = "/home/z/my-project/workspace/snap005/staging"
RES = "/home/z/my-project/workspace/snap003/resources_pins"
C19 = f"{RES}/scripts__c19_promotions.yaml"
CONCEPTS_YAML = f"{RES}/graph__igcse-chemistry__concepts.yaml"
HEAD = "1245df009712216b309f163aacdd1c6d8ef39f1b"  # syllabai-resources pin (unchanged since snap-002)

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


_TRANS = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"',
          ord("–"): "-", ord("—"): "-", ord("″"): '"', ord("′"): "'"}


def norm(s: str) -> str:
    """Verbatim copy of c13_chunk_sp_substrate.py@1.0.0 norm (C10/C13-shared, pinned)."""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\\", "")
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[*_`#>]+", "", s)
    s = s.translate(_TRANS)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def main():
    store_raw = open(STORE, "rb").read()
    assert hashlib.sha256(store_raw).hexdigest()[:16] == STORE_SHA16, \
        "resources store bytes != pinned e8b58a7109104bb7 (fail-closed)"
    store = yaml.safe_load(store_raw)
    store_rows = {r["mapping_id"]: r for r in store["rows"]}

    hv_raw = open(HV_SOURCE, "rb").read()
    assert sha(hv_raw) == HV_SHA256, "projection bytes != records-committed sha (fail-closed)"
    projection = json.loads(hv_raw)
    proj_by_mid = {r["mapping_id"]: r for r in projection["rows"]}

    conn = psycopg2.connect(DB_URL, sslmode="require", connect_timeout=30)
    conn.set_session(readonly=True, autocommit=False)
    cur = conn.cursor()

    # ---------------- chunks.jsonl.gz (producer query verbatim from snap004) --
    print("== chunks")
    cur.execute(
        """SELECT d.checksum, c.chunk_index, c.content, c.kind, d.kind,
                  c.page_end, c.page_start, c.paper_code, d.validation_state,
                  c.token_estimate, c.spec_codes, c.subject_id
           FROM document_chunks c JOIN documents d ON d.id = c.document_row_id
           WHERE d.kind IN ('QUESTION_PAPER','MARK_SCHEME','EXTERNAL_QUESTIONS','EXTERNAL_NOTES')
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
    check(kind_mismatch == 0, "chunk.kind == document.kind on every row", f"{kind_mismatch} mismatches")
    check(all(sha(c["content"].encode()) == c["content_sha256"] for c in chunks),
          "chunk content_sha256 self-consistency", f"{len(chunks)} rows")
    check(len({c["chunk_ref"] for c in chunks}) == len(chunks), "no duplicate chunk_refs")

    old = json.load(gzip.open(f"{SNAP4}/chunks.jsonl.gz"))
    old_by_ref = {c["chunk_ref"]: c for c in old}
    new_by_ref = {c["chunk_ref"]: c for c in chunks}
    added_refs = set(new_by_ref) - set(old_by_ref)
    removed_refs = set(old_by_ref) - set(new_by_ref)
    check(not removed_refs, "no snap-004 chunk_ref removed",
          f"{len(removed_refs)} removed")
    added_by_kind = {}
    for r in added_refs:
        added_by_kind[new_by_ref[r]["kind"]] = added_by_kind.get(new_by_ref[r]["kind"], 0) + 1
    check(added_by_kind == {"EXTERNAL_NOTES": 350},
          "additive delta == the 350 EXTERNAL_NOTES chunks (SNAP5-F4), nothing else",
          json.dumps(added_by_kind))
    check(all(new_by_ref[r]["paper_state"] == "SUGGESTED" for r in added_refs),
          "all added notes chunks carry paper_state SUGGESTED (production truth; "
          "VALIDATED-only serving gate excludes them exactly as production does)")
    common_refs = set(old_by_ref) & set(new_by_ref)
    content_drift = [r for r in common_refs if old_by_ref[r]["content"] != new_by_ref[r]["content"]]
    check(not content_drift, "chunk contents IDENTICAL to snap-004 on the carried set",
          f"{len(content_drift)} drifts")
    kind_drift = [r for r in common_refs if old_by_ref[r]["kind"] != new_by_ref[r]["kind"]]
    check(not kind_drift, "chunk kinds IDENTICAL to snap-004 on the carried set",
          f"{len(kind_drift)} drifts")
    sc_drift = [r for r in common_refs
                if old_by_ref[r]["spec_codes"] != new_by_ref[r]["spec_codes"]]
    check(not sc_drift, "chunk spec_codes IDENTICAL to snap-004 on the carried set",
          f"{len(sc_drift)} drifts")

    state_flips, code_stamps = [], []
    for r in common_refs:
        c, o = new_by_ref[r], old_by_ref[r]
        if o and o["paper_state"] != c["paper_state"]:
            state_flips.append({"chunk_ref": r, "kind": c["kind"], "paper_code": c["paper_code"],
                                "snap004": o["paper_state"], "snap005": c["paper_state"]})
        if o and o.get("paper_code") != c.get("paper_code"):
            code_stamps.append({"chunk_ref": r, "kind": c["kind"],
                                "snap004": o.get("paper_code"), "snap005": c.get("paper_code")})
    up_flips = [f for f in state_flips if f["snap005"] == "VALIDATED"]
    down_flips = [f for f in state_flips if f["snap005"] != "VALIDATED"]
    check(len(state_flips) == len(up_flips), "no regressions to non-VALIDATED",
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
    DELTAS["SNAP5-F1_validation_flips"] = {
        "finding": "validation-state flips since the snap-004 freeze, captured at freeze "
                   "time as-is. The r6 gate is the operator/teacher card validation wave "
                   "(298 T-C27 cards); this exporter is staged pre-flip and captures "
                   "whatever the live state holds when it actually runs at the flip.",
        "chunks_flipped_suggested_to_validated": len(up_flips),
        "flips_by_kind_paper_code": flip_by_kind_code,
        "documents_with_promoted_chunks": len(promoted_docs),
        "paper_state_by_kind": ps_by_kind,
        "no_regressions": len(down_flips) == 0,
        "row_set_identity": "snap-004's 3,831 chunk_refs carried with IDENTICAL contents, "
                            "kinds and spec_codes; paper_state (and metadata-only paper_code "
                            "stamps, if any) are the only permitted value deltas on the carried "
                            "set, verified programmatically",
    }
    stamp_by_kind = {}
    for s in code_stamps:
        stamp_by_kind[s["kind"]] = stamp_by_kind.get(s["kind"], 0) + 1
    DELTAS["SNAP5-F2_chunk_paper_code_stamps"] = {
        "finding": "metadata-only paper_code stamps since snap-004 (snap-004 recorded 246 "
                   "stamps in SNAP4-F2; any further stamps are recorded here).",
        "rows_stamped": len(code_stamps),
        "by_kind": stamp_by_kind,
    }
    DELTAS["SNAP5-M1_method_note"] = {
        "finding": "unchanged read path: sanctioned production connection from the session "
                   "env, READ-ONLY (set_session(readonly=True)), SELECT-only, rolled back; "
                   "zero writes to any production table",
    }
    DELTAS["SNAP5-F4_notes_axis_inclusion"] = {
        "finding": "the 350 EXTERNAL_NOTES chunks (112 notes documents) JOIN the snapshot "
                   "corpus additively — snap-001..004 excluded them (predicate "
                   "QP/MS/EQ only) because no serving or scoring path could reach them; "
                   "snap-005 includes them because (a) the §8(d) chunk_spec_hv projection "
                   "is keyed by their chunk_refs (the join needs the rows) and (b) the "
                   "ALL-denominator resolution view scores over the full corpus (run-001 "
                   "B-proxy ALL convention). paper_state stays SUGGESTED = production "
                   "truth, so the harness VALIDATED-only serving gate keeps them out of "
                   "served views exactly as the production T-C07 predicates do; the "
                   "a/b/c chunk-axis SERVED views change only via SNAP5-F1 flips, never "
                   "via this inclusion. SYLLABUS chunks (162) stay excluded.",
        "added_chunks": sorted(added_by_kind.items()),
        "added_refs_first_last": (sorted(added_refs)[0], sorted(added_refs)[-1]) if added_refs else [],
    }

    # ---------------- DRIFT GATE: §8(d) substrate over frozen bytes -----------
    print("== drift gate (chunk_spec_hv over exported chunk contents + pinned store)")
    note_chunks = {}
    for ref, c in new_by_ref.items():
        note_chunks.setdefault(ref.rsplit(":", 1)[0], []).append(
            (int(ref.rsplit(":", 1)[1]), c["content"]))
    for k in note_chunks:
        note_chunks[k].sort()

    gate_fails = []
    recomputed_kinds = {"CLEAN": 0, "MULTI": 0, "SPAN": 0, "MISS": 0}
    for mid, proj in proj_by_mid.items():
        srow = store_rows.get(mid)
        if srow is None:
            gate_fails.append({"mapping_id": mid, "reason": "mapping_id absent from pinned store"})
            continue
        quote = norm(srow.get("evidence_quote") or "")
        if not quote:
            gate_fails.append({"mapping_id": mid, "reason": "empty evidence_quote in store"})
            continue
        checksum = proj["checksum"]
        seq = note_chunks.get(checksum)
        if seq is None:
            gate_fails.append({"mapping_id": mid, "reason": "projection document not in export",
                               "checksum": checksum})
            continue
        hits = [idx for idx, content in seq if quote in norm(content)]
        if len(hits) == 1:
            kind = "CLEAN"
        elif len(hits) >= 2:
            kind = "MULTI"
        else:
            concat = "".join(norm(content) for _, content in seq)
            kind = "SPAN" if quote in concat else "MISS"
        recomputed_kinds[kind] += 1
        if kind != proj["anchor_kind"]:
            gate_fails.append({"mapping_id": mid, "reason": "anchor kind drifted",
                               "recorded": proj["anchor_kind"], "recomputed": kind})
            continue
        if kind in ("CLEAN", "MULTI") and sorted(hits) != sorted(proj["chunk_indexes"]):
            gate_fails.append({"mapping_id": mid, "reason": "hit indexes drifted",
                               "recorded": proj["chunk_indexes"], "recomputed": sorted(hits)})
        for ref in proj["chunk_refs"]:
            if ref not in new_by_ref:
                gate_fails.append({"mapping_id": mid, "reason": "recorded chunk_ref absent from export",
                                   "chunk_ref": ref})

    check(not gate_fails, "DRIFT GATE: all mappings re-verify over frozen bytes",
          f"{len(gate_fails)} divergences" + (f": {json.dumps(gate_fails[:3])}" if gate_fails else ""))
    check(recomputed_kinds == {"CLEAN": 205, "MULTI": 4, "SPAN": 0, "MISS": 1},
          "DRIFT GATE: anchor-kind census == the records-committed bridge (205/4/0/1)",
          json.dumps(recomputed_kinds))

    # handoff §4 census block: computed LIVE from the artifact bytes (never
    # hardcoded into the manifest) and asserted against the recorded bridge
    # census at export time; the core loader re-derives it from the pinned
    # bytes and fail-closes on any mismatch (verifyHvCensusAgainstManifest).
    hv_census = {
        "rows": len(projection["rows"]),
        "rows_with_refs": sum(1 for row in projection["rows"]
                              if any(r.strip() for r in row["chunk_refs"])),
        "distinct_chunk_refs": len({r for row in projection["rows"]
                                    for r in row["chunk_refs"] if r.strip()}),
        "distinct_spec_codes": len({row["spec_code"] for row in projection["rows"]}),
        "anchor_kinds": {k: recomputed_kinds.get(k, 0)
                         for k in ("CLEAN", "MULTI", "SPAN", "MISS")},
    }
    check((hv_census["rows"], hv_census["rows_with_refs"],
           hv_census["distinct_chunk_refs"], hv_census["distinct_spec_codes"])
          == (210, 209, 164, 181),
          "DRIFT GATE: projection census == the handoff §4 census (210/209/164/181)",
          json.dumps(hv_census))

    DELTAS["SNAP5-H1_chunk_spec_hv_substrate"] = {
        "finding": "additive §8(d) substrate: chunk_spec_hv.json = the "
                   "chunk-sp-substrate-2026-09-27 projection (records 94d0d405c), copied "
                   "BYTE-IDENTICAL and manifest-pinned so BenchSnapshot's fail-closed loader "
                   "verifies it (present-but-unpinned aborts; the §5 counting rule — "
                   "validation_status, never tier — is enforced in the loader). §8(d) flips "
                   "NOT SCOREABLE -> scoreable-with-coverage at this freeze. Drift gate: "
                   "every mapping's quote containment re-verified over the FROZEN chunk bytes "
                   f"against the pinned resources store ({RESOURCES_MAIN}, store sha256_16 "
                   f"{STORE_SHA16}); anchor kinds recomputed {json.dumps(recomputed_kinds)}; "
                   f"census rows={len(projection['rows'])} "
                   f"refs={len({r for row in projection['rows'] for r in row['chunk_refs']})}.",
        "projection_sha256": HV_SHA256,
        "drift_gate_failures": len(gate_fails),
    }

    # ---------------- spec_points.json (producer query verbatim) --------------
    print("== spec_points")
    cur.execute(
        """SELECT code, node_type, title, validation_status FROM knowledge_nodes
           WHERE node_type='SUBTOPIC' AND validation_status='VALIDATED'
             AND code LIKE '4CH1-%' ORDER BY code"""
    )
    spec_points = [{"code": r[0], "node_type": r[1], "title": r[2], "validation_status": r[3]}
                   for r in cur.fetchall()]
    sp_bytes = compact(spec_points).encode()
    check(sha(sp_bytes) == sha(open(f"{SNAP4}/spec_points.json", "rb").read()),
          "spec_points BYTE-IDENTICAL to snap-004 (fidelity anchor)",
          f"{len(spec_points)} rows, {sha(sp_bytes)[:16]}")

    # ---------------- graph_edges.json (verbatim) ------------------------------
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
    graph_edges = [{"relation": r[0], "source": r[1], "target": r[2]} for r in cur.fetchall()]
    ge_bytes = compact(graph_edges).encode()
    check(sha(ge_bytes) == sha(open(f"{SNAP4}/graph_edges.json", "rb").read()),
          "graph_edges BYTE-IDENTICAL to snap-004 (fidelity anchor)",
          f"{len(graph_edges)} edges, {sha(ge_bytes)[:16]}")

    # ---------------- misconceptions.json (verbatim) ---------------------------
    print("== misconceptions")
    cur.execute(
        """SELECT code, title FROM knowledge_nodes
           WHERE node_type='MISCONCEPTION' ORDER BY code"""
    )
    misconceptions = [{"code": r[0], "title": r[1]} for r in cur.fetchall()]
    mis_bytes = compact(misconceptions).encode()
    check(sha(mis_bytes) == sha(open(f"{SNAP4}/misconceptions.json", "rb").read()),
          "misconceptions BYTE-IDENTICAL to snap-004", f"{len(misconceptions)} rows")

    # ---------------- question_anchors.json (verbatim) -------------------------
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
    check(sha(qa_bytes) == sha(open(f"{SNAP4}/question_anchors.json", "rb").read()),
          "question_anchors BYTE-IDENTICAL to snap-004 (fidelity anchor)",
          f"{len(anchors)} rows, {sha(qa_bytes)[:16]}")

    # ---------------- graph_code.json (verbatim producer) ----------------------
    print("== graph_code")
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
    old_gc = json.load(open(f"{SNAP4}/graph_code.json"))

    def sig(rows):
        return {r["code"]: (tuple(sorted(r["aliases"])), tuple(sorted(r["spec_points"])),
                            r["family"], r["title"]) for r in rows}

    check(sig(concepts_out) == sig(old_gc["concepts"]),
          "graph_code.concepts rows set-equal to snap-004 (pinned store @1245df0 unchanged)")
    check(mis_out == old_gc["misconceptions"], "graph_code.misconceptions byte-equal",
          f"{len(mis_out)}")
    check(graph_code["counts"] == old_gc["counts"], "graph_code.counts equal",
          json.dumps(graph_code["counts"]))
    check(not title_drift, "no title drift on emitted nodes", f"{title_drift[:5]}")
    check(old_gc["source"]["head"] == HEAD, "resources HEAD pin unchanged since snap-004", HEAD)
    gc_bytes = json.dumps(graph_code, indent=1, sort_keys=True).encode()

    # ---------------- concept_attachments.json (verbatim producer) -------------
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
          "DB serving pairs (SUGGESTED, all CONCEPT->SUBTOPIC) == ratified HV pair set",
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
    check(sha(att_bytes) == sha(open(f"{SNAP4}/concept_attachments.json", "rb").read()),
          "concept_attachments BYTE-IDENTICAL to snap-004 (same ratified inputs)",
          sha(att_bytes)[:16])

    conn.rollback()
    conn.close()

    # ---------------- staging writes ------------------------------------------
    if FAILS:
        print(f"\nEXPORT ABORTED — verification failed ({len(FAILS)}): {FAILS}")
        sys.exit(1)

    os.makedirs(STAGING, exist_ok=True)
    outs = {
        "spec_points.json": sp_bytes,
        "graph_edges.json": ge_bytes,
        "misconceptions.json": mis_bytes,
        "question_anchors.json": qa_bytes,
        "concept_attachments.json": att_bytes,
        "graph_code.json": gc_bytes,
        "chunk_spec_hv.json": hv_raw,
    }
    for name, data in outs.items():
        open(f"{STAGING}/{name}", "wb").write(data)
    gz = gzip.GzipFile(filename="", mode="wb", fileobj=open(f"{STAGING}/chunks.jsonl.gz", "wb"),
                       mtime=0)
    gz.write(json.dumps(chunks, sort_keys=True, separators=(",", ":")).encode())
    gz.close()

    json.dump(DELTAS, open(f"{STAGING}/verification_deltas.json", "w"), indent=1)

    manifest = {
        "snapshot_version": "snap-005",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lineage": "snap-001 -> snap-002 -> snap-003 -> snap-004 -> snap-005 (r6 card-flip)",
        "files_sha256": {name: sha(open(f"{STAGING}/{name}", "rb").read())
                         for name in list(outs) + ["chunks.jsonl.gz"]},
        "counts": {
            "chunks": len(chunks),
            "chunks_by_kind": ps_by_kind and {k: sum(v.values()) for k, v in sorted(ps_by_kind.items())},
            "chunks_by_paper_state": ps_by_kind,
            "chunks_flipped_suggested_to_validated_vs_snap004": len(up_flips),
            "concept_attachments": len(attachments),
            "edges": len(graph_edges),
            "hv_projection": hv_census,
            "misconceptions": len(misconceptions),
            "question_anchors": len(anchors),
            "spec_points": len(spec_points),
        },
        "deltas_vs_snap-004": DELTAS,
        "r6_gate": {
            "note": "recorded by the freeze run: live EXTERNAL_QUESTIONS validation census "
                    "at freeze time; the operator card wave is the r6 gate",
            "eq_chunks_flipped_this_freeze": len(up_flips),
        },
        "graph_as_code_source": {"head": HEAD, "repo": "SyllabAI/syllabai-resources"},
        "chunk_spec_hv": {
            "sha256": HV_SHA256,
            "source": "records 94d0d405c bench/evidence/chunk-sp-substrate-2026-09-27/",
            "drift_gate": "re-verified over frozen bytes at export; anchor census "
                          + json.dumps(recomputed_kinds),
        },
    }
    open(f"{STAGING}/manifest.json", "w").write(json.dumps(manifest, indent=1))

    print("\n== summary")
    print("  counts:", json.dumps(manifest["counts"], sort_keys=True))
    for name in sorted(manifest["files_sha256"]):
        print(f"  {name}: sha256 {manifest['files_sha256'][name][:16]}…")
    print(f"\nALL VERIFICATIONS PASS — snap-005 STAGING tree ready ({STAGING})")
    print("Staging only: the FROZEN snapshot commit + gold re-pair + preload-r6 + workflows +")
    print("dispatches happen at the real r6 freeze, after the operator card wave lands.")


if __name__ == "__main__":
    main()
