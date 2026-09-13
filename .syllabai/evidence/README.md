# Durable evidence policy

A milestone is not considered GREEN merely because an agent reports a successful run.

## Required evidence for material milestones

- canonical repository commit(s)
- machine-readable state manifest
- relevant test/invariant results
- database row-count/schema manifest when a database is involved
- retained dump/hash when database state is part of the claim
- provenance/corpus commit when ingestion is involved
- release or other durable external export for recovery-critical evidence

## Claim discipline

`VERIFIED` — directly demonstrated and backed by retained/reproducible evidence.

`INFERRED` — supported by evidence but not directly demonstrated.

`REPORTED` — stated by another agent without surviving evidence.

`UNVERIFIED` — currently unsupported.

Do not promote REPORTED → VERIFIED merely because the report is detailed or internally plausible.

## Reproducibility

Proofs should be executable scripts or tests. Logs are supporting evidence, not the only evidence. If an environment can disappear on reset, any state that is not exported is non-canonical execution state.
