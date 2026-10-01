# T-PS1 FLAG-REPAIR — 29 of 49 FLAGGED papers repaired & validated (2026-09-28)

**Authorization:** operator IM trace `1a0e97489503758d` "49 flags fixing" (extends the delegated-review mandate of trace `1a0e95af0892f059`; same honest provenance on all 693 audit rows — agent-performed, operator-delegated, NOT an in-app teacher session).

## Method

1. **Candidate mapping (Phase A):** every QP/MS document matching each FLAGGED paper's sitting fingerprint (code + yyyymm, orphan_map_v4 proven) pulled live with actual/embedded chunk counts. Result: 36 papers had chunk-ful candidates on both sides, 5 MS-only, 8 nothing.
2. **Content verification (Phase B):** a link is only swapped if the candidate's content is PROVEN to be this paper's: ALL qv stems attributed into the candidate chunks (12-token shingle or ≥0.85 token coverage, ≥80% required) + yyyymm fingerprint + SUGGESTED state. Bonus: the §D3 code-only docs (`4CH0-1C/qp.pdf` etc.) were session-identified BY CONTENT — four matched at 100% (7/7, 13/13, 10/10, 10/10).
3. **Diagnostics (Phase B2):** 12 June-sitting candidates failed attribution with difflib ratios 0.07–0.29 despite correct headers — genuinely divergent/partial content (likely CR-variant or partial extractions). Swapping those would attach mismatched print evidence. Refused.
4. **Apply (Phase C):** one fail-closed tx — 57 link swaps (PLACE audit rows with old→new doc + evidence), UNFLAG + VALIDATE per paper, VALIDATE children (278 qv + 242 schemes) and the 58 post-swap linked docs (all verified real chunks). Committed 19:39:03Z.
5. **Verify (Phase D, fresh connection):** census 70V/20F/1S/13R; all swap-targets VALIDATED with real chunks; swapped-away shells left unvalidated; the 20 remaining flags' children untouched; PLACE/UNFLAG/VALIDATE audit chain present; teacher_validation_events 0; post-swap G5 ≥80% on all 29 and G6 clean. **ALL PASS.**

## Outcomes

| Group | n | Disposition |
|---|---|---|
| Repaired & VALIDATED | **29 papers** (+278 qv +242 schemes +58 docs) | shell docs swapped for content-verified chunk-ful docs; full gate re-pass |
| Remains FLAGGED — divergent QP candidate | 12 | June sittings whose pdf-lane candidate covers <80% of the paper's questions (evidence: phaseB2_diag.json) — needs re-ingest or variant resolution |
| Remains FLAGGED — no content exists | 8 | all 4CH0 "CR" sittings 2013–2017: no chunk-ful QP/MS doc anywhere; re-ingest lane item |
| (from Task 58) supersession-deferred | 1 | 4CH1/2C Jan 2021, untouched |

Papers census: **70 VALIDATED / 20 FLAGGED / 1 SUGGESTED / 13 REJECTED**. Serving pool 1,118 → **2,020** (+902 rev2-embedded chunks on the newly validated docs).

## §D3 resolutions earned (content-identified)

| §D3 doc | uri | identified as |
|---|---|---|
| 4e469ae8 | 4CH0-1C/qp.pdf | 4CH0/1C January 2012 QP (7/7) |
| efd57f65 | 4CH0-1C/qp.pdf | 4CH0/1C June 2012 QP (13/13) |
| 1e6a27f5 | 4CH1-1C/qp.pdf | 4CH1/1C June 2024 QP (10/10) |
| f29edeea | 4CH1-1CR/qp.pdf | 4CH1/1CR June 2019 QP (10/10) |

Remaining §D3 docs still unassigned (40d34459 tried 0/7 for Jan-2012; 7d7c11c9, 6c9ae70c tried 1/7; others untried) — retire/map later.

## Files
phaseA_candidates.json · phaseB_verify.json · phaseB2_diag.json · phaseC_report.json (+ Task-58 pack in the parent folder). Scripts in agent workspace `scripts/psaxis_review/`.
