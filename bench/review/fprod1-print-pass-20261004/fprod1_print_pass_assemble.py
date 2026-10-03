#!/usr/bin/env python3
"""fprod1_print_pass_assemble.py — F-PROD-1 print pass, final assembly (2026-10-04).

Builds fprod1_review_worksheet_v3_print_pass.csv from v2 + the print-pass
evidence (P1 fprod1_print_p1_evidence.json, P3/P2 fprod1_print_p3p2_evidence.json,
P2 fprod1_print_p2_evidence.json + the targeted forensic reads recorded in
PRINT-PASS-REPORT-2026-10-04.md). Also emits the per-row verdict table for the
report. Read-only; no production contact; corpus read-only.
"""
import csv
import json
from pathlib import Path

WS_V2 = "/home/z/my-project/repos/syllabai/bench/review/fprod1-bridge-review-20261003/fprod1_review_worksheet_v2_gap_accepted.csv"
WS_V3 = "/home/z/my-project/repos/syllabai/bench/review/fprod1-bridge-review-20261003/fprod1_review_worksheet_v3_print_pass.csv"
P1 = json.load(open("/home/z/my-project/scripts/fprod1_print_p1_evidence.json"))
P3P2 = json.load(open("/home/z/my-project/scripts/fprod1_print_p3p2_evidence.json"))["papers"]
P2EV = json.load(open("/home/z/my-project/scripts/fprod1_print_p2_evidence.json"))

# ── P1 verdicts (from the P1 forensic pass; full reasoning in the REPORT) ──
P1_VERDICTS = {
    ("4CH0/1C", "January 2013", "2"): ("qp-print-authoritative",
        "QP prints 'Total for Question 2 = 6 marks'; the MS prints no separate Q2 total "
        "(Q1 block total is itself unprinted; the Q2 block's 'Total 15' is cumulative Q1+Q2 = 9+6). "
        "The bridge's 'MS 15' was a cumulative-block misread. QP per-question prints sum to 120 = printed paper total."),
    ("4CH0/1CR", "June 2013", "5"): ("both-prints-agree(11)",
        "QP prints 'Total for Question 5 = 11 marks'; MS Q5 block total prints 11 (aligned 1:1). "
        "The bridge's 'MS 16' was Q6's total — a cross-format alignment misparse."),
    ("4CH0/1CR", "June 2013", "7"): ("both-prints-agree(16)",
        "QP prints 16; MS Q7 block total prints 16. The bridge's 'MS 9' was Q9's total — misparse."),
    ("4CH0/2C", "January 2013", "1"): ("both-prints-agree(4)",
        "QP prints 'Total for Question 1 = 4 marks'; MS Q1 block total prints 4. "
        "The bridge's 'MS 8' was Q3's total — misparse."),
    ("4CH0/2CR", "June 2017", "4"): ("both-prints-agree(9)",
        "QP prints 9; MS Q4 block total prints 9. The bridge's 'MS 6' was Q2's/Q5's total — misparse."),
    ("4CH1/1C", "June 2019", "1"): ("both-prints-agree(4)",
        "QP prints 4; MS Q1 block total prints 4. The bridge's 'MS 9' was Q11's/Q12's total — misparse."),
    ("4CH1/1C", "June 2019", "13"): ("both-prints-agree(12)+bank-total-verified",
        "QP prints 'Total for Question 13 = 12 marks'; MS Q13 block total prints 12; bank serves 12. "
        "All three agree; the bridge's 'MS 9' was Q15's total — misparse."),
}

# ── P3 manual resolutions (the 6 rows the evidence-base pass flagged) ──
P3_MANUAL = {
    ("4CH0/1C", "June 2016", "10"): ("bank-total-verified",
        "gap row: bank 6 = QP print 6 (QP per-question totals complete for this paper)."),
    ("4CH0/1CR", "June 2016", "11"): ("bank-total-verified",
        "gap row: bank 15 = QP print 15."),
    ("4CH1/1C", "June 2019", "10"): ("bank-total-verified",
        "gap row: bank 7 = QP print 7; the MS Q10 block total (7) agrees — printed in the MS."),
    ("4CH0/1C", "June 2013", "10"): ("defect(bank-repair lane)",
        "ms-only row: bank serves 1; QP print = 13 and the MS Q10 block total = 13 agree "
        "(the bridge's ms=9 was Q11's total — misparse). Partial bank entry — bank-repair lane."),
    ("4CH0/1C", "June 2017", "11"): ("defect(bank-repair lane)",
        "ms-only row: bank serves 1; QP print = 11 (and the bridge's own MS parse 11 agrees with the QP print). "
        "The bank row is a 1-mark partial entry — refer to the bank-repair lane."),
    ("4CH0/1C", "June 2018", "12"): ("defect(bank-repair lane)",
        "ms-only row: bank serves 1; QP print = 11 (bridge MS parse 11 agrees). Partial bank entry — bank-repair lane."),
    ("4CH0/1CR", "June 2017", "11"): ("defect(bank-repair lane)",
        "ms-only row: bank serves 1; QP print = 9 (bridge MS parse 9 agrees). Partial bank entry — bank-repair lane."),
}


def main():
    rows = list(csv.DictReader(open(WS_V2)))
    fieldnames = list(rows[0].keys())
    # P2 completions: the four partial-print cases diagnosed in the targeted passes
    P2_OVERRIDES = {
        "4CH1/1C|June 2019": ("ms-total-derived-agrees",
            "QP prints 'TOTAL FOR PAPER = 110 MARKS' (end page; the cover box is image-only); "
            "MS paper total not printed; the MS's 15 printed per-question block totals sum to 110. "
            "QP print and MS-derived total agree."),
        "4CH0/1CR|June 2017": ("ms-total-derived-agrees",
            "QP prints 120; MS prints 14 of 15 block totals (sum 110); the unprinted block is Q14 "
            "(page-break artifact), whose QP print is 10: 110+10 = 120. No conflict anywhere both prints speak."),
        "4CH0/2C|June 2015": ("ms-total-derived-agrees",
            "QP prints 60; MS prints 5 of 6 block totals (sum 46); the unprinted block is Q6, whose "
            "QP print is 14: 46+14 = 60. No conflict anywhere both prints speak."),
        "4CH1/1C|June 2020": ("ms-total-derived-agrees",
            "QP prints 110; MS prints 6 of 10 block totals (sum 58); the unprinted blocks are Q5/Q7/Q8/Q9, "
            "whose QP prints are 12/14/14/12 (52): 58+52 = 110. No conflict anywhere both prints speak."),
    }
    tally = {}
    out_rows = []
    for r in rows:
        verdict = (r["teacher_verdict"] or "").strip()
        if verdict:  # gap-accepted rows from v2 carry forward unchanged
            out_rows.append(r)
            tally[verdict] = tally.get(verdict, 0) + 1
            continue
        key = (r["paper_code"], r["session_label"], r["question"])
        pk2 = (r["paper_code"], r["session_label"])
        note = ""
        if r["finding_class"] == "mismatch":
            verdict, note = P1_VERDICTS[key]
        elif r["finding_class"] == "identity-mismatch":
            ov = P2_OVERRIDES.get(f"{pk2[0]}|{pk2[1]}")
            if ov:
                verdict, note = ov
            else:
                ev = P2EV[f"{pk2[0]}|{pk2[1]}"]
                verdict = ev["verdict"]
                note = ev["basis"]
        else:  # banked parse-side
            man = P3_MANUAL.get((pk2[0], pk2[1], r["question"]))
            e = P3P2[f"{pk2[0]}|{pk2[1]}"]
            q = int(r["question"])
            if man:
                verdict, note = man
                if verdict == "bank-total-verified":
                    note = f"bank {r['bank_marks']} verified against the authoritative print. " + note
            else:
                qp_print = e["qp_totals"].get(str(q))
                bank = int(r["bank_marks"])
                if qp_print is not None and qp_print == bank:
                    verdict = "bank-total-verified"
                    note = f"bank {bank} = QP print {qp_print} ('Total for Question {q} = {qp_print} marks')."
                else:
                    verdict = "UNRESOLVED"
                    note = f"bank {bank} vs QP print {qp_print} — needs manual read"
        r["teacher_verdict"] = verdict
        r["teacher_notes"] = ("print pass 2026-10-04 (operator trace 1a103290c88606f9, corpus "
                              "checksum-verified PDFs per REPORT protocol 4b): " + note)
        out_rows.append(r)
        tally[verdict] = tally.get(verdict, 0) + 1

    with open(WS_V3, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    blank = [r for r in out_rows if not (r["teacher_verdict"] or "").strip()]
    print(f"v3 written: {len(out_rows)} rows; blank verdicts: {len(blank)}")
    for v, n in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  {n:3d}  {v}")


if __name__ == "__main__":
    main()
