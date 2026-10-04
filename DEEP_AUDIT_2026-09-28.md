# Deep Audit — 2026-09-28 (RECONSTRUCTED FROM COMMIT ARCHAEOLOGY)

> **PROVENANCE — read this first.** The original deep-audit findings document of the
> 2026-09-28 lane was never committed anywhere (every branch of `syllabai-core` and
> this repo searched per the open coordination ask, operator directive trace
> `1a0e6b95154d5cb5`). This document is a **reconstruction**, executed 2026-10-04
> (operator word trace `1a1064399ca6e989`, registry entry T-C81) by reverse-engineering
> the lane's commits: **25 audit-citing commits on `syllabai-core` main,
> 2026-09-27T19:47Z → 2026-10-02T05:52Z**, whose messages carry the per-finding
> findings, mechanics, and honest residuals. The commits — not this file — remain the
> authoritative record; this file exists so the findings taxonomy is discoverable
> without re-deriving it from `git log`. Where the reconstruction is interpretive, it
> says so. One numbering collision (two sweeps both used M1–M3) is presented as
> observed, not silently resolved. No code, DB, corpus, or serving change was made by
> this recovery; r6 is untouched (WAITING_FOR_GENUINE_TEACHER_VALIDATION, trace
> `1a0e6753792f76fd`).

**Method:** full commit-message + file inventory of every `syllabai-core` commit in the
window whose message cites the audit (`deep-audit 09-28`, `audit Mx/Lx`, `H1`, `H2`,
`M1, deep-audit 09-28`, `MED-2`), tails extracted verbatim, cross-checked against the
anchor-sweep monitors (`scripts/anchor_matrix_sweep.py`, master-pack T-C39 ledger) and
the registry (which had no entry for this lane — the ask's own observation).

**Severity vocabulary:** HIGH (exploitable serving-integrity failure), MEDIUM
(boundary/availability/cost defect), LOW (parity/robustness defect). The lane's own
commits are the source for every classification below.

---

## 1. What the audit was

Three parallel sweeps plus a live production probe (the R-tranche-1 commit's own
header: *"Re-derivation of the lost 09-28 audit backlog (3 parallel sweeps + live
probe)"*):

1. **Tutor safety & grounding sweep** — the fail-open guard, prompt-injection surface,
   citation mechanics (produced H1, H2).
2. **Identity & boundary sweep** — authN/authZ, throttling, request-size and
   content-type boundaries, data integrity (produced M1–M7 and the R-series).
3. **Serving-path integrity sweep** — per-ask failure semantics and read amplification
   (produced the second M1–M3 and L1–L3; landed 2026-10-01/02).

The audit's fixes were landed in waves and cite the document by tag
(`deep-audit 09-28`) in each commit message. The document itself was lost before
commit — the lane later had to re-derive its own backlog (the R-series exists because
of that loss).

---

## 2. HIGH findings

### H1 — paraphrased paper-question identities could bypass the fail-open guard

**Finding** (commit `63df406`, message verbatim in substance): the paper guard fires
only on a COMPLETE parsed identity (qnum + series + year). The question-number grammar
recognized exactly `question|q` + ASCII digits, so trivial paraphrases — *"the tenth
question of june 2019 paper 2"*, *"question number 10"*, *"10th question"*, full-width
digits — left `qnum` null, were classed not-a-paper-ask, and **generic retrieval
answered a named paper question from textually-similar wrong-paper chunks WITH
citations**. The 9-anchor matrix pinned three parseable phrasings, so CI stayed green
while the semantic class stayed open.

**Fixes (3 commits):**
- `63df406` — parser-only grammar widening: word numbers 1–49 in cardinal and ordinal
  form (keyword-led and ordinal-led), `number/no` interposition, NFKC normalization
  (full-width digits bind), letter-adjacent hyphen folding; part letters a–h still
  keyword-led only. Guard posture: widening what counts as a stated identity widens the
  **fail-closed** surface — an accidental identity now refuses honestly instead of
  serving unanchored. The over-refusal direction is the deliberate trade.
- `ae15cf4` — test-assertion correction only (`'paper 2'` binds via the resolver's
  PAPER_HINT, not the parser; the guard keys on qnum+series+year). The bypass closure
  itself was green in CI.
- `fc07389` — ops regression pins: paraphrase anchors **A4/A5** added to the monitor;
  matrix **9 → 11**; pre-fix these phrasings SERVED wrong-paper bleed with citations
  (live-evidenced), post-fix they GUARD-REFUSE with
  `provider=deterministic-paper-refusal`. (Archaeology note: `fc07389`'s message cites
  the fix as `d133e41/ae15cf4` — `d133e41` is the same change's pre-rebase SHA on the
  lane branch; on main the fix is `63df406`.)

**Remains open (BY-DESIGN, recorded in the commit):** a green run proves these strings,
never the whole paraphrase class — the anchors carry PARAPHRASE-DETECTION BY-DESIGN
rules (code-coupled: fix the parser or retire/flip deliberately).

### H2 — untrusted input rode unfenced into the prompt; citation markers were trusted blind

**Finding** (commit `e5cc266`): the learner's raw question rode unfenced into the
QUESTION block, and the model's `[n]` citation markers were trusted while the server
binds every marker to a real document deepLink — so an injection in the question (or a
hostile upload surfacing in SOURCES) could steer **which real sources a fabricated
claim appears to cite**. The audit's second HIGH.

**Fix (one commit, `e5cc266`, both closures in `GroundedTutorGenerator` — the single
choke point shared by KA-RAG and CLA):**
- **INPUT fencing (prompt v5 → v6, `tutor-grounded/v6`):** every untrusted block — the
  question, each conversation turn, each SOURCES item's content — wrapped in a
  per-request fence pair `<<<UNTRUSTED-X>>> … <<<END-UNTRUSTED-X>>>`, X drawn per ask
  from a SecureRandom lookalike-free alphabet (no 0/O/1/I/L); a payload can never close
  its own fence or forge a block header (guessed-code closes are inert data by
  construction, regression-pinned). Server-composed briefs and the scaffolding stay
  outside the fences; only data goes between a pair.
- **OUTPUT validation:** `sanitizeAnswer` strips any `[n]`/`【n】` marker whose number
  falls outside `[1..evidenceCount]` (same 1–3-digit marker shape the web plugin
  rewrites; `[2025]` is content, not a marker) plus any echoed fence marker — the
  learner-visible answer can only cite REAL evidence slots; in-range markers pass
  byte-identical. Strips log info-level (counts only, no content, per the LIM raw-text
  posture).

**REMAINS OPEN — explicit and load-bearing (commit verbatim in substance):** *"whether
a cited source truly supports a statement is the retrieval pipeline's grounding
contract, not a string operation."* **Claim–evidence entailment is out of scope of the
H2 closure and must not be read as closed by it.** Any entailment-checking work is a
separate, future, dated instrument.

---

## 3. MEDIUM — identity & boundary sweep (M1–M7)

### M1 — no throttling anywhere (rate limiting at the security-chain boundary)

**Finding:** the service shipped with no throttling at all — login brute force and LLM
cost amplification were both unbounded. **Fix:** `2f11707` — a `RateLimitFilter` inside
the security chain, after the JWT filter: AUTH tier keyed by client IP (XFF left-most
hop first, as then understood): login 10/window, register 5, bootstrap-admin 3,
password change 10; LLM tier keyed by learner identity: tutor/ask + cla/ask share one
20/window per-learner budget (deliberately above the anchor sweep's ~11 asks so the
harness never trips it). In-memory fixed windows, size-guard sweep, 429 + Retry-After
in the ApiError shape; **fail-open on internal limiter error, with the reasoning in
code: an availability/cost control, not a data gate — fail-closed stays reserved for
correctness boundaries.** Horizontal scale-out needs a shared store — **documented as
out of scope for the single instance; remains open as a scale posture item.**
`84991b9` — boot fix follow-up (`@Autowired` on the limiter's primary constructor;
multiple constructors left Spring unable to wire it). M1 was later hardened twice by
the re-derivation pass (R5-final per-target-account budget; R8 LLM-tier coverage —
see §6).

### M2 — upstream 503 error-body pass-through

**Finding:** the tutor generator propagated the LLM chain's aggregate message (upstream
provider error bodies — untrusted third-party content, up to ~200 chars per provider)
into the client-facing `TutorGenerationException`. **Fix** (in `1551c1a`): fixed honest
messages on BOTH 503 handlers; full detail stays server-side (cause chain + WARN
logs). The failover chain's diagnosability contract is untouched — it lives in logs,
not learner bodies. (This is the **boundary sweep's** M2; see §4 for the serving
sweep's separate M2.)

### M3 — ZIP decompression bombs

**Finding:** both ingestion unzippers (SME question bank, revision notes) used
`ZipInputStream.readAllBytes()` — allocating the FULL uncompressed entry before any
check; a ~42 KB bomb OOMed the pod (the multipart cap bounds compressed bytes;
compression ratio is attacker-chosen). **Fix:** shared bounded walker `ZipSafety` —
per-entry / total / entry-count budgets enforced DURING streaming, plus structural
traversal guard on entry names; absolute caps, not ratio checks; 1000:1-ratio bomb
probe pinned.

### M4 — unbounded JSON request bodies

**Finding:** multipart limits never covered `application/json` (teacher drafts, GLM
OCR pairs, marking batches) — a huge POST made Jackson allocate the whole document.
**Fix:** `JsonBodyLimitFilter` at the very front of the servlet chain: Content-Length
over budget → ApiError-shaped 413 before a byte is read; chunked bodies capped
mid-read. Default 2 MiB, configurable (`syllabai.http.max-json-body-bytes`).

### M5 — documented-but-missing `@PreAuthorize` layer

**Finding:** SecurityConfig's javadoc claims method-level role enforcement while
`@EnableMethodSecurity` was active with **ZERO annotations** — the route matchers were
the single gate. **Fix:** all 3 admin + 10 teacher controllers carry class-level
`@PreAuthorize` mirroring their route rules exactly (pure defense in depth, no behavior
change); learner/auth surfaces deliberately stay unannotated (chain-governed,
identity-scoped); `GlobalExceptionHandler` rethrows `AccessDeniedException` per Spring
Security's documented pattern (without it the catch-all turns method denials into
500s); reflection matrix test pins annotations + machinery live. Follow-ups:
`df6ef7e7` (two teacher ITs authenticate for direct secured-controller calls), and the
policy's adoption by later features (e.g. `0a997a9`, assignment controllers, *"deep-audit
M5 defense in depth"*).

### M6 — learner-owned rows had no FK closure (deletion posture was prose, not physics)

**Finding:** eight `learner_id` columns (attempts, skill_states, misconception_states,
review_schedules, telemetry_events, tutor_topic_engagements, learner_self_marks,
tutor_sessions) carried NOT NULL with **no FK to `users(id)`** — V42's own header
claimed deletion-follows-account, but nothing enforced it. **Fix:** `V45` adds all
eight `<table>_learner_id_fkey` constraints with ON DELETE CASCADE — one defect class,
one migration, not just the audit-named pair. **Prod pre-flight (2026-09-28,
read-only): 0 orphans across all eight tables** — no cleanup pass; a future DB with
orphans fails the migration loudly (fail-closed; orphans are forensics, not garbage).
`LearnerOwnedRowFkIT` pins the contract against real Postgres (constraints exist with
CASCADE; the cascade actually follows the account through the full
question_version → part → attempt → answer chain; unknown learner_id rejected by the
DB). Test follow-up `05f2621` (NOT NULL timestamps the cascade IT omitted).

### M7 — hardcoded campaign JWT secret in the repo

**Finding:** `run_ingestion_campaign.py` carried a hardcoded HS256 secret — any repo
reader could mint valid JWTs for every stage-2 boot. **Fix:** secret from the
environment (`CAMPAIGN_JWT`, or `SYLLABAI_JWT_SECRET` to match the app's own contract);
the run fails closed with a clear message before any boot if neither is set.

---

## 4. MEDIUM — tutor-serving integrity sweep (second sweep; landed 2026-10-01/02)

> **Numbering collision, observed not resolved:** this sweep's commits cite
> `(audit M1)`, `(audit M2)`, `(audit M3)` — labels already used by the identity &
> boundary sweep (§3). The reconstruction reads this as per-section numbering within
> the lost document (identity/boundary section vs serving-path section). To keep this
> file unambiguous the serving-sweep findings are written M1′/M2′/M3′ here.

### M1′ — research telemetry sat ON the serving path and could 5xx a delivered act

**Finding** (`67709057`, merged via PR #46): all thirteen telemetry listeners were
synchronous `@EventListener @Transactional` inside the call chain that produced the act
they observe — a Neon write jitter surfaced as a 500 on a fully-generated tutor answer,
a marked attempt, or a CLA exchange; healthy requests paid the round-trips too.
**Fix:** handlers dispatch `@Async` on a dedicated bounded executor (2–4 pool, 500
queue, CallerRuns backpressure, graceful drain) AND guard their own bodies — a failed
write drops the row with a WARN, never propagates. *"Telemetry is an append-only
research record — dropping a row is recoverable, failing the ask is not."* Accepted
semantic trade, documented: in async mode a telemetry row commits in its own
transaction and no longer rolls back with a domain transaction that fails after
publishing (the correct direction of failure for a research record). Determinism seam:
`syllabai.telemetry.dispatch=async|sync` — production async, IT profile pins sync.

### M2′ — per-hit `documents.findById()` N+1 on both retrieval arms

**Finding** (`7e29755a`, merged via PR #45): both serving retrievers resolved document
provenance with a per-hit findById — one extra query per evidence candidate, every ask,
vector AND lexical arm. **Fix:** the chunk-search SQL (already inner-joining documents)
now selects `d.doc_version`; `ChunkHit.docVersion` arrives with the hit; retrievers
drop their DocumentRepository dependency entirely (**the compile is the pin: no
document-row re-read is possible**). Frozen-corpus replays unchanged (snapshot
documents are doc_version 1 — exactly what the old `.orElse(1)` fallback produced).

### M3′ — per-ask DB round trips on request-invariant data (two tranches)

**Finding** (`2b1b2e4f`, PR #48 — tranche 1): the serving ask re-read data that does not
change within a request (or within 30 s of wall-clock): the winning version's subtree
CTE ran twice per resolution; the full UNIT/TOPIC/SUBTOPIC list was re-read on every
ask; skillStates fetched twice per ask for two derivations. **Tranche-1 fix:**
per-resolution subtree memo (never shared across requests), 30 s TTL snapshot on the
structure list (single volatile immutable generation, wholesale expiry — the per-node
VALIDATED gate still runs AFTER the cache, so serving eligibility never rides on
staleness), one skillStates read with two local derivations. Zero signature changes;
zero TTL semantics in the fail-closed scope decision. **Tranche 2** (`babf7fb8`, PR
#50): the remainder that needed signature-level propagation — `TutorPolicyService.select`
and `TutorMemoryService.digest` take caller-resolved readings (LearnerModelService
dependency removed from the policy), `LearnerContextAssembler.assemble` reads the
learner model ONCE and propagates to brief + digest + policy (was 2× skillStates + 2×
misconceptionReadings per authenticated ask); KG prerequisite/misconception chain reads
IN-batched (one recursive-CTE pass for ALL matched topics — was ~5 queries per topic);
CLA note-section evidence resolves the note document once (was up to
NOTE_CHUNK_LIMIT re-reads).

---

## 5. LOW — tutor-serving integrity sweep (L1–L3; one commit, `396a7f56`, PR #49; L1 separate, `d06dfeea`, PR #47)

### L1 — blocking /ask session append failed closed (parity bug)

The streaming path guarded its §22 session append (*"a persistence failure must not
corrupt the delivered answer"*) but the blocking path appended unguarded: a Neon jitter
on the session write turned a fully-generated, fully-delivered answer into a 500. The
blocking append now mirrors the stream guard exactly — the write failure is logged
(ERROR, session id attached) and the answer is returned anyway; the exchange is lost
from the transcript, the learner keeps the answer.

### L2 — an empty provider stream completed "successfully"

A provider stream that closed without a single surviving token used to complete
successfully — citations, then a blank done with `provider=null` and no meta, a
TutorAnsweredEvent with a null provider, and a learner staring at an empty answer
bubble. **An empty generation is a generation FAILURE:** the completion step now checks
the meta-sent flag and surfaces `Flux.error(TutorGenerationException)` — no meta is
invented, no research event publishes, no session append runs (the same
nothing-persists posture as a mid-stream provider death), and the client gets the fixed
error event.

### L3 — infrastructure failure DISARMED the fail-open guard

`PaperQuestionResolver.resolveWithVerdict`'s catch-all converted ANY infrastructure
failure into `Resolution.notPaperAsk()` — which disarmed the fail-open guard exactly
when the corpus was unavailable: an ask carrying a complete paper identity silently
degraded to generic retrieval instead of the deterministic paper refusal. The parse is
pure in-memory work, so the identity verdict is now recovered on the fetch-failure path
by local re-parse, and the mid-resolution catch keeps `identityParsed=true` when the
identity was complete (anchor state KNOWN-bad ⇒ guard refuses) while genuinely unknown
states still fall back honestly. **The old pin that asserted the disarm
(`cardFailureDegradesToNotPaperAsk`) is rewritten to the fail-closed expectation** — a
rare case of a test that pinned the wrong posture by design.

---

## 6. The re-derivation pass (R1–R19 + operator-approved residuals)

The lane re-derived its own lost backlog with three parallel sweeps + a live production
probe; findings numbered R1–R19 across two landed tranches, plus live-probe corrections
and two operator-approved residuals.

**Tranche 1 (`d77a0610`, R1–R6):**
- **R1+R2 — token revocation + disabled accounts:** tokens lived 12h with NO kill
  switch — a stolen bearer survived password rotation AND account disablement (the JWT
  filter trusted parsed claims and never read the row; the documented
  investigate/disable flow would have silently not worked). `V46` adds
  `users.token_version`; tokens carry a ver claim; the filter resolves the user row per
  request, **failing CLOSED on stale ver, deleted user, or disabled account**.
  `rotatePasswordHash` bumps the column: rotation ends EVERY live session. Deploy note:
  pre-V46 tokens rejected once — all pilot users re-login once (accepted fail-closed).
  Cost: one PK lookup on a ~200-row table, the same per-request class the M1 limiter
  already pays.
- **R3 — bootstrap window re-armed on cold boot:** the 15-minute first-admin window was
  anchored to JVM boot; every cold boot re-armed a fresh ANONYMOUS ADMIN claim window,
  contradicting V19's own EXPIRED-is-terminal contract. Now anchored to the row's
  persisted `updated_at`, enforced ON the claim path (stale PENDING flips EXPIRED
  terminally at claim time). Prod unaffected (claimed terminally long ago).
- **R4 — no HSTS in production:** behind Render's TLS-terminating proxy Tomcat sees
  plain HTTP, so the default `isSecure()`-gated HSTS writer never fired. HSTS now
  forced on every response (includeSubDomains, 1y, preload) + explicit referrer policy.
- **R5 — auth-tier rate-limit bypass CONFIRMED by live probe:** the M1 limiter keyed
  login/register/bootstrap/password budgets on the LEFTMOST XFF entry — live probing
  (10 logins on fake XFF A, 401 on fresh fake XFF B) proved each fake value mints a
  fresh budget (Render APPENDS, does not overwrite; the old "proxy overwrites"
  assumption was false). First correction `8292caa0`: key on the FIRST PUBLIC hop from
  the right. **Final form `5e4d155f`:** extended live probing (25-request battery)
  established the proxy does NOT forward a trustworthy client IP at all — ANY
  XFF-derived per-IP key is attacker-controlled or varying infrastructure. **The bound
  that survives source spoofing is the TARGET: failed logins counted per account email
  at the service layer** (`LoginAttemptBudget`, checked BEFORE any bcrypt work; success
  clears history). Deliberate documented trade: a hostile party can exhaust one
  victim's per-account budget (one 429 window) — the standard OWASP credential-stuffing
  cost, strictly smaller than the unbounded brute force it prevents.
  `isPrivateAddress` now covers 100.64.0.0/10 (CGNAT) — where the proxy's varying hops
  live.
- **R6 — password floor:** self-registration accepted 8 chars with no complexity while
  the platform's own bootstrap bar was 12+letters+digits. One documented bar everywhere
  (RegisterRequest + Password change).

**Tranche 2 (`c37582df`, R7–R19):**
- **R7** — `PartAnswerRequest.answerText` unbounded end-to-end (persisted AND embedded
  verbatim into Smart Mark LLM prompts; a ~2 MiB body would be stored and re-sent to
  the provider every marking run) → capped at 4000 (the tutor turn cap).
- **R8** — Smart Mark learner surfaces drove the LLM chain but were NOT in the M1 LLM
  tier (smart mark runs the pipeline once per PART per call) →
  tutor/cla/smart-mark/feedback/improvement share one per-learner budget.
- **R9** — teacher smartMarkBatch served raw `Exception.getMessage()` to the client
  (provider SDK text; DataAccessException can carry bind values) → stable
  UNEXPECTED_ERROR code, detail in the log (the M2 hygiene rule).
- **R10** — `ContentDocumentController.parse` echoed Jackson parse excerpts into the
  400 body → fixed message, detail logged.
- **R11** — `ChunkVectorRepository` built kind filters by string concat — never
  injectable (an enum), but one refactor from an injection seam → exhaustive switch
  (adding a `Document.Kind` constant is now a compile error, not silent SQL drift).
- **R12** — TOPIC_TEXT regex (nested lazy quantifiers) backtracks polynomially on long
  non-matching queries → 300-char guard at the use site.
- **R13** — `POST /tutor/sessions` created a row per call with no per-learner cap
  (authenticated DB-growth vector) → capped at 50; intervention/evidence/complete DTOs,
  HumanMarkRequest comments/perPointDecisions, noteId lookups size-capped.
- **R14** — asset serving accepted script-capable media types (SVG mapped
  image/svg+xml; revision-note packages accepted text/html via a generic regex) →
  demoted to download-only / fixed raster+pdf allowlist.
- **R15** — the campaign runner passed the JWT signing secret as a JVM ARGUMENT
  (world-readable in `/proc/<pid>/cmdline` for the whole stage-2 boot) → rides the
  environment (`SYLLABAI_JWT_SECRET`).
- **R16** — three scripts imported the fail-closed DB-identity gate from an EXTERNAL
  path (`/home/z/my-project/scripts`) that no longer exists, shadowing the audited
  in-repo gate → imports resolve to the in-repo copy.
- **R17** — `.gitignore` covered only `.env` → `.env.local/.env.production/*.pem/*.key`
  added.
- **R18** — `export_evidence.sh` interpolated `$DIR` into a psql meta-command and
  inline python → quote-safe env passing + a refusing path check.
- **R19** — springdoc/OpenAPI served anonymously in prod (full API contract
  enumeration) → disabled in the prod profile; endpoints stay auth-gated.

**Operator-approved residuals (`d9cb3ddc`; operator decision trace
`1a0e7c351ae6c9e5`):** BCrypt cost 10 → 12 (OWASP floor is 10, but every paying surface
is now rate-budget-bound; existing hashes carry their own cost factor — nothing
re-hashes); JWT TTL 12h → 2h (token_version revocation already kills a stolen token at
its next API call; 2h bounds the copied-token window 6× while keeping a full study
session intact; env-overridable). `IdentityCostPinsTest` pins all three silent-regression
risks (bean hash prefix `$2a$12$`, yml fallback, @Value fallback).

---

## 7. What remains open after the landed fixes (the audit's honest residue)

1. **H2 claim–evidence entailment** — explicitly out of the closure's scope (*"the
   retrieval pipeline's grounding contract, not a string operation"*). **Must not be
   read as closed.** Any entailment work = a separate, dated, future instrument.
2. **M1 horizontal scale-out** — the limiter is in-memory by design; a shared store is
   required for multi-instance and is documented out of scope for the single instance.
3. **R5 victim-exhaustion trade** — per-account budgets can be exhausted by a hostile
   party for one window; documented OWASP-standard cost, accepted.
4. **Anchor BY-DESIGN boundaries** — the A4/A5 (and later B3) monitors prove their
   exact strings per run, never the whole paraphrase/refusal class; every anchor
   carries retire/flip rules (master-pack T-C39 ledger; anchor-sweep docstring).
5. **Paraphrase-class closure is grammar-bounded** — H1 widened the grammar (word
   numbers 1–49, NFKC, hyphen folding); forms outside it (e.g. spelled-out hundreds,
   non-English numerals) remain future parser work by construction.

*(No H3+, M8+, or L4+ finding exists in any lane commit message — searched across the
full window; the "(L5)" strings in the 10-02 window are the citation-surface lane's
independent layer labels, not audit findings.)*

---

## 8. Adjacent-but-separate instruments (scope boundary — NOT deep-audit findings)

- **anchor-sweep monitors** (A-series paraphrase anchors; B-series refusal/provenance
  pins: B2 provenance gap identified+closed `8ee3da65`, B3 refusal pin `77c7a7ce`,
  matrix 9 → 11 → 12) — the ops harness the audit hardened and extended; ledger in the
  master pack (T-C39).
- **MED-2 / ADR-032** — misconception evidence ages toward the base rate, computed
  never persisted (`fb8600fa`, PR #43) — the model-integrity review's finding, its own
  ADR.
- **S1 / ADR-031** — forgetting decay computed, never persisted (`f1a3a5e9`, PR #39).
- **T-C40 / V56** — HNSW filtered-scan settings (the 2026-09-28 HNSW **incident**
  remedy, `hnsw.iterative_scan='strict_order'` + `ef_search=40`) — an ops incident, not
  an audit finding.
- **L1–L5 citation-surface labels** (F-022 tranches) — independent naming series.

## 9. Receipts — the complete audit-citing commit map

| Finding(s) | Commit(s) (syllabai-core main) | Date (UTC) |
|---|---|---|
| H1 fix / assertion fix / anchors A4-A5 | `63df406` · `ae15cf4` · `fc07389` | 09-27 19:47–20:12 |
| H2 fix (prompt v6) | `e5cc266` | 09-28 05:46 |
| M1 limiter + boot fix | `2f11707` · `84991b9` | 09-28 06:14–06:21 |
| M2–M5 boundary + M5 IT follow-up | `1551c1a` · `df6ef7e` | 09-28 07:05–07:12 |
| M6+M7 integrity + IT fix | `795a7ac` · `05f2621` | 09-28 07:57–08:07 |
| R1–R6 | `d77a0610` | 09-28 09:17 |
| R7–R19 | `c37582df` | 09-28 09:32 |
| R5 XFF correction | `8292caa0` | 09-28 09:49 |
| R5 final form | `5e4d155f` | 09-28 10:03 |
| residuals (BCrypt 12, TTL 2h) | `d9cb3ddc` | 09-28 11:38 |
| M5 policy adoption (assignment) | `0a997a9` | 09-28 19:43 |
| M1′ telemetry async | `67709057` (PR #46) | 10-01 20:35 |
| M2′ docVersion N+1 | `7e29755a` (PR #45) | 10-01 20:28 |
| L1 blocking append parity | `d06dfeea` (PR #47) | 10-01 20:37 |
| M3′ tranche 1 | `2b1b2e4f` (PR #48) | 10-01 20:45 |
| L2 + L3 | `396a7f56` (PR #49) | 10-01 20:52 |
| M3′ tranche 2 | `babf7fb8` (PR #50) | 10-02 05:42 |

*(Merges of PRs #45–#50 landed on main 2026-10-02 05:09–05:52.)*

**Registry:** this recovery + the retroactive lane entry are recorded as **T-C81**
(`.syllabai/tasks/T-C81.yaml`, DONE with receipts). The ask's TODO item is resolved
against this file.
