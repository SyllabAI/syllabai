-- T-C41 wave prestate (read-only) — run per wave unit BEFORE validate-all.
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
join documents d on d.id = p.question_paper_document_id
              or d.id = p.mark_scheme_document_id
left join document_chunks c on c.document_row_id = d.id
where p.paper_code = :paper_code
group by 1, 2, 3, 4, 5 order by 4;
