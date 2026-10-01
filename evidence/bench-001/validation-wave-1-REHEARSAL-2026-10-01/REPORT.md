# Wave-1 REHEARSAL + frozen-vector probe — bench_replay (2026-10-01, T-C41/T-C42)

**Status:** REHEARSAL EXECUTED END-TO-END, ZERO PRODUCTION CONTACT.
`bench_replay` is a disposable Postgres 17.11 + pgvector 0.8.6 replay DB
(workspace-local, :5433). No production credential exists in this lane; no
production row was read or written. **Gate 2 of the calibration pack remains
PENDING the operator's production probe** — nothing here clears it.

## What this rehearsal proves

1. **The wave kit now executes.** Its first-ever execution caught two kit bugs
   that would have failed the operator's first production run:
   - `prestate.sql` + `restamp.sql` joined `documents.id` (uuid) to
     `exam_papers.question_paper_document_id` (varchar(80), the
     `documents.document_id` business key; DDL V8:24, correct join per V35:112)
     → `ERROR: operator does not exist: uuid = character varying`. Fixed to
     `d.document_id = p.question_paper_document_id`.
   - `:paper_code` binds were unquoted; psql needs `:'paper_code'` for a
     quoted literal (trailing-junk error at `= 4CH1/2C`). Fixed in both files.
   - `poststate.sql` was correct as composed (uses `d.document_id`); the
     T-C42 probe kit SQL was verified correct (same shape).
2. **The prestate is production-faithful.** Loader = production `Run003B.loadSnapshot`
   + bit-exact `preload-r7` vectors + the 2026-09-28 cut-over-mirror stamp →
   **exactly 965 chunks at rev2** (the recorded production census) / 3,216 at rev1.
3. **The funnel mechanics hold.** Per unit: validate-all (real endpoint, real
   fail-closed service path, minted bench TEACHER JWT) → paired restamp →
   poststate. Rowcount gates matched EXACTLY every time; reachable_at_rev2
   moved by exactly the unit's predicted unlock:

| unit | at_rev1 (prestate) | restamp UPDATE | reachable_at_rev2 after |
|---|---:|---:|---:|
| (pre-wave) | — | — | 965 |
| 4CH1/2C | 350 | 350 | 1,315 |
| 4CH0/2C | 354 | 354 | 1,669 |
| 4CH1/2CR | 255 | 255 | 1,924 |
| 4CH1/1C | 505 | 505 | **2,429** |

   Deltas 350/354/255/505 = WAVES.md SUGGESTED predictions (164+186, 178+176,
   103+152, 231+274) to the chunk. Final state: reachable_chunks ==
   reachable_at_rev2 == 2,429 (zero rev-residue; the rev1 trap did not fire).
   Note: T-C41's "~1,853 SUGGESTED" includes 389 EXTERNAL_QUESTIONS chunks that
   a QP/MS-paper validate-all does not touch (card-doc surface) — reconciled.
4. **Bench structural note (snapshot truth):** the snapshot carries no exam
   sessions, so the loader emits one paper row PER DOCUMENT (40 rows for
   4CH1/2C etc.). On production, expect ONE row per code+session with both QP
   and MS document ids — fewer validate-all calls, same SQL, same gates.

## The probe (rehearsal transport — frozen vectors, NOT the production gate)

Transport deviation (recorded): the kit's Path A makes one live
gemini-embedding-001 / RETRIEVAL_QUERY / 768 embedContent call. This rehearsal
bound the **frozen, SHA-pinned PRB vectors**
(`embed-bridge-v2/frozen/embeddings_probes.jsonl`, same transport semantics,
self-verified drift 3.4e-05 at pack build) into the pack's byte-identical
gate-2 SQL. Production transport parity for the gate record still requires the
operator's Path A run (or an explicit operator acceptance of the frozen-vector
equivalence).

Pack gate-2 SQL, `bench_replay` VALIDATED pool at embed_rev=2, post-wave pool
(n=2,429), pct with cosine > 0.50:

| probe | pct_above_050 | note |
|---|---:|---|
| **PRB-01 (canonical)** | **58.7%** | clears the mass gate in replay space |
| PRB-02 | 22.6% | sparse-topic region |
| PRB-03 | 53.8% | |
| PRB-04 | 61.2% | |
| PRB-05 | 27.6% | |
| PRB-06 | 43.2% | |
| PRB-07 | 69.2% | |
| PRB-08 | 30.3% | |
| PRB-09 | 19.7% | |
| PRB-10 | 78.8% | |
| (mean of 10) | 46.5% | wide spread — pool mass is query-dependent |

Honest reading: the binding rule is defined on the canonical probe, and in
replay space it passes (58.7% comfortably over half) — but the 10-probe spread
(19.7–78.8%) is a real finding for the calibration pack's "small-n" honesty
boundary: single-query pool-mass is fragile as a gate statistic. The
production probe (operator-run) remains the deciding record either way.

## Rehearsal environment (reproducibility)

- Postgres 17.11 + pgvector 0.8.6 (pgvector/pgvector:pg17 image layers, user-space,
  `scripts/pgstack_fetch.sh`); core @ origin/main 69365ff (V1→V56 Flyway, all applied)
- Corpus: snap-006 (4,181 chunks) + preload-r7 (artifact verify fail-closed PASS)
- App: syllabai-core-0.1.0-SNAPSHOT.jar on :8085, jwt-secret provision-only,
  campaign identity UNCLAIMED; TEACHER JWT minted locally (HS256, same claim
  shape as JwtService; uid = MD5-v3 of "bench-teacher|wave1-rehearsal")
- Loader source: `Wave1Load.java.record.txt` (compiles core test-scope)
- Driver: `scripts/wave1_rehearse.sh` (kit SQL verbatim, rowcount-gated)

## Production handoff (the operator-held run)

Wave-1 production execution and the gate-2 probe need exactly two
operator-held inputs: the **Neon `DATABASE_URL`** and a **TEACHER JWT** (plus
`GEMINI_API_KEY` only if running the kit's fresh-call Path A). The commands
are unchanged from the kit; this rehearsal is the recorded dry run. Suggested
order: probe first (one call + two SELECTs), then wave-1 units in kit order.
