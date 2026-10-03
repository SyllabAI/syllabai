#!/usr/bin/env python3
"""fprod1_build_packet.py — build the F-PROD-1 teacher-review packet from the
two read-only probe results (no DB access here; pure file transform).

Outputs (records-repo pack + download copies):
  bench/review/fprod1-bridge-review-20261003/
    REPORT.md                        — the lane record + rosters + protocol
    fprod1_review_worksheet.csv      — 176 actionable findings, verdict columns
    dossiers/<code>-<session>.md     — 25 per-paper dossiers
  (scripts + probe JSONs are copied into the pack by the caller)
"""
import csv
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone

PACK = "/home/z/my-project/repos/syllabai/bench/review/fprod1-bridge-review-20261003"
DL = "/home/z/my-project/download"
TRACE = "1a101959c4bc29ad"

ACTIONABLE = {"mismatch", "qp-only", "ms-only", "gap", "identity-mismatch"}

VERDICTS = {
    "mismatch": "QP-print-right | MS-print-right | both-wrong(see notes)",
    "qp-only": "MS-print-verified | gap-accepted | defect(bank-repair lane)",
    "ms-only": "QP-print-verified | gap-accepted | defect(bank-repair lane)",
    "gap": "prints-verified-no-conflict | gap-accepted | defect(bank-repair lane)",
    "identity-mismatch": "paper-totals-verified | variant-misalignment-escalate | accepted",
}


def qnorm(s):
    if s is None:
        return None
    s = str(s).strip().upper()
    m = re.match(r"^Q?\s*(\d+)", s)
    return m.group(1) if m else s


def slug(code, session):
    return f"{code.replace('/', '-')}-{session.replace(' ', '-')}"


def warn_pattern(detail):
    s = re.sub(r"\d+", "#", str(detail)).strip()
    s = re.sub(r"\s+", " ", s)
    return s[:90]


def main():
    probe = json.load(open("/home/z/my-project/scripts/fprod1_probe_result.json"))
    bank = json.load(open("/home/z/my-project/scripts/fprod1_bank_result.json"))
    serving = {(r["paper_code"], r["session_label"]): r
               for r in json.load(open("/home/z/my-project/scripts/fprod1_serving_docs.json"))}
    recs = probe["review_required_records"]
    chunk_counts = probe["review_required_chunk_counts"]
    census = {(r["paper_code"], r["session_label"]): r for r in bank["paper_bank_census"]}
    bidx = defaultdict(list)
    for r in bank["banked_questions"]:
        bidx[(r["paper_id"], qnorm(r["external_ref"]))].append(r)

    os.makedirs(PACK, exist_ok=True)
    os.makedirs(os.path.join(PACK, "dossiers"), exist_ok=True)
    os.makedirs(DL, exist_ok=True)

    # ── worksheet rows + dossier data ────────────────────────────────────
    ws_rows = []
    totals = Counter()
    per_paper = []
    for rec in sorted(recs, key=lambda r: (r["paper_code"], r["session_label"])):
        paper_rows = []
        warn_by_src = defaultdict(Counter)
        matches = []
        cc = chunk_counts.get(rec["bridge_id"], {})
        for f in rec["review_findings"]:
            sev = f.get("severity")
            src = f.get("source")
            if sev == "warning":
                warn_by_src[src][warn_pattern(f.get("detail"))] += 1
                continue
            if sev == "match":
                matches.append(f.get("detail"))
                continue
            if sev not in ACTIONABLE:
                continue
            qn = qnorm(f.get("questionNumber"))
            brows = bidx.get((rec["paper_id"], qn)) or bidx.get(
                (rec["paper_id"], str(f.get("questionNumber"))))
            if brows:
                br = brows[0]
                bank_marks, part_marks = br["bank_marks"], br["part_marks"]
                bank_state = br["bank_state"]
                bank_active = br["active"]
                bver = br["bank_version"]
                if sev == "mismatch":
                    if bank_marks == f.get("qpMarks"):
                        note = f"bank serves {bank_marks} = the QP side (v{bver}, {bank_state})"
                    elif bank_marks == f.get("msMarks"):
                        note = f"bank serves {bank_marks} = the MS side (v{bver}, {bank_state})"
                    else:
                        note = (f"bank serves {bank_marks} — a THIRD total "
                                f"(QP {f.get('qpMarks')} / MS {f.get('msMarks')}); verify on prints")
                else:
                    note = (f"bank serves {bank_marks} (v{bver}, {bank_state}, "
                            f"{'active' if bank_active else 'INACTIVE'})")
            else:
                bank_marks = part_marks = bank_state = bank_active = ""
                note = ("question not in the structured bank — chunk-layer serving unaffected"
                        if f.get("severity") != "identity-mismatch"
                        else "paper-level identity row (both paper totals unreadable to the parser)")
            row = {
                "paper_code": rec["paper_code"], "session_label": rec["session_label"],
                "bridge_id": rec["bridge_id"], "question": f.get("questionNumber"),
                "finding_class": sev, "detail": f.get("detail"),
                "qp_marks": f.get("qpMarks"), "ms_marks": f.get("msMarks"),
                "bank_marks": bank_marks, "bank_part_marks": part_marks,
                "bank_state": bank_state, "bank_active": bank_active,
                "pre_adjudication": note,
                "teacher_verdict": "", "teacher_notes": "",
            }
            ws_rows.append(row)
            paper_rows.append((f, note))
            totals[sev] += 1
        per_paper.append((rec, paper_rows, warn_by_src, matches, cc))

    # ── worksheet CSV ────────────────────────────────────────────────────
    ws_path = os.path.join(PACK, "fprod1_review_worksheet.csv")
    cols = ["paper_code", "session_label", "bridge_id", "question", "finding_class",
            "detail", "qp_marks", "ms_marks", "bank_marks", "bank_part_marks",
            "bank_state", "bank_active", "pre_adjudication", "teacher_verdict",
            "teacher_notes"]
    with open(ws_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in ws_rows:
            w.writerow(r)

    # ── dossiers ─────────────────────────────────────────────────────────
    for rec, paper_rows, warn_by_src, matches, cc in per_paper:
        key = (rec["paper_code"], rec["session_label"])
        cen = census.get(key, {})
        sv = serving.get(key, {})
        L = []
        L.append(f"# {rec['paper_code']} — {rec['session_label']} — bridge REVIEW_REQUIRED dossier")
        L.append("")
        L.append(f"- **Bridge record:** `{rec['bridge_id']}` · created {rec['bridge_created_at']} · "
                 f"extraction {rec['extraction_methods']} · reconciliation **{rec['reconciliation_status']}** · "
                 f"{len(rec['review_findings'])} findings")
        L.append(f"- **IDENTITY SPLIT (the lane's sub-finding):** the bridge record anchors to the "
                 f"campaign-era import `QP {rec['qp_document_id']}` / `MS {rec['ms_document_id']}` — those rows "
                 f"are now {rec['qp_state']} ({cc.get('qp_chunks_str','?')} chunks) / {rec['ms_state']} "
                 f"({cc.get('ms_chunks_str','?')} chunks). The SERVING documents are a different import "
                 f"lineage: QP `{sv.get('qp_canon')}` {sv.get('qp_state')} v{sv.get('qp_ver')} "
                 f"({sv.get('qp_chunks')}/{sv.get('qp_rev2')} chunks@rev2) · MS `{sv.get('ms_canon')}` "
                 f"{sv.get('ms_state')} v{sv.get('ms_ver')} ({sv.get('ms_chunks')}/{sv.get('ms_rev2')} "
                 f"chunks@rev2). The findings below describe the bridge import's QP/MS DRAFTS — the printed "
                 f"papers are the same physical documents, so print-total verification remains valid against them.")
        L.append(f"- **Paper:** validation_state **{rec['paper_state']}** (serving at the chunk layer)")
        L.append(f"- **Bank census:** {cen.get('n_questions','?')} questions "
                 f"({cen.get('n_active','?')} active) · latest versions: {cen.get('n_qv_validated','?')} VALIDATED / "
                 f"{cen.get('n_qv_suggested','?')} SUGGESTED / {cen.get('n_qv_rejected','?')} REJECTED · "
                 f"total banked marks {cen.get('total_bank_marks','?')}")
        L.append(f"- **Review items (actionable):** {len(paper_rows)} · informational: "
                 f"{len(matches)} reconciliation matches · "
                 f"{sum(warn_by_src['QP_WARNING'].values())} QP warnings · "
                 f"{sum(warn_by_src['MS_WARNING'].values())} MS warnings")
        L.append("")
        L.append("## Review items (fill the verdict column; full-worksheet CSV carries the same rows)")
        L.append("")
        L.append("| Q | class | bridge detail | QP | MS | bank serves | pre-adjudication | verdict |")
        L.append("|---|---|---|---|---|---|---|---|")
        for f, note in paper_rows:
            bm = f.get("qpMarks"); ms = f.get("msMarks")
            L.append(f"| {f.get('questionNumber')} | **{f.get('severity')}** | {f.get('detail')} "
                     f"| {bm if bm is not None else '—'} | {ms if ms is not None else '—'} "
                     f"| {note.split(';')[0] if note else '—'} | {note} | ☐ |")
        L.append("")
        L.append(f"Verdict vocabulary: {VERDICTS.get(paper_rows[0][0]['severity'] if paper_rows else 'gap','—')}")
        L.append("")
        if matches:
            L.append(f"## Reconciliation matches ({len(matches)} — informational, totals agree)")
            L.append("")
            L.append("; ".join(m for m in matches[:30]) + (" …" if len(matches) > 30 else ""))
            L.append("")
        if warn_by_src:
            L.append("## Draft warnings (informational — parser notes on the QP/MS drafts, not itemized for verdict)")
            L.append("")
            for srcname, cnt in (("MS_WARNING", None), ("QP_WARNING", None)):
                c = warn_by_src.get(srcname)
                if not c:
                    continue
                L.append(f"**{srcname}** ×{sum(c.values())} — top patterns:")
                L.append("")
                for pat, n in c.most_common(6):
                    L.append(f"- ×{n} — `{pat}`")
                L.append("")
        open(os.path.join(PACK, "dossiers", slug(rec["paper_code"], rec["session_label"]) + ".md"),
             "w").write("\n".join(L) + "\n")

    # ── REPORT.md ────────────────────────────────────────────────────────
    n_actionable = len(ws_rows)
    by_class = Counter(r["finding_class"] for r in ws_rows)
    n_banked = sum(1 for r in ws_rows if r["bank_marks"] != "")
    today = datetime.now(timezone.utc).date().isoformat()
    R = []
    R.append(f"# F-PROD-1 — the 25-paper REVIEW_REQUIRED bridge review batch (teacher review packet)")
    R.append("")
    R.append(f"**Status:** REVIEW PACKET RECORDED — the item-by-item teacher review is the operator's act; "
             f"this packet is its designed input (ContentReviewService.validateAllForPaper's own guard language: "
             f"\"review its findings item-by-item\"). Zero production writes in this lane.")
    R.append(f"**Date:** {today} | **Authority:** operator directive \"{TRACE[-16:]}\" trace `{TRACE}` "
             f"(\"F-PROD-1's 25-paper review batch\"), closing the standing item from the wave-1 PRODUCTION run "
             f"(T-C41 ① close-out finding F-PROD-1, 2026-10-02).")
    R.append("**The finding being discharged (wave-1 REPORT):** \"25 papers serve while carrying unresolved "
             "REVIEW_REQUIRED bridge findings — 4CH0/1C ×7, 4CH0/1CR ×3, 4CH0/2C ×5, 4CH0/2CR ×3, 4CH1/1C ×3, "
             "4CH1/1CR ×2, 4CH1/2CR ×2. All 25 bridge REVIEW_REQUIRED papers in production are VALIDATED and "
             "serving … these papers either pre-date the bridge gate or were validated with force=true. The "
             "bridge findings need item-by-item workbench review by the teacher.\"")
    R.append("")
    R.append("## Method (read-only by construction)")
    R.append("")
    R.append("- Production is never touched: extraction ran on a **copy-on-write Neon review branch** "
             "(`fprod1-review-ro`, `br-purple-sun-a5huwldd`'s child `br-purple-sun-a5906j1t`), created from "
             "production, queried SELECT-only, and **deleted after extraction** — the branch's throwaway "
             "credential dies with it. The production roles' credentials were never revealed, reset, or used "
             "(the console API surface exposes no reveal/update routes for existing roles — probed and recorded).")
    R.append("- Transport quirks honored (records WORKLOG precedents): `api.neon.tech` has no public A record → "
             "control plane via `console.neon.tech/api/v2`; SQL over the Neon serverless HTTP `/sql` transport "
             "(psql absent). DB identity gates PASS: `current_database()=neondb`, `campaign_db_identity` row "
             "alive (`T-C04-CAMPAIGN`).")
    R.append("- **Production truth confirmed 2026-10-03:** 59 bridge records = 25 `REVIEW_REQUIRED` + 34 `OK` "
             "— the F-PROD-1 roster reproduces exactly, unchanged since the wave-1 finding.")
    R.append("- **NEW SUB-FINDING (F-PROD-1b, this lane) — the bridge is identity-detached from serving:** "
             "every one of the 25 REVIEW_REQUIRED records anchors to the campaign-era GLM-OCR import's "
             "document ids, and in ALL 25 cases those ids DIFFER from the paper's serving canonical document "
             "ids (`exam_papers.question_paper_document_id` / `mark_scheme_document_id`). The bridge-linked "
             "rows are superseded imports (REJECTED, 0 chunks); the serving docs are a different lineage, all "
             "VALIDATED and rev2-complete (0 anomalies across the 25). The drift is NOT REVIEW_REQUIRED-"
             "specific: 24 of the 34 OK records drift the same way (49/59 overall) — the re-ingest waves "
             "created fresh document identities while the bridge records stayed on the campaign import. "
             "Consequences: (a) the findings remain honest PRINT-time reconciliation notes (same printed "
             "papers), so the review protocol is unaffected; (b) the REVIEW_REQUIRED gate mechanically blocks "
             "validate-all on these papers forever, yet it guards an import that no longer serves — the gate "
             "is attached to the wrong lineage; (c) any future status-clearing lane must FIRST decide the "
             "identity semantics (re-point bridge records to serving docs vs mark them superseded vs rebuild "
             "bridges on the serving lineage) — recorded as an open design item for the operator, not "
             "decided by this lane.")
    R.append("- Scripts persisted beside this pack (`fprod1_bridge_probe.py`, `fprod1_bank_probe.py` + their "
             "JSON outputs `fprod1_probe_result.json` / `fprod1_bank_result.json`); no credentials anywhere in "
             "the pack (env-file pattern, session-only).")
    R.append("")
    R.append("## What the findings are (1,366 total across the 25 papers)")
    R.append("")
    R.append("| source | severity | n | meaning |")
    R.append("|---|---|---:|---|")
    R.append("| RECONCILIATION | qp-only | 121 | QP question total parsed, MS side unparsed |")
    R.append("| RECONCILIATION | match | 69 | QP vs MS totals agree (informational) |")
    R.append("| RECONCILIATION | mismatch | 7 | **QP vs MS totals genuinely conflict** |")
    R.append("| RECONCILIATION | identity-mismatch | 23 | paper-level identity rows (paper totals unreadable both sides) |")
    R.append("| RECONCILIATION | ms-only | 14 | MS total parsed, QP side unparsed |")
    R.append("| RECONCILIATION | gap | 11 | both sides unparsed |")
    R.append("| QP_WARNING | warning | 57 | parser notes on the QP draft (unclassified headings etc.) |")
    R.append("| MS_WARNING | warning | 1,064 | parser notes on the MS drafts (boilerplate/guidance vocabulary) |")
    R.append("")
    R.append(f"**Actionable review load: {n_actionable} rows** (mismatch {by_class.get('mismatch',0)} · "
             f"identity-mismatch {by_class.get('identity-mismatch',0)} · qp-only {by_class.get('qp-only',0)} · "
             f"ms-only {by_class.get('ms-only',0)} · gap {by_class.get('gap',0)}). "
             f"Of these, **{n_banked} sit on questions that exist in the structured bank** (each carries the "
             "bank's current served marks + state beside the two print totals); the other "
             f"{n_actionable - n_banked} describe parse gaps on questions that never entered the bank — "
             "chunk-layer serving is unaffected by them, and the verdict vocabulary lets the teacher accept "
             "a verified parse gap explicitly instead of leaving it open.")
    R.append("")
    R.append("## The review protocol")
    R.append("")
    R.append("1. **Work paper-by-paper** (`dossiers/`, ordered by priority below), or row-by-row in "
             "`fprod1_review_worksheet.csv` (same rows, verdict + notes columns blank for the teacher).")
    R.append("2. **Priority 1 — the 7 `mismatch` rows** (real print conflicts; one banked: 4CH1/1C June 2019 Q13, "
             "QP 12 vs MS 9, bank serves 12 = the QP side, VALIDATED): check the printed QP and MS for that "
             "question; the verdict names which print is authoritative.")
    R.append("3. **Priority 2 — the 23 `identity-mismatch` paper rows**: the parser could not read EITHER paper "
             "total, so the QP↔MS identity check never ran; verdict `paper-totals-verified` requires the two "
             "printed paper totals to agree (the 2026-10-02 folder-mislabel audit's lesson: checksums + page-1 "
             "content are the identity, folder names are not).")
    R.append("4. **Priority 3 — the 146 parse-side rows** (`qp-only`/`ms-only`/`gap`): for banked rows, verify "
             "the bank's total against the authoritative print; for unbanked rows, `gap-accepted` is an honest "
             "terminal verdict (the question was never extracted; nothing serves from it).")
    R.append("4b. **The identity split does NOT block the review:** the findings describe the bridge import's "
             "drafts of the same printed papers; verdicts are made against the PRINTS (or the corpus's "
             "checksum-verified PDFs), not against either import lineage.")
    R.append("5. **What happens after the verdicts:** the completed worksheet is recorded as data in the records "
             "repo. There is NO endpoint today that flips a bridge record's `reconciliation_status` — a status "
             "clearing, if the operator wants one, is a governed SQL action lane afterwards (the wave kit / "
             "bank-defect tx pattern), operator-gated, with the completed worksheet as its evidence base.")
    R.append("")
    R.append("## Cross-lane checks recorded")
    R.append("")
    R.append("- **Bank-defect repair lane (2026-10-02) overlap: NONE.** Its four repaired questions "
             "(4CH1/1CR 2013 Q9, 4CH1/1CR 2022 Q11, 4CH1/1CR 2016 Q1, 4CH1/1C 2016 Q10) sit on 4CH1 paper "
             "sessions that are NOT among these 25 REVIEW_REQUIRED papers (whose 4CH1 members are "
             "1C 2019/2020/2024, 1CR 2019/2020, 2CR 2019/2023). The two lanes are disjoint.")
    R.append("- **Serving state of the 25 (verified on the SERVING docs, not the bridge rows):** every paper "
             "is VALIDATED with both serving documents VALIDATED and every chunk embedded at rev2 (0 anomalies "
             "across the 25; per-paper counts in the dossiers) — they are live serving content, which is why "
             "the doctrine treats unreviewed findings as a governance debt, not a theoretical one. See the "
             "F-PROD-1b sub-finding above for the identity split behind this.")
    R.append("- **Structured-bank state: all 249 questions on these papers have `active=false`** — the papers "
             "serve at the CHUNK layer (tutor evidence), and none of their structured question items are live "
             "learner-facing rows. The bridge findings therefore guard chunk-layer correctness today, and the "
             "bank rows' future re-activation.")
    R.append("- **Workbench review surface is stale by design boundary:** its derived dataset "
             "(`data/review`, campaign-era, 34 REVIEW_REQUIRED sessions on a different code distribution) does "
             "not match production; this packet IS the fresh production truth. Refreshing the workbench read "
             "model from a production snapshot is a separate follow-up lane, not part of this review.")
    R.append("")
    R.append("## The 25-paper roster (bank census × bridge findings)")
    R.append("")
    R.append("| paper | session | questions (active) | qv VALIDATED | banked marks | actionable findings | dossier |")
    R.append("|---|---|---|---:|---:|---:|---|")
    for rec, paper_rows, warn_by_src, matches, cc in per_paper:
        cen = census.get((rec["paper_code"], rec["session_label"]), {})
        R.append(f"| {rec['paper_code']} | {rec['session_label']} | {cen.get('n_questions','?')} "
                 f"({cen.get('n_active','?')}) | {cen.get('n_qv_validated','?')} | "
                 f"{cen.get('total_bank_marks','?')} | {len(paper_rows)} | "
                 f"`{slug(rec['paper_code'], rec['session_label'])}.md` |")
    R.append("")
    open(os.path.join(PACK, "REPORT.md"), "w").write("\n".join(R) + "\n")

    # download copies for the operator
    shutil.copy(ws_path, os.path.join(DL, "fprod1_review_worksheet.csv"))
    shutil.copy(os.path.join(PACK, "REPORT.md"), os.path.join(DL, "fprod1_bridge_review_REPORT.md"))
    print(f"packet written: {PACK}")
    print(f"actionable rows: {n_actionable} | by class: {dict(by_class)} | banked: {n_banked}")
    print(f"dossiers: {len(per_paper)}")


if __name__ == "__main__":
    main()
