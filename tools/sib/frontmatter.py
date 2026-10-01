"""Deterministic YAML front-matter parsing for SIB artifacts.

Strategy:
1. If PyYAML is importable, use ``yaml.safe_load`` (dicts preserve insertion
   order on Python 3.7+; determinism is enforced downstream by sorted output).
2. Otherwise fall back to a small built-in parser that handles exactly the
   SIB front-matter subset:
     * ``key: value`` scalars (str / bool / int),
     * one-level nested mappings (``temporal_scope:``, ``source_scope:``,
       ``provenance:``),
     * inline comments, quoted scalars.

The SIB schema's front matter is a constrained subset, so the fallback is
sufficient for protocol-defined metadata; anything richer is flagged by the
artifact validator rather than guessed at here.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

FRONTMATTER_DELIM = "---"

_LINE_RE = re.compile(
    r"^(?P<indent>[ ]*)(?P<key>[^#:\s][^:]*?):(?P<value>.*)$")
_BOOL_TRUE = {"true", "True", "TRUE"}
_BOOL_FALSE = {"false", "False", "FALSE"}


@dataclass(frozen=True)
class FrontMatterResult:
    metadata: Dict[str, Any]
    body: str
    parse_mode: str          # "pyyaml" | "builtin"
    parse_error: Optional[str]  # None when parsed OK


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1], True
    return value, False


def _coerce_scalar(raw: str) -> Any:
    value, quoted = _strip_quotes(raw)
    if quoted:
        # quoted scalars are strings by definition (matches PyYAML)
        return value
    if value in _BOOL_TRUE:
        return True
    if value in _BOOL_FALSE:
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d*", value) or re.fullmatch(r"-?\.\d+", value):
        return float(value)
    return value


def _canonicalize(value: Any) -> Any:
    """Canonicalize PyYAML parse results to the subset semantics shared with
    the builtin parser: date/timestamp scalars become ISO strings so that
    both parse paths yield identical metadata for identical input."""
    import datetime
    if isinstance(value, dict):
        return {k: _canonicalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_canonicalize(v) for v in value]
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


def _builtin_parse(lines: List[str]) -> Dict[str, Any]:
    """Parse the SIB front-matter subset deterministically."""
    meta: Dict[str, Any] = {}
    current_map: Optional[Dict[str, Any]] = None
    current_key: Optional[str] = None

    for raw in lines:
        line = raw.rstrip("\n")
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = _LINE_RE.match(line)
        if not m:
            # continuation or unsupported syntax -- surface as scalar-less key
            raise ValueError(f"unsupported front-matter line: {line!r}")
        indent = len(m.group("indent"))
        key = m.group("key").strip()
        value = m.group("value").strip()
        value = re.sub(r"\s+#.*$", "", value)  # trailing comment

        if indent == 0:
            if value == "":
                current_map = {}
                meta[key] = current_map
                current_key = key
            else:
                meta[key] = _coerce_scalar(value)
                current_map = None
                current_key = None
        else:
            if current_map is None:
                raise ValueError(
                    f"nested value outside a mapping near: {line!r}")
            current_map[key] = _coerce_scalar(value)
            _ = current_key  # retained for clarity; single-level maps only
    return meta


def parse_front_matter(text: str) -> FrontMatterResult:
    """Split ``text`` into front matter + body and parse the metadata.

    Front matter must be delimited:
        ---
        <yaml>
        ---
    """
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return FrontMatterResult({}, normalized, "builtin",
                                 "missing opening '---' front-matter delimiter")
    try:
        close = next(i for i in range(1, len(lines))
                     if lines[i].strip() == FRONTMATTER_DELIM)
    except StopIteration:
        return FrontMatterResult({}, normalized, "builtin",
                                 "missing closing '---' front-matter delimiter")
    fm_lines = lines[1:close]
    body = "\n".join(lines[close + 1:])
    try:
        import yaml  # type: ignore
        meta = yaml.safe_load("\n".join(fm_lines))
        if meta is None:
            meta = {}
        if not isinstance(meta, dict):
            return FrontMatterResult({}, body, "pyyaml",
                                     "front matter is not a mapping")
        return FrontMatterResult(_canonicalize(meta), body, "pyyaml", None)
    except ImportError:
        pass
    except Exception as exc:  # yaml syntax error
        return FrontMatterResult({}, body, "pyyaml", f"yaml parse error: {exc}")
    try:
        meta = _builtin_parse(fm_lines)
        return FrontMatterResult(meta, body, "builtin", None)
    except ValueError as exc:
        return FrontMatterResult({}, body, "builtin", str(exc))
