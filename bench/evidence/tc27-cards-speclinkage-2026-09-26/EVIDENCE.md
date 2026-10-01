# T-C27 evidence — question cards corpus + chunk→spec-code linkage (2026-09-26)

**Lane:** T-C27 (bank layer v2) — registered session 130 (`279d1cd`), executed 2026-09-26
by the Super Z lane (chat `54c94863-9377-41e2-923e-dd45fe835c1a`) under the operator's
item-① directive. Status at close: **EXECUTING (partially cashed — embeds blocked exogenously,
see §5).**

## 1. What landed (all fail-closed, derive-locked, one sanctioned lane)

### 1.1 Chunk→spec-code linkage (the controlled-taxonomy join)

- **Census first** (`prestate.json`): 449 QP/MS chunks (rev1 321+274, rev2 79+43 rev2-ep-scoped)
  resolve via `chunk → documents ↔ exam_papers varchar pointers → question (exam_paper_id +
  external_ref '#q<atom_number>')`; **0** carried spec mappings; EXTERNAL_NOTES 350/350 and
  SYLLABUS 162/162 already populated (prior lane, post-census).
- **AI-mapping pass** (the sme-eq import precedent: AI mappings land `AI_VALIDATED`):
  298 cardable `paperDir#qN` questions (327 total − 29 empty stems) mapped against the
  **182-code controlled taxonomy** (SUBTOPIC nodes, `4CH1-x.y[C]`) via batched LLM calls
  (glm-4-plus, 8 questions/call, 429-aware backoff). **295/298 carry 1–3 codes**
  (84 single, 211 multi), confidence min 0.80 / median 0.90, **144/182 distinct codes used**,
  3 honestly skipped (no confident mapping). `llm_mappings.jsonl` verbatim.
- **Landing** (one transaction, NULL→value only, idempotent):
  `question_spec_points` 1,725 → **2,359** (+634: 295 PRIMARY + 339 SECONDARY,
  provenance/validation = `AI_VALIDATED`, exact sme-eq field values);
  `document_chunks.spec_codes` 512 → **923** (+411 QP/MS chunks via the deterministic join);
  GIN containment verified (`spec_codes @> '["4CH1-1.1"]'`); 0 empty arrays;
  teacher-validation of the new qsp rows remains the owner queue (node statuses untouched;
  no content validation asserted).

### 1.2 Question cards corpus (per-bank-question)

- **Emitter** (`tc27_card_emitter.py`, deterministic): one canonical-1.0 draft per bank
  question (298; mirrors the `qcard-bridge` v1.0.0 family — `Q-Card | <code> | <Mon Year> |
  Q<n> | marks | type | spec: <codes> | stem: <hint≤200 chars>`), **token-subset of print**
  (hint = verbatim stem prefix; every text byte traces to stored print fields), series
  canonicalized JAN/JUN/NOV (V33 §8.1), `specCodes` carried in the retrieval block (295/298).
  Identity via the CanonicalIdentity recipe (`sha256:"sha256:<ck>|engine:tc27-card-bridge|
  version:1.0.0"` → version-5 uuid layout); 298 distinct checksums.
- **Drive** (`tc27_drive.py`, resumable, fail-closed): teacher-authed minted-JWT API drive —
  `POST /api/v1/teacher/content/documents?kind=EXTERNAL_QUESTIONS` → 201 ×**298** (1 dedup hit
  en route, no conflicts) → **298 documents / 298 chunks, all SUGGESTED, 0 embedded**
  (blocked, §5), retrieval identity stamped exactly (`kind EXTERNAL_QUESTIONS, embed_rev 1,
  series/year/paper_code/atom_number`, sample verified). DB totals: documents 701 → **999**,
  chunks 4,045 → **4,343** (+298 each). GIN spec-filter demo on cards: 12 chunks for
  `4CH1-2.16`.
- **Serving posture:** cards are SUGGESTED + un-embedded → the T-C20 gate structurally
  excludes them from serving; **no retrieval change shipped** (both retrieval repositories
  reference `spec_codes` zero times — verified by source grep).

## 2. §9 eval-gate record (honest)

- Plan §9 (via `ReciprocalRankFusion` javadoc + T-C26 row): unit gates pin the ordering;
  the T-C13 bench re-runs on the next corpus change. No core/parser code changed in this
  lane, and cards are serving-inert until validated + embedded, so **no retrieval change
  shipped today**; the recorded bench (snap-003 re-freeze + gold-v2 regeneration) remains
  **operator-held** per the snap-002 FREEZE_RECORD, and is owed at the serving flip.
- The A/B serving probe (`serving_probe_pre/post.json`) could not measure hit deltas:
  the search endpoint 500s pre AND post (identical failure both sides) — §5.

## 3. Out-of-scope findings recorded en route (no action taken)

- **Phantom June-2020 sitting rows**: `4CH1/2C June 2020` (ep `7d40476f…`, 7 q) and
  `4CH1/2CR June 2020` (ep `d3d7e0f2…`) carry pre-F10 v1 documents; the corpus has no
  `2020-06` session (F10 merged phantom 2020-06 → 2020-11; Nov-2020 2C landed in the bank
  wave as NEW). Same duplicate-sitting class the wave merged for Summer 2022 — candidate
  for an operator-sanctioned merge wave (2CR has no Nov-2020 bank row; 2C does).
- **10 dangling glmocr-era MS pointers** (ep rows whose mark_scheme_document_id matches no
  document): Summer 2013/2015/2016/2019 ×3, June 2014 ×2, January 2015, January 2020,
  Summer 2024 — pre-existing, outside this lane.

## 4. Blocker hit mid-lane (exogenous, recorded verbatim)

`gemini_403_denial.json`: the configured `SYLLABAI_EMBEDDING_GEMINI_API_KEY` returns
**HTTP 403 "Your project has been denied access. Please contact support."
(PERMISSION_DENIED)** from `generativelanguage.googleapis.com` (model gemini-embedding-001,
re-verified 2026-09-26). Consequences: every `/documents/search` → `embedQuery` → 500 on the
live build (deploy `1a644d5`, 11:29:53Z — pre-existing to this lane's probes; the T-C23
5/5-hit probe at 09-25 17:16Z predates the denial), and every `/documents/{id}/embed`
fails identically. This is a provider-account-level denial — **operator action required**
(new key/project); it also blocks the other lane's embed window (09-27).

## 5. Remaining to close T-C27 (the honest bar)

1. Re-run `tc27_drive.py` (resumable) — or the embed window job — to embed the 298 card
   chunks once the provider is restored (295 already carry spec codes; nothing else changes).
2. Operator: restore/replace the Gemini key (403 denial).
3. At the serving flip: snap-003 re-freeze + gold-v2 regeneration + the recorded T-C13 bench
   (operator-held per discipline), then `T-C27 → DONE`.
