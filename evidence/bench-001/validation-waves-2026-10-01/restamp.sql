-- T-C41 paired rev re-stamp (WRITE — AGENT.md rule 2: run
-- scripts/campaign_db_preflight.py FIRST; verify current_database() is the
-- campaign DB). In-transaction with, or immediately after, the wave's
-- validate-all. Guarded: touches ONLY embed_rev=1 chunks of THIS paper's two
-- documents (the cut-over precedent — evidence/serving-rev2-restamp-cutover-
-- 2026-09-28 — and its recorded follow-up).
BEGIN;
update document_chunks c
set embed_rev = 2, embedded_at = now()
from documents d, exam_papers p
where (d.id = p.question_paper_document_id or d.id = p.mark_scheme_document_id)
  and p.paper_code = :paper_code
  and c.document_row_id = d.id
  and c.embedding is not null
  and c.embed_rev = 1
  -- serving-set safety: only rows that JUST became servable via validation
  and p.validation_state = 'VALIDATED';
-- assert: rowcount equals the prestate's at_rev1 column for this unit
COMMIT;
