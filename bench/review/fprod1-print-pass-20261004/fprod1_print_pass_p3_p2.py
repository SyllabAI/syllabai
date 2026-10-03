#!/usr/bin/env python3
"""fprod1_print_pass_p3_p2.py — F-PROD-1 print pass, phase C (2026-10-04).

P3 (32 banked parse-side rows): verify the bank's served total against the
authoritative print (QP side for qp-only rows, MS side for ms-only rows, both
for gap rows), using the alignment machinery proven in the P1 pass.
P2 (23 identity rows): QP printed paper total vs MS printed paper total —
printed phrase where present ('Total for paper' / 'PAPER TOTAL:' / 'Total
marks'), else derived as the sum of the MS's printed per-question block
markers (the derivation is recorded in the evidence, not assumed).

Read-only on the corpus.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/z/my-project/scripts")
from fprod1_print_pass_questions import (  # noqa: E402
    CORPUS, QP_QTOTAL_RE, MS_QTOTAL_LINE_RE, align_ms_blocks, pdf_text)

P2_PATTERNS = [
    re.compile(r"total\s+for\s+(?:the\s+)?paper\s*[^0-9\n]{0,30}(\d{2,3})", re.I),
    re.compile(r"paper\s+total\s*:?\s*(\d{2,3})", re.I),
    re.compile(r"total\s+marks?\s*:?\s*(\d{2,3})", re.I),
]

WORKSHEET = "/home/z/my-project/repos/syllabai/bench/review/fprod1-bridge-review-20261003/fprod1_review_worksheet_v2_gap_accepted.csv"
OUT = Path("/home/z/my-project/scripts/fprod1_print_p3p2_evidence.json")


def banked(r):
    return any((r.get(k) or "").strip()
               for k in ("bank_marks", "bank_part_marks", "bank_state", "bank_active"))


def ms_paper_total(full_text: str):
    for pat in P2_PATTERNS:
        m = pat.search(full_text)
        if m:
            return int(m.group(1)), m.group(0).strip()[:60]
    return None, None


def work_rows():
    import csv
    rows = list(csv.DictReader(open(WORKSHEET)))
    out = [r for r in rows
           if (r["teacher_verdict"] or "").strip() == "" and r["finding_class"] != "identity-mismatch"
           and banked(r)]
    ident = [r for r in rows if r["finding_class"] == "identity-mismatch"]
    return out, ident


def paper_dir(code, session):
    spec = "4ch0" if code.startswith("4CH0") else "4ch1"
    sess = session.replace("June ", "2019-").replace("January ", "")
    # build from explicit maps to avoid mistakes
    year, mon = SESSION_MAP[(code, session)]
    return CORPUS / spec / "past-papers" / f"{year}-{mon}" / code.replace("/", "-")


SESSION_MAP = {
    ("4CH0/1C", "January 2013"): ("2013", "01"), ("4CH0/1C", "June 2012"): ("2012", "06"),
    ("4CH0/1C", "June 2013"): ("2013", "06"), ("4CH0/1C", "June 2015"): ("2015", "06"),
    ("4CH0/1C", "June 2016"): ("2016", "06"), ("4CH0/1C", "June 2017"): ("2017", "06"),
    ("4CH0/1C", "June 2018"): ("2018", "06"),
    ("4CH0/1CR", "June 2013"): ("2013", "06"), ("4CH0/1CR", "June 2016"): ("2016", "06"),
    ("4CH0/1CR", "June 2017"): ("2017", "06"),
    ("4CH0/2C", "January 2013"): ("2013", "01"), ("4CH0/2C", "June 2013"): ("2013", "06"),
    ("4CH0/2C", "June 2015"): ("2015", "06"), ("4CH0/2C", "June 2017"): ("2017", "06"),
    ("4CH0/2C", "June 2018"): ("2018", "06"),
    ("4CH0/2CR", "June 2013"): ("2013", "06"), ("4CH0/2CR", "June 2016"): ("2016", "06"),
    ("4CH0/2CR", "June 2017"): ("2017", "06"),
    ("4CH1/1C", "June 2019"): ("2019", "06"), ("4CH1/1C", "June 2020"): ("2020", "11"),
    ("4CH1/1C", "June 2024"): ("2024", "06"),
    ("4CH1/1CR", "June 2019"): ("2019", "06"), ("4CH1/1CR", "June 2020"): ("2020", "11"),
    ("4CH1/2CR", "June 2019"): ("2019", "06"), ("4CH1/2CR", "June 2023"): ("2023", "06"),
}


def extract_paper(code, session):
    d = paper_dir(code, session)
    qp_txt = pdf_text(d / "qp.pdf")
    if len(qp_txt.strip()) < 200:
        qp_txt = ""  # image-only; not the case for P3 papers (all have text bodies)
    qp_totals = {int(q): int(v) for q, v in QP_QTOTAL_RE.findall(qp_txt)}
    ms_full = pdf_text(d / "ms.pdf")
    ms_markers = [int(v) for v in MS_QTOTAL_LINE_RE.findall(ms_full)]
    ms_total, ms_ev = ms_paper_total(ms_full)
    qp_paper_total = None
    m = re.search(r"total\s+mark\s+for\s+this\s+paper\s+is\s+(\d{2,3})", qp_txt, re.I) or \
        re.search(r"total\s+marks?\s*[:\s]*(\d{2,3})", qp_txt[:4000], re.I) or \
        re.search(r"TOTAL FOR PAPER\s*=\s*(\d{2,3})", qp_txt, re.I)
    if m:
        qp_paper_total = int(m.group(1))
    alignment = align_ms_blocks(qp_totals, ms_markers)
    return {"dir": str(d), "qp_totals": qp_totals, "ms_markers": ms_markers,
            "ms_paper_total_printed": ms_total, "ms_paper_total_evidence": ms_ev,
            "qp_paper_total": qp_paper_total, "alignment": alignment}


def main():
    p3_rows, p2_rows = work_rows()
    papers = sorted({(r["paper_code"], r["session_label"]) for r in p3_rows} |
                    {(r["paper_code"], r["session_label"]) for r in p2_rows})
    cache, failures = {}, []
    for code, session in papers:
        try:
            cache[(code, session)] = extract_paper(code, session)
            e = cache[(code, session)]
            cov = "align-ok" if e["alignment"] else "ALIGN-FAIL"
            print(f"{code} {session}: qp={len(e['qp_totals'])}qs qp_total={e['qp_paper_total']} "
                  f"ms_printed={e['ms_paper_total_printed']} markers={len(e['ms_markers'])} [{cov}]")
        except SystemExit as ex:
            failures.append((code, session, str(ex)[:100]))
            print(f"{code} {session}: EXTRACTION FAILED {str(ex)[:80]}")

    json.dump({"papers": {f"{k[0]}|{k[1]}": v for k, v in cache.items()},
               "failures": failures}, open(OUT, "w"), indent=1)
    print(f"== evidence base -> {OUT} ({len(cache)} papers, {len(failures)} failures) ==")


if __name__ == "__main__":
    main()
