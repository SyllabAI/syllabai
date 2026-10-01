# corpus_ops — Corpus Acquisition & Organization Tooling (Stage A/A′)

**Status:** **Ratified 2026-09-17** (owner-delegated self-review, §12) — implementation commissioned same day; see rollout gate in §10 before any production use
**Date:** 2026-09-17
**Tracker row:** T-C16 (registered in the master workbook TODO.md, content-ops track)
**Governing spec sections:** Master Spec §9 (content-processing architecture), §27 (parser abstraction), ADR-021 (Markdown as durable interchange)
**Related rows:** T-C03 (GLM-OCR pair CLI — downstream consumer), T-C04 (batch gate), T-C17 (clean-and-verify protocol — consumes `corpus_ops intake` output, supplies the `clean/` subtree)
**Repository:** `SyllabAI/syllabai-parser`, new package `tools/corpus_ops/` (sibling of `tools/ocr_batch/`, `tools/glmocr/`)
**Precedent this tooling retro-fits:** `Past-Papers/paper 1/MANIFEST.json` — the full
2026-09-11…13 cycle (same-second image download with *"2,002 local copies, zero
failures"*; `operator_cleanup` removing 1,362 images with references scrubbed
programmatically; `structural_repair` fixing 7 files; `operator_cleanup_2` removing 3
residual strays) was executed ad-hoc by an agent. **None of that tooling was
committed.** This proposal makes the loop a repeatable, tested artifact instead of
archaeology.

---

## 1. Why this exists

The corpus workflow has one manual, external step (ocr.z.ai conversion) and several
mechanical steps around it that today are agent folklore:

1. **Retroactive image rescue** — existing MD folders full of signed-URL image
   references must be downloaded *before the URLs expire (~1 week)*. `tools/ocr_batch`
   solves this only **at OCR time from PDFs**; it cannot operate on already-converted
   markdown.
2. **Pair organization** — raw conversion outputs (mixed QP/MS files, arbitrary names)
   must become the per-session layout `Past-Papers` canonized:
   `<year>-<Mon>[-R]/QP.md + MS.md + assets/` + a paper-level `MANIFEST.json`.
3. **Post-deletion scrub** — after the operator deletes unwanted images, every MD
   reference to a deleted file must be removed, checksums recomputed, manifest updated
   — exactly what `operator_cleanup`/`operator_cleanup_2` record having been done
   by hand-written, since-lost code.

## 2. Position relative to `ocr_batch`

| | `tools/ocr_batch` (existing) | `tools/corpus_ops` (proposed) |
|---|---|---|
| Input | official **PDFs** | existing **markdown + image URLs** |
| When | at OCR time | after OCR (retroactive), any time |
| Downloads | crops returned by the OCR service, same second | every image URL referenced in MD, before expiry |
| Output convention | `<stem>.md + assets/ + manifest.json` | the `Past-Papers` per-session layout + paper MANIFEST |
| Shared invariants | same-second download; honest failure recording; deterministic manifests | identical — one output convention, two entry points |

Long-term the two packages can share a `corpuslib` for checksums/manifest writing; do
not merge them now.

## 3. Package layout

```
tools/corpus_ops/
  corpus_ops.py          # CLI entry: intake | scrub | verify | rename
  pairing.py             # pair detection + pairing-proposal generation
  downloader.py          # concurrent fetch, retry, MIME sniff, dimensions
  manifest.py            # deterministic MANIFEST reader/writer (v1.1)
  scrub.py               # reference removal engine (grammar-aware, subtractive)
  clean_diff.py          # Stage B gate G3 implementation (see T-C17 §9)
  test_corpus_ops.py     # mocked-HTTP + fixture-tree tests (CI-enforced)
  README.md
```

stdlib-only for the `intake` core (same discipline as `ocr_batch api` backend);
`pypdfium2` not required (no PDF handling). Python 3.10+.

## 4. Command 1 — `intake` (download + organize)

```
python3 tools/corpus_ops/corpus_ops.py intake <raw-folder> -o <corpus-root> \
    [--paper "paper 1"] \
    [--mapping sessions.csv]        # optional: file → session-name mapping
    [--confirm pairing-proposal.json]
    [--concurrency 8] [--dry-run]
```

Behavior:

1. **Pair detection** — scan `<raw-folder>` for QP/MS candidates by filename tokens
   (`QP`/`question paper`, `MS`/`mark scheme`) and name similarity. Emits
   `pairing-proposal.json`; **mutates nothing**.
2. **Pairing is operator-confirmed** — run again with `--confirm` to accept. The tool
   never infers exam identity from document content (`AGENT.md` rule 2: *never infer or
   silently repair ambiguous paper/session identity*).
3. **Session naming** — with `--mapping`, use operator-provided session names
   (`2012-Jan`). Without it, create provisional folders (`UNIDENTIFIED-001/…`) and let
   a later `rename` command (same proposal/confirm pattern) fix them once covers are
   readable.
4. **Same-second download** — for every image URL referenced by any MD in the pair:
   concurrent fetch (default 8 workers, per-host throttle), retry with backoff,
   MIME sniffing (bytes, not extension), dimensions capture; store under
   `<session>/assets/` with the original OCR crop filename. **Failures are recorded,
   never retried silently into success**: each failure lands in
   `MANIFEST.download_failures[]` with URL, error class, and timestamp. Nothing is
   fabricated; an unavailable image keeps its failure state in the MD reference
   (the T-C02 honesty pattern).
5. **Reference rewrite** — MD links are rewritten to local relative `assets/…` paths
   (the `Past-Papers` convention) at intake time; original URLs are preserved in the
   manifest per image for provenance.
6. **Asset filename collisions (fail-closed):** two distinct URLs that resolve to the
   same crop filename are a hard FAIL unless the downloaded bytes are sha256-identical
   (then they are one asset, deduped, `referenced_by` listing every referent). Different
   bytes under one name is exactly the silent-overwrite class this package exists to
   prevent.
7. **Duplicate documents:** two raw MD files with identical sha256 are recorded in
   `dropped_duplicates[]` (legacy key, verified present in `paper 1/MANIFEST.json`) and
   only the first is organized — never silently ignored.
8. **MANIFEST build** — deterministic, insertion-ordered JSON (§7).

## 5. Command 2 — `scrub` (post-operator-deletion reference removal)

```
python3 tools/corpus_ops/corpus_ops.py scrub <corpus-root> \
    (--deletions deletions.csv     # session,asset_filename,operator_note
     | --from-staging)             # collect from <session>/assets/_deleted/
    [--dry-run]
```

Deletion input options (operator's choice): a CSV as above, or a staging convention —
the operator moves unwanted files into `<session>/assets/_deleted/` and `scrub
--from-staging` collects them. Both produce the same internal deletion record.

Behavior — **fail-closed at every step**:

1. Every deletion record must resolve to an existing asset file; a record whose file
   is already gone is an error (double-scrub) unless `--idempotent` re-runs a
   previously recorded cleanup batch (checked by batch id in the manifest).
2. Every removed file's references are removed from QP/MS by **exact relative-path
   match, with original-URL fallback** (files saved before the rewrite convention
   stabilized). Removal is subtractive, grammar-aware: the enclosing image island is
   deleted whole (T-C17 §3 invariant 4). Verified against the live corpus, the island
   is the **single-line** center-div form —
   `<div style='text-align: center;'><img src='assets/crop_1_<ts>.png' alt='OCR图片'/></div>` —
   so island removal is whole-line removal; a scrub that ever needs to edit *within*
   that line has mis-matched and must fail instead.
3. Orphan detection runs **after** scrubbing: any remaining image reference with
   neither a file nor a deletion record → hard FAIL with the full ledger (this closes
   the "ref exists, file never downloaded, never deleted" gap that silent passes leave).
4. QP/MS SHA-256 recomputed; MANIFEST updated with a new `ops_log[]` entry (§7):
   batch id, date, counts, per-session removed lists (the original URL of every removed
   image is preserved in the entry — provenance survives deletion, exactly as the
   2026-09-11 manifest did).
5. `image_count` fields recomputed; nothing else in the manifest is touched.

## 6. Command 3 — `verify` (read-only)

```
python3 tools/corpus_ops/corpus_ops.py verify <corpus-root> [--json]
```

Checks (all read-only; exit 1 on any FAIL-class):

- **Manifest ↔ filesystem agreement** — every referenced asset exists; every asset is
  referenced (strays beyond an explicit allowlist are FAIL-class);
- **Pair completeness** — every session folder has QP+MS (missing half is FAIL);
- **Asset integrity** — MIME-vs-extension consistency, dimensions present, checksum
  spot-verification (configurable depth);
- **Provisional identities** — sessions still named `UNIDENTIFIED-*` are WARN-class;
- **Clean-readiness** — `clean/` subtrees (T-C17) have valid clean-reports whose raw
  checksums match the manifest.

## 7. MANIFEST schema v1.1 (additive)

The existing `paper 1/MANIFEST.json` keys are canonical and preserved:
`paper, generated_at_utc, structure, notes, dropped_duplicates, download_failures,
sessions, operator_cleanup, structural_repair, operator_cleanup_2`.

v1.1 adds, without renaming or reshaping legacy keys:

- `schema_version: 1.1`
- `sessions{}` — **correction made at ratification:** the legacy manifest's `sessions`
  was verified to be *already a keyed object* (session id → `{documents{MS,QP →
  {original_name, path, sha256}}, image_count, images{url → {saved_as, bytes, format,
  sha256, referenced_by[]}}}`). v1.1 therefore only **adds optional fields**: per image
  `mime` (sniffed, not extension-derived) and `width_px`/`height_px` (parsed from PNG
  IHDR / JPEG SOF bytes, stdlib), per document `size`; `images`' keys already ARE the
  source URLs, so no separate `source_urls` layer is added. Legacy entries are read and
  rewritten unchanged except for added fields.
- `ops_log[]` — the general form of the legacy `operator_cleanup*` blocks (batch id,
  kind: `intake | image-cleanup | structural-repair | rename | reference-scrub`, date,
  counts, per-session detail; removed-image original URLs preserved inside the entry,
  exactly as the 2026-09-11 `operator_cleanup` entry did);
- `clean{}` — per session: `qp_sha256`, `ms_sha256`, `report_ref` (T-C17 outputs);
  raw files stay the provenance root, clean artifacts are recorded as derivatives.

Writer determinism is tested: same inputs → byte-identical manifest (modulo
`generated_at_utc`, which is pinned under a test env flag, mirroring the glmocr
epoch-pinning trick).

## 8. Failure philosophy and exit codes

Inherited from the project's fail-closed culture (T-C02, health gate, c12 promote):

- exit `0` — all gates green; exit `1` — any FAIL-class finding; exit `2` — usage error.
- A retry that eventually succeeds is *not* silent: total attempts and per-attempt
  errors go into the manifest entry (the sync-dashboard lesson from `syllabai-ops`).
- `--dry-run` exists for every mutating command and prints the exact planned mutation
  set; dry-run output feeds the operator confirm step.

## 9. Testing plan (CI-enforced)

- **Mocked HTTP** for downloader paths (success, partial failure, expiry-403, timeout,
  MIME mismatch) — no network, no key, mirroring `ocr_batch`'s 32-test discipline.
- **Fixture tree** — a miniature corpus (2 sessions × QP/MS × 3 assets) exercised
  through intake → operator-simulated deletion → scrub → verify, asserting manifest
  determinism and orphan detection.
- **Grammar-aware scrub tests** — reference removal inside image islands never
  disturbs adjacent tables/fences (reuses the glmocr fixture corpus).
- **clean_diff.py** — Stage B gate G3 unit tests on synthetic raw/clean draft pairs
  (spillover removal accepted; real-mark change rejected).

## 10. Rollout sequence

1. Ratify T-C16 (+ T-C17) — this design and the protocol travel together.
2. Implement `manifest` + `downloader` + `intake` with tests; dogfood on the next
   ocr.z.ai conversion batch **before** it touches `Past-Papers`.
3. Implement `scrub` + `verify`; replay against the *historical* `paper 1/` manifest
   records as an integration oracle (the 2026-09-11 cleanup is the expected-output
   fixture).
4. Add `clean_diff.py` once T-C17's cleaning agent produces its first real pairs.
   *(Ratification amendment: clean_diff.py is implemented alongside the package — its
   unit tests run on synthetic draft pairs per §9 — but its first **real-world**
   validation still awaits Stage B's first raw/clean pair; until then it is
   CI-tested, not corpus-proven.)*
5. Only then run the first live CLEANED batch → `GlmOcrPairCli` → T-C02 ingestion.

## 11. Honesty notes

- Pair detection heuristics are best-effort convenience; the operator confirm step is
  the actual pairing authority. Do not let a high match-score bypass a confirm.
- `verify`'s "no unreferenced strays" rule will initially flag historical assets that
  predate the manifest conventions; an explicit, dated allowlist in the manifest is
  the escape hatch — not silent tolerance.
- Downloaded bytes are not validated against the *printed paper* — image rescue
  preserves what the OCR service produced; content truth remains downstream
  (extraction drafts → SME validation).
- `clean_diff.py`'s G3 checks are the machine-checkable subset of T-C17 §9 (counts,
  mark identity, warning classes, `paperTotalConflict`); the "explainable line-by-line"
  requirement remains human-audited per T-C17 §13 until the operations ledger gets an
  automated mapping.

## 12. Ratification record (self-review, 2026-09-17)

Reviewer: main agent (owner-delegated). Every factual claim in this design was checked
against primary sources before ratification:

- **Legacy manifest shape** — `Past-Papers/paper 1/MANIFEST.json` re-read: top-level
  keys exactly as §7 lists them; `sessions` verified to be a keyed dict with entry shape
  `{documents, image_count, images}` (§7 corrected accordingly — the draft's "legacy
  list form" hedge was wrong); `operator_cleanup` entry shape
  `{date_utc, description, removed_image_count, removed_images{session: [urls]}}`
  confirmed as the `ops_log[]` template; `structure` string confirms the per-session
  layout; session names confirm the `<year>-<Mon>[-R]` convention (`2013-Jun-R`,
  `2020-Jan-R` … all live).
- **Corpus reality** — live QP.md image references are the single-line center-div
  island form above; MS.md in the sampled session carries zero image refs (normal);
  asset filenames are the OCR crop names (`crop_1_<ts>.png`).
- **Cross-references** — T-C17 §3 invariant 4 / §9 G3 verified present at the cited
  sections of `CLEAN_VERIFY_PROTOCOL_QP_MS_MARKDOWN.md` v1.1; T-C17 §9 already names
  `tools/corpus_ops/clean_diff.py` as the G3 implementation, so package layout is
  consistent in both directions. `AGENT.md` rule 2 quote verified verbatim.
- **Position vs `ocr_batch`** — `tools/ocr_batch/README.md` confirms the PDF-only
  input scope and the same-second/expiry discipline this package retro-fits.
- **Amendments applied at ratification:** §4 steps 6–7 (collision + duplicate rules),
  §5 signature (`--from-staging` promoted from prose to the CLI contract) and island
  shape pinned to the verified form, §7 legacy-shape correction + field additions
  narrowed to what is genuinely absent (`mime`, dimensions, document `size`), §10
  step-4 timing note, §11 clean_diff scope note.

**Verdict: RATIFIED with the amendments above.** Rollout gate (§10 step 2: dogfood on
the next conversion batch before it touches `Past-Papers`) remains owner-held.
