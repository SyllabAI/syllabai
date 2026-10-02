#!/usr/bin/env python3
"""validation_wave_kit.py — T-C41 ①: turn the T-C40 validation worklist into
READY-TO-RUN operator waves.

Law of this lane (unchanged): content validation is the TEACHER's act through
the teacher surface (ContentController POST /api/v1/teacher/content/exam-papers/
{id}/validate-all — the designed batch instrument, T-C23 Option A), never an
agent assertion (AGENT.md core rule 6; S8D §6). This kit therefore composes the
waves, names the exact calls, provides the fail-closed preflight/poststate
probes AND the paired embed_rev re-stamp guard — and hands execution to the
operator.

The re-stamp pairing is NOT optional: the 2026-09-28 cut-over re-stamped ONLY
the 965 gate-eligible (already-VALIDATED) rev1 chunks 1→2; SUGGESTED chunks
left behind at embed_rev=1 will still not serve at CURRENT_EMBED_REV=2 after a
validate-all — the exact empty-funnel trap T-C23 lived through. Every wave
unit therefore carries: validate-all → paired re-stamp (embed_rev=1 rows of
that paper's QP/MS documents only) → serving postcheck.

Deterministic: reads the committed worklist.json + snapshot bytes only.
"""
import gzip, hashlib, json, os
from collections import defaultdict

SNAP = os.environ.get("BENCH_SNAPSHOT", "evidence/bench-001/snapshots/snap-006")
WORKLIST = os.environ.get("BENCH_WORKLIST", "evidence/bench-001/validation-worklist-2026-10-01/worklist.json")
OUT = os.environ.get("BENCH_OUT", "evidence/bench-001/validation-waves-2026-10-01")
WAVE1_SIZE = int(os.environ.get("BENCH_WAVE1_SIZE", "4"))
os.makedirs(OUT, exist_ok=True)

worklist = json.load(open(WORKLIST))
snapshot_version = worklist["snapshot"]

# merge QP/MS rows of the same paper into ONE wave unit (one exam_papers row,
# one validate-all call covers both the question-paper and mark-scheme side)
units = defaultdict(lambda: {"rows": [], "suggested": 0, "t1": 0, "t2": 0,
                             "classes": set(), "chunks": 0})
for row in worklist["rows"]:
    u = units[row["batch"]]
    u["rows"].append(row)
    u["suggested"] += row["SUGGESTED"]
    u["t1"] += row["gold_queries_tier1"]
    u["t2"] += row["gold_queries_tier2"]
    u["classes"].update(row["gold_classes"])
    u["chunks"] += row["chunks_total"]
# a unit is actionable if ANY of its rows still has SUGGESTED chunks
scored = []
for code, u in units.items():
    actionable = u["suggested"] > 0
    scored.append({"paper_code": code, "actionable": actionable, **u})
scored.sort(key=lambda u: (0 if u["actionable"] else 1,
                           -u["t2"], -u["t1"], -len(u["classes"]), u["paper_code"]))

wave1 = scored[:WAVE1_SIZE]

prestate_sql = """-- T-C41 wave prestate (read-only) — run per wave unit BEFORE validate-all.
-- :paper_code = the unit's code (e.g. '4CH1/2C')
select p.id as paper_id, p.paper_code, p.validation_state as paper_state,
       d.kind, d.validation_state as doc_state,
       count(c.id) as chunks,
       count(c.id) filter (where c.embedding is not null) as embedded,
       count(c.id) filter (where c.embedding is not null and c.embed_rev = 1) as at_rev1,
       count(c.id) filter (where c.embedding is not null and c.embed_rev = 2) as at_rev2,
       coalesce((select reconciliation_status from glm_ocr_bridge_records b
                 where b.paper_id = p.id limit 1), 'NO_BRIDGE') as bridge_status
from exam_papers p
join documents d on d.document_id = p.question_paper_document_id
              or d.document_id = p.mark_scheme_document_id
left join document_chunks c on c.document_row_id = d.id
where p.paper_code = :'paper_code'
group by 1, 2, 3, 4, 5 order by 4;
"""

validate_calls = """# T-C41 wave execution — TEACHER surface only (AGENT.md core rule 6).
# Auth: a TEACHER/ADMIN principal (the pilot-teacher credential, operator-held;
# T-C38). validate-all fails closed on FLAGGED/REJECTED/REVIEW_REQUIRED unless
# force=true — never force on the first pass; review the bridge findings first.
BASE=https://syllabai-core.onrender.com/api/v1/teacher/content
TOKEN=<teacher jwt>
for PAPER_ID in <paper_id from prestate>; do
  curl -sS -X POST "$BASE/exam-papers/$PAPER_ID/validate-all" \\
    -H "Authorization: Bearer $TOKEN" | tee "validate-$PAPER_ID.json"
done
"""

restamp_sql = """-- T-C41 paired rev re-stamp (WRITE — AGENT.md rule 2: run
-- scripts/campaign_db_preflight.py FIRST; verify current_database() is the
-- campaign DB). In-transaction with, or immediately after, the wave's
-- validate-all. Guarded: touches ONLY embed_rev=1 chunks of THIS paper's two
-- documents (the cut-over precedent — evidence/serving-rev2-restamp-cutover-
-- 2026-09-28 — and its recorded follow-up).
BEGIN;
update document_chunks c
set embed_rev = 2, embedded_at = now()
from documents d, exam_papers p
where (d.document_id = p.question_paper_document_id
    or d.document_id = p.mark_scheme_document_id)
  and p.paper_code = :'paper_code'
  and c.document_row_id = d.id
  and c.embedding is not null
  and c.embed_rev = 1
  -- serving-set safety: only rows that JUST became servable via validation
  and p.validation_state = 'VALIDATED';
-- assert: rowcount equals the prestate's at_rev1 column for this unit
COMMIT;
"""

poststate_sql = """-- T-C41 serving postcheck (read-only) — the empty-funnel numbers MUST move.
-- Mirrors ChunkVectorRepository.searchServingEligible's gate (SCOPE_EXISTS_
-- VALIDATED) + diagnoseEmpty stages; drift-guarded by ChunkVectorRepository
-- DiagnoseTest in code.
-- F-PROD-2 correction (wave-1 PRODUCTION 2026-10-02): the scope subselects
-- previously resolved the curriculum with `order by created_at limit 1`,
-- which on production lands on the ARCHIVED IAL-CHEM-2018 version and
-- reports reachable = 0 while 2,935 chunks serve. Serving truth is
-- CurriculumScopeResolver.resolveActive: ACTIVE-only candidates, refuse on
-- zero or ambiguous scope. The subselects now pin the ACTIVE version, and
-- the fail-closed census guard below refuses the whole probe unless exactly
-- one ACTIVE curriculum_version exists. Execution-proven reference:
-- evidence/bench-001/validation-wave-1-PRODUCTION-2026-10-02/
-- poststate-2026-10-02.sql (recorded reachable 2,935 / 2,935).
do $fprod2_scope_guard$
declare active_versions int;
begin
  select count(*) into active_versions from curriculum_versions where status = 'ACTIVE';
  if active_versions <> 1 then
    raise exception 'F-PROD-2 scope guard: resolveActive refuses on zero or ambiguous scope — found % ACTIVE curriculum_versions, expected exactly 1; resolve the scope by hand before re-running the postcheck', active_versions;
  end if;
end
$fprod2_scope_guard$;
with scope as (
  select c.id, c.embed_rev, c.embedding is not null as embedded
  from document_chunks c
  join documents d on d.id = c.document_row_id
  where (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
                 where s.curriculum_version_id = (select id from curriculum_versions
                       where status = 'ACTIVE' order by created_at desc limit 1)
                   and p.validation_state = 'VALIDATED'
                   and (p.question_paper_document_id = d.document_id
                     or p.mark_scheme_document_id = d.document_id)))
     or (exists (select 1 from subjects s2
                 where s2.curriculum_version_id = (select id from curriculum_versions
                       where status = 'ACTIVE' order by created_at desc limit 1)
                   and s2.id = c.subject_id and d.validation_state = 'VALIDATED')))
select 'reachable_chunks' as metric, count(*) from scope where embedded
union all
select 'reachable_at_rev2', count(*) from scope where embedded and embed_rev = 2;
"""

def fmt_unit(u, idx):
    rows = "; ".join(f"{r['kind']} chunks {r['chunks_total']} (SUGGESTED {r['SUGGESTED']})" for r in u["rows"])
    return (f"{idx}. **{u['paper_code']}** — {rows}. Wave unlock: **{u['t1']} tier-1** + "
            f"**{u['t2']} tier-2** gold queries across {len(u['classes'])} classes "
            f"({', '.join(sorted(u['classes']))}).")

md = f"""# Validation waves — wave 1 kit (T-C41, 2026-10-01, snapshot {snapshot_version})

**Status:** READY FOR OPERATOR EXECUTION — composed deterministically from the committed
T-C40 worklist; every number traceable to snapshot bytes. **No validation is asserted here**
(AGENT.md core rule 6): the validate-all calls are teacher-surface actions (pilot-teacher
credential, operator-held per T-C38).

## Wave 1 units (top {WAVE1_SIZE} by gold unlock, QP+MS merged — one validate-all per paper)

""" + "\n".join(fmt_unit(u, i + 1) for i, u in enumerate(wave1)) + f"""

Combined wave-1 reach: **{sum(u['t1'] for u in wave1)} tier-1 + {sum(u['t2'] for u in wave1)} tier-2 gold queries** become
potentially reachable — the precondition for any recall movement the next §8.1-governed run can measure.

## Execution order per unit (binding)

1. **Prestate probe** (`prestate.sql`, read-only): record paper_id, paper/doc validation states,
   chunk/embed/rev census, bridge reconciliation status. If `bridge_status = REVIEW_REQUIRED`:
   STOP — review findings item-by-item via the workbench; only `force=true` overrides, and that
   is an operator judgment, never a default.
2. **validate-all** (teacher auth; `validate_calls`): `POST /api/v1/teacher/content/exam-papers/{{id}}/validate-all`.
   Fail-closed on FLAGGED/REJECTED papers or REJECTED/FLAGGED versions — resolve first.
3. **Paired rev re-stamp** (`restamp.sql`, guarded write): re-stamps ONLY this paper's
   `embed_rev = 1` embedded chunks to `embed_rev = 2`, and only when the paper row is now
   VALIDATED. Skip silently-degenerates: if prestate `at_rev1 = 0`, no re-stamp is needed
   (rev2-born corpus serves immediately). AGENT.md rule 2: `scripts/campaign_db_preflight.py`
   runs before any write.
4. **Serving postcheck** (`poststate.sql`, read-only): `reachable_at_rev2` MUST increase by the
   unit's expected chunk count (prestate SUGGESTED ∩ embedded). A zero delta = the T-C23
   empty-funnel trap — stop, diagnose via `X-Search-Empty-Cause`/`diagnoseEmpty` before the
   next unit. The probe is now self-guarding (F-PROD-2): it refuses unless exactly one ACTIVE
   curriculum_version exists, and its scope subselects pin the ACTIVE version — a scope
   resolved any other way reads reachable = 0 against a serving corpus (recorded on
   production, 2026-10-02).
5. **Evidence pack** per wave: `prestate.json`, `validate-<paperId>.json` (the API's BatchResult),
   restamp rowcount, `poststate.json`, `SHA256SUMS` — under
   `evidence/bench-001/validation-wave-1-<date>/` (house pattern).

## Why this exact order (the three recorded traps)

- **The rev1 trap:** CURRENT_EMBED_REV = 2 (core `ChunkVectorRepository`); the 09-28 cut-over
  re-stamped only the 965 already-VALIDATED chunks. A validate-all WITHOUT the paired re-stamp
  validates the paper but serves nothing — the empty funnel returns with a new cause.
- **The REVIEW_REQUIRED trap:** bridge records with reconciliation findings block validate-all
  unless forced; forcing past unreviewed findings is how mis-validated content enters the
  serving pool. First pass never forces.
- **The scope trap (F-PROD-2, wave-1 PRODUCTION 2026-10-02):** a curriculum scope resolved by
  `order by created_at limit 1` lands on the ARCHIVED IAL-CHEM-2018 version on production and
  reports reachable = 0 while 2,935 chunks serve. Serving truth is
  `CurriculumScopeResolver.resolveActive` — ACTIVE-only, exactly one, else refuse. The
  generated `poststate.sql` now enforces both (fail-closed census guard + ACTIVE-pinned
  subselects).

## After wave 1

- Re-run `bench/validation_worklist.py` against a FRESH snapshot re-freeze (the worklist's
  SUGGESTED counts are snapshot bytes, not live DB) OR rely on the live poststate probes;
  then the **Run005C re-record** (run-005-c-r8) measures the reachable-pool delta against the
  §8.1 v1.1 VALIDATED bars. Waves and re-records alternate: validate → re-freeze/re-record →
  read the bars → validate the next wave.
"""
open(f"{OUT}/WAVES.md", "w").write(md)
open(f"{OUT}/prestate.sql", "w").write(prestate_sql)
open(f"{OUT}/validate_calls.sh", "w").write(validate_calls)
open(f"{OUT}/restamp.sql", "w").write(restamp_sql)
open(f"{OUT}/poststate.sql", "w").write(poststate_sql)
with open(f"{OUT}/SHA256SUMS", "w") as f:
    for fn in ("WAVES.md", "prestate.sql", "validate_calls.sh", "restamp.sql", "poststate.sql"):
        h = hashlib.sha256(open(f"{OUT}/{fn}", "rb").read()).hexdigest()
        f.write(f"{h}  {fn}\n")
print("wave kit written to", OUT)
for i, u in enumerate(wave1, 1):
    print(f"  wave-1 unit {i}: {u['paper_code']} t1={u['t1']} t2={u['t2']} suggested={u['suggested']} classes={len(u['classes'])}")
