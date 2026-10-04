#!/usr/bin/env python3
"""tc82_bank_impact.py — READ-ONLY production probe: does the June-2017 2C
19-mark route-hint artifact reach the BANK anywhere?

SELECT-ONLY (default_transaction_read_only=on session; Render-PAT direct
recipe, the m6_prod_verify precedent). Evidence saved for the pack:
  A. flyway head (census state)
  B. the ep-linkage rows for the 2016/2017 4CH0 papers (how the print
     lineage is banked)
  C. the 2017-06 + 2017-01 2C serving docs' checksums vs the corpus print
     pins (serving lineage byte-identity)
  D. every banked question row + scheme for the 2017-06 2C ep row (does
     ANY row read marks=19 / carry a duplicate (b)(ii) scheme?)
  E. global census pins (post-V61 baseline comparability)
"""
import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import pg8000.native

PROJ = Path("/home/z/my-project")
PAT = (PROJ / ".render_token").read_text().strip()
SVC = "srv-dagijie7bikc73bc0460"

PRINT_PINS = {
    "4CH0-2C-201701/ms.pdf": "d4690be69076196d6be0702ef94cf65b9ce50d1ec3882e35a4f2f427daf1875d",
    "4CH0-2C-201701/qp.pdf": "c71dfc1b6c8080931e8d94b3402d147329ea7689390a9399042738fff60f6cad",
    "4CH0-2C-201706/ms.pdf": "6204523f27e12b63aa27ef58623199dd2cb90deba968e3240a9d1aeeaba398e0",
    "4CH0-2C-201706/qp.pdf": "f5b49ec7c1b8cebf7b98299d46f13957677f955d095b52fd37202a124c447085",
}


def connect():
    env = json.load(urllib.request.urlopen(urllib.request.Request(
        f"https://api.render.com/v1/services/{SVC}/env-vars",
        headers={"Authorization": f"Bearer {PAT}", "Accept": "application/json"}),
        timeout=30))
    env = {i["envVar"]["key"]: i["envVar"]["value"] for i in env}
    u = urlparse(env["SYLLABAI_DATABASE_URL"].replace("jdbc:postgresql://",
                                                      "postgresql://", 1))
    con = pg8000.native.Connection(
        user=env["SYLLABAI_DATABASE_USERNAME"],
        password=env["SYLLABAI_DATABASE_PASSWORD"],
        host=u.hostname, port=u.port or 5432,
        database=u.path.lstrip("/"), ssl_context=True)
    con.run("SET default_transaction_read_only = on")
    return con


def main():
    out = {"print_pins": PRINT_PINS, "mode": "SELECT-ONLY"}
    con = connect()
    try:
        rows = con.run("SELECT version, description, success FROM "
                       "flyway_schema_history ORDER BY installed_rank "
                       "DESC LIMIT 3")
        out["flyway_head"] = [{"version": str(r[0]), "description": r[1],
                               "success": r[2]} for r in rows]

        rows = con.run(
            "SELECT ep.id::text, s.code, ep.series, ep.year, ep.paper_code, "
            "       ep.validation_state,"
            "       (SELECT count(*) FROM questions q "
            "         WHERE q.exam_paper_id = ep.id) AS n_q"
            "  FROM exam_papers ep JOIN subjects s ON s.id = ep.subject_id"
            " WHERE ep.year IN (2016, 2017)"
            " ORDER BY s.code, ep.year, ep.series, ep.paper_code")
        out["ep_linkage"] = [{"id": r[0], "subject": r[1], "series": r[2],
                              "year": r[3], "paper": r[4], "state": r[5],
                              "questions": r[6]} for r in rows]

        docs = con.run(
            "SELECT id::text, kind, validation_state, checksum, source_uri"
            "  FROM documents"
            " WHERE source_uri IN ('4CH0-2C-201706/ms.pdf',"
            "                      '4CH0-2C-201706/qp.pdf',"
            "                      '4CH0-2C-201701/ms.pdf',"
            "                      '4CH0-2C-201701/qp.pdf')")
        out["serving_docs"] = []
        for r in docs:
            pin = PRINT_PINS.get(r[4].split("/")[-2].upper().replace("4CH0", "4CH0")
                                 and r[4])
            out["serving_docs"].append({
                "id": r[0], "kind": r[1], "state": r[2], "checksum": r[3],
                "source_uri": r[4],
                "matches_corpus_print_pin": r[3] == PRINT_PINS.get(r[4])})

        ep_jun = [e for e in out["ep_linkage"]
                  if e["year"] == 2017 and e["series"] == "JUN"
                  and e["paper"] == "4CH0/2C"]
        out["bank_201706_2c"] = []
        for e in ep_jun:
            q = con.run(
                "SELECT q.id::text, q.external_ref, q.marks, q.active, "
                "       qv.id::text, qv.marks, qv.validation_state,"
                "       ms.id::text, ms.validation_state, "
                "       ms.extraction_method,"
                "       (SELECT count(*) FROM mark_points mp "
                "         WHERE mp.mark_scheme_id = ms.id),"
                "       (SELECT sum(mp.marks) FROM mark_points mp "
                "         WHERE mp.mark_scheme_id = ms.id)"
                "  FROM questions q"
                "  LEFT JOIN question_versions qv ON qv.question_id = q.id"
                "  LEFT JOIN mark_schemes ms ON ms.question_version_id = "
                "       qv.id"
                " WHERE q.exam_paper_id = :e ORDER BY q.external_ref",
                e=e["id"])
            out["bank_201706_2c"].append({
                "ep": e["id"], "rows": [
                    {"q": r[0], "ref": r[1], "q_marks": r[2],
                     "active": r[3], "qv": r[4], "qv_marks": r[5],
                     "qv_state": r[6], "ms": r[7], "ms_state": r[8],
                     "ms_method": r[9], "n_points": r[10],
                     "points_sum": r[11]} for r in q]})

        ep_jan = [e for e in out["ep_linkage"]
                  if e["year"] == 2017 and e["series"] == "JAN"
                  and e["paper"] == "4CH0/2C"]
        out["bank_201701_2c"] = []
        for e in ep_jan:
            q = con.run(
                "SELECT q.external_ref, q.marks, q.active"
                "  FROM questions q WHERE q.exam_paper_id = :e"
                " ORDER BY q.external_ref", e=e["id"])
            out["bank_201701_2c"].append({
                "ep": e["id"], "rows": [{"ref": r[0], "q_marks": r[1],
                                         "active": r[2]} for r in q]})

        rows = con.run(
            "SELECT (SELECT count(*) FROM exam_papers),"
            "       (SELECT count(*) FROM questions),"
            "       (SELECT count(*) FROM question_versions),"
            "       (SELECT count(*) FROM mark_schemes),"
            "       (SELECT count(*) FROM mark_points)")
        out["census"] = {"exam_papers": rows[0][0], "questions": rows[0][1],
                         "question_versions": rows[0][2],
                         "mark_schemes": rows[0][3],
                         "mark_points": rows[0][4]}

        # the mandate check: any bank row reading 19 for the 2017-06 2C?
        n19 = sum(1 for b in out["bank_201706_2c"] for r in b["rows"]
                  if r["q_marks"] == 19 or r["qv_marks"] == 19)
        out["bank_rows_reading_19"] = n19
        print(json.dumps(out, indent=1, default=str)[:200])
        print(f"\nVERDICT: bank rows reading 19 for 2017-06 2C = {n19}")
        print(f"census: {out['census']}")
        for d in out["serving_docs"]:
            print(f"  {d['source_uri']:22s} {d['kind']:14s} "
                  f"pin_match={d['matches_corpus_print_pin']}")
    finally:
        con.close()
    json.dump(out, open(PROJ / "scripts/tc82-lane/bank_impact.json", "w"),
              indent=1, default=str)
    print("saved -> scripts/tc82-lane/bank_impact.json")


if __name__ == "__main__":
    main()
