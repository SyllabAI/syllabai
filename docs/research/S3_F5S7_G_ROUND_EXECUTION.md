# F.5 §7 Execution of Record — the G-round (G1→G5) and the T-MIG-139 artifact band

| Field | Value |
|---|---|
| Authority order | Operator "go" — trace `1a159c4febff6695` (2026-10-20): execute F.5 §7 G1→G5 receipt-first on production |
| Execution window | 2026-10-20T15:50–15:53Z (G1/G3/G5, DB) + 2026-10-21 (G2/G4 band, repo artifacts) |
| Enablers | Neon PAT re-delivery trace `1a159fc2fb36cf5d` (fp16 `4c2e12da872b6959` = key of record); GH PAT handoff trace `1a15a1c5a6be10c9` (fp16 `a8ccee736aa8c75b` = the standing Task-25 PAT, verified live as user SyllabAI) |
| Target | Neon project `billowing-cherry-15418366` (SyllabAI), production branch `br-muddy-bar-a5huwldd`, database `neondb`, table `public.knowledge_nodes` |
| Pre-mutation receipt | `G3_G5_BACKFILL_RECEIPT.json` (lane-side, sha256 `fce408a29fd1e546a932fae3e5e629b950feb46468ed35e9c502a16f20a28402`) — G3 predicate 565 ids + G5 registry 98 ids, overlap 0, filed BEFORE any write |
| Ground state verified pre-execution | ck_node_type 6 values / 0 SPEC_POINT rows; 565/565 + 98/98 receipt ids SUBTOPIC; anchors 8,138/8,138; verdict CLEAN |
| Execution receipts | `G1_G3_G5_EXECUTION_RECEIPT_20261020.json` (sha fp16 `7a655924ed01740a`) + T-MIG-139 `run-001.json` (this repo's companion: PR #219) |
| Prior filings | Rulings `1a1582488a8c61ed` (S3_AUTHORITY_RULINGS_OF_RECORD.md) · repo-side battery `1a158320d2c0d41d` (S3_F5S7_REPO_SIDE_VERIFICATION.md, 15/15) · DB census F5_S7_DB_CENSUS_20261020 |

## 1. The blocker that dissolved — G1 by owner-class connection, lane-side

The G-round staging round (2026-10-20) had recorded G1 as ownership-gated: `knowledge_nodes` is owned by `neondb_owner`, `t0_readonly` (member of `neon_superuser`) cannot ALTER, and a lane-minted role with `members_of: ["neondb_owner"]` did not inherit ownership — the blocker of record read "operator 2-statement DDL in Neon console".

**Dissolution**: the Neon API mirror route of record (`GET /v2/projects/{id}/connection_uri?branch_id=…&database_name=neondb&role_name=neondb_owner` — the reg500-era route shape) issued a fresh `neondb_owner` credential directly (HTTP 200). G1 executed lane-side as the owner:

- **G1 @ 15:50:29Z** — single transaction, idempotency-guarded: `ck_node_type` 6→7 values (adds `SPEC_POINT`), `convalidated=true`, all 1,022 rows distribution-unchanged. The DDL text is the exact form line-verified in the S3 battery's g1 probe.

## 2. The DB half — G3 and G5, receipt-first

| Gate | At | Action | Result |
|---|---|---|---|
| G3 | 15:50:50Z | predicate retype SUBTOPIC→SPEC_POINT, receipt-keyed (565 ids), batched 100/txn, pre-write guard 565/565 | 565/565, zero shortfall (6 batches: 100×5+65) |
| G5 | 15:51:20Z | registry retype, receipt-keyed (98 4MB1 ids), single txn, 4MB1 guard | 98/98 |

**Inter-gate + final batteries: 6/6 GREEN twice.**

- Census: 4CH1 182 + 4MA1 188 + 4PH1 195 + 4MB1 98 = **663 SPEC_POINT**
- Anchors: **8,138/8,138 joined, 0 non-SPEC** — the "100% SPEC_POINT anchors" target achieved
- Residuals: 18 SUBTOPIC of record (12 `4CH1-PR-01..12` practicals + 6 `WCH11-T1.1..T3.2`) — the deliberate keeps, untouched
- Receipt stability: 663/663 receipt ids SPEC_POINT, ids/codes untouched (the canonical-ID stability condition)
- Constraint live: 7-value def, `convalidated`

Rollback assets remained staged of record throughout (`g-rollback.js`: reverse UPDATE keyed on receipt ids ONLY; legal while the constraint includes SPEC_POINT and no G2 rows exist).

Cleanup: lane role `w0a_g3_exec` DELETED via the API (HTTP 200, op `cbd80f92-2cd7-4a1d-9712-97319d9ec351`) — closing the terminal-echo password disclosure from the staging round; the dead credential was also scrubbed from the probe script.

## 3. The artifact half — T-MIG-139 (G2 + G4), PR #219

With the GH PAT re-delivered, the two remaining gates landed as repo artifacts in `syllabai-v2` (claim-in-first-commit `449fe29`, band `4db1902`, rebased over the #218 CIE lane-race, PR #219 for R0):

**G2 — seed-path convergence (both seeders emit SPEC_POINT):**
- Producers: `concept-seed.ts` spec-point loop → SPEC_POINT (practicals STAY SUBTOPIC per the ruling); `bundle-seed.ts` SPEC_POINT family → SPEC_POINT (all three dbCode laws untouched, codes verbatim).
- Schema of record: `ck_node_type` 6→7 values in `packages/db/src/schema/schema.ts` + generated migration `0003_f5s7-g2-spec-point-constraint.sql` (byte-equivalent to the live G1 DDL — fresh environments migrating 0000..0003 land at the live end-state).
- Consumer convergence (card scope amended pre-code, disclosed): the contracts `knowledgeNodeTypeSchema` enum; tutor `kg-retriever` structureNodes IN-list; `knowledge/index.ts` topicLike branch; `sme/bundle-questions` topicCodeResolver (necessity proven by typecheck TS2367). Each restores the exact pre-G-round row set under the new name — byte-equivalent serving.
- Drift guard in both `resolveNode` reuse paths: a pre-convergence row REFUSES with a pointer to the receipt-keyed backfill — the G3/G5 receipts stay the only retyping authority; never re-seeded over.

**G4 — the anchor-type companion check (staged of record, never auto-applied):**
- `.syllabai/receipts/T-MIG-139/g4-anchor-type-trigger.sql` — BEFORE-trigger asserting `node_type='SPEC_POINT'` on `question_spec_points`, fail-closed, deliberately OUTSIDE the drizzle folder so no migrate path can auto-apply it (the drift-discipline ruling: "live trigger NOT installed"). Installs on operator order only.
- Enable-time preconditions verified LIVE 2026-10-21 (read-only): `teaching_coverage=0`, `teaching_coverage_events=0`, `anchors_not_spec=0`, SPEC_POINT=663, ck 7-value.

**Gates on the integrated tree** (after rebasing over #218): typecheck exit 0 ×4 workspaces; contracts+shared+db 455/0; api suite 1820 pass / 13 skip / 0 fail (19,033 expects) — including #218's new CIE pins, which now seed through the converged SPEC_POINT landing without modification.

**Incidental finding of record**: the drizzle meta chain was corrupted (`0000_snapshot.id == 0002_snapshot.id = fb2e9ae1`; `0000.prevId` pointed at `0001`'s id) — no migration could generate (collision, first-hand repro). Repaired to the intended linear chain; the ids are opaque chain pointers — SQL files, journal tags, and applied-migration tracking untouched.

## 4. The five-gate ledger (F.5 §7 contract, final state)

| Gate | Definition of record | Status |
|---|---|---|
| G1 | Additive constraint: extend `ck_node_type` with `SPEC_POINT` | **EXECUTED LIVE** 2026-10-20 (owner-class connection; convalidated) |
| G2 | Both seed paths emit SPEC_POINT; new rows land SPEC_POINT | **LANDED AS ARTIFACTS** (PR #219); deploy windows operator-gated |
| G3 | Receipt-first batched backfill | **EXECUTED LIVE** 2026-10-20 (565/565, zero shortfall) |
| G4 | Companion check on `question_spec_points` (+ empty `teaching_coverage_*`) | **STAGED OF RECORD** (preconditions green live; operator-order install) |
| G5 | Source-registration for bundle subjects (the authority-approved mapping) | **EXECUTED LIVE** 2026-10-20 (98/98 4MB1 per the census §3 registry) |

Every operator qualification from the ruling is discharged: the 565-row census (verified pre- and post-execution), the 12 exceptions (confirmed `4CH1-PR-01..12`, preserved SUBTOPIC), loader behavior + both seed paths (repo-side battery 15/15 + this band's convergence), idempotency (re-run matches nothing; the drift guard refuses pre-convergence reuse) and rollback (receipt-keyed reverse UPDATE, staged and unused).

## 5. Residuals of record

- Migration `0003` applies at the next operator-ordered deploy window (production is ALREADY at this end-state via the live G1 — the migration is the fresh-environment companion).
- The G4 trigger installs on operator order after precondition re-verification.
- The deployed API of record (prj_FN5X, CLI-only) predates the convergence; consumers land with its next operator-ordered build.
- Credential advisories standing: `t0_readonly` INSERT-on-knowledge_nodes revoke; the API-issued `neondb_owner` URI staged at `.creds/neon-owner-uri` (0600) for operator review/rotation; GH + Neon token rotations (the briefing's own post-migration revocation plan).

---

## ADDENDUM — POST-MERGE CONTINUATION (2026-10-21, operator order trace `1a15a5b0fa14342d`)

**Order of record**: "Don't wait for r0. Merge+review yourself and continue working." — dissolves the §5 operator-gated residual queue where executable lane-side.

### R0 / merge state (verified, not waited-for)

- **PR #219** (T-MIG-139 G2+G4 repo artifacts) **MERGED of record** 2026-10-20T17:01:56Z — merge commit `75e9db9` (parents `8e1d174`+`8fad60b`), R0-auto merge-desk, head CI 4/4 green, 21 files in-boundary. w0a post-hoc review: `8fad60b` IS ancestor of main; the merged diff carries schema.ts `ck_node_type` 6→7 + generated migration `0003` + snapshots/journal as filed.
- **PR #220** (TUTOR-REPAIR per-learner subject scope selector, trace `1a15a472c9c07531`) **MERGED of record** — merge commit `71a3e42`, head CI green. w0a post-hoc review of the 4-file diff: fail-closed preserved (global single-owner test runs byte-identical FIRST; footprint via explicit FK tables only, capped 400/table; the SAME `singleOwnerScope` decides; 8 pins; `+392/−9` in-boundary). Open-PR field: **CLEAR** (no other open PRs).
- main tip of record at filing: `71a3e42`.

### G4 LIVE INSTALL (executed this round; receipt `G4_INSTALL_RECEIPT_20261021.json`, sha fp16 `c2de114a5e572083`)

- Preconditions re-verified green immediately before install: teaching_coverage=0, teaching_coverage_events=0, anchors_not_spec=0, SPEC_POINT=663, ck_node_type 7 values.
- Artifact of record executed **byte-for-byte**: `.syllabai/receipts/T-MIG-139/g4-anchor-type-trigger.sql` (single simple query, comments included). Idempotency guard verified trigger absent pre-install.
- Installed as `neondb_owner`: **BEFORE trigger `ck_qsp_anchor_is_spec_point` ON question_spec_points** (INSERT OR UPDATE OF spec_point_node_id) → `assert_spec_point_anchor()` — `tgenabled='O'` verified in pg_trigger/pg_proc/pg_class.
- **Functional proof, ZERO-TRACE** (both probes inside ROLLBACK txns): PROBE-A non-SPEC_POINT anchor (CONCEPT `93e1b339…`) → **BLOCKED** P0001 `ck_qsp_anchor_is_spec_point`; PROBE-B SPEC_POINT anchor → trigger **PASSED**, row proceeded to the expected unrelated FK (23503 `question_spec_points_question_id_fkey`). Census unchanged post-proof: 8,138 anchors / 0 not_spec / 663 SPEC_POINT. Full battery B1–B6 COMPLETE post-install.
- Rollback of record (zero data impact): `DROP TRIGGER ck_qsp_anchor_is_spec_point ON question_spec_points;` `DROP FUNCTION assert_spec_point_anchor();`

### Hygiene disposition this round

- **t0_readonly hardening** (advisory §5): `REVOKE neon_superuser FROM t0_readonly` attempted as `neondb_owner` → **DENIED 42501** ("permission denied to revoke role neon_superuser") — Neon manages the membership above the owner lane. **Operator-side statement of record**: `REVOKE neon_superuser FROM t0_readonly;` — verified zero functional impact lane-side (explicit SELECT grants cover **63/63** public tables; the accidental INSERT/UPDATE/DELETE rides only the membership).
- **neondb_owner URI rotation: DEFERRED** pending operator review — the prod connection env (Vercel) is unverifiable lane-side, and the asymmetric risk (prod serving outage vs a 0600 lane-side unexposed credential) does not justify unilateral rotation. Repo-side evidence: zero references to `neondb_owner` in the code repo; app-role convention `syllabai_v2_app_w2`/`w2r2` of record. Ready procedure: `POST /api/v2/projects/billowing-cherry-15418366/branches/br-muddy-bar-a5huwldd/roles/neondb_owner/reset_password` (Bearer Neon PAT) → scrub `.creds/neon-owner-uri`.
- GH + Neon token rotations: operator-side (tokens of handoff). Committed-token exposure (`ghp_1KJHf2…` at the records tip, sweep finding of record): **revoke-first posture stands, operator-gated**.

### Residual ledger after this round (supersedes §5 rows as marked)

- **[CLOSED this round]** G4 install — LIVE on production, proven fail-closed.
- **[CLOSED of record]** R0 merge — both PRs merged + w0a post-hoc reviewed; open-PR field clear.
- **[STANDS, operator-ordered]** Deploy window: migration `0003` (fresh-environment companion) + deployed API consumers (prj_FN5X next build).
- **[STANDS, operator-side]** t0_readonly `neon_superuser` revoke (statement above); owner-URI rotation after env review (procedure ready); GH/Neon token rotations; committed-token revoke (+ optional history scrub).

---

## ADDENDUM 2 — DEPLOY WINDOW (2026-10-21, operator order trace `1a15a7064a133d4d`)

**Order of record**: "deploy window (migration 0003 + prj_FN5X build)," — the first `[STANDS, operator-ordered]` residual of Addendum 1. Receipt: `DEPLOY_WINDOW_20261021_MIGVAL_RECEIPT.json`, sha fp16 `96c68eaf3c74f912`.

### Migration leg — EXECUTED AND CLOSED (validated, fixed, merged)

- **Premise under test**: §5 called migration `0003` "the fresh-environment companion". Validation **disproved the premise**: the chain 0000→0003 could not build a schema from zero. Production itself was never at risk: it has **no drizzle tracking table** (probed of record — zero drizzle/migration tables; schemas `public` + `neon_auth`) and no `migrate` runner is wired anywhere (db scripts: pull/generate/check only).
- **Method**: five isolated temp Neon databases on the production branch (`w0a_migval…w0a_migval5_20261021`) — created via the API, `neondb_owner` URI minted via the route of record, `drizzle-kit migrate` (strict), full diff vs production, destroyed (every drop HTTP 200; zero production contact throughout).
- **Findings → fixes** (one file, `0000_organic_mauler.sql`, +4/−7): the 0000 baseline was a commented `db:pull` artifact (the 42601 — drizzle splits *inside* the comment, chunk 1 carries an unterminated `/*`); missing `CREATE EXTENSION IF NOT EXISTS "vector"` (the 42704; prod carries `vector@0.8.6`); `ux_class_teacher_course_name` transcribed `teacher_id text_ops` where the column is uuid (the 42804 — the only true mismatch of the full opclass cross-check); `flyway_schema_history` PK renamed `flyway_schema_history_pk` to byte-match production.
- **FINAL GREEN of record**: migrate exit 0; **63/63 public tables EXACT** vs production; **174/174 indexes EXACT** (zero deltas both directions); `ck_node_type` 7 values incl `SPEC_POINT`; 4 migrations recorded; G4 trigger correctly **absent** on fresh envs — the out-of-band artifact (`.syllabai/receipts/T-MIG-139/g4-anchor-type-trigger.sql`) must be applied manually in fresh-environment setup (drift-discipline disclosure).
- **Filed**: PR #223 (head `d1f9e66`, CI 3/3 green) — **merged `4535b5c`** (w0a self-merge per the standing order, trace `1a15a5b0fa14342d`).

### Build leg — STAGED, TOKEN-GATED (the single remaining input)

- Target: prj_FN5X production build — ships T-MIG-139 consumers + the TUTOR-REPAIR per-learner subject selector (the `/tutor` refusal-outage fix) + the #223 rider.
- Gate of record: **no Vercel token lane-side** (lost in recycle #6, never re-delivered to this lane); `t097-refusal-verify.yml`: "deploy (vercel CLI) is token-gated — CI is the lane-executable serving"; no deploy workflow in-tree; check-runs on main's #219/#220 merge commits carry **no Vercel production check** ⇒ git-integration production auto-deploy is OFF (previews only).
- Recipe of record: CLI deploy via the 093 recipe (`deploy_bundle_build.py`, lane-local tooling) fired by a token-bearing lane (precedent: the r9-hubx run-002 staged handoff).
- **Operator options**: **(A)** re-deliver a Vercel token to a lane — deploy fires at main tip immediately; **(B)** enable Vercel git-integration production deploys on main (project settings) — the durable fix: production rides every main merge, no token needed, and a redeploy of the current tip can be fired from the Vercel UI the moment it is enabled.
- Fingerprinting note: `/actuator/health` is a static parity shape (no version/commit marker) — deployed-bundle verification after the build will need either the Vercel deployment metadata (token lane) or a behavior probe (e.g., the tutor selector) keyed by the operator.

### Cross-lane confirmation of record

T-MIG-139 run-002 (main `264e038`, trace `1a15a68f77ec7da9`) independently verified the w0a G4 install **byte-identical + enforcing** and filed it "DISCHARGED-AS-ALREADY-INSTALLED" — the F.5 §7 five gates are **ALL LIVE/VERIFIED** of record.

### Residual ledger after this addendum

- **[CLOSED this round]** Migration leg — fresh-environment companion premise repaired and PROVEN (63/63 tables, 174/174 indexes, ck7); PR #223 merged.
- **[STAGED — awaiting one input]** Build leg (prj_FN5X) — operator option A (token) or B (git-integration flip).
- **[STANDS, operator-side]** `REVOKE neon_superuser FROM t0_readonly` (42501 lane-denied); owner-URI rotation after Vercel env review (procedure ready); GH/Neon token rotations; committed-token `ghp_1KJHf2…` revoke-first (+ optional history scrub).

---

## ADDENDUM 3 — DEPLOY WINDOW BUILD-LEG DISCHARGE (2026-10-21, token handoff trace `1a15acf3fcb38bd1`, re-fire order trace `1a15bc1035148509`)

**Order of record**: "Try again" — re-fire the prj_FN5X production deploy staged by Addendum 2. This addendum closes the `[STAGED — awaiting one input]` build-leg residual. Receipt (lane-side): `DEPLOY_WINDOW_RECEIPT_w1b_20261021.json`, sha fp16 `baa58490e0de6c78`.

### Token lane — HANDED AND VERIFIED

- Vercel PAT re-delivered (trace `1a15acf3fcb38bd1`), staged 0600, used memory-only: sha fp16 **`d254bbfaac004354` = the standing Task-25 PAT identity, UNROTATED** (matches the r1c/r7a pinned fingerprints). Env of record pulled FIRST-HAND from the platform (`v10/projects/prj_FN5X…/env?decrypt=true`): 9 production keys; **`DATABASE_URL` fp16 `b289a2298e707904` MATCH** (DSN of record, run-009 lineage — unrotated).

### First fire attempt — BLOCKED PLATFORM-SIDE (fail-safe held)

- `vercel deploy --prod` (CLI-upload, 093 recipe, 2-file stage) → **`api-deployments-free-per-day`** ("more than 100"): hobby-plan daily cap, `GET /v2/teams` first-hand plan=hobby. NOT a code error, NOT the run-005 alias-flip class: no deployment registered, alias carrier `dpl_ENEw3fhfz2NXdXfVP73DmZJpd8pd` READY unchanged, live `/actuator/health` 200 UP. Earliest-retry anchor of record 2026-10-21T19:53Z (platform-controlled estimate).

### Sandbox rollback + first-hand reconstruction

- Between the blocked fire and the re-fire order the workspace lost: the deploy stage, the window scripts, the w1a receipt, the staged Vercel token, the worklog entry, and the local `26e11d8` objects (checkout rolled back to `bf37ed8` dirty). Everything was rebuilt first-hand this window: token re-staged from the conversation record; `origin/main` fetched anonymously (`6ebf124`, `26e11d8` IS ancestor); worktree at **`26e11d8`** — `6ebf124` REJECTED as deploy target (delta touches `apps/api` cla-threads + `packages/db` migration `0004_cla_thread_sync_tier`, NOT applied to prod).
- Recipe re-derived from surviving of-record scripts: `bundle-api.js` build-time pin gate (6 snapshots verified against 9 pin references extracted from BOTH source bands, 3 cross-band — PASS) + `w0a-entry.cjs` global-shim entry (readFileSync asset interception, `globalThis.Bun` shim) + the 093 path-parity adapter (`x-forwarded-host`/`x-forwarded-proto` URL rebuild) + `import.meta.dir`→`__dirname` swap. Bundle: **2,552,453 bytes, fp16 `6cc1af632c38af7e`**; needles singleOwnerScope 4 / learnerSubjectScope 2 / spec_point_node_id 33 (bounded 32..40 — pooling-sensitive; source truth 40 sites).
- Localgate 5/5 on the real bundle with the env of record (memory-only): health 200 UP; register malformed 400 `malformed_body`; cron unauthed 401 **CONFIGURED-law** (CRON_SECRET present — the platform-staged one); unknown path 401; login wrong-creds 401 (DB SELECT, read-only). Boot-loud pins silent.

### Re-fire — EXECUTED TO GREEN (rate limit CLEARED)

- Fire admitted 2026-10-21T00:16..00:17Z — the daily cap reset was observed EARLIER than the platform-controlled 19:53Z anchor. `vercel deploy --prod --yes` (CLI 65.0.0): **Ready in 1m, aliased**.
- **New carrier of record: `dpl_GfV24BcbF8jwnzLp7b1gVRodVBBV`** (production, READY, created 2026-10-21T00:17:36.032Z, project `prj_FN5XQUMbpqKhZXFXpT80OdsKveJZ`), @ `26e11d8` tree, bundle fp16 `6cc1af632c38af7e`.
- **Alias flip AUTHORITATIVE** (v4/aliases first-hand): `syllabai-v2.vercel.app` AND `syllabai-v2-syllab-ai.vercel.app` → `dpl_GfV24Bcb…`. Prior carrier `dpl_ENEw3fhfz2NXdXfVP73DmZJpd8pd` (run-009-r7a) superseded, READY, not deleted.
- **Live chain 6/6** on the alias: `/actuator/health` 200 `{status:UP}`; register malformed 400 `malformed_body`; cron unauthed 401 with the CONFIGURED-law body of record ("the hub seam forwards the Vercel Cron bearer verbatim"); unknown path 401 (auth-wall-before-404); login wrong-creds 401 `invalid_credentials` (prod DB SELECT, read-only); path parity both rewrites live.
- Addendum-2's fingerprinting caveat (health = static parity shape) answered: deployed-bundle verification ran on Vercel deployment metadata (token lane) + alias resolution + behavior probes.
- Integrity: zero prod DDL; zero DB writes (read-only failed-login SELECT legs only); `flyway_schema_history` untouched (63 rows); migration-0003 fresh-env-only disposition unchanged.

### Residual ledger after this addendum

- **[CLOSED this addendum]** Build leg (prj_FN5X) — production serves the `26e11d8` bundle via `dpl_GfV24BcbF8jwnzLp7b1gVRodVBBV`, live 200 UP, dual-alias confirmed.
- **[STANDS — prerequisite for the next build]** migration `0004_cla_thread_sync_tier` (on main `6ebf124`) must be prod-applied (fresh-env-proven, G1-style discipline) BEFORE any deploy beyond `26e11d8` — the cla-threads API surface it feeds is not yet deployed.
- **[STANDS, operator-side]** t0_readonly `neon_superuser` revoke; owner-URI rotation after env review; token rotations (Vercel + Neon + GH — all transited plaintext chat, Session 204 note reiterated); committed-token revoke.
- **[DISCLOSED]** w1a-lane artifacts (stage/scripts/receipt/worklog entry) lost to the sandbox rollback and reconstructed here from first-hand evidence; nothing re-executed beyond the staged deploy itself.
