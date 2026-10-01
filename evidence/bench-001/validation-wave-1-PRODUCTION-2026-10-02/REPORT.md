# Wave-1 PRODUCTION run + gate-2 probe — Neon `neondb` (2026-10-02, T-C41 ①/T-C42)

**Status: EXECUTED ON PRODUCTION under operator authorization** ("the production
probe + wave-1 run", with Neon API key, pilot-teacher password, Gemini key).
Teacher actions went through the real teacher surface (login 200 →
`POST /api/v1/teacher/content/exam-papers/{id}/validate-all`, roles=["TEACHER"],
account `pilot.teacher@syllabai-test.dev`); SQL went through the Neon serverless
HTTP endpoint on the recorded `console.neon.tech/api/v2`-obtained coordinates.
DB identity gate (AGENT.md rule 2, preflight-equivalent): PASS (`neondb`,
`T-C04-CAMPAIGN` identity row alive). No `force=true` anywhere; every kit stop
condition honored.

## Gate-2 probe (T-C42): **PASS — 59.5% of the VALIDATED pool above 0.50**

Production pool at embed_rev=2, n=2,935: total 2,935 · above_050 1,745 ·
**pct_above_050 59.5%**; histogram peak in the 0.50–0.55 bucket (1,361 chunks);
zero pool mass below 0.40. Transport: frozen SHA-pinned PRB-01 vector (the
sandbox's egress IP is geo-blocked by the Generative Language API — deviation
recorded; live Path A stays available to the operator). Full record + flip
decision (**LAND**): `../cosine-calibration-2026-10-01/ADDENDUM-2026-10-02-production-probe.md`.

## Wave-1 production result: the units are ALREADY fully validated

The snapshot-based wave-1 unlock prediction (T-C40 worklist on snap-006:
+1,464 SUGGESTED chunks across the four units) **no longer describes
production**: every unit's QP/MS documents with content are already VALIDATED
and serving. The wave-1 unlock was executed on production by earlier
teacher-surface work (recorded in WORKLOG: 09-14 app-validated batches, 09-26
T-C27 card wave, 09-28 n@ app activity, the three-lane marks-repair) — the
stale worklist prediction is hereby retired with evidence.

| unit | paper rows | already VALIDATED | validate-all calls made | live unlock | reachable_at_rev2 delta |
|---|---:|---:|---:|---:|---:|
| 4CH1/2C | 13 | 12 (+1 REJECTED empty shell) | 0 (nothing SUGGESTED) | 0 | 0 (expected 0) |
| 4CH0/2C | 16 | 16 | 0 (nothing SUGGESTED) | 0 | 0 (expected 0) |
| 4CH1/2CR | 10 | 10 | 0 (nothing SUGGESTED) | 0 | 0 (expected 0) |
| 4CH1/1C | 12 | 11 | **1** (`fd1bf331…`: HTTP 200, `versionsValidated: 0` — the paper's QP+MS were the only SUGGESTED docs on the whole paper axis, both 0-chunk placeholders) | 0 | 0 (expected 0) |

- Final serving funnel: `reachable_chunks == reachable_at_rev2 == 2,935`
  (**zero rev-residue** — production is fully re-stamped at rev2; the T-C23
  rev1 trap cannot fire; all four paired restamps rowcount 0 == prestate at_rev1 0).
- Baseline (pre-wave) == final: the run's teacher action was legitimate but
  funnel-neutral by construction (0-chunk documents).

## Findings (operator-facing)

1. **F-PROD-1 (governance, HIGH): 25 papers serve while carrying unresolved
   `REVIEW_REQUIRED` bridge findings** — 4CH0/1C ×7, 4CH0/1CR ×3, 4CH0/2C ×5,
   4CH0/2CR ×3, 4CH1/1C ×3, 4CH1/1CR ×2, 4CH1/2CR ×2. All 25 bridge
   REVIEW_REQUIRED papers in production are VALIDATED and serving. Per the
   wave kit's own doctrine, "forcing past unreviewed findings is how
   mis-validated content enters the serving pool" — these papers either
   pre-date the bridge gate or were validated with `force=true`. The bridge
   findings need item-by-item workbench review by the teacher.
2. **F-PROD-2 (kit defect, fixed here): the kit's poststate SQL resolves the
   curriculum scope with `order by created_at limit 1`**, which on production
   now lands on the ARCHIVED `IAL-CHEM-2018` version (6 curriculum_versions
   exist) and reports `reachable = 0` while 2,935 chunks serve. Current serving
   truth is `CurriculumScopeResolver.resolveActive` = exactly one
   `status='ACTIVE'` version. Corrected SQL ships in this pack
   (`poststate-2026-10-02.sql`); the committed kit
   (`bench/validation_wave_kit.py`, `evidence/bench-001/validation-waves-2026-10-01/poststate.sql`)
   should be regenerated/patched before the next wave.
3. **F-PROD-3 (worklist staleness): the T-C40 worklist is snapshot-derived and
   no longer predicts production state.** Wave-1's predicted 1,464-chunk unlock
   was already executed; the next validation wave must be composed from a FRESH
   snapshot re-freeze (or live probes), and its actionable surface is NOT the
   QP/MS paper axis: production SUGGESTED content lives in EXTERNAL_QUESTIONS
   (747 chunks), SYLLABUS (162), and QP/MS documents of unplaced ingest-era
   papers (QP 369 + MS 395, subjects NULL/DRAFT curriculum versions).
4. **F-PROD-4 (housekeeping): 4CH1/2C carries one REJECTED empty paper pair**
   (`7d40476f…`, 0 chunks, both docs REJECTED) — an ingest-era shell; consider
   archiving/removing it in a governed lane so paper counts per code stop
   conflating sessions.

## Corrected poststate SQL (F-PROD-2) — mirrors resolveActive exactly

See `poststate-2026-10-02.sql` in this pack: identical to the kit's poststate
except the two curriculum-version subselects pin
`where status = 'ACTIVE' order by created_at desc limit 1`, plus a driver-side
assert that exactly one ACTIVE version exists (ambiguous/zero scope ⇒ serving
refuses ⇒ the wave probe must refuse too).

## Environment / reproducibility

- Neon API via `console.neon.tech/api/v2` (org `org-withered-mud-59985156`,
  project `billowing-cherry-15418366`, branch `production`
  `br-muddy-bar-a5huwldd`, endpoint `ep-ancient-cake-a52e4kfd…`, db `neondb`,
  role `neondb_owner`); SQL executed over the Neon HTTP `/sql` transport
  (psql not installed in the sandbox; TCP 5432 verified open, HTTP path chosen).
- Render core `https://syllabai-core.onrender.com` (health 200; campaign
  identity last_seen 2026-10-01 19:01Z).
- Teacher JWT obtained from the real login surface; token never persisted in
  any tracked file (scripts hold credentials only in 0600 git-ignored files).
- Runner transcripts: `probe_prod_output.txt`, `wave1_prod_output.txt`;
  machine records: `probe_prod_result.json`, `wave1_production_log.json`.
