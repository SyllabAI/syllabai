# queue-v2 500 — THREE defect layers found, fixed, verified in production (2026-09-24)

The queue-v2 defect reported during the G-4 human round (SMART_MARKED 500)
had **three independent layers**. Each was found by probing, fixed with its
own regression, and the last one verified live in production the same day.

**Final production matrix (all verified 2026-09-24 ~15:45Z):**

| probe | pre-fix | post-fix |
|---|---|---|
| v2 PENDING (84 rows, 7 bank) | 500 (layer 1 era) → 200 (layer 1 fixed) | **200** |
| v2 SMART_MARKED (29 rows, all bank) | 500 | **200 — 29 items, 1 unfiled group** |
| v2 HUMAN_MARKED (72 rows) | 500 | **200 — 15 groups** |
| v2 OVERRIDDEN (243 rows incl. the G4 26) | 500 | **200 — 16 groups** |
| throughput | 500 (bank pending) | **200** |
| v1 `answers?state=…` | 200 | **200** (unchanged read path) |

Artifacts: `queuev2_diagnostic_20260924.json` (final matrix),
`queuev2_bisect_20260924.json` (the 29/29-detail-200 isolation probe),
`queuev2_discriminator_20260924.json` (in-queue pipeline census that ruled
1.0.0/1.2.0 run shapes in/out).

## Layer 1 — null examPaperId crash for question-bank answers (9530b37 + 1b3d85e)

Question-bank (SME) questions carry NO paper: `examPaperId` is null by design.
The nullable id flowed into (a) `examPapers.findAllById` (rejects null
elements) and (b) the group-sort tie-break's bare `compareTo`; `throughput()`
had a third instance. Fixed null-safe; regression tests added; deployed
2026-09-24 (free-tier lag ~2h; operator Render intel: no failed builds,
latest failure 2026-09-20). **Live verification:** PENDING renders its 7 bank
rows in the unfiled bucket + throughput 200 — both impossible pre-fix.
**CI archaeology bonus:** 02e98d2 closed the CI-red gap session-117 left
(check-run `build` success confirmed).

## Layer 2 — detached lazy answerId in the marked-state queue assembly (1da5e3d, merge 9438b2f)

After layer 1's deploy, every MARKED state still 500ed while PENDING worked.
Isolation: 29/29 per-answer detail endpoints 200ed (SAME 4-arg view incl.
breakdown) ⇒ per-row serialization clean; the only state-dependent ingredient
was **non-empty `latestSmart`/`latestHuman` maps**. With `open-in-view: false`
and no service transaction, the queue keys those maps by `run.answerId()` /
`mark.answerId()` — through the LAZY `Answer` `@ManyToOne` on DETACHED
entities → `LazyInitializationException`, exactly and only for marked states.
Fix: `@EntityGraph(attributePaths = {"answer"})` on both batched lookups (the
house pattern). Mock-based unit tests cannot see lazy loading; prior v2 IT
coverage was PENDING-only.

**Regression IT** (`MarkingQueueFlowIT.markedStateQueuesRenderMarks`): real
Postgres + real HTTP, provider-free (blank answers smart-mark
deterministically), pins all three marked-state queues rendering with
`latestSmartMark`/`latestHumanMark` attached, disjoint membership, newest-wins
on the OVERRIDDEN revision. CI also corrected one wrong assumption of mine:
OVERRIDDEN is **evidence-gated** (a revision of an evidence-emitted attempt),
not smart-then-human per se — pre-gate smart marks are provisional and fire no
evidence, so a fresh container's smart-then-human lands HUMAN_MARKED
(production showed the override shape because the gate was OPEN there).

## Layer 3 — immutable empty paper map NPE on all-bank queues (565336d)

Layer 2's deploy changed the matrix to: PENDING 200, HUMAN_MARKED 200,
OVERRIDDEN 200 (72/243 items, runs + marks attached — the EntityGraph
verified live), **SMART_MARKED alone still 500** with all 29 details 200ing.
Reason: SMART_MARKED was the ONLY state whose queue holds **zero paper rows**
→ `paperIds` empty → `papers = Map.of()` (immutable) → the unfiled group's
`papers.get(null)` → **NPE** (immutable maps reject null key queries —
verified on JDK 21). Every other state carries ≥1 paper row →
`Collectors.toMap` builds a HashMap → `get(null)` returns null → their
unfiled groups render. Layer 2 had MASKED layer 3: the lazy exception fired
earlier in the assembly; fixing it let execution reach the NPE.

Fix: the null `paperId` IS the unfiled group's identity — skip the lookup
(`paper == paperId == null ? null : papers.get(paperId)`). Sibling audit:
`throughput()`'s `Map.of()` branch is unreachable-when-queried;
`LearnerStateController`'s empty-titles map is only keyed by non-null node
ids. Regression: a ZERO-paper-row queue unit test (the mixed-queue test from
9530b37 exercised only the HashMap branch — which is why layer 3 survived its
own regression). CI green on `565336d`.

## Production acceptance

`queue-v2?state=SMART_MARKED` == 200 with the 29 bank answers in one unfiled
group — passed ~15:45Z after the 565336d deploy; full matrix above all green.

## Production census recorded along the way

- The G4 26 (the operator's blind-round answers) transitioned
  SMART_MARKED → **OVERRIDDEN** when the human marks recorded over the
  agent's: `latestHumanMark` = operator decisions, `latestSmartMark` = 1.2.0
  runs — the both-marks shape, intact for any future κ pairing.
- SMART_MARKED 29 = HNA 269a 13 + probe s113 6 + G4 Probe 10 (pipelines
  1.0.0/1.2.0/1.2.1 era probes); PENDING 84 across 7 learners.
- Small census anomaly noted for the core lane: the G4 q7|b part (re-marked
  1.2.1 in session-117 after the budget fix) reads as pipeline 1.2.0 in the
  queue — worth one look at which run row is actually latest for that answer.
