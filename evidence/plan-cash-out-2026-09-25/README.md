# Plan Cash-Out — 2026-09-25 (session 130)

Operator directive: "I want the plan fully cashed out" — after the
plan-application audit (trace 1a0d9265b3190115) named the leftovers,
this session executed the cashable ones and re-verified the rest
against CURRENT origin (the audit snapshot was stale: T-C24 merged,
tc17-work bridge v1.2.0 merged to main).

## Executed this session

1. **Plan §7 per-kind RRF weights reach the serving fusion** — core
   `7803102` (core-ci SUCCESS run 36160128846). ReciprocalRankFusion is
   the canonical PLAN_V2_WEIGHTS home + fuseWithPlanWeights();
   KaRagService + ClaService serving fusion now weighted (KG anchors
   1.0, chunk kinds per plan §7); unweighted 1-arg fuse bit-identical.
   ServingPlanWeightsTest pins table/ordering/defaults/bit-identity.
2. **pdflane G5 card source fields** — parser `55166af` (parser-ci
   SUCCESS run 36161511189). Per-atom `summaryHint` (verbatim first stem
   sentence, <=200 chars) + `commandWord` populated via a faithful port
   of the Java CommandWordLexicon; parts carry their own command word;
   schema gains optional summaryHint (tag stays 1.1). Benchmark A
   (4CH0/1C Jan-2012): commandWord 0/11 -> 10/11, hints 11/11, products
   byte-identical to main modulo the new fields, validate_atoms V1-V5
   PASS, deterministic re-run.
3. **pdflane G6 vision routing** — same parser commit. SCANNED units
   emit deterministic vision pre-products (page renders + figure crops,
   _meta/vision/<unit>/) + SCANNED-VISION-PREP-EMITTED; transcription +
   freeze stay review-queue-gated (anti-role preserved); fail-safe
   degradation to the unwired escalation code.
4. **Spec-axis coverage report v1** (plan §2.1/decision #9) — read-only
   production census: 182 spec points, 170 (93.4%) carry >=1 serving
   question; 12 uncovered listed; 2 questions without spec codes; corpus
   by kind: QP 177 / MS 169 / SYLLABUS 162 / EXTERNAL_NOTES 112 /
   EXTERNAL_QUESTIONS 81. Files: syllabai-spec-coverage-2026-09-26.{md,json}
   (this dir) + /download/ copies.

## Re-verified against current origin (not executed here, with reasons)

- G3 (furniture) + G4 (alt-text): ALREADY APPLIED — bridge v1.2.0
  (tc17-work f0b6f81, now an ancestor of parser main) bundled them with
  group_key + retrieval block; 25->42 tests on that commit.
- G7 (authoritative source per paper): APPLIED for the bank (A1 from
  atoms).
- G8 (scale): substantially advanced (grammar rounds g12-g17, RC-C lane).
- Failsafe plan Phases 0-3: executed 09-18; Phase 4 integration executed
  via the v2 ingest; serving currently rolled back to rev1 by the
  operator's T-C23 Option B decision (d523f57) — deploy of d523f57 +
  7803102 still pending on Render at 16:45Z (probe: still 0 hits;
  operator dashboard check remains the resolving action).
- Textbook tier: P4 BY DESIGN (plan §13.3 licensing open).
- Chunk->spec-code linkage: BY DESIGN deferred to the controlled-taxonomy
  lane (bridge v1.2.0: "specCodes null by design (taxonomy joins on
  paperDir#qN)") — registered as T-C27 with the cash-out spec.
- Question cards corpus: registered as T-C27 (substrate complete: G5
  fields + CARD source mapping + 0.3 weight + corpus docs present;
  emission is an eval-gated ingest campaign).

## Lane discipline

- Fresh git fetch before work; T-C24/V39 lease verified RELEASED
  (origin/main 3c1600c) before touching core; T-C25 (web, other session)
  untouched; RC-C grammar lane untouched (their G2 residual on Jan-2012
  left exactly as found — gate signature identical pre/post my change).
- Read-only production surfaces for the census; no content validation
  asserted; no migrations; no secrets rotated; teacher creds used for
  sanctioned read surfaces only.
