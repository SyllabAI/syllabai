-- T-C41 serving postcheck (read-only) — the empty-funnel numbers MUST move.
-- Mirrors ChunkVectorRepository.searchServingEligible's gate (SCOPE_EXISTS_
-- VALIDATED) + diagnoseEmpty stages; drift-guarded by ChunkVectorRepository
-- DiagnoseTest in code.
with scope as (
  select c.id, c.embed_rev, c.embedding is not null as embedded
  from document_chunks c
  join documents d on d.id = c.document_row_id
  where (exists (select 1 from exam_papers p join subjects s on s.id = p.subject_id
                 where s.curriculum_version_id = (select id from curriculum_versions
                       order by created_at limit 1)
                   and p.validation_state = 'VALIDATED'
                   and (p.question_paper_document_id = d.document_id
                     or p.mark_scheme_document_id = d.document_id)))
     or (exists (select 1 from subjects s2
                 where s2.curriculum_version_id = (select id from curriculum_versions
                       order by created_at limit 1)
                   and s2.id = c.subject_id and d.validation_state = 'VALIDATED')))
select 'reachable_chunks' as metric, count(*) from scope where embedded
union all
select 'reachable_at_rev2', count(*) from scope where embedded and embed_rev = 2;
