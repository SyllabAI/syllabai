#!/usr/bin/env python3
"""fprod1_print_pass_questions.py — F-PROD-1 print pass, phase B (2026-10-04).

Question-level print evidence for the 7 P1 mismatch rows (priority 1).
For each row: extract the QP's printed question total ('Total for Question N is
X marks') and the MS's printed question total ('Total N' block marker), with
context quotes, so each verdict names the authoritative print with evidence.

Papers needing question-level work: the 5 mismatch papers. The 2019-06 4CH1-1C
QP is image-only -> OCR (tesseract). Read-only on the corpus.
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

CORPUS = Path("/home/z/my-project/repos/syllabai-pastpapers/past-papers/pearson-edexcel/international-gcse/chemistry")
OUT = Path("/home/z/my-project/scripts/fprod1_print_p1_evidence.json")

MISMATCH_ROWS = [
    ("4CH0/1C", "January 2013", "4ch0", "2013-01", "4CH0-1C", [2]),
    ("4CH0/1CR", "June 2013", "4ch0", "2013-06", "4CH0-1CR", [5, 7]),
    ("4CH0/2C", "January 2013", "4ch0", "2013-01", "4CH0-2C", [1]),
    ("4CH0/2CR", "June 2017", "4ch0", "2017-06", "4CH0-2CR", [4]),
    ("4CH1/1C", "June 2019", "4ch1", "2019-06", "4CH1-1C", [1, 13]),
]

QP_QTOTAL_RE = re.compile(r"total\s+for\s+question\s*:?\s*(\d{1,2})\s*[=:]\s*(\d{1,3})", re.I)
MS_QTOTAL_LINE_RE = re.compile(r"^\s*Total\s*:?\s*(\d{1,3})\s*$", re.I | re.M)


def align_ms_blocks(qp_totals: dict, ms_markers: list):
    """Map MS block markers onto QP questions. Returns list of
    (qp_questions_in_block, ms_value). Handles cumulative blocks (an MS block
    spanning several QP questions when the MS prints no separate total)."""
    qs = sorted(qp_totals)
    out = []
    qi = 0
    for v in ms_markers:
        if qi >= len(qs):
            out.append(([], v))
            continue
        acc = 0
        grp = []
        # a block matches the marker if the running sum of consecutive QP
        # questions equals it (1:1 being the single-question case)
        while qi < len(qs):
            acc += qp_totals[qs[qi]]
            grp.append(qs[qi])
            qi += 1
            if acc == v:
                break
            if acc > v:
                return None  # misalignment -> caller falls back
        else:
            if acc != v:
                return None
        out.append((grp, v))
        if qi < len(qs) and len(ms_markers) - len(out) > len(qs) - qi:
            continue
    if qi < len(qs):
        return None  # QP questions left uncovered
    return out


def pdf_text(p: Path, first=None, last=None) -> str:
    cmd = ["pdftotext", "-layout"]
    if first:
        cmd += ["-f", str(first), "-l", str(last or 9999)]
    cmd += [str(p), "-"]
    r = subprocess.run(cmd, capture_output=True, timeout=180)
    return r.stdout.decode("utf-8", "replace")


def ocr_pages(p: Path, first, last, dpi=200) -> str:
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-f", str(first),
                        "-l", str(last), str(p), f"{td}/pg"], check=True, timeout=900)
        parts = []
        for img in sorted(Path(td).glob("pg*")):
            r = subprocess.run(["tesseract", str(img), "-", "--psm", "6"],
                               capture_output=True, timeout=180)
            parts.append(r.stdout.decode("utf-8", "replace"))
        return "\n".join(parts)


def qp_question_totals(qp_text: str):
    return {int(q): int(v) for q, v in QP_QTOTAL_RE.findall(qp_text)}


def main():
    out = []
    for code, session, spec, sess_dir, variant, questions in MISMATCH_ROWS:
        d = CORPUS / spec / "past-papers" / sess_dir / variant
        rec = {"paper_code": code, "session_label": session, "questions": questions,
               "dir": str(d)}
        qp_txt = pdf_text(d / "qp.pdf")
        qp_ocr = False
        if len(qp_txt.strip()) < 200:
            qp_ocr = True
            pages = pdf_text(d / "qp.pdf", first=1, last=1)  # will be empty
            n_pages = int(subprocess.run(["pdfinfo", str(d / "qp.pdf")], capture_output=True,
                                         text=True).stdout.split("Pages:")[1].split()[0])
            qp_txt = ocr_pages(d / "qp.pdf", 1, n_pages)
        rec["qp_ocr"] = qp_ocr
        rec["qp_question_totals"] = qp_question_totals(qp_txt)

        ms_txt = pdf_text(d / "ms.pdf")
        ms_ocr = False
        if len(ms_txt.strip()) < 200:
            ms_ocr = True
            n_pages = int(subprocess.run(["pdfinfo", str(d / "ms.pdf")], capture_output=True,
                                         text=True).stdout.split("Pages:")[1].split()[0])
            ms_txt = ocr_pages(d / "ms.pdf", 1, n_pages)
        rec["ms_ocr"] = ms_ocr
        # MS per-question totals: 'Total' block markers in order; QP defines question
        # numbering, MS usually follows the same order. Record the ordered list.
        ms_totals = [int(v) for v in MS_QTOTAL_LINE_RE.findall(ms_txt)]
        rec["ms_total_markers_ordered"] = ms_totals

        for q in questions:
            # context quote around the QP question-total line
            m = None
            for mm in re.finditer(rf"total\s+for\s+question\s*:?\s*{q}\s*[=:]\s*(\d{{1,3}})", qp_txt, re.I):
                m = mm
            rec[f"qp_q{q}"] = {"total": int(m.group(1)) if m else None,
                               "quote": qp_txt[max(0, m.start()-60):m.end()+20].replace("\n", " ⏎ ") if m else None}

        alignment = align_ms_blocks(rec["qp_question_totals"], ms_totals)
        rec["ms_alignment"] = ([{"qp_questions": g, "ms_printed_total": v} for g, v in alignment]
                               if alignment else None)
        out.append(rec)
        print(f"{code} {session}: QP totals {sorted(rec['qp_question_totals'].items())} (ocr={qp_ocr})")
        for q in questions:
            print(f"   Q{q}: qp_print={rec[f'qp_q{q}']['total']} | {str(rec[f'qp_q{q}']['quote'])[:80]}")
        print(f"   MS markers {len(ms_totals)}: {ms_totals}")
        if alignment:
            for g, v in alignment:
                if any(q in g for q in questions):
                    print(f"   MS block {g} -> printed {v} {'<== covers target' if len(g) > 1 else ''}")
        else:
            print("   MS alignment FAILED — manual read needed")

    OUT.write_text(json.dumps(out, indent=1))
    print(f"== P1 evidence -> {OUT} ==")


if __name__ == "__main__":
    main()
