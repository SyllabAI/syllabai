#!/usr/bin/env python3
"""snap-006 exporter — the notes-axis-promotion freeze substrate (2026-09-28).

Sixth versioned freeze in the snap-N series. Adapted from the frozen
snap005_export.py (carried in evidence/bench-001/snapshots/snap-005/) with ALL
producer queries preserved verbatim; comparison base advances snap-004 -> snap-005.

Purpose: the r7 freeze. The operator's named decision (IM trace
1a0e88af08e12df5, verbatim "pursue (a). And check current state, and other
agents' work. Check if they completed these or not", where (a) was presented in
trace 1a0e88d81372240d) was applied 2026-09-28 as batch
`notes-axis-promotion-2026-09-28` (content_review_audit batch_run_id
ef4c1fe4-1b18-4697-b3bd-074e4e0f582b): the 112 EXTERNAL_NOTES documents
SUGGESTED -> VALIDATED + their 350 chunks embed_rev 2 -> 1, purely additive to
the serving gate (replica 615 -> 965; notes chunks all gemini-embedding-001@768
both revs). This freeze captures that production truth so §8(d)
SpecificationPoint resolution — scored 0.0 at r6 because the HV-mapped notes
chunks were SUGGESTED and the VALIDATED-only serving gate excluded exactly
them — is measured over a SERVED view that now contains the mapped chunks.

Changes vs snap-005 (all recorded as manifest-bound deltas, never silent):
  SNAP6-F1  validation flips captured at run time. Expected cohorts (both are
            recorded operator decisions, verified first-hand before staging):
            (i) exactly the 350 EXTERNAL_NOTES chunks SUGGESTED -> VALIDATED
            (notes-axis promotion, batch ef4c1fe4…, operator trace
            1a0e88af08e12df5); (ii) exactly the 3 T-C27 card chunks
            FLAGGED -> VALIDATED (the flagged-3 flip, records 7f3a8f3ec,
            applied 2026-09-28T11:34Z per the operator's own named flip
            decision, trace 1a0e7865c3b35715, after the flagged-3 source
            verification). ANY OTHER up-flip, and ANY down-flip, aborts.
  SNAP6-F2  metadata-only paper_code stamps (same rule as SNAP5-F2).
  SNAP6-F3  question_anchors multiset SUPERSET of snap-005 (no removal or
            mutation; growth recorded — the SNAP5-F6 rule carried forward).
  SNAP6-H1  additive §8(d) substrate: chunk_spec_hv.json BYTE-IDENTICAL to the
            records-committed projection (sha256 b5b20ffa…, the SNAP5-H1
            artifact), manifest-pinned so BenchSnapshot's fail-closed loader
            verifies it; drift gate re-verified over the frozen chunk bytes.
  SNAP6-M1  method note: sanctioned session-env read path, SELECT-only, rolled
            back (SNAP3-M1/SNAP4-M1/SNAP5-M1 lineage unchanged).

Fidelity anchors (must hold or the script exits non-zero):
  - chunks               snap-005's 4,181 row set carried IDENTICAL (same
    chunk_refs, contents, kinds, spec_codes); the ONLY permitted value deltas
    are paper_state (SNAP6-F1) and metadata-only paper_code stamps (SNAP6-F2).
    NO new rows, NO removed rows. Any other drift = FAIL.
  - spec_points / graph_edges / misconceptions / question_anchors /
    concept_attachments  re-fetched live; byte-identical or superset-equal per
    the rules above; graph_code re-emitted, rows set-equal (source.date
    differs by design).
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
from collections import Counter
from datetime import datetime, timezone

import psycopg2
import yaml

SNAP5 = "/home/z/my-project/workspace/r7_staging/snap-005"
HV_SOURCE = "/home/z/my-project/workspace/r7_staging/snap-005/chunk_spec_hv.json"
HV_SHA256 = "b5b20ffa96b620bd1d2f27b698eefd325c6f62299f85b15bb16cd141518a32e3"
STORE = "/home/z/my-project/workspace/r7_staging/spec_chunk_mappings.yaml"
STORE_SHA16 = "e8b58a7109104bb7"
RESOURCES_MAIN = "1245df009712216b309f163aacdd1c6d8ef39f1b"
STAGING = "/home/z/my-project/workspace/snap006/staging"
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

    # ---------------- chunks.jsonl.gz (producer query verbatim from snap005) --
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

    old = json.load(gzip.open(f"{SNAP5}/chunks.jsonl.gz"))
    old_by_ref = {c["chunk_ref"]: c for c in old}
    new_by_ref = {c["chunk_ref"]: c for c in chunks}
    added_refs = set(new_by_ref) - set(old_by_ref)
    removed_refs = set(old_by_ref) - set(new_by_ref)
    check(not removed_refs, "no snap-005 chunk_ref removed",
          f"{len(removed_refs)} removed")
    check(not added_refs, "no new chunk_ref since snap-005 (SNAP6 row-set frozen; "
          "the notes chunks joined at snap-005)",
          f"{len(added_refs)} added")
    common_refs = set(old_by_ref) & set(new_by_ref)
    content_drift = [r for r in common_refs if old_by_ref[r]["content"] != new_by_ref[r]["content"]]
    check(not content_drift, "chunk contents IDENTICAL to snap-005 on the carried set",
          f"{len(content_drift)} drifts")
    kind_drift = [r for r in common_refs if old_by_ref[r]["kind"] != new_by_ref[r]["kind"]]
    check(not kind_drift, "chunk kinds IDENTICAL to snap-005 on the carried set",
          f"{len(kind_drift)} drifts")
    sc_drift = [r for r in common_refs
                if old_by_ref[r]["spec_codes"] != new_by_ref[r]["spec_codes"]]
    check(not sc_drift, "chunk spec_codes IDENTICAL to snap-005 on the carried set",
          f"{len(sc_drift)} drifts")

    state_flips, code_stamps = [], []
    for r in common_refs:
        c, o = new_by_ref[r], old_by_ref[r]
        if o and o["paper_state"] != c["paper_state"]:
            state_flips.append({"chunk_ref": r, "kind": c["kind"], "paper_code": c["paper_code"],
                                "snap005": o["paper_state"], "snap006": c["paper_state"]})
        if o and o.get("paper_code") != c.get("paper_code"):
            code_stamps.append({"chunk_ref": r, "kind": c["kind"],
                                "snap005": o.get("paper_code"), "snap006": c.get("paper_code")})
    up_flips = [f for f in state_flips if f["snap006"] == "VALIDATED"]
    down_flips = [f for f in state_flips if f["snap006"] != "VALIDATED"]

    # SNAP6-F1: the ONLY sanctioned up-flip cohorts (both operator-recorded):
    #   (i)  EXTERNAL_NOTES SUGGESTED -> VALIDATED  (notes-axis promotion,
    #        batch ef4c1fe4-1b18-4697-b3bd-074e4e0f582b, trace 1a0e88af08e12df5)
    #   (ii) EXTERNAL_QUESTIONS FLAGGED -> VALIDATED (the flagged-3 flip,
    #        records 7f3a8f3ec, operator trace 1a0e7865c3b35715)
    notes_flips = [f for f in up_flips
                   if f["kind"] == "EXTERNAL_NOTES" and f["snap005"] == "SUGGESTED"]
    flag3_flips = [f for f in up_flips
                   if f["kind"] == "EXTERNAL_QUESTIONS" and f["snap005"] == "FLAGGED"]
    unexpected_up = [f for f in up_flips if f not in notes_flips and f not in flag3_flips]
    check(not unexpected_up,
          "up-flips are ONLY the sanctioned cohorts (SNAP6-F1)",
          f"{len(unexpected_up)} unexpected: {json.dumps(unexpected_up[:3])}")
    check(len(notes_flips) == 350,
          "notes-axis promotion captured: exactly the 350 EXTERNAL_NOTES chunks "
          "SUGGESTED -> VALIDATED (operator batch ef4c1fe4…)",
          f"{len(notes_flips)} notes flips")
    check(len(flag3_flips) == 3,
          "flagged-3 flip captured: exactly the 3 T-C27 card chunks "
          "FLAGGED -> VALIDATED (operator decision, records 7f3a8f3ec)",
          f"{len(flag3_flips)} flag flips")
    check(not down_flips, "zero down-flips since snap-005 (SNAP6-F2; the snap-005 "
          "FLAG decisions were already captured there)",
          f"{len(down_flips)} down-flips")

    ps_by_kind = {}
    for c in chunks:
        ps_by_kind.setdefault(c["kind"], {}).setdefault(c["paper_state"], 0)
        ps_by_kind[c["kind"]][c["paper_state"]] += 1
    print(f"  paper_state by kind: {json.dumps(ps_by_kind, sort_keys=True)}")
    flip_by_kind_from = {}
    for f in state_flips:
        key = f"{f['kind']}|{f['snap005']}->{f['snap006']}"
        flip_by_kind_from.setdefault(key, 0)
        flip_by_kind_from[key] += 1
    print(f"  flips by kind|from->to: {json.dumps(flip_by_kind_from, sort_keys=True)}")

    DELTAS["SNAP6-F1_validation_flips"] = {
        "finding": "validation-state flips since the snap-005 freeze, captured at freeze "
                   "time as-is. Two cohorts, both recorded operator decisions verified "
                   "first-hand before this freeze: (i) the notes-axis promotion (operator "
                   "trace 1a0e88af08e12df5 'pursue (a)', batch notes-axis-promotion-2026-09-28, "
                   "content_review_audit batch_run_id ef4c1fe4-1b18-4697-b3bd-074e4e0f582b): "
                   "112 EXTERNAL_NOTES documents SUGGESTED -> VALIDATED + their 350 chunks "
                   "embed_rev 2 -> 1 — the serving-gate replica moved 615 -> 965 purely "
                   "additively; (ii) the flagged-3 flip (records 7f3a8f3ec, applied "
                   "2026-09-28T11:34Z per the operator's named flip decision, trace "
                   "1a0e7865c3b35715): the 3 T-C27 cards #207/#278/#291 FLAGGED -> VALIDATED. "
                   "This is the delta that moves §8(d) off its r6 0.0: the VALIDATED-only "
                   "serving gate no longer excludes the HV-mapped notes chunks.",
        "chunks_flipped_to_validated": len(up_flips),
        "notes_chunks_suggested_to_validated": len(notes_flips),
        "card_chunks_flagged_to_validated": len(flag3_flips),
        "flips_by_kind_from_to": flip_by_kind_from,
        "paper_state_by_kind": ps_by_kind,
        "no_down_flips": len(down_flips) == 0,
        "row_set_identity": "snap-005's 4,181 chunk_refs carried with IDENTICAL contents, "
                            "kinds and spec_codes; zero added, zero removed; paper_state "
                            "(and metadata-only paper_code stamps, if any) are the only "
                            "permitted value deltas, verified programmatically",
    }
    stamp_by_kind = {}
    for s in code_stamps:
        stamp_by_kind[s["kind"]] = stamp_by_kind.get(s["kind"], 0) + 1
    DELTAS["SNAP6-F2_chunk_paper_code_stamps"] = {
        "finding": "metadata-only paper_code stamps since snap-005 (recorded, never gating).",
        "rows_stamped": len(code_stamps),
        "by_kind": stamp_by_kind,
    }
    DELTAS["SNAP6-M1_method_note"] = {
        "finding": "unchanged read path: sanctioned production connection from the session "
                   "env, READ-ONLY (set_session(readonly=True)), SELECT-only, rolled back; "
                   "zero writes to any production table",
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

    DELTAS["SNAP6-H1_chunk_spec_hv_substrate"] = {
        "finding": "§8(d) substrate carried BYTE-IDENTICAL from snap-005 (sha256-pinned "
                   "to the records-committed artifact, records 94d0d405c): the 210 "
                   "HUMAN_VALIDATED chunk→SP mappings are unchanged; what CHANGES at "
                   "snap-006 is the serving state of the chunks those refs anchor — "
                   "VALIDATED after the notes-axis promotion, so the served view now "
                   "contains the mapped chunks and §8(d) is measured with coverage "
                   "(r6 scored it 0.0 over the same substrate because the gate excluded "
                   "exactly these chunks). Drift gate: every mapping's quote containment "
                   f"re-verified over the FROZEN chunk bytes against the pinned resources "
                   f"store ({RESOURCES_MAIN}, store sha256_16 {STORE_SHA16}); anchor kinds "
                   f"recomputed {json.dumps(recomputed_kinds)}; "
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
    check(sha(sp_bytes) == sha(open(f"{SNAP5}/spec_points.json", "rb").read()),
          "spec_points BYTE-IDENTICAL to snap-005 (fidelity anchor)",
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
    check(sha(ge_bytes) == sha(open(f"{SNAP5}/graph_edges.json", "rb").read()),
          "graph_edges BYTE-IDENTICAL to snap-005 (fidelity anchor)",
          f"{len(graph_edges)} edges, {sha(ge_bytes)[:16]}")

    # ---------------- misconceptions.json (verbatim) ---------------------------
    print("== misconceptions")
    cur.execute(
        """SELECT code, title FROM knowledge_nodes
           WHERE node_type='MISCONCEPTION' ORDER BY code"""
    )
    misconceptions = [{"code": r[0], "title": r[1]} for r in cur.fetchall()]
    mis_bytes = compact(misconceptions).encode()
    check(sha(mis_bytes) == sha(open(f"{SNAP5}/misconceptions.json", "rb").read()),
          "misconceptions BYTE-IDENTICAL to snap-005", f"{len(misconceptions)} rows")

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
    # SNAP6-F3: fidelity = multiset SUPERSET (no removal/mutation); growth = recorded delta
    s5_rows = json.load(open(f"{SNAP5}/question_anchors.json", "rb"))
    s5_counter = Counter(compact(r) for r in s5_rows)
    live_counter = Counter(compact(r) for r in anchors)
    removed_rows = s5_counter - live_counter
    added_rows = live_counter - s5_counter
    check(sum(removed_rows.values()) == 0,
          "question_anchors SUPERSET of snap-005 — zero removal/mutation (SNAP6-F3)",
          f"{sum(removed_rows.values())} removed/mutated")
    check(True, "question_anchors growth recorded (SNAP6-F3)",
          f"+{sum(added_rows.values())} rows vs snap-005 ({len(s5_rows)} -> {len(anchors)})")
    DELTAS["SNAP6-F3_question_anchor_movement"] = {
        "finding": "the VALIDATED question_versions anchor set vs snap-005. Fidelity is "
                   "multiset superset — zero removal, zero mutation; growth is recorded "
                   "honestly (expected +0: the app-side teacher wave, pilot.teacher 11 qv "
                   "+ 1 ep, was already captured at snap-005 via SNAP5-F6; the T-PS1 "
                   "papers/schemes sheet remains unapplied).",
        "rows_added": sum(added_rows.values()),
        "rows_removed": sum(removed_rows.values()),
        "rows_snap005": len(s5_rows),
        "rows_snap006": len(anchors),
    }

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
    old_gc = json.load(open(f"{SNAP5}/graph_code.json"))

    def sig(rows):
        return {r["code"]: (tuple(sorted(r["aliases"])), tuple(sorted(r["spec_points"])),
                            r["family"], r["title"]) for r in rows}

    check(sig(concepts_out) == sig(old_gc["concepts"]),
          "graph_code.concepts rows set-equal to snap-005 (pinned store @1245df0 unchanged)")
    check(mis_out == old_gc["misconceptions"], "graph_code.misconceptions byte-equal",
          f"{len(mis_out)}")
    check(graph_code["counts"] == old_gc["counts"], "graph_code.counts equal",
          json.dumps(graph_code["counts"]))
    check(not title_drift, "no title drift on emitted nodes", f"{title_drift[:5]}")
    check(old_gc["source"]["head"] == HEAD, "resources HEAD pin unchanged since snap-005", HEAD)
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
    check(sha(att_bytes) == sha(open(f"{SNAP5}/concept_attachments.json", "rb").read()),
          "concept_attachments BYTE-IDENTICAL to snap-005 (same ratified inputs)",
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
        "snapshot_version": "snap-006",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "lineage": "snap-001 -> snap-002 -> snap-003 -> snap-004 -> snap-005 -> snap-006 "
                   "(notes-axis promotion freeze)",
        "files_sha256": {name: sha(open(f"{STAGING}/{name}", "rb").read())
                         for name in list(outs) + ["chunks.jsonl.gz"]},
        "counts": {
            "chunks": len(chunks),
            "chunks_by_kind": ps_by_kind and {k: sum(v.values()) for k, v in sorted(ps_by_kind.items())},
            "chunks_by_paper_state": ps_by_kind,
            "chunks_flipped_to_validated_vs_snap005": len(up_flips),
            "notes_chunks_suggested_to_validated_vs_snap005": len(notes_flips),
            "card_chunks_flagged_to_validated_vs_snap005": len(flag3_flips),
            "concept_attachments": len(attachments),
            "edges": len(graph_edges),
            "hv_projection": hv_census,
            "misconceptions": len(misconceptions),
            "question_anchors": len(anchors),
            "spec_points": len(spec_points),
        },
        "deltas_vs_snap-005": DELTAS,
        "notes_axis_gate": {
            "note": "recorded by the freeze run: the r7 gate is the operator's notes-axis "
                    "promotion decision (trace 1a0e88af08e12df5 'pursue (a)' on the option "
                    "presented in trace 1a0e88d81372240d); applied 2026-09-28 as batch "
                    "notes-axis-promotion-2026-09-28 with an independent post-verify and "
                    "records commit 9ea54e1e2 (kit + evidence). This freeze is the measured "
                    "consequence: the served view now contains the HV-mapped notes chunks.",
            "content_review_audit_batch_run_id": "ef4c1fe4-1b18-4697-b3bd-074e4e0f582b",
            "operator_trace": "1a0e88af08e12df5",
            "documents_flipped_suggested_to_validated": 112,
            "chunks_restamped_embed_rev_2_to_1": 350,
            "serving_gate_replica_before_after": "615 -> 965",
        },
        "flagged3_gate": {
            "note": "recorded by the freeze run: the operator's named flip decision for the "
                    "3 source-verified T-C27 cards (records 7f3a8f3ec applied 11:34Z, after "
                    "the snap-005 freeze), captured here as the second sanctioned cohort.",
            "operator_trace": "1a0e7865c3b35715",
            "card_chunks_flagged_to_validated": len(flag3_flips),
        },
        "graph_as_code_source": {"head": HEAD, "repo": "SyllabAI/syllabai-resources"},
        "chunk_spec_hv": {
            "sha256": HV_SHA256,
            "source": "records 94d0d405c bench/evidence/chunk-sp-substrate-2026-09-27/ "
                      "(byte-identical carry from snap-005)",
            "drift_gate": "re-verified over frozen bytes at export; anchor census "
                          + json.dumps(recomputed_kinds),
        },
    }
    open(f"{STAGING}/manifest.json", "w").write(json.dumps(manifest, indent=1))

    print("\n== summary")
    print("  counts:", json.dumps(manifest["counts"], sort_keys=True))
    for name in sorted(manifest["files_sha256"]):
        print(f"  {name}: sha256 {manifest['files_sha256'][name][:16]}…")
    print(f"\nALL VERIFICATIONS PASS — snap-006 STAGING tree ready ({STAGING})")
    print("Staging only: the FROZEN snapshot commit + gold re-pair + preload-r7 + workflows +")
    print("dispatches happen next in the recorded r7 sequence.")


if __name__ == "__main__":
    main()
