#!/usr/bin/env python3
"""Card review-sheet header parser — RECONSTRUCTED WITH THE TASK-54 FIX.

Provenance (2026-10-01, records lane): the original sheet generator
(scripts/generate_teacher_card_review_sheet_20260928.py) was an agent-side
sandbox script lost in the sandbox rollbacks of 2026-10-01. Task 54
(bench/evidence/flagged3-source-verify-2026-09-28/) identified its defect:

  the header regex REQUIRED a "spec:" segment; the 3 honest no-linkage cards
  (#207/#278/#291) have headers omitting it, so the whole match failed and the
  fallback fabricated qnum="?", marks=0, qtype="?" -> "Q? · 0 marks · ?" on the
  rendered sheet, even though the cards' own textBlocks carry the true values
  (Q3/11, Q1/5, Q1/4).

This module reimplements the parser core with the FIX:
  * segment-scanning instead of one monolithic regex — every field is parsed
    independently, so ONE missing optional segment can never nuke the rest;
  * the "spec:" segment is OPTIONAL (absent or empty -> spec=None);
  * FAIL-CLOSED: a header missing a required field raises HeaderParseError —
    the parser never fabricates "?" placeholders. The caller owns any
    fallback policy (and should prefer aborting over printing false headers).

Pinned artifacts are untouched: the imported sheet
(teacher_card_review_sheet_2026-09-28_completed.md, sha256 89c07146…d67e)
and the DB wave it drove are historical records; this fix is for FUTURE sheets.

Header grammar (pipe-delimited, from the live card corpus):
  Q-Card | <code> | <session> | Q<num> | marks: <int> | type: <qtype>
       [| spec: <codes>] | stem: <text>
Real examples (verbatim from bench/evidence/flagged3-source-verify-2026-09-28/):
  'Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: STRUCTURED | stem: This question is about copper and its compounds.'
  'Q-Card | 4CH1/2CR | Jun 2020 | Q1 | marks: 5 | type: STRUCTURED | stem: ...'
  'Q-Card | 4CH1/2CR | Jan 2023 | Q1 | marks: 4 | type: STRUCTURED | stem: ...'
"""
from __future__ import annotations

import re
from typing import Optional

HEADER_MARKER = "Q-Card"
NO_SPEC_NOTE = "(none — card has no spec linkage)"

_SESSION_RE = re.compile(r"^[A-Za-z]{3,9}\.?\s+\d{4}$")
_QNUM_RE = re.compile(r"^Q\d+[a-z()]*$", re.IGNORECASE)
_CODE_RE = re.compile(r"^[A-Za-z0-9]+/[0-9A-Za-z]+$")


class HeaderParseError(ValueError):
    """Raised on a header missing a required field or structurally invalid.

    Fail-closed by design: the original bug silently degraded to
    "Q? · 0 marks · ?" — this parser never does that.
    """


def parse_card_header(line: str) -> dict:
    """Parse one q_card header line into its fields.

    Returns {'code', 'session', 'qnum', 'marks', 'qtype', 'spec', 'stem'}.
    spec is None when the segment is absent or empty (honest no-linkage card).
    Raises HeaderParseError on any missing required field — never returns '?'.
    """
    if line is None:
        raise HeaderParseError("header line is None")
    parts = [p.strip() for p in str(line).split("|")]
    if not parts or parts[0] != HEADER_MARKER:
        raise HeaderParseError(f"not a {HEADER_MARKER} header (prefix mismatch): {line!r}")

    fields: dict = {"code": None, "session": None, "qnum": None,
                    "marks": None, "qtype": None, "spec": None, "stem": None}
    code_candidates: list[str] = []

    for idx, part in enumerate(parts[1:], start=1):
        low = part.lower()
        if low.startswith("marks:"):
            raw = part[len("marks:"):].strip()
            if fields["marks"] is not None:
                raise HeaderParseError(f"duplicate marks segment at part {idx}: {part!r}")
            if not re.fullmatch(r"\d+", raw or ""):
                raise HeaderParseError(f"marks is not a plain integer at part {idx}: {part!r}")
            fields["marks"] = int(raw)
        elif low.startswith("type:"):
            val = part[len("type:"):].strip()
            if fields["qtype"] is not None:
                raise HeaderParseError(f"duplicate type segment at part {idx}: {part!r}")
            if not val:
                raise HeaderParseError(f"empty type segment at part {idx}")
            fields["qtype"] = val
        elif low.startswith("spec:"):
            val = part[len("spec:"):].strip()
            if fields["spec"] is not None:
                raise HeaderParseError(f"duplicate spec segment at part {idx}: {part!r}")
            fields["spec"] = val or None  # 'spec:' or 'spec: ' -> honest no-linkage
        elif low.startswith("stem:"):
            # stem text may itself contain '|': keep everything after the first
            # 'stem:' occurrence, joined back, so no content is silently dropped
            joined = " | ".join([part[len("stem:"):].strip()] + parts[idx + 1:])
            fields["stem"] = joined if joined else None
            break
        elif _QNUM_RE.match(part) and fields["qnum"] is None:
            fields["qnum"] = part.upper()
        elif _SESSION_RE.match(part) and fields["session"] is None:
            fields["session"] = part
        elif _CODE_RE.match(part):
            code_candidates.append(part)
        else:
            # unrecognised bare segment: tolerate ONLY if it looks like a
            # truncated paper code variant (no '/'); otherwise fail closed
            raise HeaderParseError(f"unrecognised segment at part {idx}: {part!r}")

    if len(code_candidates) == 1:
        fields["code"] = code_candidates[0]
    elif len(code_candidates) > 1:
        raise HeaderParseError(f"ambiguous code segments: {code_candidates}")

    missing = [k for k in ("code", "session", "qnum", "marks", "qtype") if fields[k] is None]
    if missing:
        raise HeaderParseError(f"header missing required field(s) {missing}: {line!r}")
    return fields


def render_sheet_header(seq: int, parsed: dict) -> str:
    """Render the sheet catalog header exactly in the pinned sheet's format.

    Pinned-sheet format: '#### #207 · Q3 · 11 marks · STRUCTURED'.
    Requires a fully parsed card — the renderer has NO fallback path, so a
    parse failure upstream can never reach the sheet as 'Q? · 0 marks · ?'.
    """
    req = ("qnum", "marks", "qtype")
    if any(parsed.get(k) is None for k in req):
        raise HeaderParseError(f"render_sheet_header called with unparsed card: missing {req}")
    return f"#### #{seq} · {parsed['qnum']} · {parsed['marks']} marks · {parsed['qtype']}"


def render_spec_segment(parsed: dict) -> str:
    """Render the spec display segment; honest note for no-linkage cards."""
    return parsed["spec"] if parsed.get("spec") else NO_SPEC_NOTE


def parse_or_raise_many(lines: list[str]) -> list[dict]:
    """Convenience: parse a list; any failure raises (fail-closed batch)."""
    return [parse_card_header(l) for l in lines]


def code_constants_without_docstrings(path: str) -> list[str]:
    """All string constants that are NOT docstrings (for the fabrication guard)."""
    import ast
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), mode="exec")
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            if doc is not None:
                docstrings.add(doc)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value not in docstrings:
                out.append(node.value)
    return out


if __name__ == "__main__":  # pragma: no cover - operator smoke tool
    import sys
    REAL = [
        "Q-Card | 4CH1/2C | Jan 2020 | Q3 | marks: 11 | type: STRUCTURED | stem: This question is about copper and its compounds.",
        "Q-Card | 4CH1/2CR | Jun 2020 | Q1 | marks: 5 | type: STRUCTURED | stem: Answer ALL questions.",
        "Q-Card | 4CH1/2CR | Jan 2023 | Q1 | marks: 4 | type: STRUCTURED | stem: Answer ALL questions.",
    ]
    if len(sys.argv) < 2:
        lines = REAL
    else:
        with open(sys.argv[1]) as fh:
            lines = [l.rstrip("\n") for l in fh]
    for i, ln in enumerate(lines, start=1):
        f = parse_card_header(ln)
        print(f"#{i}: {render_sheet_header(i, f)}   spec: {render_spec_segment(f)}")
