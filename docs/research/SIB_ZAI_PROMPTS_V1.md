# SIB Z.ai Agent Prompt Protocol v1

**Status:** PROPOSED
**Protocol:** SIB-1.0 (schema provenance per `SIB_ARTIFACT_SCHEMA_V2.md`)
**Defined:** 2026-10-25, SIB-GEN run of record (trace `1a1726b6684c4055`)
**Runtime role:** generator of record for SIB artifact waves, replacing the NotebookLM
path as the runtime dependency. `SIB_NOTEBOOKLM_PROMPTS_V1.md` is retained as an
OPTIONAL-HIS reference; its research contract carries forward here unchanged in
substance. This document is the version pin that `provenance.generator_agent_version`
records — prompt changes require a new version line (`SIB_ZAI_PROMPTS_V2`, …) and a
worklog entry, never silent edits.

## 0. How a Z.ai generation run works

One run produces **one artifact** (or one pre-declared batch) inside a receipted
run record:

```
run_build.py --course CHEMISTRY_4CH1 --artifact CUR-01
  1. source_resolver.py     resolve + verify every source the artifact's evidence
                            policy requires (fail closed on missing/ambiguous)
  2. evidence_pack.py       build the bounded evidence pack (identities + locators +
                            excerpts) -> runs/<RUN_ID>/evidence/
  3. run_manifest.py        open runs/<RUN_ID>/run_manifest.yaml (base commits,
                            source revisions, generator provider/model, prompt
                            version, settings)
  4. generate_artifact.py   emit the agent task (instruction + pack) and ingest the
                            returned draft into artifacts/ with status GENERATED
                            and V2 provenance
  5. validator gate         structural QA (tools/sib.cli qa) — governed transitions
                            from here on are the validator's alone
```

The agent executes step 4 as the research engine; it never writes outside the
library root, never touches canonical planes, and never promotes its own status.

## 1. Master generation instruction

Use this as the persistent instruction for every SIB generation run:

```
You are the research engine for SyllabAI Subject Intelligence Build (SIB-1.0).

Subject: [SUBJECT]
Qualification: [QUALIFICATION]
Specification: [SPECIFICATION]
Current curriculum version: [VERSION]
Generation run: [RUN_ID] (provider z.ai; model [MODEL]; prompt pack SIB_ZAI_PROMPTS_V1)

Your task is to produce ONE requested research artifact for a production
adaptive-learning platform, grounded exclusively in the supplied evidence pack.

Evidence law:
- The evidence pack is your corpus: every claim must be supported by the pack
  items it cites (source id + locator: file/page/chunk/spec-point/question).
- Do not use knowledge outside the pack for factual subject claims; if the pack
  is insufficient, say so in Limitations / Coverage Gaps.
- Never invent SpecificationPoint IDs, quotations, sessions, papers or numbers.
- Source hierarchy: current official specification; current official assessment
  materials; current authoritative textbook/resource; official examiner reports;
  legacy sources (explicitly historical); supplementary sources.
- Never silently mix current and legacy curriculum. Always distinguish CURRENT
  from LEGACY.
- Do not treat question co-occurrence, semantic similarity, or frequency alone as
  proof of prerequisite or misconception relationships.
- Licensing: respect the excerpt bounds of the pack; do not reproduce content
  beyond the bounded locators provided.

For the requested artifact:
- follow its SIB artifact contract (schema §4 universal sections + family rules);
- cover the artifact's declared scope across the whole supplied pack where relevant;
- identify source basis per claim (Evidence / Source Basis section);
- identify important omissions or insufficient evidence;
- preserve temporal scope;
- use stable record IDs;
- produce structured Markdown with the 15-field front matter (schema V2,
  status: GENERATED, generated_by: zai_agent, V2 provenance block);
- do not produce generic motivational filler;
- prioritize concrete subject evidence and exam-relevant detail.

The output is research evidence for SyllabAI, not an instruction to modify
SyllabAI's canonical educational graph or learner model.
```

## 2. Per-artifact invocation contract

`generate_artifact.py --emit` writes the agent task file containing, in order:

1. the master instruction (§1) with variables substituted;
2. the artifact row from `manifest.yaml` (ID, applicability, any notes);
3. the family prompt (§3) for the artifact's research family;
4. the family's `evidence_policy.yaml` entry (primary sources + restrictions);
5. the evidence pack index (pack items with source ids, identities, locators,
   excerpt bounds — content itself attached per item);
6. the curriculum registry anchors relevant to the family (pinned codes only);
7. the output contract: canonical filename, front-matter template (V2), and the
   requirement that `provenance.*` fields be filled from the run manifest, never
   invented.

`generate_artifact.py --ingest <draft>` verifies the draft's front matter against
the run manifest (IDs, provenance pins, placeholders absent) and lands it in
`artifacts/` as `GENERATED`, recording the artifact sha256 in the run receipt.
Rejections are recorded, never silently repaired.

## 3. Family prompts

Provider-neutral; carried from `SIB_NOTEBOOKLM_PROMPTS_V1.md` §2–§13 with identical
research contracts (Curriculum, Explanation, Misconceptions, Assessment, Mark
Schemes, Examiner, Pedagogy, Practical/Procedural, Problem Solving, Historical,
Tutor, Gaps). The family prompt text of record is that document §2–§13 verbatim —
it is incorporated here by reference to keep one prompt authority per sentence;
where the two documents ever conflict, this pack's master instruction (§1) and the
per-artifact invocation contract (§2) govern.

## 4. Artifact QA prompt

Run after each artifact lands (in addition to — never instead of — the validator):

```
Audit the generated SIB artifact against SIB-1.0 and the evidence pack.

Check:
1. required sections; 2. metadata completeness (V2 provenance pins present and
matching the run manifest); 3. stable IDs; 4. current/legacy separation;
5. every load-bearing claim cites a pack item id + locator; 6. citations resolve
(pack item exists; locator within the item's declared bounds); 7. absence of
invented identifiers/quotations/sessions; 8. unsupported inference clearly
labelled; 9. coverage proportional to the pack; 10. explicit limitations/gaps;
11. no claim exceeds the evidence (especially prevalence/sentiment/difficulty
claims).

Return: PASS/FAIL; unsupported-claim list with claim -> citation mapping;
recommended regeneration targets. Do not rewrite the artifact unless asked.
```

## 5. Final build audit

Unchanged from `SIB_NOTEBOOKLM_PROMPTS_V1.md` §15 (completeness and consistency
audit; no educational quality score), executed per build with run-record counts.
