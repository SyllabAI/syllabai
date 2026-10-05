# T-C79 — V62/V63 PRODUCTION VERIFICATION (post-flight, the V61 pattern)

**Date:** 2026-10-05 · **Lane:** superz (main agent, zai session web-23eb7684-9eb6-4100-a2b3-22cfb322258b)
**Authority:** operator word trace `1a10ab67883fadad` ("V62/V63 production verification here is render key …") — discharging the T-C79 residue recorded as UNVERIFIED in Session 198 and re-scoped credential-gated in Session 200 ("every probe route is credential-gated").
**Scope:** read-only. Zero DB writes (driver-enforced `default_transaction_read_only=on` + readonly session), zero API mutations (one GET; the route's PUT/DELETE verbs untouched), zero code/corpus/records-content change. Secrets (Render key, DB credentials, JWT secret, the minted token) lived in memory only — never printed, never persisted; the evidence files were leak-scanned before commit.

## Target

core PR #81 (merged 2026-10-04T12:51:10Z as `113bcf9bf`, head `c814462`, base `bbc438e`) carries
`V62__exam_series_calendar.sql` (tables `exam_series` + `learner_course_enrolments`) and
`V63__exam_series_seed_pearson_2026_2027.sql` (5 fixed-UUID Pearson rows, every row https-cited +
`retrieved_at 2026-10-04`, not-yet-published series honestly absent per ADR-035).

## Method

1. Render API `GET /v1/services/srv-dagijie7bikc73bc0460/env-vars` (retry loop — the API intermittently
   returned 400/empty on this account during the session; env-vars and the one successful deploys call
   both captured). `SYLLABAI_DATABASE_URL` is jdbc-form (scheme-less after the `jdbc:postgresql://`
   strip) with the credentials in the separate `SYLLABAI_DATABASE_USERNAME` / `…_PASSWORD` vars —
   joined in-memory into a keyword DSN.
2. psycopg2 connection to `ep-ancient-cake-a52e4kfd-pooler.us-east-2.aws.neon.tech` (== the T-C54 pin)
   with `sslmode=require` (pooler requirement) and startup options limited to
   `-c default_transaction_read_only=on` (the pooler rejects `statement_timeout` in startup parameters —
   recorded as a Neon API delta, the session-options lesson's third entry).
3. 16 assertions (`v62_v63_prod_verify.py`, persisted; every failure aborts loud).
4. API surface: mint one HS256 JWT per the `JwtService` contract (`sub`/`jti`/`uid`, `ver` == the
   selected enabled STUDENT's `users.token_version`, `roles:["STUDENT"]`, TTL 10 min) and issue one
   `GET /api/v1/learners/me/exam-series` against `https://syllabai-core.onrender.com` (the G8/W2
   credcheck recipe; the V46 revocation anchor honored — the token only validates against a real
   enabled user row).

## Results — DB 16/16 PASS

| # | Check | Result |
|---|-------|--------|
| 1–2 | flyway V62 `exam series calendar` / V63 `exam series seed pearson 2026 2027` present, `success=true` | installed **2026-10-04 12:53:26.701601Z** / **12:53:28.965773Z** — ~2 min after the 12:51:10Z merge (auto-deploy apply) |
| 3 | flyway max version == 63 | max(version::numeric) = 63 (lexicographic `max()` on the varchar column is a trap — `'9' > '63'`; numeric cast used) |
| 4 | V62 tables exist | `exam_series`, `learner_course_enrolments` |
| 5 | `exam_series` columns == migration SQL (15 cols) | exact |
| 6 | `learner_course_enrolments` columns == migration SQL (6 cols) | exact |
| 7 | constraints `uq_exam_series` + `ck_exam_series_window` live | exact |
| 8 | `exam_series` row count == 5 | 5 |
| 9 | 5/5 seed rows **date-for-date** vs the V63 SQL (ids, windows, entry deadlines, results dates, published=true, estimated=false, retrieved 2026-10-04) | all 5 exact — the Session 194 Pearson retrieval record reproduces row-for-row |
| 10 | `learner_course_enrolments` readable | 0 rows (no learner has declared a target yet — the honest empty state) |
| 11 | documents census | **1023 / 0 SUGGESTED** (the act-(a) poststate, intact) |
| 12 | chunks | **4740 total / 4740 embedded / 4740 `gemini-embedding-001` / 4740 embed_rev=2** |
| 13 | exam_papers | **108 = 95 VALIDATED / 13 REJECTED** |
| 14 | content_review_audit | **2835** (2829 + the act-(a) 6, intact) |
| 15 | teacher_validation_events | **0** (untouched) |
| 16 | serving gate == 4,661 | **4,661 reproduced exactly** on the VALIDATED-doc leg (see recipe note) |

**Zero collateral:** the additive migrations touched nothing outside their two new tables — every
Session 196/200 pin re-read identical.

## Serving-gate recipe note (honest archaeology)

The 4,661 pin reproduces **uniquely** under the VALIDATED-doc leg (`chunks of documents with
validation_state='VALIDATED' AND embedding IS NOT NULL`). The ep-link leg alone — chunks of documents
referenced by VALIDATED `exam_papers` rows via `question_paper_document_id`/`mark_scheme_document_id`
(190 distinct docs) — recomputes **2,730** under this lane's join shape (informational, not a failure).
The W2/act-(a) receipts' arithmetic (4,593 → 4,661 at the ep batch; delta exactly 0 at the doc flips)
is consistent with the VALIDATED-doc recipe being the pin's carrier.

## API surface — 200, 5/5 series

`GET /api/v1/learners/me/exam-series` → **HTTP 200**, 5 rows, byte-consistent with `ExamSeriesView.from()`
(12 fields: id, board, qualification, seriesCode, label, windowStart/End, entryDeadline, resultsDate,
estimated, sourceUrl, retrievedAt). The response carries **no countdown fields by design** —
`daysToWindowStart`/`entryDeadlinePassed` are computed at read on the `CourseExamTargetView` surface
(ADR-031: derived is recomputed, never stored); the base picker view is the pure calendar. Route
confirmed protected (401 unauthenticated) and live (`/actuator/health` UP; cold-start required two
wake attempts — Render free-tier spin-down, recorded).

## Deploy chain

Render's deploys endpoint was flaky (400/empty on retries); the one successful call captured the
latest deploy: commit **`6cad6ef`** — the current core main HEAD (the T-C83 seam merge on top of
`113bcf9`). Combined with the flyway install timestamps (12:53:26/28Z, minutes after the merge), the
auto-deploy channel is proven live and current.

## Verdict

**T-C79's production residue is DISCHARGED**: V62/V63 applied in production, objects and seed data
byte-faithful to the migration SQL, zero collateral on every recorded pin, and the deployed app
serves the imported calendar end-to-end. Remaining on the card (unchanged, operator-owned): the
hub-side Vercel signed-in dashboard check (picker + countdown chip).

## Files

- `REPORT.md` — this report
- `v62_v63_prod_verify.json` — the 16 machine-readable check results
- `exam_series_api_probe.json` — the API response (public Pearson reference data; no tokens, no PII)
- `SHA256SUMS` — sums of the above
