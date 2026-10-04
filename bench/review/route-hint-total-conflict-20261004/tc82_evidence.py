#!/usr/bin/env python3
"""tc82_evidence.py — assemble the T-C82 pack evidence JSONs:
substrate_pins.json (G6 discipline: computed == manifest sha256) and
g5_receipt.json (the fix receipt: q5 before/after, the conflict receipt,
the whole-paper closure vs the QP prints and the paper-total witness).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CORPUS = Path("/home/z/my-project/repos/syllabai-pastpapers/"
              "past-papers/pearson-edexcel/international-gcse/chemistry/"
              "4ch0/past-papers")
G4_WT = "/home/z/my-project/repos/parser-g4base/tools"
G5_WT = "/home/z/my-project/repos/parser-g5/tools"
OUT = Path("/home/z/my-project/scripts/tc82-lane")

PAPERS = {
    "4CH0-2C-201701/ms.pdf": "d4690be69076196d6be0702ef94cf65b9ce50d1ec3882e35a4f2f427daf1875d",
    "4CH0-2C-201701/qp.pdf": "c71dfc1b6c8080931e8d94b3402d147329ea7689390a9399042738fff60f6cad",
    "4CH0-2C-201706/ms.pdf": "6204523f27e12b63aa27ef58623199dd2cb90deba968e3240a9d1aeeaba398e0",
    "4CH0-2C-201706/qp.pdf": "f5b49ec7c1b8cebf7b98299d46f13957677f955d095b52fd37202a124c447085",
}
QP_TOTALS_201706 = {"1": 4, "2": 11, "3": 11, "4": 19, "5": 15}
PAPER_TOTAL = 60


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_with(tools, pdf):
    code = f"""
import subprocess, sys, json
sys.path.insert(0, {tools!r})
from pdflane import parse_ms as pm
out = subprocess.run(['pdftotext', '-layout', {str(pdf)!r}, '-'],
                     capture_output=True, text=True).stdout
pages = [{{'page': i, 'text': t}} for i, t in enumerate(out.split(chr(12)), 1)
         if t.strip()]
r = pm.parse_pages(pages)
qs = {{}}
for q in r['questions']:
    qs[str(q['number'])] = {{'sum': q['sum_points'],
                             'total_row': q['total_row'],
                             'n_points': len(q['points']),
                             'conflict': q.get('_total_row_conflict')}}
print(json.dumps(qs))
"""
    res = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[-400:])
    return json.loads(res.stdout.strip().splitlines()[-1])


def main():
    # substrate pins (G6: computed == manifest)
    mapping = {
        "4CH0-2C-201701/ms.pdf": "2017-01/4CH0-2C/ms.pdf",
        "4CH0-2C-201701/qp.pdf": "2017-01/4CH0-2C/qp.pdf",
        "4CH0-2C-201706/ms.pdf": "2017-06/4CH0-2C/ms.pdf",
        "4CH0-2C-201706/qp.pdf": "2017-06/4CH0-2C/qp.pdf",
    }
    pins = {}
    for rel, want in PAPERS.items():
        got = sha256(CORPUS / mapping[rel])
        pins[rel] = {"corpus_path": mapping[rel],
                     "computed_sha256": got, "manifest_sha256": want,
                     "match": got == want}
    json.dump(pins, open(OUT / "substrate_pins.json", "w"), indent=1)
    print("substrate pins:", all(p["match"] for p in pins.values()))

    ms = str(CORPUS / "2017-06/4CH0-2C/ms.pdf")
    g4 = parse_with(G4_WT, ms)
    g5 = parse_with(G5_WT, ms)
    receipt = {
        "engine": {"g4_head": "9c538ad", "g5_head": "c507ff1"},
        "print_pin_ms": pins["4CH0-2C-201706/ms.pdf"],
        "g4_q5": g4["5"], "g5_q5": g5["5"],
        "g5_all_questions": {k: {"sum": v["sum"],
                                 "total_row": v["total_row"]}
                             for k, v in sorted(g5.items())},
        "qp_printed_totals": QP_TOTALS_201706,
        "paper_sum_g5": sum(v["sum"] for v in g5.values()),
        "qp_paper_total_witness": PAPER_TOTAL,
        "paper_closes": sum(v["sum"] for v in g5.values()) == PAPER_TOTAL,
        "all_questions_match_qp_prints": all(
            g5[k]["sum"] == QP_TOTALS_201706[k] for k in QP_TOTALS_201706),
        "jan2017_control": None,
    }
    jan = str(CORPUS / "2017-01/4CH0-2C/ms.pdf")
    jg4 = parse_with(G4_WT, jan)
    jg5 = parse_with(G5_WT, jan)
    receipt["jan2017_control"] = {
        "g4_q6": jg4["6"], "g5_q6": jg5["6"],
        "unchanged": jg4["6"]["sum"] == jg5["6"]["sum"] == 13,
        "b_cell_survives": jg5["6"]["conflict"] is None}
    json.dump(receipt, open(OUT / "g5_receipt.json", "w"), indent=1)
    print(json.dumps(receipt, indent=1)[:900])


if __name__ == "__main__":
    sys.exit(main())
