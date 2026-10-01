#!/usr/bin/env python3
"""Regression tests for card_sheet_header_parser (the Task-54 regex-fallback fix).

Ground truths:
  * the 3 real no-linkage card headers are VERBATIM from
    records bench/evidence/flagged3-source-verify-2026-09-28/flagged3_canonical.json
    (cards #207/#278/#291 of the pinned teacher card review sheet);
  * the pinned sheet's broken renderings were
    '#### #207 · Q? · 0 marks · ?' (#207), same shape for #278 and #291;
  * the true values (from the cards' own textBlocks and verified against the
    bank in Task 54): #207 -> Q3 / 11 marks / STRUCTURED,
    #278 -> Q1 / 5 / STRUCTURED, #291 -> Q1 / 4 / STRUCTURED.
Run: python3 test_card_sheet_header_parser.py  (stdlib unittest, no deps)
"""
from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

import card_sheet_header_parser as P

# Verbatim from records bench/evidence/flagged3-source-verify-2026-09-28/flagged3_canonical.json
REAL_NO_LINKAGE = [
    ("#207", "1c15d529", "Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: STRUCTURED | stem: This question is about copper and its compounds.",
     dict(code="4CH1/2C", session="Jan 2020", qnum="Q3", marks=11, qtype="STRUCTURED")),
    ("#278", "ee882008", "Q-Card | 4CH1/2CR | Jun 2020 | Q1 | marks: 5 | type: STRUCTURED | stem: Answer ALL questions. 1 The diagram shows some pieces of apparatus. A B C D",
     dict(code="4CH1/2CR", session="Jun 2020", qnum="Q1", marks=5, qtype="STRUCTURED")),
    ("#291", "1195ca6c", "Q-Card | 4CH1/2CR | Jan 2023 | Q1 | marks: 4 | type: STRUCTURED | stem: Answer ALL questions. Some questions must be answered with a cross in a box .",
     dict(code="4CH1/2CR", session="Jan 2023", qnum="Q1", marks=4, qtype="STRUCTURED")),
]

# The exact broken lines the old generator produced for these cards (pinned sheet)
PINNED_BROKEN = {
    "#207": "#### #207 · Q? · 0 marks · ?",
    "#278": "#### #278 · Q? · 0 marks · ?",
    "#291": "#### #291 · Q? · 0 marks · ?",
}

SPEC_PRESENT = ("Q-Card | 4CH1/1C | Jun 2025 | Q12 | marks: 8 | type: MCQ "
                "| spec: 1.18, 1.19 | stem: What is the formula of calcium chloride?")


class TestRealNoLinkageHeaders(unittest.TestCase):
    """THE fix: headers without a spec segment parse ALL present fields."""

    def test_true_values_parsed(self):
        for seq, uuid, line, exp in REAL_NO_LINKAGE:
            with self.subTest(card=seq):
                f = P.parse_card_header(line)
                for k, v in exp.items():
                    self.assertEqual(f[k], v, f"{seq} field {k}")
                self.assertIsNone(f["spec"], f"{seq} spec must be None (honest no-linkage)")
                self.assertTrue(f["stem"], f"{seq} stem must survive")

    def test_renderer_emits_true_header_not_qmark(self):
        for seq, uuid, line, exp in REAL_NO_LINKAGE:
            with self.subTest(card=seq):
                f = P.parse_card_header(line)
                n = int(seq[1:])
                out = P.render_sheet_header(n, f)
                self.assertNotEqual(out, PINNED_BROKEN[seq],
                                    "must never reproduce the pinned broken rendering")
                self.assertEqual(out, f"#### {seq} · {exp['qnum']} · {exp['marks']} marks · {exp['qtype']}")

    def test_spec_note_wording(self):
        f = P.parse_card_header(REAL_NO_LINKAGE[0][2])
        self.assertEqual(P.render_spec_segment(f), P.NO_SPEC_NOTE)
        self.assertEqual(P.NO_SPEC_NOTE, "(none — card has no spec linkage)")


class TestSpecPresentHeaders(unittest.TestCase):
    def test_full_parse_with_spec(self):
        f = P.parse_card_header(SPEC_PRESENT)
        self.assertEqual(f["code"], "4CH1/1C")
        self.assertEqual(f["session"], "Jun 2025")
        self.assertEqual(f["qnum"], "Q12")
        self.assertEqual(f["marks"], 8)
        self.assertEqual(f["qtype"], "MCQ")
        self.assertEqual(f["spec"], "1.18, 1.19")
        self.assertEqual(f["stem"], "What is the formula of calcium chloride?")
        self.assertEqual(P.render_sheet_header(298, f),
                         "#### #298 · Q12 · 8 marks · MCQ")
        self.assertEqual(P.render_spec_segment(f), "1.18, 1.19")

    def test_empty_spec_is_honest_none(self):
        line = ("Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: STRUCTURED "
                "| spec: | stem: x")
        f = P.parse_card_header(line)
        self.assertIsNone(f["spec"])
        self.assertEqual(P.render_spec_segment(f), P.NO_SPEC_NOTE)


class TestFailClosed(unittest.TestCase):
    def _raises(self, line, why):
        with self.assertRaises(P.HeaderParseError, msg=why):
            P.parse_card_header(line)

    def test_missing_marks(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | Q3 | type: STRUCTURED", "no marks")

    def test_missing_qnum(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | marks: 11 | type: STRUCTURED", "no qnum")

    def test_missing_type(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11", "no type")

    def test_wrong_marker(self):
        self._raises("Q-CardX | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: S", "marker")

    def test_non_integer_marks(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 1a | type: S", "marks int")

    def test_duplicate_marks(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | marks: 12 | type: S", "dup")

    def test_unrecognized_bare_segment(self):
        self._raises("Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: S | ??? | stem: x", "junk")

    def test_renderer_never_fabricates(self):
        with self.assertRaises(P.HeaderParseError):
            P.render_sheet_header(1, {"qnum": None, "marks": None, "qtype": None})

    def test_stem_with_pipes_survives(self):
        line = "Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: STRUCTURED | stem: A | B | C"
        f = P.parse_card_header(line)
        self.assertEqual(f["stem"], "A | B | C")


class TestNoRegressionToFabrication(unittest.TestCase):
    """Guard: the module must contain NO '?'-fabrication fallback path."""

    def test_no_qmark_fallback_in_module(self):
        # scan CODE string constants only (docstrings legitimately document the old bug)
        consts = P.code_constants_without_docstrings(P.__file__)
        offenders = [c for c in consts if "Q?" in c]
        self.assertEqual(offenders, [],
                         f"module code must never fabricate the 'Q?' placeholder; found in: {offenders}")

    def test_smoke_cli_runs_on_real_headers(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            P.__dict__  # touch module
        # run the __main__ body via exec of the documented real headers
        import runpy, sys, tempfile, os
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
            tf.write("\n".join(r[2] for r in REAL_NO_LINKAGE) + "\n")
            path = tf.name
        try:
            sys.argv = [P.__file__, path]
            with redirect_stdout(io.StringIO()) as out:
                try:
                    runpy.run_path(P.__file__, run_name="__main__")
                except SystemExit:
                    pass
            self.assertIn("#### #1 · Q3 · 11 marks · STRUCTURED", out.getvalue())
            self.assertIn("(none — card has no spec linkage)", out.getvalue())
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
