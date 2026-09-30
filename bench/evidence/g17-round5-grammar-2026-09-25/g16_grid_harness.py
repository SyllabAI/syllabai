"""G1.5 round-5 harness: the 13 R4-GRID cards vs real full-MS parses."""
import json, sys
sys.path.insert(0, '/home/z/my-project/workspace/syllabai-parser/tools')
from pdflane import parse_ms

cards=json.load(open('/home/z/my-project/workspace/r4_cards_raw.json'))
cls=json.load(open('/home/z/my-project/workspace/records-clone/bench/evidence/g16-round4-cards-2026-09-25/g16_classification.json'))

def letter_sums(points):
    s={}
    for p in points:
        if p.get('marks'): s[p['part']] = s.get(p['part'],0)+p['marks']
    return s

cache={}
n_ok=0
for key,c in cls['cards'].items():
    if c['mechanism']!='R4-GRID': continue
    slug,q=key.split(':')
    if slug not in cache:
        p=f'/home/z/my-project/workspace/r4_runs/{slug}/_meta/pdftotext/ms-layout.txt'
        pages=open(p).read().split('\f')
        cache[slug]=parse_ms.parse_pages([{'page':n+1,'text':t} for n,t in enumerate(pages)])
    qd=[x for x in cache[slug]['questions'] if x['number']==int(q)]
    if not qd:
        print(f"{key}: q{q} NOT PARSED"); continue
    got=letter_sums(qd[0]['points'])
    exp={x['letter']:x['qp'] for x in c['letter_cmp']}
    mism=[f"{L}:{got.get(L)}!={want}" for L,want in sorted(exp.items()) if got.get(L)!=want]
    ok = not mism
    n_ok += ok
    print(f"{key}: sum={sum(got.values())}/{c['printed']} | {'OK' if ok else '; '.join(mism)}")
print(f"== {n_ok}/13 letter-exact")
