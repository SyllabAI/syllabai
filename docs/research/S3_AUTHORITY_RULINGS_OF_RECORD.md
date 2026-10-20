# Authority Rulings of Record — the S3 review queue (DP-1..8, PF-1/2, F.5 §7)

| Field | Value |
|---|---|
| Delivered by | Operator (the authority of record), chat `1148fa2b` |
| Operator trace | `1a1582488a8c61ed` |
| Date of record | 2026-10-20 |
| Disposition | 11/11 items ruled. Queue DISCHARGED of record. S4 unblocked in principle (§11 order), subject to the qualifications below. |
| Filed of record | This commit IS the of-record filing (operator word "fire", trace `1a15855d05e15889`, 2026-10-20). Delivery chain: ruled in-chat `1a1582488a8c61ed` → staged fp16 `a8ccee736aa8c75b` (SEPT #10, operator persistent-storage directive `1a1584044cc57b85`) → filed docs-only on records main. Verbatim operator text below this line. |

---

## Proposed rulings

| Decision | My answer | Rationale |
| -------- | --------- | --------- |
| F.5 §7   | Approve the six-step contract in principle, conditional on the data-path audit and explicit migration safeguards. | Canonical SpecificationPoints must be distinguishable and verifiable. The reported 565 mis-typed rows need a reviewed mapping and reconciliation plan before any mutation. Preserve the 12 chemistry practicals as `SUBTOPIC` as specified, subject to confirming their identities. |
| DP-1     | `SUPPORTED_SUCCESS`, with a separate reason code for retake blocked by prior answer exposure. | The student may have answered correctly, but the evidence does not establish independent success. Keep correctness and independence as distinct dimensions so the success is not erased or overstated. |
| DP-2     | No. | An exposure-blocked attempt must not qualify as the prior success required for transfer. Otherwise, transfer can inherit the very evidence defect the retake gate is meant to prevent. |
| DP-3     | Prefer a dedicated evidence-events table, unless the existing telemetry contract can guarantee equivalent semantics and constraints. | Learner evidence has identity, provenance, ordering, idempotency, correction, and retention requirements beyond generic telemetry. Reuse is acceptable only if it preserves those guarantees without overloading telemetry semantics. |
| DP-4     | Substantive rewrites mint a new question row. Never mutate a served question in place. | This preserves the historical meaning of attempts and makes retake identity auditable. The system still needs a governed rule for deciding whether a rewrite is substantively different. |
| DP-5     | Use the `experiments` entity, with an explicit, required delay value and recorded evaluation arm. | A linked experiment alone is insufficient if no actual delay value is recorded. The transfer gate should fail closed when the value is absent or invalid. Treat 24 hours and 7 days as candidate S9 arms, not accepted thresholds. |
| DP-6     | Propose retaining learner-personal evidence events for 24 months after the event, then deleting or irreversibly anonymizing them, subject to legal, safeguarding, and operational review. | This is a concrete starting policy, not a source-established requirement. The contract should define deletion, legal holds, audit needs, and how aggregate evaluation results survive event expiry. |
| DP-7     | Do not certify until every assistance-serving surface has been inventoried and tested. | Until coverage is verified, assistance must remain `UNKNOWN` where instrumentation is incomplete, and the classifier must fail closed. Absence of an event is not proof that no help was given. |
| DP-8     | Use `exam_papers` for the explicit transfer-designation flag, provided the transfer designation belongs to the authored assessment/question definition and not an individual delivery. | This keeps assessment intent with the canonical assessment artifact. If transfer status actually varies by assignment or delivery context, that belongs in `assignments` or a versioned assessment instance instead. |
| PF-1     | Hint- or solution-assisted correct attempts do not qualify as prior success for transfer. | Otherwise, the transfer claim could be based on success achieved with support rather than a previously demonstrated independent capability. Preserve assisted success as useful learning evidence, but do not let it satisfy an independent prior-success requirement. |
| PF-2     | Past help alone should not permanently block a retake of the same question. | The key distinction is between historical assistance and answer exposure. A hint may support learning without revealing the answer. However, assistance during the current attempt must be recorded, and answer exposure must continue to block an independence claim under F.1. |

## Important qualifications before implementation

- F.5 §7: My approval is for the proposed contract, not for immediate execution. First verify the 565-row census, the 12 exceptions, loader behavior, both seed paths, and the backfill's idempotency and rollback strategy. The canonical ID must be stable and unique; changing IDs must not orphan historical evidence.
- DP-3: A dedicated table is my preference, not a hard requirement. If telemetry is chosen, it must satisfy the same evidence-event contract: stable identity, provenance, idempotency, ordering, corrections, and retention.
- DP-6: The proposed 24-month period is a starting policy choice, not a verified legal requirement. The privacy/data-governance owner must approve it before implementation.
- DP-7: Certification requires a surface inventory and evidence that each relevant assistance pathway is instrumented. Until then, missing instrumentation remains `UNKNOWN`.
- PF-1: This is an explicit policy choice to resolve the recorded tension with the current classifier. The implementation must not silently be treated as already matching this recommendation.
