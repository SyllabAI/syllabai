> **ARCHIVED 2026-09-15.** Index stub for `docs/DATA_MODEL_ERD.md`; AGENT.md and `PROJECT_KNOWLEDGE_MAP.md` now point directly at `docs/DATA_MODEL_ERD.md`.

# SyllabAI ERD / EERD package

See `DATA_MODEL_ERD.md` for the detailed interpretation, current-vs-target boundary, and schema gaps.

## Diagrams

### Current ERD

The current ERD represents the relational model implemented by `syllabai-core` through migration V18. Dashed relationships represent logical/application-level references where the current SQL schema does not define an FK.

Source: `diagrams/erd_current.dot`

### Target EERD

The target EERD represents the canonical enhanced domain model. It includes subject enrollment, normalized board/qualification hierarchy, first-class specification points, resource specialization, question/specification mappings, and learner overlays. Target-only entities must not be treated as already implemented physical tables.

Source: `diagrams/eerd_target.dot`

## Rendering

The checked-in Graphviz sources can be rendered with:

```bash
dot -Tsvg diagrams/erd_current.dot -o diagrams/SyllabAI_ERD_Current.svg
dot -Tsvg diagrams/eerd_target.dot -o diagrams/SyllabAI_EERD_Target.svg
```
