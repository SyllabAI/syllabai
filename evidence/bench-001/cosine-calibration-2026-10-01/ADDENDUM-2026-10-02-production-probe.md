# ADDENDUM 2026-10-02 — gate 2 production probe RECORDED (T-C42)

**Verdict: gate 2 PASS.** Both binding gates of this pack are now recorded PASS;
the flip decision is **LAND** (one-line constant change on a fresh branch off
core main, this pack as its evidence).

## The probe (pack gate-2 SQL, byte-identical, :qv bound)

- Date: 2026-10-02 (UTC), executor: superz main agent on operator authorization
  ("the production probe + wave-1 run"), Neon project `billowing-cherry-15418366`
  (branch `production`, db `neondb`), reached via the recorded control-plane
  quirk path (`console.neon.tech/api/v2`; `api.neon.tech` unresolvable).
- Database identity gate (core AGENT.md rule 2, preflight-equivalent): PASS —
  `current_database() = neondb`, `campaign_db_identity` row present
  (`T-C04-CAMPAIGN`, last_seen 2026-10-01 19:01Z, alive Render claimant).

### Transport deviation (recorded)

The executing sandbox's egress IP is **geo-blocked by the Generative Language
API** (`User location is not supported for the API use` on every
generativelanguage/aiplatform variant), so the kit's Path A live
`gemini-embedding-001` `embedContent` call could not originate there. This
record uses the **frozen, SHA-pinned PRB-01 vector**
(`embed-bridge-v2/frozen/embeddings_probes.jsonl`,
sha256 `74c78cde90009a358fbd47302edf61840f934238a485cccd2e9b05cfff2b5e7d`,
verified fail-closed against `embed-bridge-v2/SHA256SUMS`; production-transport
semantics, self-verified drift 3.4e-05 at pack build). The live Path A remains
available to the operator from any supported network location and would supersede
this record only if it disagreed — the SQL is unchanged either way.

## Result — production VALIDATED pool at embed_rev = 2 (n = 2,935)

| bucket | cosine range | count |
|---:|---|---:|
| 9  | [0.40, 0.45) | 46 |
| 10 | [0.45, 0.50) | 1,144 |
| 11 | [0.50, 0.55) | **1,361** |
| 12 | [0.55, 0.60) | 266 |
| 13 | [0.60, 0.65) | 80 |
| 14 | [0.65, 0.70) | 27 |
| 15 | [0.70, 0.75) | 10 |
| 16 | [0.75, 0.80) | 1 |

**Summary: total = 2,935 · above_050 = 1,745 · pct_above_050 = 59.5%**

- Pack binding rule: flip lands when the pool's relevance-bearing mass sits
  **above 0.50** — **59.5% clears the mass gate** (replay space measured 58.7%
  on n=2,429; production sits consistent, slightly higher, on the larger
  post-census pool).
- Distribution shape: dominant mass concentrated in buckets 10–12 straddling
  0.50, peak in 0.50–0.55; **no pool mass below 0.40** — corroborates the pack's
  finding that 0.15 is a no-op floor in serving space (100% of this pool clears
  0.15; indeed 100% clears 0.40).
- Honesty boundary carried from the pack: single canonical query (PRB-01); the
  bench 10-probe sweep (19.7–78.8%) showed single-query pool-mass is a fragile
  gate statistic — this record decides the flip per the pack's binding rule but
  does not dissolve that boundary.

## Flip decision

**LAND** — `MIN_COSINE 0.15 → 0.50` as the one-line constant change on a fresh
branch off core main (`t-c42-min-cosine-050-flip`), with this pack as evidence.
The staged replay branch `tc40-min-cosine-050` stays replay-only (its Run005C
loader pairing commit is bench tooling, not production code). Post-deploy watch
item: tutor retrieval refusal rate at the 0.50 floor (baseline refusal 27–31%
at the no-op 0.15 floor is expected to rise; that is the designed behavior).
