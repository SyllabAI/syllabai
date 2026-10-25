"""Deterministic YAML front-matter parsing for SIB artifacts.

Strategy:
1. If PyYAML is importable, use ``yaml.safe_load`` (dicts preserve insertion
   order on Python 3.7+; determinism is enforced downstream by sorted output).
2. Otherwise fall back to ``yamlmini.parse`` -- the same deterministic
   stdlib parser backing ``yamlmini.load_yaml`` -- so both parse paths
   handle the identical SIB front-matter subset, including nested
   mappings of any depth (schema v2 ``provenance.generator``), and
   anything outside the subset surfaces as a parse error, never a
   silent misparse.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

FRONTMATTER_DELIM = "---"

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
    the stdlib fallback (yamlmini): date/timestamp scalars become ISO strings
    so that both parse paths yield identical metadata for identical input."""
    import datetime
    if isinstance(value, dict):
        return {k: _canonicalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_canonicalize(v) for v in value]
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return value


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
    from . import yamlmini
    try:
        meta = yamlmini.parse("\n".join(fm_lines))
    except ValueError as exc:  # YamlMiniError: outside the supported subset
        return FrontMatterResult({}, body, "builtin", str(exc))
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        return FrontMatterResult({}, body, "builtin",
                                 "front matter is not a mapping")
    return FrontMatterResult(meta, body, "builtin", None)
