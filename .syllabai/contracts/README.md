# Cross-repository contract registry

Cross-repo interfaces are treated as contracts, not informal assumptions.

## Required contract families

- `parser-core/` — parser bundle schema, fixtures, version policy.
- `core-web/` — API/OpenAPI contracts and representative fixtures.
- `assessment/` — canonical Question/QuestionPart/evidence contracts.
- `knowledge/` — authoritative KG promotion/serialization contracts.

## Change protocol

1. Identify producer and consumer.
2. Classify the change as backward-compatible, coordinated, or breaking.
3. Update contract fixture/schema first when the contract itself changes.
4. Update producer and consumer in a coordinated change when required.
5. Run contract tests plus each repository's normal suite.
6. Record the contract version and evidence in the task packet.

A parser output field that core cannot consume is a failed contract, not a reason to silently ignore unknown educational data. Educational-content contract failures should remain fail-loud unless an explicit compatibility decision says otherwise.
