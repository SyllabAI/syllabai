# Embedding Transport Invariant — frozen vectors vs production vectors

**Status:** BINDING (durable knowledge per `KNOWLEDGE_DURABILITY_POLICY.md` / `PROJECT_KNOWLEDGE_MAP.md` §7, §10).
**Named:** 2026-09-20 (`evidence/bench-001/embed-bridge-v2/CORRECTION.md`).
**Durable-ized:** 2026-10-01 (T-C40 ③c) — the 2026-10-01 RAG engine review (R5) listed the drift as "unexplained"; the root cause HAD been named in the pack, but below discoverability. This artifact closes the durability gap; the review's "nobody has named the cause" is thereby corrected to "the naming was not durable."

## The finding (VERIFIED)

Embeddings of **byte-identical chunk content** (300/300 SHA-verified) differ materially by API transport:

- CI artifact path: raw single `embedContent` REST calls (model `gemini-embedding-001`, `RETRIEVAL_DOCUMENT`, `outputDimensionality=768`)
- Production path: Spring AI `GoogleGenAiTextEmbeddingModel` **batched transport** (same model/taskType/dimensions)
- Result: per-chunk cosine artifact-vs-DB **min 0.8619 / mean 0.9083 / max 0.9467**, top-10 neighbor rank agreement **0.7907**, max abs component diff **8.91e-2** (float4 both sides)

A ~0.9 mean pairwise cosine between same-text embeddings is NOT float nondeterminism — it is a materially different effective request. **Transport (or a parameter the transport layers set differently) is not value-transparent for this embedding API.**

## Canonical substrates (unchanged)

1. **Chunk vectors:** the PRODUCTION DB vector set (`document_chunks`, `embed_rev = 2`) is the canonical eval substrate — `eval_report_dbvectors.json`, per the 2026-09-20 CORRECTION.
2. **Query vectors:** the frozen gold query vectors (`embed-backfill-snap-001`) remain canonical (G4: production semantics, reconciled against CI run-004-a-r3).

## Rules this imposes (binding on all lanes)

1. Any frozen vector artifact used for replay, gates, or regression baselines MUST be produced through the **production provider path** — or be explicitly marked `transport-variant` and never cited as serving truth.
2. Artifact-space numbers are never presented as serving-truth numbers; when both exist, the production-space number is the one the gate reads.
3. Any change on the embedding axis (model version bump, dimension change, provider swap, Spring AI upgrade that could alter request shape) requires a **paired re-verify** — re-embed a pinned sample through both old and new paths and diff (the V33 embed-rev discipline already models this; this rule extends it to transport-level changes).

## Mechanism status (OPEN, narrowed — the one honest remainder)

The API-level mechanism is not yet pinned. Candidates, in order of plausibility given the magnitude: different effective request payload between `batchEmbedContents` and single `embedContent` (field mapping differences in the batched shape), `outputDimensionality` handling differences (MRL truncation point), or an unset default (e.g. taskType fallback) applied on one path only. Float/quantization noise is EXCLUDED by magnitude.

**Decisive experiment (operator-run, ~30 min + a small embedding-quota spend):** re-embed a pinned 5-chunk sample through both transports with identical payloads, then vary ONE parameter at a time — batch vs single call; explicit vs default taskType; `outputDimensionality` present vs absent; `title` field present vs absent — recording per-configuration cosine against the production vector. The configuration whose flip reproduces the 0.9 cosine is the named mechanism; record the matrix beside this file.

## Why this is load-bearing

The T-C13 promotion discipline leans on replay determinism: recorded runs replay vectors from frozen artifacts while serving reads DB vectors. Unnamed, the drift is a silent skew between "what the gate measured" and "what learners get" (it already flipped gold probe FET-002 hit→miss, 1.0→0.0). Named and gated, it is a managed boundary.

**Evidence:** `evidence/bench-001/embed-bridge-v2/` (CORRECTION.md, eval_report.json, eval_report_dbvectors.json, SHA256SUMS); `bench/cosine_calibration.py` output pack `evidence/bench-001/cosine-calibration-2026-10-01/` (re-verified recorded top-3 from raw frozen vectors, 10/10 PASS; transfer downshift quantified at −0.024…−0.057 on hit cosines).
