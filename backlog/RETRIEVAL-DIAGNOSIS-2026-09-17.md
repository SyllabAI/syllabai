# SpecificationPoint-Aware Retrieval — Root-Cause Diagnosis and Data-Construction Requirements (T-C13/T-C14, 2026-09-17, Session 77)

**Commission:** the operator's Track-3 directive — resume T-C13/T-C14 with the
reframed question: *not* "can BM25 run?" (settled — it can), but **why is
SpecificationPoint-aware retrieval failing, and what evidence/data construction
is necessary before retrieval can be promoted?** With the stated hypothesis
that the zero HUMAN_VALIDATED chunk→SpecificationPoint mapping coverage is a
major confounder: KG-aware retrieval cannot be fairly evaluated if the corpus
lacks the authoritative mapping connecting retrieved evidence to
SpecificationPoints.

**Method:** a corpus+mapping audit and a retrieval evaluation harness over the
REAL corpus (112 SME notes → 732 heading-level chunks; the T-C10 store's 209
note-level HUMAN_VALIDATED mappings; the 182-point registry; the 4 C12
operator-ratified question mappings + the session-77 pilot's live tutor
question as real-query golds). Harness:
`scripts/s77/retrieval/{retrieval_audit.py,retrieval_eval.py}` (session-77
sandbox; deterministic, no LLM). Raw results:
`scripts/s77/out/{retrieval_audit.json,retrieval_eval.json}`.

---


## 0. Reconciliation with the concurrent lanes (recorded post-authoring)

This diagnosis was authored and measured in parallel with — and independently
of — the concurrent T-C13/T-C14 benchmark lane (sessions 86–95: gold-v1
frozen, snap-001, Run-001 B-proxy, Run-002 A0, run-003-b arm B, the arm-A
embed-backfill now executing at the Gemini free-tier daily quota wall, and
the landed `RetrievalProvider` fabric + `Bm25Retriever`/V28). The two
surfaces are complementary and consistent:

- **their lane** benchmarks the PAPER corpus (2,333 chunks) through the
  production fabric with a frozen gold set; **this diagnosis** audits the
  SME NOTES corpus (732 chunks) and the mapping-granularity structure —
  the notes are a different retrieval surface, not inside snap-001.
- their run-003-b honestly records the spec-resolution axis as **NOT
  SCOREABLE — "zero HUMAN_VALIDATED chunk→spec mapping rows, named data
  gap"**; this diagnosis independently confirms the same zero and supplies
  the CONSTRUCTION PATH: 197/209 T-C10 evidence quotes anchor
  deterministically to specific chunks (94.3%) — the validated store
  already contains passage anchors stored at the wrong granularity.
- their T-C19 registers the concept-node mapping gap (pedagogy edges
  unreachable in production); the chunk→SP store here is the spec-point
  analogue and the shared fix family (validated mapping rows through
  T-C06/F-168 provenance).
- their T-C20 registers the vector serving-surface gap (no VALIDATED
  predicate on the vector path); consistent with this diagnosis's step 4
  (ingestion must ride the serving-eligible boundary).
- the "production vector side is empty" observation (the live pilot tutor
  ask returned zero document evidence) is now **7/2,333 chunks embedded**
  (session-95 backfill, resumable at the quota wall) — the structural
  finding stands: 0.3% embedded changes nothing about the mapping gap.

Session numbering: this session is **96** (the 77–95 range was consumed by
the concurrent lanes; renumbered per the session-89/93/94 collision
precedent).

## 1. The audit: what retrieval-relevant data actually exists

| Fact | Number | Source |
|---|---|---|
| Notes corpus | 112 notes | `Chemistry IGCSE Revision Notes/` |
| Heading-level chunks | 732 (avg 6.54/note, p50 398 chars) | the natural retrieval granularity |
| Note-level SP mappings | **209, all HUMAN_VALIDATED** (operator, 2026-09-11) | the T-C10 store (spec_map front-matter) |
| SPs with ≥1 mapped note | 181/182 | only **4CH1-4.15** has none |
| **Direct chunk→SP rows, anywhere** | **0** | no production table (V11 chunks carry no SP), no resources-repo store, content-package v0.1 models note-level only |
| C10 evidence quotes locatable in a specific chunk | 197/209 (94.3%) — 196 exact + 1 fuzzy | **derivable** chunk-level anchors |
| SPs with ≥1 derivable anchor chunk | 169/182 (93%) | from the quotes alone |

Two corpus-quality defect classes found during anchoring (both enumerable
worklists, not open-ended repairs):

1. **Source-conversion artifacts corrupt ~12 passages** — e.g. the
   Reactions-of-acids note literally contains `they form a **salt** and
   **ydrogen gas](https://…` (a mangled link that ate the "h" of "hydrogen"
   and glued a URL into the sentence); LaTeX-wrapped formulas
   (`CnH2n+2` rendered as math) break plain-text quote anchoring. 12/209
   evidence quotes cannot anchor verbatim for this reason.
2. **Chunk text must include its own heading** — several C10 evidence quotes
   ARE heading titles ("Predicting properties in Group 7"). The audit's first
   pass missed 84 quotes; markdown-insensitive normalization + heading
   inclusion recovered 72 of them. Production `ChunkingService` should make
   the same choice (chunks retrievable by their heading words).

## 2. The evaluation: why SpecificationPoint-aware retrieval fails

Three providers over the same corpus (all diagnostics honest about their
gold — the only gold is NOTE-granularity + derived anchors; **no chunk-level
validated gold exists**):

- **P1 BM25 over chunks** (the settled baseline);
- **P2 SP-note-route** — the ONLY SP-aware path the current data supports:
  resolve query→SP, return ALL chunks of ALL notes mapped to that SP;
- **P3 SP-anchor-route** — the data-construction PREVIEW: the same routing
  restricted to the quote-anchored chunks.

### Q1 — spec-wording queries (the 181 mapped SPs; gold = the query's own SP)

| Measurement | Result | Reading |
|---|---|---|
| BM25 top-5 contains a chunk from a gold-mapped note | **97.8%** | lexical retrieval finds the right NOTES — BM25 is not the problem |
| BM25 top-5 contains the derived anchor chunk | 72.4% | passage-level: right note, not always right passage |
| P2 note-route chunks returned per SP | **mean 7.95, p50 7, max 29** (4CH1-3.9) | the fan-out explosion |
| P3 anchor-route chunks per SP | **mean 1.09**, coverage 93.4% | what chunk-level construction gives |
| **Precision ceiling of note-inheritance** | **13.7%** (1.09 / 7.95) | the quantified failure: routing an SP through note-level mappings returns ~8 chunks of which ~1 is the evidence passage — and NOTHING in the data can rank or filter them |

### Q2 — real learner/exam questions (HUMAN_VALIDATED golds)

| Query | BM25 top-5 note-gold | SP resolver (BM25 over spec wordings) top-5 |
|---|---|---|
| C12 fractional distillation (gold 4.8/4.7) | hit | gold in top-5 |
| C12 ionic conduction (gold 1.56C/1.43) | hit | gold in top-5 |
| C12 acid rain (gold 4.16/4.14) | hit | gold in top-5 |
| C12 fuels/sulfur (gold 4.16/4.15) | hit | gold in top-5 |
| **Pilot learner tutor ask (gold 1.42/1.43)** | **hit (ranks 1–2: the ionic-bonding notes)** | **MISS — resolves to 1.58C/2.47/2.26C/1.52C/2.34 (electrolysis/tests/solubility), then P2 cascades to 39 chunks from the WRONG SPs** |

The pilot's live production tutor ask is the smoking gun in one row: the
learner's real phrasing ("sodium chloride… giant lattice… not molecules")
retrieves the RIGHT notes at BM25 ranks 1–2, while the SP-wording resolver
misroutes to electrolysis/solubility SPs (vocabulary of the query matches the
wrong SP contexts), and the SP-route then fans out to 39 wrong chunks. In
production the tutor survived this only because the vector side is empty and
the KG side (title-token matching) carried the citations — 4 correct spec
topics, zero document evidence (live confirmation that the production
`documents`/`document_chunks` corpus is not ingested for the notes —
consistent with V20 §4's note that campaign-imported papers lack documents
rows).

## 3. The root-cause chain (why it fails, in order)

1. **No production retrieval corpus.** The notes corpus has never been
   ingested into `documents`/`document_chunks` — the vector side of the
   "hybrid" KA-RAG is empty in production, so all document-side claims about
   retrieval quality are about a corpus learners cannot be served from.
2. **The only authoritative SP↔content mapping is note-granular.** 209
   validated mappings attach whole notes to SPs; a note averages 6.5 chunks;
   so an SP routes to ~8 chunks (max 29) with a **13.7% precision ceiling**
   and no ranking signal — chunk→SP rows are zero everywhere.
3. **SP resolution by spec wording fails on learner language.** Examiner
   wording ≠ learner wording; the real pilot question misroutes completely
   (0/2 golds in resolver top-5) while plain BM25-over-chunks already finds
   the right notes. The SP-aware path currently makes retrieval WORSE on
   exactly the queries it exists to serve.
4. **No chunk-level gold → no fair evaluation (the operator's confounder,
   confirmed).** Every KG-aware metric above is a diagnostic against
   partial, note-granularity gold. Promotion cannot be decided on this
   evidence — not because the numbers are bad, but because the numbers
   cannot exist yet.

## 4. What evidence/data construction is necessary before promotion

In dependency order (each step is small, enumerable, and uses established
governance — no new architecture):

1. **Chunk-level mapping store (the keystone).** A chunk→SP mapping record
   with C10/C12-grade provenance: verbatim evidence quote, confidence,
   rationale, `validation_status: SUGGESTED`, promoted to HUMAN_VALIDATED
   only by the operator gate. **Seed = the 197 derivable anchors** (94.3% of
   the C10 store anchors deterministically — the evidence quotes were passage
   anchors all along, stored at the wrong granularity). This is not a new
   mapping campaign; it is a granularity refinement of an already-validated
   store, plus new authored candidates only for the gaps.
2. **The enumerable gap worklist (~25 rows, not open-ended):**
   - 12 SPs whose notes exist but no quote anchors (4CH1-1.1, 1.12, 1.26,
     1.51, 2.33C, 4.3, 4.5, 4.14, 4.19, 4.24, 4.29C, 4.40C) — author
     chunk-level candidates with fresh verbatim quotes;
   - 12 passages corrupted by source-conversion artifacts (mangled links,
     LaTeX-wrapped formulas) — repair the markdown so quotes anchor verbatim;
   - 1 unmapped SP (4CH1-4.15) — the C12 question-store already maps it at
     question level; a note-level/chunk-level mapping decision is needed.
3. **Chunking canonicalization.** Chunk text = heading title + section body
   (this harness's choice, and the C10 heading-quote lesson). Pin it in the
   production `ChunkingService` before ingestion so the mapping survives
   re-chunking.
4. **Corpus ingestion into production** (the existing parser canonical path,
   T-C06 gates): mapped notes → `documents`/`document_chunks` + embeddings —
   otherwise the vector side stays empty and "hybrid" remains KG-only.
5. **Resolver upgrade riding the new mapping — "retrieve then attribute"
   instead of "resolve then route".** With chunk→SP rows, the query side
   becomes: BM25 over chunks → attribute top chunks to SPs via the mapping →
   SP context for the tutor/CLA. This fixes failure #3 structurally (the
   pilot question's top chunks ARE the 1.42/1.43 notes' chunks — attribution
   gets the SP right where the wording resolver got it wrong). Keep the
   wording resolver only as a secondary signal.
6. **The fair evaluation protocol (only now possible):** held-out
   operator-validated chunk-level gold; a real-learner query regression set
   (the pilot tutor question is case #1); chunk-granularity P/R@k; resolver
   accuracy on learner phrasing; KG+lexical fusion vs each alone. Promotion
   to production defaults per `RAG_RETRIEVAL_RESEARCH.md`'s standing rule:
   benchmark evidence first — and the benchmark becomes fair exactly when
   step 1's validated mapping exists.

## 5. What this session does NOT claim

- No new retrieval provider was added (per the directive — that is not the
  problem).
- No mapping was authored or promoted here; the 197 derivable anchors are a
  MEASURED SEED COUNT, not new data. All construction steps above are
  proposals for the operator's gate.
- The production tutor/CLA code paths were not modified; the live tutor ask
  was an honest pilot learner action (Track 2), reused here as evaluation
  evidence.
- The Q1 diagnostics credit P2/P3 with a perfect SP resolver (generous);
  real-world SP-aware numbers are strictly worse than reported.
