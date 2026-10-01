# SyllabAI Documentation Accuracy Audit — 2026-10-01

**Audit date:** 2026-10-01
**Scope:** `SyllabAI/syllabai` master pack (README, MASTER_SPEC, DECISIONS, PROJECT_CONTEXT, TODO, PROGRESS, WORKLOG, WORKLOG_GAP, backlog TSV) cross-checked against the 10 sibling repos' READMEs/descriptions, GitHub metadata, `syllabai-core` `pom.xml`, and git history at HEAD `425e040` (master) / `99feab2` (TSV).
**Method:** every numeric/positional claim in the current-facing docs was re-derived from the artifact it cites (the definitive backlog TSV, the DECISIONS registry, git history, live URLs). Claims verified accurate are listed at the end so future audits do not re-litigate them.
**Precedent:** continues `DOCUMENTATION_CONTRADICTION_AUDIT_2026-09-07.md` (whose Master Spec findings 1/3/4 are verified FIXED in v1.3.0 — see Non-findings).

## Executive summary

The master pack is in good structural health — the 2026-09-07 audit's required fixes all landed, cross-repo stack claims are byte-accurate against `pom.xml`, and the repo map / ADR-029 promotion story is consistently told in README, PROJECT_CONTEXT, and DECISIONS. However, the audit found **10 residual inaccuracies**, concentrated in one pattern: **documents that state a count or inventory as current, while the authoritative artifact they themselves designate has moved on**. The worst instances: the Cycle-1 backlog cut is stated as 34 rows in four places while the definitive tracker holds 36; MASTER_SPEC §3 still describes an 8-repo set that predates the ADR-029 promotion (omitting the product frontend from the architecture section); and the session-record chain (WORKLOG/PROGRESS/WORKLOG_GAP) has drifted out of sync with its own maintenance rules, leaving sessions 79/104/105 without any durable record and Session 131 — the operator-GO T-C11 core sync — recorded only in a commit message.

No finding contradicts the research papers, the architecture decisions themselves, or any production-evidence claim. All are documentation-synchronization defects of the same class the project has fixed before.

## Findings

### F-1 — HIGH: "34 backlog rows" is stale; the definitive tracker says 36

**Claim:** `README.md` line 40 ("34 backlog rows, 12 of them the critical-path spine"); `MASTER_SPEC.md` line 1503 (§39a: "34 rows; 12 of them are the critical-path spine"); `PROGRESS.md` line 144 ("Cycle-1 scope is ambitious (34 rows / 8 weeks)"); `DECISIONS.md` ADR-010 body ("34 rows; 12-spine critical path").

**Reality:** `backlog/syllabai-master-project.tsv`, column 14 (`Cycle`), contains exactly **36** rows marked `Cycle 1`: F-012, F-013, F-020, F-021, F-022, F-028, F-029, F-032, F-033, F-034, F-036, F-037, F-039, F-040, F-041, F-043, F-047, F-053, F-055, F-056, F-059, F-060, F-092, F-137, F-138, F-140, F-142, F-144, F-148, F-152, F-153, F-159, F-160, F-161, F-162, F-163. The "12 critical-path spine" half of the claim **is** correct (exactly 12 rows carry the Critical Path marker).

**Resolution:** update README, §39a, and PROGRESS to 36 (or replace the hard number with "the Cycle-1 cut as marked in the tracker" so the claim cannot drift again). ADR-010's body is an immutable historical record — leave the text, but see F-6.

### F-2 — HIGH: MASTER_SPEC §3 repository architecture predates ADR-029 — wrong count, omits the product frontend

**Claim:** §3 states "8 repositories" and the tree lists: `syllabai`, `syllabai-web`, `syllabai-core`, `syllabai-parser`, `syllabai-pastpapers`, `syllabai-resources`, `syllabai-teacher-workbench`, `Past-Papers`.

**Reality:** the GitHub account holds **11** repos. ADR-029 (2026-09-28) promoted `syllabai-hub` to **the product frontend** and demoted `syllabai-web`; `syllabai-demo` exists as the frozen prototype; `syllabai-ops` exists. The spec's architecture section — whose header calls it "the operational source of truth for SyllabAI engineering" — contains no mention of the repo that now owns the entire student/teacher product surface.

**Mitigating:** §3 itself says "the README repo map is the authoritative list", and the spec is honestly versioned v1.3.0 (2026-09-11, pre-ADR-029).

**Resolution:** a controlled spec revision (v1.3.1 additive note or §3 tree update) naming `syllabai-hub`, `syllabai-demo`, `syllabai-ops`, and the count 11 — or an explicit banner on §3 pointing to ADR-029 + README until the next version bump. Note the spec already records two §3 amendment dates (2026-09-03, 09-13, 09-15), so amending it again is the established pattern, not an exception.

### F-3 — HIGH: session-record chain out of sync with its own rules; sessions 79/104/105 have no durable record anywhere; Session 131 exists only as a commit message

Three sub-defects, all against the project's own handoff invariant ("a future agent can reconstruct accepted architecture from repository artifacts alone") and WORKLOG_GAP's maintenance rule:

1. **`WORKLOG.md` top banner (2026-09-15) is false in both directions.** It says the log "holds durable entries only for sessions 2-20 and 35". In fact: sessions **2–5 are NOT in the file** (the earliest entry is Session 6), while sessions 21–35, 37–53, 55–65, 67–77, 80–83, 85–90, 92–93, 96, and 106–130 **are** (backfilled after 09-15, banner never updated). The banner also sits above an out-of-order file (Session 106 at line 3, before Session 35 at line 13).
2. **`WORKLOG_GAP.md` Table B is stale.** It lists sessions 40, 43, 44, 46–53, 68 as unrecoverable — every one of them now has a WORKLOG entry. Only **7 and 54** remain actually unrecovered from that table. The file's own rule ("when a Table A summary needs correction or a Table B session is recovered… update this file") was not followed.
3. **Coverage holes vs the living state:** sessions **79, 104, 105** appear in neither WORKLOG nor PROGRESS nor WORKLOG_GAP (unindexed gaps — the register's coverage ends at session 71). `PROGRESS.md` ends at Session 129 (no 130), `WORKLOG.md` ends at Session 130 (no 131). **Session 131 — the T-C11 core sync executed on the operator's 7-edge-package GO** — is durably recorded only in commit `c2b8e2e`'s message and `evidence/t-c11-core-sync-2026-10-01/`; neither living-state doc carries it.

> **POST-AUDIT CORRECTION (2026-10-01, recorded before the fix commit):** PROGRESS.md's 2026-09-30 header ALREADY DISCLOSES the Session-129 boundary ("per-session sections below end at Session 129 — sessions 130+ are tracked in TODO.md task entries + `.syllabai/tasks/` + repo ledgers"). F-3's PROGRESS leg is therefore a self-disclosed convention change, not a silent gap; this audit accepts it and the fix pass leaves PROGRESS ending at 129. The WORKLOG banner staleness, the WORKLOG_GAP staleness, sessions 79/104/105, and the Session-131 reconstruction remain fully valid findings and were fixed as specified.

**Resolution:** (a) rewrite the WORKLOG banner to describe actual contents; (b) update WORKLOG_GAP Tables A/B per its maintenance rule; (c) add Session 130 to PROGRESS and Session 131 to WORKLOG (or an explicit pointer from both to the evidence dir); (d) mark 79/104/105 in Table B (extended past 71) rather than leaving them unindexed.

### F-4 — MEDIUM: README "Start here" understates DECISIONS.md coverage ("ADR-001…022")

**Claim:** `README.md` Start-here item 4: "DECISIONS.md — architecture decision records (ADR-001…022; ADR-021 mirrored from its standalone file)".

**Reality:** DECISIONS.md contains full entries **ADR-001 through ADR-029** (29 `## ADR-` headers verified, including 023 LLM provider pool hardening, 024 InterventionRun, 025 Smart Mark product contract, 026 SME import surface, 027 teacher-marking-surface scoping, 028 Learning Hub import, 029 hub promotion). Additionally, **six** standalone ADR mirror files exist at the repo root (017, 020, 021, 023, 025, 027) — not just 021.

**Resolution:** reword to "ADR-001…029 (standalone mirrors: ADR-017/020/021/023/025/027; DECISIONS.md is canonical)".

### F-5 — MEDIUM: syllabai-web README contradicts the repo's post-ADR-029 charter

**Claim:** `syllabai-web` README opens "SyllabAI frontend — Next.js 16 / React 19 / TypeScript **Learner Workbench**" with a feature inventory headed "Current state, 2026-09-15" describing learner-facing surfaces (practice player, mastery map, tutor chat…).

**Reality:** per ADR-029 and the master README/PROJECT_CONTEXT, syllabai-web is the **internal teacher/ops console** (Smart Mark / marking queue home) with "product-surface development frozen". Recent web activity is consistent with the freeze (PR #12 touched `ClassIntelligenceView` + kg-explorer adapters — teacher-side), but the repo's own README still hands a new agent the pre-demotion charter.

**Resolution:** add an ADR-029 status banner to the web README (verbatim-preserving, house style) pointing to the hub for product surfaces.

### F-6 — MEDIUM: ADR-010 carries no supersession annotation

**Claim:** DECISIONS.md ADR-010 Status line reads only "Accepted"; the body asserts "Edexcel IAL Chemistry" as the authoritative Cycle-1 scope and "(34 rows…)".

**Reality:** ADR-019 (2026-09-11, same file) pivoted the subject to Edexcel IGCSE Chemistry (4CH1); F-1 shows the row count moved too. An agent following README's source hierarchy could read ADR-010's "authoritative execution scope" sentence without reaching ADR-019's correction. The house convention for superseded-scope text was established on 2026-09-15: a verbatim-preserving banner (applied to `DOCUMENTATION_CONTRADICTION_AUDIT_2026-09-07.md`).

**Resolution:** one-line Status amendment: "Accepted — subject scope superseded by ADR-019 (2026-09-11); Cycle-1 cut count superseded by the live tracker (36 rows as of 2026-10-01). Body preserved verbatim."

### F-7 — MEDIUM: TODO.md T-031's LLM-key re-provision note is stale; PROGRESS Session-67 self-contradicts on the same fact

**Claim:** TODO.md T-031 row (checked complete) still ends "Remaining for full closure: re-provision SYLLABAI_GROQ/GEMINI/OPENROUTER_API_KEY (+ optional embedding key) in the Render dashboard." PROGRESS.md's Session-67 header says "18/19 — the 1 miss is the LLM keys wiped… pending operator re-provision" while the Session-67 headline in the same file says "Render service verified LIVE… with the complete env contract (**incl. LLM keys**, answering the operator's question)".

**Reality:** production LLM calls demonstrably work as of 2026-09-22: sessions 116–118 executed the full Smart Mark LLM pipeline in production (refusal re-run → root-cause → budget fix → post-deploy re-run `q7|b` SMART_MARKED 3/5, sample 26/26 validation-passed), which is impossible without provisioned keys. The tutor 503 of Session 67 is not reproducible today (the hub streams tutor answers through core).

**Resolution:** strike the T-031 residual note (replace with the session-117 production-verification pointer); reconcile the two Session-67 statements in PROGRESS with a one-line correction note rather than a rewrite.

### F-8 — LOW: PROJECT_CONTEXT.md repo table omits `syllabai-ops`

The table holds 10 rows; the README repo map holds 11. `syllabai-ops` has zero mentions in PROJECT_CONTEXT.md. Since the file's role is the "living project state" orientation doc, add the ops row (automation & ops: dashboard refresh + Discord pulse via public Actions minutes).

### F-9 — LOW: relative-time staleness in TODO.md wave headers

"## Wave 0 — foundations (this week)" was written 2026-09-03; every wave is now historical (all Wave 0–2 rows checked, Wave 3 rows checked or explicitly open). Replace "(this week)" with the actual date or drop the parenthetical — the project's own audits flag exactly this class of drift for future agents.

### F-10 — LOW: MinerU/Surya status wording conflicts across four docs; parser README status row ~3 weeks stale

- Master README repo map: "GLM-OCR Python tooling (**MinerU/Surya deferred**)".
- `syllabai-parser` GitHub description: "**MinerU/Surya offline** for scans".
- PROJECT_CONTEXT.md: "opendataloader-pdf in-process; MinerU/Surya **offline**".
- MASTER_SPEC §3: "Python/Rust offline engines (MinerU / Surya / anydoc / pdf-inspector)".

"Deferred" (not yet integrated) and "offline" (integrated, runs offline) are opposite states; at most one is right. Related: the parser README's status row is dated "(Session 9)" while the repo's latest work is the 2026-09-25 G1–G6 extraction-grammar lanes — its self-description predates its own most significant recent work. Pick the true state from the parser repo and align all four.

## Non-findings (checked, verified accurate)

1. **Sep-7 audit remediations landed:** MASTER_SPEC line 271/455 make `SpecificationPoint` canonical with `LearningObjective` as legacy alias (F-1 of that audit); line 202 labels the former pseudo-repos as bounded-context modules (F-3); ADR-012 retitled "(public corpus repository tracked separately)" (F-4).
2. **Stack claims match code:** `pom.xml` = spring-boot-starter-parent **4.1.1**, `<java.version>` **25**, `spring-ai.version` **2.0.1** — matches every README/spec assertion of "Java 25 · Spring Boot 4.1 · Spring AI 2.0".
3. **`syllabai-hub.vercel.app` is live** (HTTP 200, 2026-10-01), and the hub README's ADR-029 narrative, core-proxy architecture, and no-LLM-keys-in-hub claim are internally consistent.
4. **ARCHITECTURE_REFERENCE_REGISTER.md** really does contain the OpenHuman entry dated ADDED 2026-09-05, as README says; **REPOSITORY_RESEARCH.md** really has "section 0 — SyllabAI integration verdicts (verified 2026-09-03)".
5. **AGENT.md's** 19 referenced files resolve: 18 in the master repo; `RAG_RETRIEVAL_CORPUS_GUIDANCE.md` exists in `syllabai-resources` exactly as AGENT.md states ("in `syllabai-resources`").
6. **Backlog artifacts exist** (`syllabai-master-project.xlsx` + TSV export + `syllabai-original-v0.tsv`), and the 09-07 claim "181 data rows = 173 F + 8 TFA" still matches the TSV (182 lines − header).
7. **PROGRESS "Session 2012-Jan"** (line 304) is an exam-session reference (Jan 2012 paper session), not a work-session numbering typo — dismissed as a finding.
8. **Web freeze claim is behaviorally consistent**: post-ADR-029 web PRs touch teacher/ops surfaces only (PR #12 file list verified).

## Recommended fix order

1. F-3 (session-chain repair) — protects the handoff invariant, the project's most-load-bearing documentation rule.
2. F-1 + F-6 (count alignment + ADR-010 banner) — one DECISIONS/README/§39a pass.
3. F-2 (spec §3 note or v1.3.1) — restores the spec's own authority claim.
4. F-4, F-5, F-7, F-8 (banner/reword pass) — mechanical, low risk.
5. F-9, F-10 (cosmetic alignment) — fold into the next doc-touching session.

All fixes are documentation-only; none touches code, migrations, gates, or evidence packs.
