-- T-C41 wave serving postcheck — 2026-10-02 CORRECTED VERSION (F-PROD-2).
-- Mirrors ChunkVectorRepository.searchServingEligible + CurriculumScopeResolver
-- .resolveActive as they exist on core main (9385011): the scope is the single
-- ACTIVE curriculum version (resolveActive refuses on zero or ambiguous ACTIVE
-- owners — the driver asserts count(ACTIVE)=1 before running this).
-- Diff vs evidence/bench-001/validation-waves-2026-10-01/poststate.sql: the two
-- `order by created_at limit 1` subselects become
-- `where status = 'ACTIVE' order by created_at desc limit 1`.
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
select 'reachable_chunks' as metric, count(*) as n from scope where embedded
union all
select 'reachable_at_rev2', count(*) from scope where embedded and embed_rev = 2;
