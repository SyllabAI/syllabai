# G1 MS-classifier upgrade — landing evidence (2026-09-22)

Lane: parser G1 (old-spec MS row grammar) + G1.1 (MS-only mode) + corpus
landing (re-ingest + re-embed). Parser commits: `9f38dda` (G1 classifier,
pushed 2026-09-22 07:03Z, parser-ci success) and `dffeb1d` (MS-only mode +
`Total for Q<N> = X` abbreviated total rows, pushed 08:0xZ, parser-ci success,
run 35700676083).

## What landed

1. **Parser G1 upgrade** (9f38dda): old-spec mark-scheme row grammar —
   furniture vs grid classification, guidance-hijack guard, phantom-point
   kill, capped alternative groups, part inheritance, QP-aware arithmetic
   closure. Sample 4CH0/1C jan2012: marksVerified false→true, unclassified
   40+→0, PART-MARKS-MISMATCH 11/11→0.
2. **MS-only mode** (dffeb1d): run_paper --ms-only for papers shipping ms.pdf
   without qp.pdf (Nov 2020 COVID: 4CH1-1CR/2C/2CR). Honest atoms: type
   ms-only, marksVerified=false by construction, MS-ONLY-NO-QP flag. Bridge
   emits a single ms.canonical.json. Suite 101 passed / 1 skipped.
3. **Corpus landing** (this lane): the G8-era MS canonicals were re-derived
   from the upgraded parser and diffed against production canonical_json
   (normalized, provenance.extractedAt excluded). Chain validation: the OLD
   repo products re-bridged to EXACTLY the DB canonicals (modulo extractedAt)
   — staging/bridge/identity reproduction proven before any diff was trusted.

## Delta (delta_full.json)

- 170 rev2 QP/MS docs mapped to current PDFs (0 unmatched)
- QUESTION_PAPER: 73 UNCHANGED + 12 URI-ONLY + 0 content changes (G1 did not
  touch QP parsing — confirmed by the corpus diff)
- MARK_SCHEME: 83 CONTENT-CHANGED + 2 UNCHANGED
- 3 MS-only papers had no prior docs (new coverage)

## Landing execution

- ARCHIVE: 83 old MS docs (canonical_json + chunks, embeddings f32-LE b64) →
  download/g1_ms_replace_archive/ (SHA256SUMS pinned; 1,249 chunks)
- DELETE: guarded single transaction — prestate asserted (kind=MARK_SCHEME,
  rev2-only chunks, 0 pending, 0 exam_papers pointer references) → 83 rows,
  1,249 chunks cascaded
- POST: 86 canonicals (83 replacements + 3 ms-only) through the app's own
  ingest `POST /api/v1/teacher/content/documents?kind=MARK_SCHEME`; 201/86,
  0 duplicates, chunk counts == bridge previews (86/86)
- EMBED: ops-g1-finish run 35702395719 — round 1 key[1] 91fdfb06ac embedded
  796 then RPD-exhausted (38 docs fail-fast), round 2 key[2] 797b77a879
  embedded 548, 0 failures; 1,344/1,344 chunks COMPLETE

## Render API contract notes (new)

- deploys POST now answers **HTTP 202 with an EMPTY body** (no deploy id);
  finish_g1.py discovers the id from the deploys list (freshest within 120s)
- one observed transient: env-vars GET returned 200 empty-body
  (run 35702012873); http_json retries empty-body 2xx with backoff

## Post state (g1_final_db_state.json)

- rev2: 3,787 chunks / 0 pending / rev1: 0; single model, app-transport only
- kind mix {MS 1364 (+95), QP 1153 (=), CARDS 758, NOTES 350, SPEC 162}
- documents 700; MS paper identities 88 = 85 (qp+ms) + 3 (ms-only) —
  **paper-axis coverage 88/88, the MS-only gap is closed**
- QP side byte-identical to pre-landing (no churn on unchanged content)

## Post-landing serving soak (g1_post_probes.json)

- health UP; 9 search probes serve 3.9–4.8s (8 r5 baselines + new MSO-1
  MARK_SCHEME-lane probe); top MSO-1 hits resolve to the freshly-landed
  09-22 docs (scores 0.72–0.73) with correct v1.2.0 chunk headers
- rev-leakage: 90 hits → embed_rev=2, 0 leaks, 0 unresolved
- determinism double-pass: PASS
- Fetch FET-002/FET-003: papers=2 both — identical to the r5 baseline
- Enumerate ENU-002 (metallic bonding): 1 question — identical to baseline

## Honest disclosure (exogenous drift, not this landing)

- Enumerate structured node 4CH1-1.32 (empirical/molecular formula) now
  resolves the node but returns 0 bank questions (was 1 at Task-34/35
  verify). The G1 landing touched ONLY documents/document_chunks; bank
  questions/knowledge_nodes are other lanes' active territory (session-115/116
  calibration + "deduped census in the question taxonomy", core ad44cee).
  Fetch + ENU-002 semantics unchanged → the deterministic bank path is intact.

## Standing security note

Render serving key is now sha256:797b77a879 (pool[2]); keys [1] and [3] were
RPD-drained today and recover after Pacific-midnight reset. Rotation of all 4
Gemini keys + PATs remains on the standing list; the GitHub PAT used this
session is stored in scripts/.ghenv (0600, local only).
