"""yamlmini -- deterministic YAML-subset loader (stdlib fallback).

SyllabAI SIB tooling must run on stdlib-only environments (GitHub
``setup-python`` images do not ship PyYAML). ``load_yaml`` therefore uses
PyYAML when importable and otherwise falls back to the parser below.

Supported subset (covers all SIB-side YAML: manifests, source manifests,
curriculum registries, artifact front matter):

* top-level mappings and nested mappings (indentation-based);
* lists of scalars (``- 1.4``) and lists of mappings (``- id: X`` with
  continuation ``key: value`` lines at deeper indent);
* scalars: booleans, integers, floats, quoted/unquoted strings;
  empty values parse as ``None``;
* blank lines and ``#`` comments (full-line and trailing, outside quotes).

Not supported (deliberately): anchors/aliases, multi-line block scalars,
flow collections, tags, multiple documents. Where richer YAML is needed,
PyYAML is required -- and its absence surfaces as a parse error, never a
silent misparse.
"""
from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple


class YamlMiniError(ValueError):
    """Raised when input exceeds the supported subset."""


def load_yaml(text: str) -> Any:
    """PyYAML-backed loader with a deterministic stdlib fallback."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return parse(text)
    try:
        from .frontmatter import _canonicalize
        return _canonicalize(yaml.safe_load(text))
    except ImportError:
        return parse(text)


# ---------------------------------------------------------------- scalars

_BOOL_TRUE = {"true", "True", "TRUE"}
_BOOL_FALSE = {"false", "False", "FALSE"}


def _strip_comment(line: str) -> str:
    out: List[str] = []
    quote: Optional[str] = None
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(raw: str) -> Any:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value == "" or value in ("~", "null", "Null", "NULL"):
        return None
    if value in _BOOL_TRUE:
        return True
    if value in _BOOL_FALSE:
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d*", value) or re.fullmatch(r"-?\.\d+", value):
        return float(value)
    return value


_KEY_VALUE_RE = re.compile(r"^(?P<key>[^#:\s][^:]*?):(?P<value>.*)$")


def _parse_block(lines: List[Tuple[int, str]], pos: int, indent: int,
                 doc: bool = False) -> Tuple[Any, int]:
    """Parse one block (mapping or list) starting at ``pos``.

    ``lines`` items are ``(indent, content)`` pairs (comments/blanks
    removed). ``doc=True`` allows the root block at any indent == 0.
    """
    is_list = lines[pos][1].startswith("- ") or lines[pos][1] == "-"
    result: Any = [] if is_list else {}
    while pos < len(lines):
        ind, content = lines[pos]
        if ind < indent:
            break
        if ind > indent and not is_list and result:
            raise YamlMiniError(f"unexpected indent at: {content!r}")
        if is_list:
            if content == "-":
                # nested block under a bare dash
                value, pos = _parse_block(lines, pos + 1, _next_indent(lines, pos, ind))
                result.append(value)
                continue
            if not content.startswith("- "):
                break
            inner = content[2:]
            m = _KEY_VALUE_RE.match(inner)
            if m and m.group("value").strip() == "":
                # list-of-mappings: first key inline, following keys deeper
                item: dict = {m.group("key").strip(): None}
                pos += 1
                if pos < len(lines) and lines[pos][0] > ind:
                    child, pos = _parse_block(lines, pos, lines[pos][0])
                    if isinstance(child, dict):
                        item.update(child)
                    else:
                        item[m.group("key").strip()] = child
                result.append(item)
                continue
            if m and m.group("value").strip() != "":
                key = m.group("key").strip()
                item2: dict = {key: _scalar(m.group("value"))}
                pos += 1
                while pos < len(lines) and lines[pos][0] > ind:
                    child, pos = _parse_mapping_lines(lines, pos, lines[pos][0])
                    item2.update(child)
                result.append(item2)
                continue
            result.append(_scalar(inner))
            pos += 1
            continue
        # mapping line
        m = _KEY_VALUE_RE.match(content)
        if not m:
            raise YamlMiniError(f"unsupported YAML-subset line: {content!r}")
        key = m.group("key").strip()
        value_raw = m.group("value").strip()
        if value_raw == "":
            # nested block or null
            if pos + 1 < len(lines) and lines[pos + 1][0] > ind:
                child, pos = _parse_block(lines, pos + 1, lines[pos + 1][0])
                result[key] = child
                continue
            if pos + 1 < len(lines) and lines[pos + 1][0] == ind and \
                    (lines[pos + 1][1].startswith("- ") or lines[pos + 1][1] == "-"):
                child, pos = _parse_block(lines, pos + 1, ind)
                result[key] = child
                continue
            result[key] = None
            pos += 1
            continue
        result[key] = _scalar(value_raw)
        pos += 1
    return result, pos


def _parse_mapping_lines(lines: List[Tuple[int, str]], pos: int,
                         indent: int) -> Tuple[dict, int]:
    """Parse consecutive mapping lines (no list items) at ``indent``."""
    out: dict = {}
    while pos < len(lines):
        ind, content = lines[pos]
        if ind != indent or content.startswith("- "):
            break
        m = _KEY_VALUE_RE.match(content)
        if not m:
            raise YamlMiniError(f"unsupported YAML-subset line: {content!r}")
        key = m.group("key").strip()
        value_raw = m.group("value").strip()
        if value_raw == "":
            if pos + 1 < len(lines) and lines[pos + 1][0] > ind:
                child, pos = _parse_block(lines, pos + 1, lines[pos + 1][0])
                out[key] = child
                continue
            out[key] = None
            pos += 1
            continue
        out[key] = _scalar(value_raw)
        pos += 1
    return out, pos


def _next_indent(lines: List[Tuple[int, str]], pos: int, ind: int) -> int:
    if pos + 1 < len(lines) and lines[pos + 1][0] > ind:
        return lines[pos + 1][0]
    raise YamlMiniError("bare '-' without nested block")


def parse(text: str) -> Any:
    """Parse the YAML subset deterministically. Empty input -> None."""
    prepared: List[Tuple[int, str]] = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        prepared.append((indent, line.strip()))
    if not prepared:
        return None
    value, _ = _parse_block(prepared, 0, prepared[0][0], doc=True)
    return value
