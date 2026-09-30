# The 0-hit serving anomaly — root cause, discriminating evidence, and the sanctioned first action

**Date:** 2026-09-25 · **Lane:** serving/embed (operator-directed: "dig into the 0-hit serving anomaly") · **Trace:** 1a0d88b65a04bb55
**Finding probe:** 2026-09-25, trace 1a0d8239e54492b5 (CI-green lane's SERVING PROBE): `GET /api/v1/teacher/content/documents/search` returns **200 with 0 hits** despite an embedded corpus (700 docs / 6,120 chunks, 0 pending) and VALIDATED papers.

---

## 1. The serving path (code anatomy, core @ `20d7ff1`)

```
GET /teacher/content/documents/search            ContentDocumentController:101
  → curriculumScopes.resolveActive(requesterId)  CurriculumScopeResolver:75
      owners = ACTIVE curriculum versions that own surface
      (KG: ≥1 VALIDATED UNIT/TOPIC/SUBTOPIC under a subject root
       OR papers: examPapers.existsBySubjectId — ANY validation state)
      owners != 1  →  Optional.empty()            (log: "scope unresolved … refusing")
  → .orElse(List.of())                            ← 0 hits WITHOUT any Gemini call
  → retrieval.search(query, kind, scope, limit)   ContentRetrievalService:42
      → embedding.embedQuery(query)               (Gemini; ONLY reached if scope resolved)
      → ChunkVectorRepository.searchServingEligible:139
          where  c.embedding is not null
            and  c.embed_rev = CURRENT_EMBED_REV   (= 2 since the 2026-09-20 cut-over, V33/Task 32)
            and  ( paper branch:    paper VALIDATED + paper.subject in scope
                 OR subject branch: chunk.subject_id in scope AND doc VALIDATED )
```

Both refusal sites return `200 + []` — the endpoint is silent about WHY it is empty.

## 2. Candidate causes (from the finding probe)

- **(a) Scope refusal** — `IAL-CHEM-2018` (ACTIVE stub `10000000-…-0001`, 11 KG nodes) gaining surface → owners=2 → resolver refuses.
- **(b) Chunk-level filters** — `embed_rev=2` read filter (V33) and/or the T-C20 VALIDATED-only predicate excluding everything.

## 3. Probes (all read-only; scripts in this directory)

### Probe 1 — curriculum surface + timing (`probe_serving_anomaly.py`)

- `/teacher/curriculum/versions`: `4CH1-2017` ACTIVE (`356840e6…`, 227 VALIDATED / 98 SUGGESTED / 4 UNVALIDATED); `IAL-CHEM-2018` ACTIVE (`10000000-…-0001`); 4 DRAFT ingest stubs (0/0/0).
- `/teacher/curriculum/versions/{ial}/nodes`: **11 nodes = 1 SUBJECT (VALIDATED) + 1 UNIT + 3 TOPIC + 6 SUBTOPIC (all UNVALIDATED)**. VALIDATED **structure** nodes (the resolver's `hasValidatedStructure` counts UNIT/TOPIC/SUBTOPIC only): **0** → IAL owns NO KG surface. (The SUBJECT node's VALIDATED status does not count — nodeType not in the resolver's structure set.)
- Review queue: 80 SUGGESTED papers across 3 subjects (`0f3cc8ba` 4CH1-titled ×19, `de18dcbb` 4CH0-titled ×7, `e56dc9ee` mixed ×54 incl. the VALIDATED practice papers).
- Timing: DB-only baseline (review-queue ×3) median **2,406 ms**; search ×3 → **9,043 / 4,747 / 4,503 ms**, all `200 hits=0`. Timing alone is NOT decisive (the resolver's per-node N+1 walk over ~340 nodes can also consume seconds), so probe 2/3 pin the SQL predicates directly.

### Probe 2 — corpus census + VALIDATED-paper documents (`probe_serving_anomaly2.py`)

Documents census (700 rows, 700 DISTINCT logical documentIds — zero multi-version sharing between generations):

| created | docs | chunks | generation |
|---|---|---|---|
| 2026-09-14 | 172 | 2,333 | **rev1** (glmocr legacy corpus; the resolver javadoc's "91 papers carrying all 2,333 chunks", DB-verified 09-17) |
| 2026-09-20 | 366 | 1,410 | **rev2** (corpus-v2 bridge) |
| 2026-09-21 | 76 | 1,033 | **rev2** |
| 2026-09-22 | 86 | 1,344 | **rev2** |

The v1 smart-marked queue now carries only question-bank rows (0 paper refs) — VALIDATED papers pinned instead via probe 3.

### Probe 3 — VALIDATED papers point at rev1 documents (`probe_serving_anomaly3.py`)

The four papers from the G-4 practice queue (all served through the always-VALIDATED-only question surface), each **`validationState=VALIDATED`**, every one pointing at **2026-09-14 documents (rev1)**:

| paper | state | QP / MS docs (createdAt) |
|---|---|---|
| 4CH1/2C Specimen 2017 (`23ef5e6e…`) | VALIDATED | `1dc68349…` / `e9cb4e28…` — **2026-09-14** |
| 4CH0/2C January 2018 (`2852f64f…`) | VALIDATED | `b7849fb8…` / `48500b4f…` — **2026-09-14** |
| 4CH0/2C January 2014 (`7f3ecd08…`) | VALIDATED | `0ebc841c…` / `edaf179c…` — **2026-09-14** |
| 4CH0/1C June 2011 (`fdccde9f…`) | VALIDATED | `476c5950…` / `144da9ac…` — **2026-09-14** |

Sessions 121–127 corroborate: every bank drive lands rows **SUGGESTED** ("all SUGGESTED, pdflane-atoms-draft-v1"); the only teacher-VALIDATED rows are glmocr-era (4ch1-2c-202101, 4ch1-2cr-202001, 4ch0-2c-201701) — all rev1. **Zero rev2-era content is VALIDATED.**

## 4. Root cause

**The serving-eligible intersection is EMPTY — cause (b), a rev-generation × validation-state gap; the scope resolver is NOT refusing:**

- The only VALIDATED papers point at **rev1** documents → excluded by `embed_rev = 2`.
- The entire **rev2** corpus (528 docs / 3,787 chunks, fully embedded) belongs to papers **born SUGGESTED** → excluded by the T-C20 VALIDATED-paper predicate (and corpus docs are born SUGGESTED per V29, so the subject branch is equally closed).
- IAL-CHEM-2018 (probe 1) owns nothing → the resolver resolves the 4CH1-2017 scope; no refusal is active.

**Why it appeared on 09-24:** T-C20's closure (`637502d`+`c8798d4`) switched `/search` from the neutral `search` (no VALIDATED predicate — it had been serving SUGGESTED rev2 bridge chunks, exactly the boundary gap T-C20 named) to `searchServingEligible`. The gate works as designed; the corpus pipeline simply has no content on the serving side of BOTH gates simultaneously. **Fail-closed correct, zero hits honest — not a serving bug.**

## 5. Sanctioned action executed — the operator's curriculum decision

Operator (trace 1a0d88b65a04bb55): *"we are not doing the ial chemistry for pilot 1. We moved to igcse chemistry."*

- `POST /teacher/curriculum/versions/10000000-0000-0000-0000-000000000001/archive` → **200**, status ACTIVE → **ARCHIVED** (the designed, reversible status surface; nothing deleted; the 11 KG nodes remain for audit). `archive_ial_version.py` (precheck = exactly-one ACTIVE row with the pinned id; postcheck = IAL ARCHIVED ∧ 4CH1-2017 ACTIVE).
- Production state after: `4CH1-2017` (Edexcel **IGCSE** Chemistry, 2017 spec) is the **sole ACTIVE curriculum version**; `IAL-CHEM-2018` archived. This also permanently removes the latent scope-refusal risk (any future VALIDATED node/paper under IAL would have flipped the resolver to refusal by design).
- Honest post-archive re-probe: search still **0 hits** — expected and correct; the archive was never the 0-hit fix (probe 1 proved IAL owns no surface).

## 6. Restoring serving — the operator's decision (registered as TODO T-C23)

Everything is already embedded; the moment a rev2-era paper is VALIDATED (and placed under a 4CH1-2017 subject), its chunks serve. Options, evidence-pinned:

- **A (recommended — the designed §7 path):** validate rev2-era papers via the review workflow (`POST /exam-papers/{id}/validate-all` per paper, or the workbench UI). Content-authority action → **operator-gated** (the validated-supersession packages from sessions 123/124 set the precedent: teacher sign-off, never agent assertion). Smallest honest batch: the placed 4CH1 papers whose QP/MS docs were created 09-20/21/22.
- **B (rollback lever):** flip `ChunkVectorRepository.CURRENT_EMBED_REV` back to 1 (the documented rollback posture) — instantly serves the VALIDATED rev1 corpus. Trade-off, stated honestly: rev1 retrieval measured **0/9 hit@10 vs rev2 9/9** on the frozen gold subset (eval gates that justified the cut-over); this knowingly serves the worse corpus and reverses the eval-gated direction. Only if availability outranks quality right now.
- **C:** stay 0-hit until R5 completes (validate rev2 + retire rev1) — the designed end state, no interim hits.

## 7. Core-lane ticket candidates (recorded, not implemented here)

1. **Serving-emptiness observability:** the search endpoint cannot distinguish "scope refused" / "rev-empty" / "validation-empty" from the outside (200 + [] for all three); this dig required three probes. A debug/ops signal (or an ops endpoint reporting per-gate counts) would make the serving state legible.
2. **`resolveActive` N+1:** per-search node walk (findSubtreeIds + findById per node, ~340 nodes across ACTIVE versions) plausibly costs seconds on free-tier infrastructure; batch the validation-status read.

## 8. Boundary discipline

Probes 1–3 read-only; the archive is the ONE production write, operator-decided verbatim, through the designed surface, pre/post-checked, non-destructive. No content validated, no embed_rev flip, no threshold/gate code touched, no credentials printed. Teacher credentials used for sanctioned teacher-surface reads/writes only (rotation still standing).
