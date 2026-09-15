> **ARCHIVED 2026-09-15.** Session-9 point-in-time report (2026-09-04, GLM-OCR pipeline implemented and verified); its content is summarized in WORKLOG.md (sessions 9-11) and PROGRESS.md. Retained as history.

# SyllabAI Session 9 Report — Recovery, GLM-OCR Pipeline, Determinism, Conformance

**Date:** 2026-09-05
**Repos touched:** `syllabai-parser` (main `2f8a628` → `9eb35ab`, 5 commits), `syllabai` (this report + control docs). Untouched by design: `syllabai-core` (PR #1 verified only, never merged), `syllabai-web`, `Past-Papers`.
**Toolchain:** Temurin OpenJDK 25.0.4.1 · Apache Maven 3.9.16 (offline) · Python 3.12.

---

## A. Recovery

Workspace forensics (git status / reflog / `fsck --no-reflogs --unreachable` / stash census across all five repos): **no unpushed commits, no stashes, no dangling objects anywhere.** The only uncommitted work was three untracked Java files in `syllabai-parser` (1,130 lines: `GlmOcrMarkdownParser`, `GlmOcrPaperDraft`, `GlmOcrQuestionExtractor`) plus three empty test directories.

**Honest correction of the prior session's record:** the `tools/glmocr/` Python reference implementation it described **never existed** — not on GitHub, not in any local workspace (proven by reflog + fsck + full-workspace file search). It was created this session, as a faithful port, so §12 conformance could exist at all. Origin documented in `tools/glmocr/README.md`.

Recovered work was committed **as-is first** (`8baacbf`, compile-verified before modification), then fixed forward in reviewable units — no history rewrite.

## B. GitHub (commits pushed and remotely verified)

| Commit | Repo | Content |
|--------|------|---------|
| `8baacbf` | syllabai-parser | `content: implement glm-ocr java adapter` — the recovered 3 files, unmodified |
| `2f833d1` | syllabai-parser | `fix: make canonical identity deterministic` |
| `45f8ea2` | syllabai-parser | `content: add question and mark-scheme extraction` (+ fixtures, +tests) |
| `7c37993` | syllabai-parser | `content: preserve glm-ocr image references` |
| `9a5da41` | syllabai-parser | `test: add real-corpus conformance` (Python reference + harness + CI job) |
| `9eb35ab` | syllabai-parser | `docs: record session 9 implementation and verification` |
| (this commit) | syllabai | `docs: record session 9 — recovery, implementation, conformance` |

Every push verified with `git ls-remote` (remote main == local HEAD after each push).

## C. Java implementation (completed)

- `GlmOcrMarkdownParser` — Markdown + HTML-island adapter → `CanonicalDocument` (headings, lists, image divs, HTML tables incl. rowspan, centered divs, `$$` math, entity decoding recorded in provenance, `pageCount=1` + `pageBoundaries=none-in-source` honesty, positional `e%06d` ids)
- `GlmOcrQuestionExtractor` — both numbering styles (`1:` June / `1 ` October), `*N` + `*(a)` QWC, MCQ hindsight validation + MCQ grid tables, letter/roman parts (correct parenting), centered `(N)` marks blocks, answer prompts, totals (both placements + glued forms), meta (paper ref, log number, publication code)
- `GlmOcrMarkSchemeExtractor` (new this session) — table-first MS entries, rowspan-deferred marks, IC tables in all 3 corpus shapes, MarkPoints with dependent-on-MP / ecf / Or / any-two-from / reject vocabulary, classified guidance, both total placements, paperTotal
- `GlmOcrMarkReconciliation` (new) — D6 rule: QP↔MS totals + paper totals; conflicts → review findings
- `GlmOcrImageAssets` (new) — expired-URL preservation + local-asset `img:<sha256>` pipeline
- `GlmOcrConformanceDump` CLI + the canonical-layer `CanonicalIdentity`

## D. Determinism (what changed and proof)

`CanonicalDocument.of()` minted `UUID.randomUUID()` — non-reproducible parses. Fixed at the canonical identity layer: `CanonicalIdentity.contentDocumentId(checksum, engine, engineVersion)` = version-5-layout UUID from SHA-256 of `sha256:<checksum>|engine:<engine>|version:<engineVersion>`; no random component; **no timestamp ever enters identity** (`extractedAt` stays a provenance fact). OpenDataLoader compatibility preserved (same call site, now deterministic; explicit-id override still honored). The GLM adapter's private derivation was removed — it routes through the canonical layer, per "do not hide the problem in the adapter".

**Proof:** CanonicalIdentityTest (8 cases — stability, engine/version sensitivity, UUID layout, normalization, timestamp exclusion), ODL parse-twice identity regression, GLM parse-twice, and the conformance harness (identical `documentId` across two languages on all 6 fixtures).

## E. Conformance (Python vs Java)

`tools/glmocr/` (reference implementation) vs Java production, all 6 real files × modes doc/qp/ms:

**FULL CONFORMANCE — 12/12 file-mode combinations, every field identical** (structure, ids, question numbers, parts, marks, QWC, MarkSchemes, MarkPoints, image references, warnings, provenance). Enforced in CI by the new `conformance` job — **remotely green on `9eb35ab`**.

## F. QP/MS (counts and validation)

| Paper | QP questions | MS entries | MarkPoints | Reconciliation |
|-------|--------------|------------|------------|----------------|
| June 2025 WPH11/01 | 20 (colon) | 31 | 32 | all shared totals match; honest one-sided gaps |
| October 2025 WPH11/01 | 20 (space) | 33 | 31 | all 8 shared totals match |
| October 2025 WPH11/01A | 19 (space) | 33 | 53 | totals match; **paper-total conflict 80 (QP) vs 120 (MS) → review finding, preserved** |

Paper identity from content (never file names): paper refs, log numbers (P78753A/P78831A/P87440A), publication codes. QP covers are expired images → QP meta honestly null; MS meta carries the pairing inputs.

## G. Images

- **Expired signed URLs (all 74/74/77 QP figure refs):** complete URL preserved (incl. `Expires=` evidence — a real bug where the convenience constructor dropped the URL was fixed and regression-pinned), decoded crop path, ownership, `availability=unavailable-signed-url`. No fetch at parse time.
- **Valid local assets (future re-exports):** implemented + tested — SHA-256 hashing, magic-byte MIME sniffing, container-header dimensions, `img:<sha256>`, source-name matching. JPEG-content-with-`.png` regression enforced.
- **Not claimed:** the 225-diagram preservation idea is dead (the corpus has no local images; the 10 Unit-4 PNGs are from an unrelated July 2026 OCR session).

## H. Tests (exact commands and results)

```
mvn -o test          → 68 tests, 0 failures, 0 errors (baseline: 27)
python3 tools/glmocr/conformance.py → 12/12 PASS, exit 0
```

Both with the real toolchain (JDK 25.0.4.1 + Maven 3.9.16), clean builds (`rm -rf target`) for all recorded results.

## I. CI

- `syllabai-parser` @ `9eb35ab`: **build = success, conformance = success** (remotely verified via API after push)
- `syllabai` (this commit): docs-only, CI n/a

## J. PR #1 (status only — not merged)

`T-026/T-027: explainable diagnosis-aware tutor policy` — **open, draft, mergeable, head `81f9906`** (5 commits, 21 files), CI run `33898467857` **SUCCESS**. Re-verified via GitHub API at session start; left fully intact; **not merged** (merge is a human decision per policy).

## K. Remaining work

- 🟢 **Verified** (local + CI + conformance): canonical identity determinism; GLM-OCR adapter; QP extraction; MS extraction; mark reconciliation; expired-image preservation; Python/Java conformance; fixtures; CI (build + conformance)
- 🟡 **Implemented, not production-verified:** local-asset image pipeline (no real local assets exist — synthetic tests only); rowspan-continuation marks heuristics (warnings emitted, sources recorded)
- 🔴 **Not implemented:** GLM-OCR → `syllabai-core` ingestion bridge (T-C02); the one controlled Past-Papers batch (T-C03); LLM capability registry with `minimax/minimax-m2.7:free` (Session 7 artifact was lost; re-scoped, design docs survive)
- ⚪ **Deferred:** the 40-batch corpus run (parked until T-C02/T-C03 review), re-export of images at OCR time, vision-LLM routing, T-025/T-028+ UI waves (blocked on the PR #1 merge decision)

**Endpoint honored:** every important artifact is committed, pushed, remotely verified, documented, and reproducible from GitHub. Only the local workspace is disposable.
