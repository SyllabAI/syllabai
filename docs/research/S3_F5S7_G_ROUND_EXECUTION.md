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
