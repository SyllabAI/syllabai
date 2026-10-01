#!/usr/bin/env python3
"""Anchor-evidence facts for the 5 HOLD (anchor-sensitive) verdict pairs."""
import yaml

CG = "/home/z/my-project/repos/syllabai-core/src/main/resources/concept-graph"
sp_doc = yaml.safe_load(open(f"{CG}/specification_points.yaml"))
concepts_doc = yaml.safe_load(open(f"{CG}/concepts.yaml"))

sp_text = {}
for sp in sp_doc.get("nodes", sp_doc.get("specification_points", [])):
    sp_text[sp["code"]] = sp.get("official_wording", "?")

concept_att = {}
for c in concepts_doc["nodes"]:
    concept_att[c["code"]] = [(a["code"], a.get("role"), (a.get("evidence") or [{}])[0].get("quote", "")[:90])
                              for a in c.get("spec_points", [])]

holds = [
    ("1.28 -> 1.26", "4CH1-CON-MR", "4CH1-CON-AR"),
    ("1.33 -> 1.32", "4CH1-CON-MOLECULAR-FORMULA", "4CH1-CON-EMPIRICAL-FORMULA"),
    ("1.33 -> 1.31", "4CH1-CON-WATER-CRYST", "4CH1-CON-EMP-MOL-CALC"),
    ("3.14C -> 3.12", "4CH1-CON-CATALYST", "4CH1-CON-ACTIVATION-ENERGY"),
    ("3.14C -> 3.13", "4CH1-CON-CATALYST", "4CH1-CON-ACTIVATION-ENERGY"),
    # the 3 confirmed spirals, for the record too
    ("1.3 -> 1.2 (KEEP)", "4CH1-CON-STATE-CHANGES", "4CH1-CON-STATE-PARTICLE-MODEL"),
    ("1.10 -> 1.5C (KEEP)", "4CH1-CON-SOLUBILITY", "4CH1-CON-SATURATED-SOLUTION"),
]

for pair, dep, pre in holds:
    print(f"\n=== {pair}  (store: {dep} REQUIRES {pre}) ===")
    for code in (dep, pre):
        atts = concept_att.get(code, [])
        print(f"  {code}: {len(atts)} attachment(s)")
        for spc, role, q in atts:
            print(f"    -> {spc} [{role}]  {q!r}")
    print("  SP wording:")
    for spc in sorted({a[0] for c in (dep, pre) for a in concept_att.get(c, [])}):
        print(f"    {spc}: {sp_text.get(spc, '?')[:160]}")
