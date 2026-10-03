# T-C74 — F-A1 recon (operator trace 1a10294d4523b921 "start the F-A1 recon")

## Verdict: F-A1 is CLOSED — executed 2026-10-02; this recon verified its landing first-hand (2026-10-03)

The lane was opened because a session summary listed "F-A1 orphan retirement" as still unexecuted.
Protocol ① (records-first) disproved that immediately: the ledger shows the F-A1 retirement was
APPLIED on 2026-10-02 under the operator's own mandate (trace 1a0fc4b91fc4c965 ②) — T-C62 retired
the one true orphan with a fail-closed divergence catch (T-C56's "0/18 ep-referenced" had used the
wrong join column; 16 of the 18 were ep-linked R-generations, NOT orphans), and T-C68 executed the
follow-up ruling (the 16 R-generations' governed source_uri relabel). The "ING-104 orphan cleanup"
is a different lane, closed 2026-10-01; the staged 499 chain likewise closed 2026-10-01 ("the 499
residue CLOSED"). The stale open-list is fully superseded; recon-first prevented a double execution.

## First-hand landing verification (2026-10-03, SELECT-only, all asserts green)

| Check | Result |
|---|---|
| Retired orphan `a7a0e028-ea16-4a31-a279-2a401a74142f` (doc `b09a8700…`, QUESTION_PAPER, 36pp) | validation_state = **REJECTED** |
| Its audit rows | original VALIDATE 08:30:33Z + the T-C62 retire **13:29:27Z** (batch `cae83ab6…`) |
| The 16 relabeled R-generations | source_uri exactly `4CH0-{1CR,2CR}-{2013,2014,2016,2017}06/{qp,ms}.pdf`, **16/16 VALIDATED** |
| Relabel audit rows in the 14:30–14:40Z window | **16** (batch `bf3485f8…`, 14:34:56Z) |
| ep topology: 8 `4CH0/1CR|2CR` rows, 16 doc links | **all VALIDATED** (the T-C56 mis-filed class is gone) |
| Serving gate (chunks under VALIDATED docs) | **4,593 — exactly the last pin** (zero drift) |
| content_review_audit total | **2,814 — exactly the T-C68 post-state** |
| Audit rows after the last batch (2026-10-02 14:35:57Z) | **0 — zero unaccounted writes** |
| exam_papers total | 104 (the value T-C62 observed landing concurrently) |

## Current live census (reference)

documents 871 VALIDATED + 146 REJECTED; chunks 4,672; qv 1,526; qsp 2,620; audit 2,814.

## What is ACTUALLY still open (per the ledger, verified against its tail)

- T-C72 seam phase 2 (rank-quality lane — another agent's, in progress)
- F-PROD-1 teacher-review packet — awaiting the operator's review
- DEEP-AUDIT-DOC coordination ask (the deep-audit 09-28 lane's findings document, committed nowhere)
- Operator standing items: secrets revocation (GH_PAT + RENDER_KEY), notes-axis promotion decision,
  AT_FLIP_RUNBOOK papers/schemes axis (if still wanted)
- F-A2: closed 3 of 3 today (T-C71 `15291f50c` + T-C73 `1f7e8355`) — no residue

## Files

- `fa1r_consolidated.json` — the asserted verification snapshot (9 checks)
- `fa1r_probe2.json` — gate/audit/activity probes
- `SHA256SUMS`
