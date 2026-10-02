# Refusal-rate watch — 2026-10-02 (T-C52; claim-first after two ID races lost — T-C49 to the ruling lane, T-C50 to the web-backport claim)

Authority: operator IM trace `1a0fb7a95cefc455` ("refusal-rate watch"); task record `.syllabai/tasks/T-C52.yaml` — the
T-C42/T-C43/T-C48 carried watch item: "watch the tutor retrieval refusal rate
at the 0.50 floor post-deploy (baseline 27–31% under the no-op 0.15 floor is
expected to rise — designed behavior)". Read-only lane; aggregates only; no
campaign writes; no core change (AGENT.md rules 1/2/6 untouched).

## Deploy boundary (when the 0.50 floor went live)

- Flip merge: core `5ef132b` (PR #44) at **2026-10-01T20:23Z**.
- First successful post-flip deploy: migrations V56/V57/V58 installed
  **2026-10-02T07:14:19–23Z** (read from `flyway_schema_history`); serving
  health-green at **07:16:30Z** per the concurrent ruling-v57-census lane's
  deploy record (`dep-davlig8ae00c73dmg5fg`; 5 crash-gated boot attempts
  05:09–06:52Z) — zero tutor asks between the two instants, so the watch
  windows are unaffected; the conservative lower edge is used as
  `WATCH_FLIP_AT`. Overnight deploys were crash-gated on the original
  V56 (restricted-roles GUC failure; unblocked by core `cd5288f`
  "V56 unblock — hnsw GUC pin tolerant of restricted roles (production deploy
  gate)"). The previous successful install was V55 at 2026-10-01T05:48Z, so
  production served the pre-flip build until the 07:14Z deploy.
- **Pre-flip window:** everything before `2026-10-02T07:14:19Z` (no-op 0.15
  floor). **Post-flip:** that instant onward (0.50 floor live).

## Instrument

Same store as the baseline: `telemetry_events`, event_type `KA_RAG_COMPLETED`
(the tutor pipeline's append-only research record; the audit's 77/287 = 26.8%
baseline was counted here, §10). D2 (audit tranche-1 rider) serializes the
refusal provider into the payload since **2026-09-27T20:07Z**, making the
class split measurable:

- `deterministic-refusal` — the **grounding gate** (empty evidence ⇒ refuse,
  no LLM). **The only class the MIN_COSINE floor can move.**
- `deterministic-paper-refusal` — the **fail-open guard** (parsed-but-unbound
  paper identity ⇒ evidence zeroed; `KaRagService` 502–517).
  **Floor-independent.**

Instrument: `bench/refusal_watch.py` (persisted, re-runnable; read-only
SELECTs; aggregates only — question text is never selected). This pack's
`refusal-watch.json` is the 2026-10-02 ~07:5xZ run.

## Findings (2026-10-02 run)

| Window | asks | refusals | rate | grounding-gate | paper-guard |
|---|---|---|---|---|---|
| PRE_FLIP_015 (all time) | 548 | 178 | **32.5%** | 0 (untagged rows pre-date D2) | 89 |
| POST_FLIP_050 (live 07:14:19Z) | **0** | **0** | — | — | — |
| Audit baseline (09-27) | 287 | 77 | 26.8% | n/a (pre-D2) | n/a |

- **Post-flip cell EMPTY: zero tutor asks since the flip went live.** The
  0.50 floor's learner-visible effect is not yet measurable. The instrument
  is persisted; re-run to fill the cell.
- **Refreshed pre-flip baseline: 32.5% cumulative** (178/548) — the audit's
  26.8% has drifted up. Recent daily band: 09-28 **22.0%**, 09-29 **28.6%**,
  09-30 **46.3%**, 10-01 **40.0%**, 10-02 (pre-flip hours) **42.9%**.
- **Class decomposition (the watch's key fact): since D2 tagging landed
  (09-27 20:07Z), 100% of tagged refusals (89/89) are
  `deterministic-paper-refusal`. Grounding-gate refusals = 0.** The recent
  40–46% days are paper-identity refusals — the fail-open guard zeroing
  pools on unbound paper identity — which the cosine floor cannot touch.
  This links the refusal rise to the F-PROD-3 surface (unplaced ingest-era
  QP/MS papers) and F-PROD-1 (unresolved bridge findings), not to any floor
  change.
- `zero_evidence == refusals == 178` exactly — every refusal had an empty
  evidence pool, consistent with deterministic refusal semantics (no LLM
  answer without evidence).
- Prompt mix (context): v2 192 / v5 176 / v6 172 / v3 7 / v4 1 — a v6 prompt
  exists post-audit (the audit's registry ended at v5).
- Corroboration (secondary): the per-learner §22 session store holds 17
  assistant turns / 0 refusals — tiny and not the baseline store; the
  telemetry record is the instrument of record.

## Reading (what to expect post-flip)

1. **The headline rate is NOT the floor's dial.** It moves with the
   paper-guard class (floor-independent, feeds F-PROD-1/F-PROD-3). A naive
   pre/post comparison of the headline rate will misattribute.
2. **The floor's effect shows in the grounding-gate class**, whose pre-flip
   baseline is exactly **0** (at the no-op 0.15 floor the gate structurally
   never fires — 100% of the corpus clears 0.15 per the calibration pack).
   Expected post-flip: non-zero grounding-gate refusals as ~40.5% of serving
   pool mass (gate-2 probe: 1,745/2,935 above 0.50) falls below the floor on
   floor-crossing asks.
3. **Watch gates (proposal):** re-run `bench/refusal_watch.py`; first
   decision-relevant read at ≥50 post-flip asks or 72 h, whichever first.
   Compare (a) grounding-gate refusal rate and (b) zero-evidence rate,
   pre/post; track paper-guard refusals as a separate trend line feeding
   F-PROD-1/F-PROD-3. No flip-back consideration is triggered by the
   paper-guard line — it cannot have been caused by the floor.

## Evidence labels (AGENT.md rule 4)

- VERIFIED (read-only production, this run): flyway tail (deploy boundary);
  548-row telemetry census; window split; class split; D2 tag lifetime
  (2026-09-27T20:07Z → 2026-10-02T00:04:45Z); zero post-flip volume.
- VERIFIED (record): audit baseline 77/287 (§10); D2 serialization design
  (TelemetryService payload keys); flip merge instant (PR #44).
- UNVERIFIED: post-flip refusal behavior (zero traffic — pending asks);
  Render deploy internals (boundary inferred from flyway installs + merge
  chronology, the audit's own method).
- REPORTED: the 09-27 39 untagged refusals (same-day pre-D2 rows, class
  unknown — likely paper-guard given every later tagged day is 100%
  paper-guard, but not provable).
