# SME Corpus Import — Verification Record & Upload Runbook

**Package:** `s104-sme-import` (reconstructed 2026-09-19 after the session-105 sandbox loss)
**Decision basis:** ADR-026 (tracker `DECISIONS.md`), build lane T-C22, scope guard igcse-chemistry-19 only
**State as of 2026-09-19 (evening): ALL COMPLETE — the upload was executed this date via §3(b) + §4 Path B and verified end-to-end (see §9).** This document now serves as the audit record; §3–§5 are retained for re-runs/rollback.

---

## 0. Current state (what is already done, live-verified)

| Component | State | Evidence |
|---|---|---|
| Core `8b0c65c` merged → CI → deployed | DONE | `origin/main` = `8b0c65c`; Render `autoDeploy` applied it; live `/actuator/health` UP; deployed OpenAPI carries all new endpoints (`/api/v1/admin/question-bank/ingest|status`, `/api/v1/admin/revision-notes/ingest|status`, `/api/v1/learners/me/attempts/{id}/self-mark`) |
| Flyway V30 (SME question bank) + V31 (learner self-marks) | APPLIED | Flyway runs at boot on Render; the endpoints above exist only from V30/V31 code, and the deployed OpenAPI exposes them — the schema is live |
| Web `20c8f85` (practice tranche) deployed | DONE | Served bundle contains `QuestionMarkdown` (react-markdown + remark-gfm + remark-math + rehype-katex + rehype-raw), "Help with this question", "Submit for marking", "Failed to record the self-mark" |
| Corpus packages built + verified | DONE | Release `sme-corpus-2026-09-18` on SyllabAI/syllabai-web; digests re-verified this session (§1) |
| Multipart size limits | VERIFIED ADEQUATE | Deployed build sets `spring.servlet.multipart.max-file-size=64MB / max-request-size=64MB` — both packages (27.9 / 14.0 MB) fit (an earlier "1 MB default" concern was checked and refuted against the deployed config) |
| **Package upload** | **DONE — 2026-09-19** | Executed via §3(b) grant + §4 Path B (§9 has the full record): question bank committed 05:58:51Z (server-side ~8 min transaction; client read-timeout at 560 s — §8 poll pattern — then status flip to 593/228/365/1725/585); notes ingest returned `{topics:4, subtopics:28, notes:112, assets:194, replaced:true}` verbatim; post statuses + 20 read-only DB checks + learner smoke all green; ADMIN grant revoked, ops account disabled |

Frozen r3/t0 baseline: **untouched by everything above** (additive migrations + evidence-safe deactivation only; attempts, BKT evidence, and the 26-answer κ marking queue are data the ingest never deletes — see §7).

---

## 1. Packages (canonical bytes, digest-pinned)

Both files in this directory are the canonical release assets (SyllabAI/syllabai-web, release `sme-corpus-2026-09-18`), re-downloaded and re-verified 2026-09-19:

```
4bb53004f8b6f01369056b1b7097e65127d27c99e039bc6db28a437a891cabaa  sme-question-package.zip   (27.9 MB)
837ea8f2576a801064abde47299cc3482698832c9cb2f47b084fdfe75fe4dc05  sme-revision-notes-package.zip   (14.0 MB)
```

These digests match the values pinned in the committed upload script (`syllabai-web` `scripts/ops/s105_upload_packages.py`) — i.e. the bytes session-105 built and verified are exactly the bytes here. The deterministic builders survive on `syllabai-resources` branch `sme-import-session-104` (`s104_build_question_package.py`, `s104_build_note_package_v2.py`, `s104_verify_mapping.py`, `s104_fetch_corpora.py`).

---

## 2. Verification record (re-run from source, 2026-09-18/19)

**Gates A–D** (from the `sme-import-session-104` corpus source, via `s104_verify_mapping.py`):

- **A — EQ spec-point mapping:** 524 questions / 1,404 parts (228 MCQ / 1,176 structured) / 3,708 marks; **1,404/1,404 parts coded, zero codes outside the official 182-point 4CH1 registry**; 154/182 distinct codes referenced (28 unreferenced — honest coverage, not a defect); `spec_point_ids ↔ codes` consistent.
- **B — EQ structure:** MCQ exactly-one-correct: 0 violations; no-choices: 0; part-marks ≠ question-total: 0; difficulty labels {easy 153, medium 209, hard 162} all mapped (2/3/4).
- **C — Revision notes:** 112/112 pages coded, all in-registry; 0 unmapped; 112 unique `rn_*` ids; 155 distinct codes; 1,924 blocks / 179 figures.
- **D — Topic join:** all 28 KG subtopics reached; each SME topic's code distribution is plurality-placed to one subtopic with the rest as SECONDARY (the "SPLIT" lines are the expected cross-topic spread — the builder records them as secondary mappings, never guesses).

**Deterministic rebuild** (from the branch source): counts match the release exactly — questions 593 (228 MCQ / 365 structured) / 3,708 marks / 585 assets / 27.9 MB; notes 112 / 28 subtopics / 194 assets / 14.0 MB; union spec-map 209 HUMAN_VALIDATED (c10 legacy) + 1 SME-resolution. Byte-level digests differ from the release only by embedded timestamps (`generatedAt`); the release bytes remain canonical.

**Split rule** (recorded): single-part MCQ → `MCQ_SINGLE`; mixed/multi-MCQ questions → each MCQ part its own `MCQ_SINGLE` (`-pN` refs), structured parts one `STRUCTURED` (`-s` ref); 524 SME questions → 593 servable questions.

---

## 3. What you need (one ADMIN credential)

The ingest endpoints are role-gated (`/api/v1/admin/**` requires ADMIN). Pick one:

- **(a) You hold the `admin@syllabai.dev` credential** (rotated through your authorized path after the V20 sandbox loss) → use it directly.
- **(b) No ADMIN credential at hand** → promote an account you control via the Neon console (production branch — you hold these credentials; this is the same sanctioned DB path the teacher account used):

```sql
-- promote your account (e.g. the pilot teacher) to ADMIN
INSERT INTO user_roles (user_id, role)
SELECT id, 'ADMIN' FROM users WHERE LOWER(email) = '<your-email>'
ON CONFLICT DO NOTHING;

-- optional, after the upload: revoke
-- DELETE FROM user_roles u WHERE u.role='ADMIN'
--   AND u.user_id = (SELECT id FROM users WHERE LOWER(email)='<your-email>');
```

---

## 4. Path B — the upload (curl, ~5 minutes)

```bash
CORE=https://syllabai-core.onrender.com
PKG=/path/to/this/s104-sme-import-directory

# 1) fail-closed digest check
cd "$PKG" && sha256sum -c SHA256SUMS.txt

# 2) login (ADMIN) -> JWT
TOKEN=$(curl -s -X POST "$CORE/api/v1/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"<admin-email>","password":"<admin-password>"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["accessToken"])')
echo "token ok: ${TOKEN:0,12}"   # if empty, login failed — stop here

# 3) pre-upload status (200 expected; records the current live bank)
curl -s "$CORE/api/v1/admin/question-bank/status" -H "Authorization: Bearer $TOKEN"

# 4) upload the QUESTION package first (free tier: may take minutes — see §8)
curl -s -X POST "$CORE/api/v1/admin/question-bank/ingest" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sme-question-package.zip;type=application/zip"

# 5) then the NOTES package
curl -s -X POST "$CORE/api/v1/admin/revision-notes/ingest" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sme-revision-notes-package.zip;type=application/zip"

# 6) post-upload status
curl -s "$CORE/api/v1/admin/question-bank/status"  -H "Authorization: Bearer $TOKEN"
curl -s "$CORE/api/v1/admin/revision-notes/status" -H "Authorization: Bearer $TOKEN"
```

### Expected responses

Step 4 — question `IngestSummary` (values computed from the canonical package bytes):

```json
{ "questions": 593, "mcq": 228, "structured": 365, "parts": 1176, "options": 912,
  "markPoints": 1404, "specPointMappings": 1725, "topicMappings": 1161,
  "assets": 585, "deactivated": <current live bank size>, "corpusVersion": "sme-eq-igcse-chemistry-19" }
```

Step 5 — notes summary:

```json
{ "topics": 4, "subtopics": 28, "notes": 112, "assets": 194, "replaced": true }
```

Step 6 — statuses:

```json
// question-bank
{ "activeQuestions": 593, "activeMcq": 228, "activeStructured": 365,
  "specPointMappings": 1725, "assets": 585 }
// revision-notes
{ "ingested": true, "notes": 112, "assets": 194, "ingestedAt": "<now>",
  "corpusVersion": "sme-revision-notes-igcse-chemistry-19-2026-09-18" }
```

Any deviation → stop, capture the response body, see §8 (a rejected package leaves the live bank untouched).

---

## 5. Path A — alternative (re-dispatch the workflow)

If you prefer the already-staged automation: grant ADMIN to the account behind the `PILOT_TEACHER_EMAIL/PASSWORD` Actions secrets (same SQL as §3b), then GitHub → SyllabAI/syllabai-web → Actions → **sme-package-upload** → Run workflow. It re-verifies both digests, probes admin status, uploads both packages in order, and exports the result artifact (`s105-upload-result.json`). Revoke the ADMIN grant afterwards if it was temporary.

---

## 6. Post-upload verification (5 minutes, browser)

1. **Practice flow:** open https://syllabai-web.vercel.app → sign in as any learner → Practice → a 4CH1 topic (e.g. S1-c Atomic structure). Expected: SME questions render as formatted markdown (sub/superscripts like isotopes, KaTeX equations, diagrams); MCQs show the **four-button option grid** → answer → worked solution; structured questions show part inputs → **Submit for marking** → **reveal-and-self-mark**; the **Help with this question** panel joins specPointCodes to the revision notes.
2. **Freeze verification (r3/t0 baseline):** the pilot learner's attempt history is unchanged (deactivation never deletes rows); the 26 PENDING part answers remain in the teacher marking queue exactly as the s77 runbook expects — the κ sample is untouched (learner self-marks write to `learner_self_marks`, never `HumanMark`).
3. **Notes:** Revision Notes view shows the 4 sections / 28 topics / 112 notes with progress rings.

---

## 7. Safety & rollback

- **Single transaction per package, fail-closed:** wrong package version, duplicate externalRefs, unresolvable KG codes, MCQ without exactly-one-correct, part-marks mismatch, or dangling asset refs reject the **whole package** — the live bank is untouched on rejection.
- **Replace, never delete:** every active question is deactivated (rows survive); attempts, evidence, FK chains, the κ queue are untouched. Re-running either upload is idempotent-by-replace.
- **Rollback:** to undo the SME bank, re-ingest a prior package (ZIP path) or re-run the campaign import (release `t-031-prod-ingestion`); the pre-SME rows are still present, deactivated.

## 8. Known operational notes (free tier, honest)

- First request may cold-start (~2–3 min). The 27.9 MB question ingest (593 questions + 1,725 mappings + 585 binary assets in one transaction) can take **several minutes on 0.1 CPU** — do not kill it mid-flight.
- If curl times out client-side, **poll the status endpoint before retrying** — the ingest is transactional (committed or not, never half-applied), and a retry is safe-by-replace regardless.
- Memory: the ingest holds the package in memory (~28 MB compressed + parsed structures) on a 512 MB JVM. If the service restarts mid-upload (OOM visible in Render logs), a retry on a warm instance usually clears it; the transaction guarantees no partial state.
- The κ-grade marking (F-161) continues to run on teacher judgment only — SME `solutionMd` feeds the reveal/self-mark flows, not the κ sample.

---

## 9. EXECUTION RECORD — 2026-09-19 (the upload itself)

**Authorization path (exactly §3(b), as designed):** the operator provided the Neon API key this date. Non-destructive discovery (API `reveal_password` — returns the *current* stored password, nothing reset) gave the production-branch DSN; a dedicated ops account `s105.upload.ops@syllabai-test.dev` was registered through the **public register API** (app-side BCrypt, STUDENT role), promoted with the exact §3(b) `INSERT INTO user_roles … 'ADMIN'` SQL via the Neon production branch (`br-muddy-bar-a5huwldd`), logged in again (roles embed in the JWT), and used for the two ingests. Afterwards the §3(b) revoke was executed (`DELETE … role='ADMIN'`, 1 row) and the account disabled (`enabled=false`); it retains only STUDENT and wrote zero attempts/answers/self-marks. Credentials live only in sandbox 0600 files, never in git.

**Question package ingest:** client read-timeout at 560 s (free-tier 0.1 CPU — §8 anticipated this); per §8 the status endpoint was polled, and the bank flipped at **05:58:51Z** (server-side transaction ≈ 8 min). The response body was lost to the timeout, so the expected IngestSummary (§4) was instead verified **field-by-field against the committed state** via read-only DB queries — all 11 fields exact:

```
questions 593 (MCQ_SINGLE 228 / STRUCTURED 365, all active)
deactivated 854 (the entire prior bank, rows preserved inactive; total questions 854→1447)
parts 1176 · options 912 · markPoints 1404 (1176 part-attached + 228 MCQ scheme-attached)
topicMappings 1161 (primary_topic_node_id set on 593 + 568 secondary question_topics rows)
specPointMappings 1725 (question_spec_points, all on active) · assets 585 (question_asset)
external refs sme-eq-* (e.g. sme-eq-1-5-…-q2) · provenance PAST_PAPER × 593
```

**Notes package ingest:** completed inside the client window; response captured verbatim — `{"topics":4, "subtopics":28, "notes":112, "assets":194, "replaced":true}`. All 112 `revision_note` rows carry `corpus_version = sme-revision-notes-igcse-chemistry-19-2026-09-18`; `revision_note_viewed` stayed **5 → 5** (the SME re-scrape preserves `rn_*` ids, so learner view history survived the replace intact).

**Post-upload statuses (verbatim):** question-bank `{activeQuestions:593, activeMcq:228, activeStructured:365, specPointMappings:1725, assets:585}`; revision-notes `{ingested:true, notes:112, assets:194, ingestedAt:2026-09-19T06:01:36Z, corpusVersion:sme-revision-notes-igcse-chemistry-19-2026-09-18}`.

**Freeze verification (r3/t0):** full table-count sweep pre-vs-post — the only deltas are the ingest footprint (questions/-versions/-parts/-options/mark_points/mark_schemes/question_topics/question_spec_points/question_asset/revision_note/revision_note_asset) and the sanctioned ops-account rows (since reverted to STUDENT+disabled). `attempts 109`, `answers {OVERRIDDEN 217, HUMAN_MARKED 72, PENDING 77}`, `human_marks 289`, `learner_self_marks 0`, evidence/BKT tables — all byte-identical. The 26-answer κ queue is untouched.

**Learner-side smoke (read-only, pilot.learner01):** topic *Chemical formulae, equations and calculations* now serves 164 SME questions; question detail carries the V30 `specPointCodes` (e.g. `4CH1-1.26`) + markdown stems (`MgCO<sub>3</sub>·2H<sub>2</sub>O`); `/api/v1/learners/me/revision-notes` serves the SME corpusVersion with rn_* ids. The §6 browser pass remains available as an operator sanity check.

**Operational notes for the record:** (i) the question ingest genuinely takes ~8 minutes server-side on the 0.1-CPU free tier — expect a client timeout and poll (§8); (ii) Neon `reveal_password` is read-only and nothing was reset, but the operator may rotate the Neon role password or the API key if the channel that shared it is considered sensitive; (iii) `admin@syllabai.dev` exists and is enabled but its password remains lost — the same Neon path can rotate its hash (BCrypt) if the operator wants the original account back; otherwise re-enabling `s105.upload.ops@syllabai-test.dev` (Neon, `enabled=true` + §3(b) grant) reproduces a working admin path at any time.
