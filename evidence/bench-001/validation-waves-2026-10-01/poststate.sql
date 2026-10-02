-- T-C41 serving postcheck (read-only) — the empty-funnel numbers MUST move.
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
