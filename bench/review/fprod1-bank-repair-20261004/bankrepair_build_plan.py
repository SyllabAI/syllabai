#!/usr/bin/env python3
"""bankrepair_build_plan.py — builds the sha-pinned repair plan (SELECT-only work).

Inputs: probe_result.json + probe2_result.json (DB read-only state),
        corpus/ pdftotext prints (checksum-verified bytes == serving docs).
Output: bankrepair_plan.json (frozen evidence + before/after images + pins) + sha256.

Fail-closed: aborts (exit 1, no plan) unless every one of the 4 targets
classifies REPAIR under the 2026-10-02 laneD standard:
  exactly-1 row, qv.marks==1 AND q.marks==1, qv VALIDATED v1,
  own-variant attribution >= 0.90 with >= 0.02 margin (where an alternate
  variant's print bytes exist),
  QP echo (local print) == MS corroboration (DB serving chunks) == print-pass value.
"""
import json
import re
import hashlib
import sys

BASE = "/home/z/my-project/scripts/bankrepair20261004"

TARGETS = [
    {"paper": "4CH0/1C", "session": "June 2013", "qn": 10, "ref": "q10-6d968517",
     "print_pass": 13,
     "corpus_dir": "2013-06_4CH0-1C", "ms_sha": "5e73646769942e9cd5745673e2f1103233f2efd221e76ca89648187c8839ae9c",
     "qp_sha": "d9e5ef81faaccb51026796af0f05b86bb5c4cef991e4ab8a11157512d45ff189",
     "alt_dirs": ["2013-06_4CH0-1CR"], "alt_labels": ["4CH0/1CR June 2013"]},
    {"paper": "4CH0/1C", "session": "June 2017", "qn": 11, "ref": "q11-8b9f4957",
     "print_pass": 11,
     "corpus_dir": "2017-06_4CH0-1C", "ms_sha": "28008020cb90708bfe438195b02417a0bb7d57232e3094220ad808971aa29a75",
     "qp_sha": "a4f7eb2c6d9b93fe678416af270b578acc567fd8a47cdfae1f3d98c9b6e4813b",
     "alt_dirs": ["2017-06_4CH0-1CR"], "alt_labels": ["4CH0/1CR June 2017"]},
    {"paper": "4CH0/1C", "session": "June 2018", "qn": 12, "ref": "q12-23323bab",
     "print_pass": 11,
     "corpus_dir": "2018-06_4CH0-1C", "ms_sha": "5381d95189fe3d5b4958ac2d2ab5636735aa458e7dffbca94b44b16f1eaa9b30",
     "qp_sha": "1ff0f7955d3fa61a03d10af626a3a4daa733cd719a987d3be7a784839e8905ae",
     "alt_dirs": [], "alt_labels": [],
     "alt_note": "no 4CH0/1CR June 2018 print bytes exist in the corpus AND no such "
                 "exam_papers row exists in the DB (probe2 family census) — the "
                 "cross-variant discriminator is structurally absent; attribution "
                 "rests on the own-print score + qv.source_document_id provenance"},
    {"paper": "4CH0/1CR", "session": "June 2017", "qn": 11, "ref": "q11-b4e24b82",
     "print_pass": 9,
     "corpus_dir": "2017-06_4CH0-1CR", "ms_sha": "f1b6e819adc5bfbdfb64c095c7b53d18b4b95dcdc1c5b6a63218c52e1d300eac",
     "qp_sha": "fa8769bea3b6ef523b0e2c6a3f339fab8502ddf317ba7d9444cb8da034bc1c5b",
     "alt_dirs": ["2017-06_4CH0-1C"], "alt_labels": ["4CH0/1C June 2017"]},
]

STOP = set("""a an the and or of to in on for with is are was were be been it its this that
these those which what how why as at by from into onto under over about between each other
than then so such not no nor but if when while during before after above below up down out
off very can will just should now i you he she they we who whom whose there here where""".split())


def norm_tokens(s, extra_stop=frozenset()):
    if not s:
        return set()
    toks = re.findall(r"[a-z0-9]+", s.lower())
    return {t for t in toks if len(t) > 1 and t not in STOP and t not in extra_stop}


BOILER = re.compile(r"(?i)pearson|copyright|permission|editions|rectif|photocopy|"
                    r"publications|uk schools|www\.")
LATEX_CMD = re.compile(r"\\[a-zA-Z]+")


def content_tokens(bank_text):
    """Bank-side token set for attribution: drop non-content segments (publisher
    copyright footers carried by the OCR stems) and LaTeX command names — applied
    identically to every variant scoring, so discrimination (margin) is unaffected."""
    segs = [s for s in re.split(r"(?<=\.)\s+|\n+|(?=\(Total|(?=\$))", bank_text)
            if not BOILER.search(s)]
    latex_stop = frozenset(m.group()[1:].lower() for m in LATEX_CMD.finditer(bank_text))
    return norm_tokens(" ".join(segs), latex_stop)


def contain_score(bank_tokens, doc_text):
    doc_tokens = norm_tokens(doc_text)
    if not bank_tokens:
        return 0.0
    return len(bank_tokens & doc_tokens) / len(bank_tokens)


def fail(msg):
    print(f"ABORT: {msg}")
    sys.exit(1)


def main():
    probe = json.load(open(f"{BASE}/probe_result.json"))
    probe2 = json.load(open(f"{BASE}/probe2_result.json"))
    probe3 = json.load(open(f"{BASE}/probe3_result.json"))

    entries = []
    for t in TARGETS:
        # ── DB row (exactly 1, expected prestate) ────────────────────────
        cand = [p for p in probe["paper_rows"]
                if p["paper"] == f"{t['paper']} {t['session']}"][0]["all_questions"]
        rows = [r for r in cand if r["external_ref"] == t["ref"]]
        if len(rows) != 1:
            fail(f"{t['ref']}: expected exactly 1 row, got {len(rows)}")
        r = rows[0]
        if r["qv_marks"] != 1 or r["q_marks"] != 1:
            fail(f"{t['ref']}: bank prestate marks != 1 (qv={r['qv_marks']} q={r['q_marks']})")
        if r["qv_state"] != "VALIDATED" or r["version"] != 1:
            fail(f"{t['ref']}: unexpected version/state {r['version']}/{r['qv_state']}")
        if r["paper_state"] != "VALIDATED":
            fail(f"{t['ref']}: paper state {r['paper_state']}")

        # ── QP echo from the local print (mechanical re-parse) ───────────
        qp_txt = open(f"{BASE}/corpus/{t['corpus_dir']}/qp.txt").read()
        m = re.search(rf"total for question {t['qn']} = (\d+) marks", qp_txt, re.I)
        if not m:
            fail(f"{t['ref']}: QP echo line not found in {t['corpus_dir']}/qp.txt")
        echo = int(m.group(1))

        # ── MS corroboration from the DB serving chunks ──────────────────
        ms_doc = [d for d in probe["serving_doc_texts"]
                  if d["role"] == "ms" and d["paper"] == f"{t['paper']} {t['session']}"][0]
        if not ms_doc.get("checksum_matches_corpus"):
            fail(f"{t['ref']}: serving MS doc checksum mismatch vs corpus bytes")
        chunk_ev = []
        corr = None
        for c in ms_doc["chunks"]:
            txt = c["text"] or ""
            m1 = re.search(rf"question\s+{t['qn']}\s+printed total:\s*(\d+)\s*marks", txt, re.I)
            m2 = re.search(rf"total for question {t['qn']} = (\d+) marks", txt, re.I)
            if m1 or m2:
                corr = int((m1 or m2).group(1))
                chunk_ev.append({"chunk_id": c["chunk_id"], "chunk_index": c["chunk_index"],
                                 "value": corr})
        if corr is None:
            fail(f"{t['ref']}: no MS chunk corroboration for q{t['qn']}")
        if echo != corr or echo != t["print_pass"]:
            fail(f"{t['ref']}: evidence mismatch echo={echo} chunk={corr} print_pass={t['print_pass']}")

        # ── attribution (laneD substrate: INGESTED CHUNK TEXT per variant) ──
        stem = [s for s in probe["stems"] if s["external_ref"] == t["ref"]][0]
        bank_text = " ".join(filter(None, [stem["q_stem"], stem["qv_stem"]] +
                                    [p["prompt"] for p in stem["parts"]]))
        bank_tokens = content_tokens(bank_text)
        own_qp_chunks = [d for d in probe["serving_doc_texts"]
                         if d["role"] == "qp" and d["paper"] == f"{t['paper']} {t['session']}"][0]
        if not own_qp_chunks.get("checksum_matches_corpus"):
            fail(f"{t['ref']}: serving QP doc checksum mismatch vs corpus bytes")
        own_chunk_text = "\n".join((c["text"] or "") for c in own_qp_chunks["chunks"])
        own_score = contain_score(bank_tokens, own_chunk_text)
        alt_scores = {}
        for label in t.get("alt_labels", []):
            alt = [a for a in probe3.get("alts", []) if a["paper"] == label]
            if not alt or not alt[0].get("found"):
                alt_scores[label] = None
                continue
            a = alt[0]
            alt_scores[label] = round(contain_score(bank_tokens, a["chunk_text_joined"]), 4)
        margin = None
        if alt_scores:
            vals = [v for v in alt_scores.values() if v is not None]
            if vals:
                margin = round(own_score - max(vals), 4)
                if own_score < 0.90 or margin < 0.02:
                    fail(f"{t['ref']}: attribution gate own={own_score:.3f} margin={margin} "
                         f"alt={alt_scores}")
        elif not t["alt_dirs"]:
            if own_score < 0.90:
                fail(f"{t['ref']}: attribution gate own={own_score:.3f} (no alternate bytes; "
                     f"own-print floor still applies)")
        # secondary recorded leg: raw pdftotext substrate (layout noise expected)
        pdftotext_scores = {t["corpus_dir"]: round(contain_score(bank_tokens, qp_txt), 4)}
        for ad in t["alt_dirs"]:
            try:
                pdftotext_scores[ad] = round(
                    contain_score(bank_tokens, open(f"{BASE}/corpus/{ad}/qp.txt").read()), 4)
            except FileNotFoundError:
                pdftotext_scores[ad] = None

        # provenance (probe2)
        prov = [p for p in probe2["provenance"] if p["ref"] == t["ref"]][0]["rows"][0]

        entries.append({
            "ref": t["ref"], "paper": t["paper"], "session": t["session"], "qn": t["qn"],
            "question_id": r["question_id"], "qv_id": r["qv_id"],
            "paper_id": r["paper_id"],
            "before": {"q_marks": r["q_marks"], "qv_marks": r["qv_marks"],
                       "qv_version": r["version"], "qv_state": r["qv_state"],
                       "n_parts": r["n_parts"], "part_marks": r["part_marks"],
                       "n_schemes": r["n_schemes"], "n_mark_points": r["n_mark_points"],
                       "q_active": r["active"]},
            "after": {"q_marks": t["print_pass"], "qv_marks": t["print_pass"]},
            "evidence": {
                "print_pass_value": t["print_pass"],
                "qp_echo": {"value": echo, "source": f"corpus/{t['corpus_dir']}/qp.pdf",
                            "qp_sha256": t["qp_sha"],
                            "serving_qp_doc": prov["source_document_id"]},
                "ms_chunk_corroboration": {"value": corr, "chunks": chunk_ev,
                                           "serving_ms_doc_sha256": t["ms_sha"],
                                           "ms_doc_id": ms_doc["doc_id"]},
                "ms_local_print_block_total": t["print_pass"],
                "attribution": {"metric": "normalized-token containment of bank stem+part prompts "
                                "against each variant's INGESTED serving-QP chunk text (laneD substrate)",
                                "own": round(own_score, 4), "alternates": alt_scores,
                                "margin": margin,
                                "pdftotext_secondary": pdftotext_scores,
                                "gate": "own>=0.90 and margin>=0.02 where alternate chunk texts exist",
                                "alt_note": t.get("alt_note")},
                "qv_provenance": {"source_document_id": prov["source_document_id"],
                                  "extraction_method": prov["extraction_method"],
                                  "extraction_confidence": str(prov["extraction_confidence"]),
                                  "qv_created_at": str(prov["qv_created"])},
            },
            "scope": "marks only — parts, mark_schemes, mark_points, states, audit untouched",
        })

    # ── census pins (fresh, from probe) ──────────────────────────────────
    c = probe["census"]
    pins = {
        "papers_by_state": {r["st"]: r["n"] for r in c["papers"]},
        "question_versions": c["qv"],
        "questions": c["questions"],
        "question_parts": c["parts"],
        "mark_schemes": c["schemes"],
        "mark_points": c["mark_points"],
        "bridge_by_status": {r["st"]: r["n"] for r in c["bridge"]},
        "audit_max_at_probe": probe2["audit_tail"]["max"],
        "audit_tail_note": "last rows PLACE@2026-10-02T14:34:56 — no bank-relevant audit "
                           "movement since; V61 pins a monotonic audit floor (>= probe max), "
                           "not an exact max, because teacher traffic may append benign rows "
                           "between probe and deploy",
    }
    total_delta = sum(e["after"]["qv_marks"] - e["before"]["qv_marks"] for e in entries)
    if total_delta != 40:
        fail(f"total delta {total_delta} != 40")
    plan = {
        "lane": "F-PROD-1 bank-repair — the 4 print-pass defect rows (worksheet v3 "
                "defect(bank-repair lane))",
        "authority": "operator trace 1a1047d4ad41baf9 'repair the 4 bank entries'",
        "precedent": "bench/review/psaxis-review-2026-09-28/bank-defect-lane-20261002/ "
                     "(laneD method: variant-pinned printed evidence, double condition, "
                     "fail-closed tx, parts untouched)",
        "referrals": "fprod1-print-pass-20261004/REPORT.md P3 (4 defects) — records 2ffbbb3",
        "built_utc": probe2["probe2_utc"],
        "targets": entries,
        "census_pins": pins,
        "write_shape": {
            "transport": "core Flyway V61 (V60 census-gated precedent) — one tx, "
                         "double-condition-guarded UPDATEs x2 tables, in-tx before/after "
                         "sum self-measurement (delta must equal +40 exactly), RAISE on any "
                         "drift aborts the deploy",
            "guards": ["external_ref pinned", "id pinned", "marks = 1 pre-condition",
                       "exam_paper join pinned by paper_code + session_label",
                       "census pins exact (papers/qv/questions/parts/schemes/mp/bridge)",
                       "audit floor monotonic", "fresh-DB no-op on empty questions table"],
            "delta_marks_total": total_delta,
            "no_state_flips": True, "no_audit_rows": True, "parts_untouched": True,
        },
    }
    blob = json.dumps(plan, indent=1, sort_keys=True).encode()
    sha = hashlib.sha256(blob).hexdigest()
    open(f"{BASE}/bankrepair_plan.json", "wb").write(blob)
    print(f"plan -> {BASE}/bankrepair_plan.json")
    print(f"  sha256={sha}")
    for e in entries:
        ev = e["evidence"]
        print(f"  {e['ref']:14s} {e['paper']}/{e['session']} Q{e['qn']}: "
              f"1 -> {e['after']['qv_marks']} (echo {ev['qp_echo']['value']} == "
              f"chunk {ev['ms_chunk_corroboration']['value']}; attr own={ev['attribution']['own']})")
    print("CLASSIFICATION: 4 x REPAIR — plan pinned")


if __name__ == "__main__":
    main()
