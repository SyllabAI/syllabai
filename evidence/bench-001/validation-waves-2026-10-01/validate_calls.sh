# T-C41 wave execution — TEACHER surface only (AGENT.md core rule 6).
# Auth: a TEACHER/ADMIN principal (the pilot-teacher credential, operator-held;
# T-C38). validate-all fails closed on FLAGGED/REJECTED/REVIEW_REQUIRED unless
# force=true — never force on the first pass; review the bridge findings first.
BASE=https://syllabai-core.onrender.com/api/v1/teacher/content
TOKEN=<teacher jwt>
for PAPER_ID in <paper_id from prestate>; do
  curl -sS -X POST "$BASE/exam-papers/$PAPER_ID/validate-all" \
    -H "Authorization: Bearer $TOKEN" | tee "validate-$PAPER_ID.json"
done
