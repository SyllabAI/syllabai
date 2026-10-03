#!/usr/bin/env python3
"""fprod1_print_pass_p2.py — F-PROD-1 print pass, phase D: the 23 identity rows.

Four MS total-line formats exist across the 25-paper corpus:
  A  'Total   15'                (positional; 2013 era)
  B  'Total 5 marks'             (positional; 2015 era)
  C  'Total for Question 1 = 7 marks'   (numbered; 2018 era)
  D  'Total for Q1 = 7 marks'    (numbered; 2020 era)
plus printed paper totals: 'Total for paper N' / 'PAPER TOTAL: N MARKS' /
'Total marks N'. The 2016 family prints NO totals at all (verified pdftotext +
PyMuPDF + OCR-probe).

Verdict tiers (recorded per row):
  - paper-totals-verified              both paper totals PRINTED and equal
  - ms-total-derived-agrees            MS paper total derived as the sum of its
                                       printed per-question totals; equals the
                                       QP's printed paper total
  - qp-total-printed-ms-total-unprinted  the MS print carries no verifiable
                                       totals (2016 family) — narrowed open
Read-only on the corpus.
"""
import json
import re
import subprocess
from pathlib import Path

sys_path = "/home/z/my-project/scripts"
import sys
sys.path.insert(0, sys_path)
from fprod1_print_pass_p3_p2 import SESSION_MAP, CORPUS, P2_PATTERNS  # noqa: E402
from fprod1_print_pass_questions import QP_QTOTAL_RE, pdf_text  # noqa: E402

OUT = Path("/home/z/my-project/scripts/fprod1_print_p2_evidence.json")

MS_MARKS_PATTERNS = [
    re.compile(r"^\s*Total\s*:?\s*(\d{1,3})\s*$", re.I | re.M),                     # A
    re.compile(r"^\s*Total\s+(\d{1,3})\s+marks\s*$", re.I | re.M),                  # B
    re.compile(r"Total for Question\s+(\d{1,2})\s*[=:]\s*(\d{1,3})", re.I),         # C
    re.compile(r"Total for Q(\d{1,2})\s*[=:]\s*(\d{1,3})", re.I),                   # D
]

IDENTITY_PAPERS = [
    ("4CH0/1C", "June 2012"), ("4CH0/1C", "June 2013"), ("4CH0/1C", "June 2015"),
    ("4CH0/1C", "June 2016"), ("4CH0/1C", "June 2017"), ("4CH0/1C", "June 2018"),
    ("4CH0/1CR", "June 2013"), ("4CH0/1CR", "June 2016"), ("4CH0/1CR", "June 2017"),
    ("4CH0/2C", "June 2013"), ("4CH0/2C", "June 2015"), ("4CH0/2C", "June 2017"),
    ("4CH0/2C", "June 2018"),
    ("4CH0/2CR", "June 2013"), ("4CH0/2CR", "June 2016"), ("4CH0/2CR", "June 2017"),
    ("4CH1/1C", "June 2019"), ("4CH1/1C", "June 2020"), ("4CH1/1C", "June 2024"),
    ("4CH1/1CR", "June 2019"), ("4CH1/1CR", "June 2020"),
    ("4CH1/2CR", "June 2019"), ("4CH1/2CR", "June 2023"),
]


def ms_totals_for(code, session):
    year, mon = SESSION_MAP[(code, session)]
    d = CORPUS / ("4ch0" if code.startswith("4CH0") else "4ch1") / "past-papers" / f"{year}-{mon}" / code.replace("/", "-")
    full = pdf_text(d / "ms.pdf")
    rec = {"dir": str(d)}
    # numbered formats carry their question numbers
    numbered = {}
    for pat in MS_MARKS_PATTERNS[2:]:
        for q, v in pat.findall(full):
            numbered.setdefault(int(q), int(v))
    if numbered:
        rec["ms_q_totals"] = numbered
        rec["ms_format"] = "numbered"
        rec["ms_sum"] = sum(numbered.values())
    else:
        marks = []
        for pat in MS_MARKS_PATTERNS[:2]:
            marks = [int(v) for v in pat.findall(full)]
            if marks:
                rec["ms_format"] = "positional"
                break
        rec["ms_markers"] = marks
        rec["ms_sum"] = sum(marks) if marks else None
    for pat in P2_PATTERNS:
        m = pat.search(full)
        if m:
            rec["ms_paper_total_printed"] = int(m.group(1))
            rec["ms_paper_total_evidence"] = m.group(0).strip()[:60]
            break
    return rec


def qp_paper_total(code, session):
    year, mon = SESSION_MAP[(code, session)]
    d = CORPUS / ("4ch0" if code.startswith("4CH0") else "4ch1") / "past-papers" / f"{year}-{mon}" / code.replace("/", "-")
    qp = pdf_text(d / "qp.pdf", first=1, last=3)
    m = re.search(r"total\s+marks?\s*[:\s]*\n?\s*(\d{2,3})", qp, re.I) or \
        re.search(r"the\s+total\s+mark\s+for\s+this\s+paper\s+is\s+(\d{2,3})", qp, re.I)
    return int(m.group(1)) if m else None


def main():
    out = {}
    for code, session in IDENTITY_PAPERS:
        ms = ms_totals_for(code, session)
        qp_total = qp_paper_total(code, session)
        printed = ms.get("ms_paper_total_printed")
        derived = ms.get("ms_sum")
        if printed is not None:
            verdict = ("paper-totals-verified" if printed == qp_total
                       else "paper-totals-conflict")
            basis = f"both printed: QP {qp_total} / MS {printed}"
        elif derived is not None and derived == qp_total:
            verdict = "ms-total-derived-agrees"
            basis = (f"QP printed {qp_total}; MS paper total not printed; sum of MS "
                     f"printed per-question totals ({ms.get('ms_format')}) = {derived}")
        else:
            verdict = "qp-total-printed-ms-total-unprinted"
            basis = (f"QP printed {qp_total}; MS print carries no verifiable totals "
                     f"(markers={ms.get('ms_markers')} sum={derived})")
        out[f"{code}|{session}"] = {"qp_printed": qp_total, "verdict": verdict,
                                    "basis": basis, **ms}
        print(f"{code:8s} {session:13s} qp={qp_total} ms_printed={printed} "
              f"ms_sum={derived} -> {verdict}")
    OUT.write_text(json.dumps(out, indent=1))
    print(f"== P2 evidence -> {OUT} ==")


if __name__ == "__main__":
    main()
