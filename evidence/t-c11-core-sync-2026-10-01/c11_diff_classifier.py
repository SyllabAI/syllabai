#!/usr/bin/env python3
"""Exhaustive diff classifier: every common-row difference must fall in an allowed class."""
import yaml, re
from collections import Counter

CORE = 'repos/syllabai-core/src/main/resources/concept-graph'
RES = 'repos/syllabai-resources/graph/igcse-chemistry'
ce = yaml.safe_load(open(f'{CORE}/concept_edges.yaml'))
re_ = yaml.safe_load(open(f'{RES}/concept_edges.yaml'))
cc = yaml.safe_load(open(f'{CORE}/concepts.yaml'))
rc = yaml.safe_load(open(f'{RES}/concepts.yaml'))

def norm_quote(q):
    return re.sub(r'\s*,\s*', ', ', re.sub(r'\s+', ' ', q or '')).strip()

def path_norm(s):
    if isinstance(s, str) and s.startswith('graph/') and not s.startswith('graph/igcse-chemistry/'):
        return 'graph/igcse-chemistry/' + s[len('graph/'):]
    return s

classes = Counter()
unclassified = []

def leaf(a, b, ctx):
    if a == b:
        return
    field = ctx[-1] if ctx else '?'
    if field == 'validation_status' and a == 'SUGGESTED' and b == 'HUMAN_VALIDATED':
        classes['anchor_status_flip'] += 1
    elif field in ('validated_by', 'validated_date') and a is None and isinstance(b, str) \
            and b == 'operator-directive-session-106' or (field == 'validated_date' and b == '2026-09-18'):
        classes['session106_stamp'] += 1
    elif field == 'file' and isinstance(a, str) and isinstance(b, str) and path_norm(a) == b:
        classes['evidence_path_norm'] += 1
    elif field == 'quote' and isinstance(a, str) and isinstance(b, str) and norm_quote(a) == norm_quote(b):
        classes['quote_whitespace_norm'] += 1
        print(f"  quote-norm: {ctx[1]}: {a!r} -> {b!r}")
    else:
        unclassified.append((ctx, a, b))

def walk(a, b, ctx):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            walk(a.get(k), b.get(k), ctx + [k])
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, ctx)
    else:
        leaf(a, b, ctx)

def ekey(e): return (e['source'], e['relation'], e['target'])
ci = {ekey(e): e for e in ce['edges']}
ri = {ekey(e): e for e in re_['edges']}
for k in set(ci) & set(ri):
    walk(ci[k], ri[k], ['edge', str(k)])
cn = {n['code']: n for n in cc['nodes']}
rn = {n['code']: n for n in rc['nodes']}
for c in set(cn) & set(rn):
    walk(cn[c], rn[c], ['node', c])

print('\nclasses:', dict(classes))
print('UNCLASSIFIED:', len(unclassified))
for x in unclassified[:15]:
    print('  ', x[0][:4], repr(x[1])[:90], '->', repr(x[2])[:90])
