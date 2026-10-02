#!/usr/bin/env python3
"""wave2_census_export.py — F-PROD-3 wave-2 composition input: the LIVE chunk
census of production (2026-10-02), exported SELECT-only over the sanctioned
session-env read path (Render env-vars API, snap-006 lineage).

Why a live census and not a snap-007 re-freeze: the wave-1 PRODUCTION report
(F-PROD-3) explicitly sanctions "a FRESH snapshot re-freeze (or live probes)".
The full snap-export machinery carries pinned workspace stores that no longer
exist in this sandbox; the wave-2 composition needs ONLY the chunk-level
(gate-state, kind, subject-scope, spec-codes) truth, exported here with the
same chunk_ref contract as snap-006 (content_sha256:chunk_index) so the
gold-v5 demand join stays byte-compatible.

Gate semantics (mirrors ChunkVectorRepository.searchServingEligible):
  owner = PAPER           -> gate_state = exam_papers.validation_state
  owner = SUBJECT_BRANCH  -> gate_state = documents.validation_state
  owner = NONE (no paper row, subject NULL) -> gate_state = doc state,
            serving impossible (fail-closed) — recorded as UNPLACEABLE
"""
import gzip
import json
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras

ENV_FILE = "/home/z/my-project/scripts/.render_env.json"
OUT = "/home/z/my-project/repos/syllabai/evidence/bench-001/wave2-prep-2026-10-02/live_census_chunks.json.gz"
OUT_MANIFEST = "/home/z/my-project/repos/syllabai/evidence/bench-001/wave2-prep-2026-10-02/live_census_manifest.json"

env = {e["envVar"]["key"]: e["envVar"]["value"]
       for e in json.load(open(ENV_FILE))["env"]}
url = env["SYLLABAI_DATABASE_URL"]
if url.startswith("jdbc:"):
    url = url[len("jdbc:"):]
u = urlparse(url)
conn = psycopg2.connect(
    f"postgresql://{env['SYLLABAI_DATABASE_USERNAME']}:{env['SYLLABAI_DATABASE_PASSWORD']}"
    f"@{u.hostname}{u.path}", sslmode="require", connect_timeout=30)
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# identity gate
cur.execute("select current_database() as db")
assert cur.fetchone()["db"] == "neondb", "identity gate: wrong database"
cur.execute("select campaign_label, db_name from campaign_db_identity where id = 1")
r = cur.fetchone()
assert r["campaign_label"] == "T-C04-CAMPAIGN" and r["db_name"] == "neondb"
print(f"[identity gate PASS] db={r['db_name']} label={r['campaign_label']}")

cur.execute("select id, code from curriculum_versions where status = 'ACTIVE'")
actives = cur.fetchall()
assert len(actives) == 1, f"ACTIVE cv count = {len(actives)}"
active = actives[0]

SQL = """
select c.id, d.document_id, d.doc_version, d.kind as doc_kind,
       d.validation_state as doc_state,
       c.chunk_index, d.checksum, c.embedding is not null as embedded,
       c.embed_rev, c.spec_codes,
       c.subject_id as chunk_subject_id,
       p.id as paper_id, p.validation_state as paper_state,
       p.paper_code,
       s.curriculum_version_id::text as paper_subject_cv,
       s2.curriculum_version_id::text as chunk_subject_cv
from document_chunks c
join documents d on d.id = c.document_row_id
left join exam_papers p on p.question_paper_document_id = d.document_id
                       or p.mark_scheme_document_id = d.document_id
left join subjects s on s.id = p.subject_id
left join subjects s2 on s2.id = c.subject_id
order by d.document_id, c.chunk_index
"""
cur.execute(SQL)
rows = cur.fetchall()
print(f"chunks exported: {len(rows)}")

out = []
for r in rows:
    has_paper = r["paper_id"] is not None
    if has_paper:
        owner = "PAPER"
        gate = r["paper_state"]
        cv = r["paper_subject_cv"]
    elif r["chunk_subject_id"] is not None:
        owner = "SUBJECT_BRANCH"
        gate = r["doc_state"]
        cv = r["chunk_subject_cv"]
    else:
        owner = "UNPLACEABLE"
        gate = r["doc_state"]
        cv = None
    out.append({
        "chunk_ref": f"{r['checksum']}:{r['chunk_index']}",
        "document_id": r["document_id"],
        "kind": r["doc_kind"],
        "doc_state": r["doc_state"],
        "paper_id": str(r["paper_id"]) if r["paper_id"] else None,
        "paper_code": r["paper_code"],
        "paper_state": r["paper_state"],
        "owner": owner,
        "gate_state": gate,
        "scope_cv": cv,
        "in_active_scope": cv == active["id"],
        "embedded": r["embedded"],
        "embed_rev": r["embed_rev"],
        "spec_codes": r["spec_codes"] or [],
    })

manifest = {
    "census": "live_census_chunks",
    "captured_at_utc": __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc).isoformat(),
    "method": "SELECT-only live export over the sanctioned session-env read path "
              "(Render env-vars API -> SYLLABAI_DATABASE_URL; snap-006 lineage). "
              "Sanctioned as the wave-2 freeze alternative by F-PROD-3 "
              "(wave-1 PRODUCTION report): 'a FRESH snapshot re-freeze (or live probes)'.",
    "identity": {"db": "neondb", "label": "T-C04-CAMPAIGN"},
    "active_curriculum_version": {"id": active["id"], "code": active["code"]},
    "chunk_count": len(out),
    "chunk_ref_contract": "content_sha256:chunk_index (identical to snap-006; "
                          "gold-v5 evidence refs join directly)",
    "gate_semantics": "owner PAPER -> paper.validation_state; SUBJECT_BRANCH -> "
                      "documents.validation_state; UNPLACEABLE -> fail-closed",
}
conn.close()

import os
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with gzip.open(OUT, "wt") as f:
    json.dump(out, f)
json.dump(manifest, open(OUT_MANIFEST, "w"), indent=1)

from collections import Counter
gated = Counter((r["owner"], r["gate_state"], r["kind"]) for r in out)
print("\ncensus by owner × gate_state × kind (non-VALIDATED only):")
for (o, g, k), n in sorted(gated.items()):
    if g != "VALIDATED":
        print(f"   {o:15s} {g:10s} {k:18s} {n}")
print(f"\nwritten: {OUT}")
print(f"written: {OUT_MANIFEST}")
