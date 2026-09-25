# Doc-lane fixes — 4ch0-1c-201601 SOURCE-PAIR-MISMATCH resolved + 3 of the 10 PDF-MAPPING-AMBIGUOUS slugs mapped (2026-09-25)

Lane: doc-lane (Session 125). Operator directive: "doc-lane fixes (Jan-2016 QP
re-fetch, 10 unmapped PDFs)" — exactly the session-124 NEXT item 2 ("Doc-lane:
re-fetch the real Jan-2016 QP for 4ch0-1c-201601; re-expose the 10
PDF-MAPPING-AMBIGUOUS slugs"). Iron rule honored: every number re-derived from
first-hand sources (Past-Papers repo tree + blob-verified downloads, fresh prod
DB probes, local pdflane runs at the round-3 parser, live Render API probes).
The pre-session summary was again stale (local worklog ended at Task 38; the
g12/g13/g14/g15 state lived only in the records repo).

## 1. The 201601 defect, reproduced and rooted first-hand

- The repo's `Paper 1/January 2016 QP - Paper 1C Edexcel Chemistry IGCSE.pdf`
  (sha256 `1b4a1cd5aa3059f9…`, 409,288 b) prints **"Monday 12 January 2015 –
  Morning"** on its cover — it is January-2015 CONTENT, byte-DISTINCT from the
  repo's real `January 2015 QP` (sha `2d6d5a5e9e747ed7…`, 363,488 b).
- **Rooting: the mislabel originates UPSTREAM of the repo.** PMT's own
  `…/Edexcel-IGCSE/Paper-1/January 2016 QP - Paper 1C …pdf` download is
  **BYTE-IDENTICAL** to the repo's wrong file (same sha) — the corpus inherited
  PMT's mislabeled file. The repo's Jan-2016 MS was verified genuine
  ("Mark Scheme (Results) January 2016") and needed no change.
- Session-124 disclosure CORRECTION (bank axis): session 124 said 201601's
  "currently-landed bank rows (driven in earlier rounds) pair a Jan-2015 QP
  with a Jan-2016 MS". Fresh probes show **4CH0/1C "January 2016" had NO
  exam_papers row and zero questions** (4CH0/1C sessions jump Jan-2015 →
  Jan-2017; the 4CH0/2C "January 2016" row is Paper 2, unaffected). The
  mispairing never reached the bank — it lived in the A1 sandbox products and
  the corpus layer only. The fix below is therefore a NEW fresh ingest, not a
  supersession, and nothing was deleted.

## 2. Real Jan-2016 QP sourced and verified

- Source: TutorChase S3 mirror
  (`https://tutorchase-production.s3.eu-west-2.amazonaws.com/28e644c1-…-Jan 2016 Paper 1C (QP).pdf`),
  216,371 b, 32 pp. Cover verified: **"Monday 18 January 2016 – Afternoon"**,
  Chemistry, Unit KCH0/4CH0 / Science (Double Award) KSC0/4SC0, Paper 1C,
  Paper Reference KCH0/1C 4CH0/1C KSC0/1C 4SC0/1C.
- Repo fix committed: Past-Papers `36bb445d02` (Git Data API, single commit,
  message documents both fixes + provenance). The wrong bytes remain in git
  history; the file path is unchanged.

## 3. The 10 PDF-MAPPING-AMBIGUOUS slugs — 3 mapped, 7 disclosed

The g12 report's 10 slugs (cands {QP: [], MS: []}, verified against the full
tree): `4ch1-1c-202011`, `4ch1-1c-202311`, `4ch1-1c-202411`, `4ch1-1c-202506`,
`4ch1-1c-202511`, `4ch1-1cr-202506`, `4ch1-2c-202311`, `4ch1-2c-202411`,
`4ch1-2c-202506`, `4ch1-2c-202511`. Re-walked the full Past-Papers tree at HEAD
(2,708 PDFs; chemistry 164; IGCSE sessions end at June 2024 + Nov 2021 + the 4
Further-Pure-Maths Nov-2023 files the operator uploaded manually). Sourcing
channels probed: PMT (June 2025 set present — QP+MS for 1C/1CR/2C), TutorChase
S3 (coverage ends Jan 2022), pastpapers.co (dropped Edexcel entirely),
thetuitioncentre (Jan/June only, no Nov sessions), dynamicpapers recent-papers
(password-gated), Pearson content-dam (SPA shell, no direct files), mymathscloud
(A-level only), alevelchemistry.co.uk (membership), exam-mate/papacambridge (no
Edexcel chemistry), web.archive.org (TLS unreachable from this environment).

- **MAPPED (this session):** `4ch1-1c-202506`, `4ch1-1cr-202506`,
  `4ch1-2c-202506` — PMT direct downloads, covers verified (QP 1C+1CR
  "Monday 19 May 2025", QP 2C "Friday 13 June 2025"; MS "Summer 2025" 4CH1
  Paper 1C/1CR/2C; 1C vs 1CR byte-distinct 366,795 vs 429,212 b). Committed in
  the same `36bb445d02` under the repo's naming convention (`June 2025
  QP.pdf`, `June 2025 (R) QP.pdf` per paper dir).
- **STILL MISSING (7 slugs / 14 PDFs, unsourceable anonymously):**
  `4ch1-1c-202011` (Nov-2020 1C — the COVID session whose 1CR/2C/2CR MS-only
  siblings were landed by G1.1 from the sandbox store), `4ch1-1c-202311`,
  `4ch1-2c-202311`, `4ch1-1c-202411`, `4ch1-2c-202411`, `4ch1-1c-202511`,
  `4ch1-2c-202511`. Operator channels that would unblock: Pearson Exam Officer
  login, the dynamicpapers password (dynamicpapers@gmail.com), or a manual
  upload like the Nov-2023 FPM precedent (`f6b6d810a8` "Upload Past Papers").

## 4. Re-gate of the 4 fixed papers (blob-verified, from repo HEAD)

Parser: `bench/g13-r3-letter-review` at `f4ec81f` (round-3 grammar + 8 fixture
tests; suite 140/1 skip/0 failures verified locally before use). Downloads
git-blob-SHA-verified; products identical to the pre-upload local runs
(local runs at `workspace/dl_runs`, repo-verified runs at
`workspace/dl_repo_runs`).

| slug | Q | marks | marksVerified | atomFlags | class |
|---|---|---|---|---|---|
| 4ch0-1c-201601 | 15 | 120 | **true** | none | **VERIFIED** — SOURCE-PAIR-MISMATCH fully cleared |
| 4ch1-2c-202506 | 6 | 70 | **true** | none | **VERIFIED** — first-time mapped, closes immediately |
| 4ch1-1c-202506 | 10 | 110 | true | q6 PART-MARKS-MISMATCH + MS-PART-NO-POINTS | ESCALATED (honest hold; G1 esc: MS total rows 5/7 not found in layout) |
| 4ch1-1cr-202506 | 11 | 110 | false | q10 PART-MARKS-MISMATCH | ESCALATED (ms_point_arithmetic mismatch q10; totals-row layout empty) |

Corpus-wide VERIFIED count: 21 → **23**.

## 5. Bank drive (2 VERIFIED papers, sanctioned NEW fresh-ingest)

Auth: 10-min ADMIN/TEACHER JWT minted from the live Render env
SYLLABAI_JWT_SECRET (e2e_search_test pattern). Converter: `atoms_to_draft.py`
(f4ec81f), identity sessionLabel "January 2016" / "June 2025", doc ids null
(the established doc-less pattern; the two NEW papers have no documents rows).

- **Idempotency-probe recovery (g15 201801 pattern, exactly):** the first
  4ch0-1c-201601 POST hit a Render cold start and the client died at the
  120 s bash cap with no response; the server side completed and committed
  late (exam_paper `1e935cfc` created 07:58:49.895Z). A re-POST arrived while
  the first transaction was still visible-incomplete, and failed CLOSED on
  `uq_knowledge_node_code` (duplicate anchor `ING-4CH01CJANUARY2016`) — the
  failed transaction rolled back entirely, leaving exactly ONE landed copy.
  Diagnosed from the Render Log Streams API (root cause line:
  ConstraintViolationException on uq_knowledge_node_code); no blind re-POST
  was issued after the state was understood.
- **4ch0-1c-201601 — NEW:** 15 q / 93 parts / 80 mp, all SUGGESTED,
  extraction `pdflane-atoms-draft-v1`.
- **4ch1-2c-202506 — NEW:** 6 q / 46 parts / 38 mp, all SUGGESTED.
- **C-gates (both papers PASS):** refs_match True; per-question marks
  bank=draft EXACT; bank=atoms EXACT (201601: 120=120; 2c-202506: 70=70);
  mark_points bank=draft (80/80, 38/38); attempts referencing = 0;
  zero rows deleted anywhere (both NEW, no supersession).
- Bank totals: 1,468 → **1,489 questions** / 4,796 → **4,914 mark points** /
  97 → **99 exam_papers**; `pdflane-atoms-draft-v1` versions 194 → **215**.

## 6. Not done / honest limits

- 7 of the 10 PDF-MAPPING-AMBIGUOUS slugs remain unmapped (operator-gated
  sourcing, §3) — they stay PDF-MAPPING-AMBIGUOUS, disclosed, not failed.
- The two ESCALATED Jun-2025 papers (1c, 1cr) keep honest holds; their
  residual shapes (q6/q10 letter-level + MS total-row layout gaps) are
  round-4 evidence-card candidates consistent with the g15 classification.
- The round-3 parser grammar still lives on branch
  `bench/g13-r3-letter-review` (`f4ec81f`), NOT merged to parser main — the
  merge is the parser lane's call; this session used the branch as-is.
- Embed refresh / serving soak for the newly landed papers: embed-lane
  cadence (unchanged disclosure since G1).
- The `uq_knowledge_node_code` find-or-create race (two concurrent identical
  POSTs → unique-violation 500 on the loser) is a known core behavior worth a
  core-lane ticket (upsert or catch-and-refetch); this session worked around
  it via the idempotency-probe protocol.

## 7. Artifacts

- `doclane_gate_report.json` — pre-upload local gate of the 4 fixed pairs
- `doclane_regate_report.json` — blob-verified re-gate from repo HEAD (authoritative)
- `doclane_drive_report.json` — drive records + poststate C-gates + bank totals
- `source-pair-forensics.json` — sha/cover/byte-identity evidence for the 201601 fix
- `SHA256SUMS` — over all files in this pack
- Past-Papers commit: `36bb445d02` (fix + additions, message = provenance)
- Scripts: `scripts/dl1…dl22*.py` (probes, sourcing, upload, drive, gates)
