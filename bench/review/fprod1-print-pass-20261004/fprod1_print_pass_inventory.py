#!/usr/bin/env python3
"""fprod1_print_pass_inventory.py — F-PROD-1 62-row print pass, phase A (2026-10-04).

For each of the 25 REVIEW_REQUIRED papers: resolve the corpus dir in
syllabai-pastpapers, VERIFY the manifest sha256 pins (G6 discipline), extract
page-1 printed identity (paper reference + series print — the folder-mislabel
audit's lesson: page-1 content is the identity), and read the two printed PAPER
totals (QP cover + MS cover). This is the evidence base for the 23
identity-mismatch rows (P2) and the substrate for the question-level pass
(P1/P3).

Print-only discipline (REPORT protocol item 4b): verdicts are made against the
corpus's checksum-verified PDFs, never against either import lineage.
Read-only on the corpus; no production contact.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

CORPUS = Path("/home/z/my-project/repos/syllabai-pastpapers/past-papers/pearson-edexcel/international-gcse/chemistry")
OUT = Path("/home/z/my-project/scripts/fprod1_print_inventory.json")

# (code, session_label, spec_dir, session_dir, variant_dir) — session_label as in the worksheet
ROSTER = [
    ("4CH0/1C", "January 2013", "4ch0", "2013-01", "4CH0-1C"),
    ("4CH0/1C", "June 2012", "4ch0", "2012-06", "4CH0-1C"),
    ("4CH0/1C", "June 2013", "4ch0", "2013-06", "4CH0-1C"),
    ("4CH0/1C", "June 2015", "4ch0", "2015-06", "4CH0-1C"),
    ("4CH0/1C", "June 2016", "4ch0", "2016-06", "4CH0-1C"),
    ("4CH0/1C", "June 2017", "4ch0", "2017-06", "4CH0-1C"),
    ("4CH0/1C", "June 2018", "4ch0", "2018-06", "4CH0-1C"),
    ("4CH0/1CR", "June 2013", "4ch0", "2013-06", "4CH0-1CR"),
    ("4CH0/1CR", "June 2016", "4ch0", "2016-06", "4CH0-1CR"),
    ("4CH0/1CR", "June 2017", "4ch0", "2017-06", "4CH0-1CR"),
    ("4CH0/2C", "January 2013", "4ch0", "2013-01", "4CH0-2C"),
    ("4CH0/2C", "June 2013", "4ch0", "2013-06", "4CH0-2C"),
    ("4CH0/2C", "June 2015", "4ch0", "2015-06", "4CH0-2C"),
    ("4CH0/2C", "June 2017", "4ch0", "2017-06", "4CH0-2C"),
    ("4CH0/2C", "June 2018", "4ch0", "2018-06", "4CH0-2C"),
    ("4CH0/2CR", "June 2013", "4ch0", "2013-06", "4CH0-2CR"),
    ("4CH0/2CR", "June 2016", "4ch0", "2016-06", "4CH0-2CR"),
    ("4CH0/2CR", "June 2017", "4ch0", "2017-06", "4CH0-2CR"),
    ("4CH1/1C", "June 2019", "4ch1", "2019-06", "4CH1-1C"),
    ("4CH1/1C", "June 2020", "4ch1", "2020-11", "4CH1-1C"),   # COVID: June 2020 series cancelled; corpus holds 2020-11 — page-1 identity decides usability
    ("4CH1/1C", "June 2024", "4ch1", "2024-06", "4CH1-1C"),
    ("4CH1/1CR", "June 2019", "4ch1", "2019-06", "4CH1-1CR"),
    ("4CH1/1CR", "June 2020", "4ch1", "2020-11", "4CH1-1CR"), # COVID mapping as above
    ("4CH1/2CR", "June 2019", "4ch1", "2019-06", "4CH1-2CR"),
    ("4CH1/2CR", "June 2023", "4ch1", "2023-06", "4CH1-2CR"),
]

TOTAL_RE = re.compile(r"total\s+marks?\s*[:\s]*\n?\s*(\d{2,3})", re.I)
TOTAL_INLINE_RE = re.compile(r"total\s+marks?\D{0,20}(\d{2,3})", re.I)
MS_PAPER_TOTAL_RE = re.compile(r"total\s+for\s+(?:the\s+)?paper\s*[^0-9\n]{0,30}(\d{2,3})", re.I)


def ocr_pdf(p: Path, first=None, last=None, dpi=200) -> str:
    """OCR fallback for image-only PDFs (tesseract via pdftoppm pages)."""
    import tempfile
    pages = f"{first or 1}-{last or 999}"
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-gray", "-f", str(first or 1),
                        "-l", str(last or 9999), str(p), f"{td}/pg"],
                       check=True, timeout=600)
        parts = []
        for img in sorted(Path(td).glob("pg*")):
            r = subprocess.run(["tesseract", str(img), "-", "--psm", "6"],
                               capture_output=True, timeout=120)
            parts.append(r.stdout.decode("utf-8", "replace"))
        return "\n".join(parts)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_pins(d: Path):
    text = (d / "manifest.yaml").read_text()
    pins = {}
    # capture per-material blocks: type: ... path: X.pdf ... sha256: Y
    for m in re.finditer(r"- type:\s*(\S+)\n(.*?)(?=\n- type:|\Z)", text, re.S):
        mat, body = m.group(1), m.group(2)
        pm = re.search(r"path:\s*(\S+)", body)
        sm = re.search(r"sha256:\s*([0-9a-f]{64})", body)
        if pm and sm:
            pins[pm.group(1)] = (mat, sm.group(1))
    return pins


def pdf_text(p: Path, first_pages=None) -> str:
    cmd = ["pdftotext", "-layout"]
    if first_pages:
        cmd += ["-f", "1", "-l", str(first_pages)]
    cmd += [str(p), "-"]
    r = subprocess.run(cmd, capture_output=True, timeout=120)
    return r.stdout.decode("utf-8", "replace")


def paper_total(text: str):
    """The printed paper total: prefer 'Total Marks N' on the cover pages."""
    head = text[:4000]
    m = TOTAL_RE.search(head) or TOTAL_INLINE_RE.search(head)
    if m:
        return int(m.group(1)), m.group(0).strip().replace("\n", " ")[:60]
    return None, None


def ms_paper_total(full_text: str):
    """MS prints the paper total as 'Total for paper N' (end grid)."""
    m = MS_PAPER_TOTAL_RE.search(full_text)
    if m:
        return int(m.group(1)), m.group(0).strip().replace("\n", " ")[:60]
    return None, None


def page1_identity(qp_text: str):
    head = qp_text[:2500]
    code = re.findall(r"4CH[01]\s*/\s*[12]C?R?", head)
    series = re.findall(r"(June|January|Summer|November|Autumn)\s*20(1\d|2\d)", head)
    date = re.findall(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday)\s+\d{1,2}\s+\w+\s+20\d\d", head)
    return {"refs": list(dict.fromkeys(code))[:4],
            "series_prints": [f"{a} {b}" for a, b in series][:4],
            "dated": date[:2]}


def main():
    out = []
    for code, session, spec, sess_dir, variant in ROSTER:
        d = CORPUS / spec / "past-papers" / sess_dir / variant
        rec = {"paper_code": code, "session_label": session, "dir": str(d)}
        if not d.is_dir():
            rec["error"] = "dir missing"
            out.append(rec)
            print(f"MISSING {code} {session}: {d}")
            continue
        pins = manifest_pins(d)
        pin_ok = {}
        for rel, (mat, want) in pins.items():
            have = sha256(d / rel)
            pin_ok[mat] = {"path": rel, "match": have == want}
            if have != want:
                rec.setdefault("pin_mismatch", []).append({"material": mat, "want": want, "have": have})
        rec["pins"] = pin_ok

        qp_txt_full = None
        qp_txt = pdf_text(d / "qp.pdf", first_pages=4)
        if len(qp_txt.strip()) < 200:  # image-only QP -> OCR the cover pages
            qp_txt = "[OCR] " + ocr_pdf(d / "qp.pdf", first=1, last=3)
            qp_txt_full_ocr = "[OCR-full]"
        else:
            qp_txt_full_ocr = None
        ms_txt_full = pdf_text(d / "ms.pdf")
        ms_txt = ms_txt_full[:6000]
        rec["qp_ocr"] = bool(qp_txt_full_ocr)
        rec["qp_identity"] = page1_identity(qp_txt)
        rec["ms_identity"] = page1_identity(ms_txt)
        qp_total, qp_ev = paper_total(qp_txt)
        ms_total, ms_ev = ms_paper_total(ms_txt_full)
        rec["qp_paper_total"] = {"printed": qp_total, "evidence": qp_ev}
        rec["ms_paper_total"] = {"printed": ms_total, "evidence": ms_ev}
        rec["totals_agree"] = (qp_total is not None and qp_total == ms_total)
        out.append(rec)
        flag = "" if rec["totals_agree"] else "  <-- TOTALS DIFFER/UNREAD"
        print(f"{code:8s} {session:13s} pins:{'ok' if all(v['match'] for v in pin_ok.values()) else 'MISMATCH'} "
              f"qp={qp_total} ms={ms_total} qp1={rec['qp_identity']['refs'][:2]} {rec['qp_identity']['series_prints'][:1]}{flag}")

    OUT.write_text(json.dumps(out, indent=1))
    print(f"== {len(out)} papers inventoried -> {OUT} ==")


if __name__ == "__main__":
    main()
