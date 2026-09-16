# Ruling-3 Gold-Label Spot-Check Worksheet — gold-v1

**Owner action item (T-C13 spec §10, ruling 3, RATIFIED v1.0):** gold-v1 labels are
auto-derived; the owner spot-checks this sample before the labels are trusted.
**Decision rule (binding):** any class below **90% owner agreement**
(CORRECT / sampled) is **manually re-authored** before the next recorded run.

- Basis: `bench/gold/` gold-v1 (manifest SHA-256 `20c2bbbde6f59f8a…`), frozen
- Snapshot: `evidence/bench-001/snapshot/` (snap-001) — chunk excerpts below resolve here
- Sample: **51 of 120** queries — classes 4/5/6 at 100%, all others ceil(20%)
- Seed: `20c2bbbde6f59f8a` (= sha256(manifest.json)[:16]; deterministic, no RNG)
- Reproduce: `python3 bench/gold_spotcheck.py` → identical sample + this worksheet
- Machine-readable: `ruling-3-spot-check-sample.json` · spreadsheet: `ruling-3-spot-check-worksheet.csv`

## How to judge one query

1. **Spec points** — would a competent teacher accept every listed gold
   SpecificationPoint as a correct anchor for this query? (missing obvious
   anchors count as INCORRECT; note the missing codes)
2. **Evidence tiers** — tier 2 = *directly answers* the query, tier 1 =
   *legitimate supporting* evidence, tier 0 = not relevant. Each excerpt
   below carries its paper code, kind, page and the leading content so the
   tier can be judged without opening the snapshot; full text lives in
   `snapshot/chunks.jsonl.gz` under the printed chunk ref.
3. Mark **CORRECT** only if (1) and (2) both hold; otherwise INCORRECT with
   corrected labels in the notes column (CSV carries a dedicated column).

## Roster

| # | Class | Sampled / Total | Rate |
|---|-------|----------------:|------|
| 1 | Direct factual questions | 3 / 15 | ceil(20%) = 3/15 |
| 2 | Conceptual explanations | 3 / 15 | ceil(20%) = 3/15 |
| 3 | Calculations | 2 / 10 | ceil(20%) = 2/10 |
| 4 | Prerequisite questions | 12 / 12 | 100% (ruling 3) |
| 5 | Misconception questions | 10 / 10 | 100% (ruling 3) |
| 6 | Why did I get this wrong? | 10 / 10 | 100% (ruling 3) |
| 7 | Exam-question retrieval | 2 / 10 | ceil(20%) = 2/10 |
| 8 | Mark-scheme retrieval | 2 / 8 | ceil(20%) = 2/8 |
| 9 | Revision-note retrieval | 2 / 10 | ceil(20%) = 2/10 |
| 10 | Vague learner-language queries | 2 / 8 | ceil(20%) = 2/8 |
| 11 | Multi-SpecificationPoint questions | 2 / 7 | ceil(20%) = 2/7 |
| 12 | Diagram/figure-dependent questions | 1 / 5 | ceil(20%) = 1/5 |
| | **Total** | **51 / 120** | |

## Review records

### Class 1 — Direct factual questions (`factual`, 3/15 sampled)

#### `g1-003` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** What are the key facts I should know about use knowledge of trends in Group 7 to predict the propertie…?
> **Gold spec points:** 4CH1-2.6
> **Provenance:** rule=R2 · source=spec_point:4CH1-2.6 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

_No gold evidence chunks for this record (spec-point-only anchor)._

#### `g1-014` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** What are the key facts I should know about calculate percentage yield?
> **Gold spec points:** 4CH1-1.30
> **Provenance:** rule=R2 · source=spec_point:4CH1-1.30 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `face72f4a8…:3` · — QUESTION_PAPER p.1 · state VALIDATED
  > D The student used a spirit burner instead of a Bunsen burner. (d) In another experiment, the student calculates that she should obtain a mass of 3.7…
- **tier 1** (`R2-term-cooccurrence`) → `295c56c31b…:15` · 4CH1/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 9 | (c)(i)(ii) | 3.25(g) | | 1 exp calculate moles of NaHCO3 | | 3 exp use equation to determine moles of Na…
- **tier 1** (`R2-term-cooccurrence`) → `042dcbb07a…:9` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > \mathrm {M g O (s)} + 2 \mathrm {H N O} _ {3} (\mathrm {a q}) \rightarrow \mathrm {M g} \left(\mathrm {N O} _ {3}\right) _ {2} (\mathrm {a q}) + \mat…
- **tier 1** (`R2-term-cooccurrence`) → `e5556d9d8c…:14` · — QUESTION_PAPER p.1 · state SUGGESTED
  > (b) (i) Use the graph to state the effect on the percentage of ammonia at equilibrium of the following changes an increase in temperature at constant…
- **tier 1** (`R2-term-cooccurrence`) → `79bd80919c…:6` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > (i) In an experiment, a chemist used 59.6 g of tungsten fluoride. What is the maximum mass of tungsten he could obtain from 59.6 g of tungsten fluori…

#### `g1-015` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** What are the key facts I should know about understand the interconversions between the three states of…?
> **Gold spec points:** 4CH1-1.2
> **Provenance:** rule=R2 · source=spec_point:4CH1-1.2 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `512af760e5…:3` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > $ ^{*} $ The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and…
- **tier 1** (`R2-term-cooccurrence`) → `cbff9c92ef…:2` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `cca430dc43…:2` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > Answer ALL questions. 1 Use the Periodic Table on page 2 to help you answer this question. (a) Give the symbol of the element that has an atomic numb…
- **tier 1** (`R2-term-cooccurrence`) → `95123d07fa…:3` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) Determine the number of atoms in a molecule of $ \mathrm{C_{3} H_{5} N_{3} O_{9}} $ (Total for Question 1 = 7 marks) 2 This question is about ru…
- **tier 1** (`R2-term-cooccurrence`) → `e02c65ad9f…:1` · — QUESTION_PAPER p.1 · state SUGGESTED
  > $7 Li | 9 Be 3 Lithium | 4 Beryllium 23 Na Sodium | 24 Mg Magnesium 39 K Potassium | 40 Ca Calcium 86 Rb Rubidium | 88 Sr Strontium 133 Cs Caesium |…

### Class 2 — Conceptual explanations (`conceptual`, 3/15 sampled)

#### `g1-019` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Explain explain the effects of changes in surface area of a solid, ….
> **Gold spec points:** 4CH1-3.11
> **Provenance:** rule=R2 · source=spec_point:4CH1-3.11 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `ce65d4fd54…:6` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > (iii) Draw a curve of best fit through the points, ignoring the anomalous result. (iv) Suggest a mistake that the student might have made to cause th…
- **tier 1** (`R2-term-cooccurrence`) → `1e3c60eb51…:9` · 4CH1/1C QUESTION_PAPER p.1 · state VALIDATED
  > (iii) Draw a dot-and-cross diagram to show the bonding in a molecule of ammonia. Show outer electrons only. BLANK PAGE 9 A student uses this apparatu…
- **tier 1** (`R2-term-cooccurrence`) → `5a0d064fb5…:10` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > Plot the values of temperature and rate of reaction on the grid. Draw a curve of best fit through the points. (2) (e) (i) Use the graph to determine…
- **tier 1** (`R2-term-cooccurrence`) → `ae36e95e78…:9` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > Some students investigate the effect of changing the concentration of acid on the rate of this reaction. The diagram shows the apparatus they use. Th…
- **tier 1** (`R2-term-cooccurrence`) → `46b20b9dbf…:15` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > 16 The diagram shows the apparatus used to investigate the rate of reaction between calcium carbonate and an excess of dilute hydrochloric acid. The…

#### `g1-027` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Explain calculate reacting masses using experimental data and chemi….
> **Gold spec points:** 4CH1-1.29
> **Provenance:** rule=R2 · source=spec_point:4CH1-1.29 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `92c6ccb0c0…:11` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > $ \mathrm{T a C l}_{5} ( \mathrm{s} )+\mathrm{H}_{2} ( \mathrm{g} )\rightarrow\mathrm{T a} ( \mathrm{s} )+\mathrm{H C I} ( \mathrm{g} ) $ (b) As tant…

#### `g1-029` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Explain know that ionic compounds do not conduct electricity when s….
> **Gold spec points:** 4CH1-1.43
> **Provenance:** rule=R2 · source=spec_point:4CH1-1.43 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `111f670fea…:6` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 4(a) | M1 bright/white light OR bright/white flame | | 2 M2 white powder/solid/ash | ALLOW white smoke ALLOW…
- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:22` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 15(a) | M1 break down/decomposition of a compoundM2 using electricity | ALLOW electrolyte/substance for comp…
- **tier 1** (`R2-term-cooccurrence`) → `034516a426…:12` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Total for question 9 = 10 marks Question number | Answer | Notes | Marks 10 | (a)(i) | measuring cylinder / burette / pipette | ALLOW syringe | 1 (ii…
- **tier 1** (`R2-term-cooccurrence`) → `df8fd0f8c2…:3` · 4CH0/1C QUESTION_PAPER p.1 · state VALIDATED
  > R _ {\mathrm {f}} = \frac {\mathrm {d i s t a n c e m o v e d b y f o o d d y e f r o m b a s e l i n e}}{\mathrm {d i s t a n c e m o v e d b y s o…
- **tier 1** (`R2-term-cooccurrence`) → `96bdc4705e…:3` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (b) How would you know when the copper(II) oxide is in excess in stage 2? (c) Why is the mixture filtered in stage 3? (d) Why do crystals form when t…

### Class 3 — Calculations (`calculation`, 2/10 sampled)

#### `g1-036` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** When nitrogen dioxide gas $ \mathrm{(N O_{2})} $ is placed in a sealed flask, it reacts to form dinitrogen tetraoxide gas $ \mathrm{(N_{2}O_{4})}. $ The equation for the reaction i…
> **Provenance:** anchor_code_non_spec=4CH1-S3-c · rule=R1+R3 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1; selector=numeric-stem fill (quota amendment, command_word unpopulated)
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `f06f808464…:9` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > 8 When nitrogen dioxide gas $ \mathrm{(N O_{2})} $ is placed in a sealed flask, it reacts to form dinitrogen tetraoxide gas $ \mathrm{(N_{2}O_{4})}.…
- **tier 1** (`R3-paper-cohort`) → `20d8089be2…:7` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 4 | a | | M1 | concentration | Ignore from the same bottle | 1 | | | M2 | temperature/same tem…
- **tier 1** (`R3-paper-cohort`) → `790877f765…:2` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 2(a)(i)(ii) | D | d | | 1 A | a | | 1 (b) | M1-B | b | contains other colours | 1 M2- the spots do…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 4(a)(i) | Contains a (carbon to carbon) double bond / contains C=C / multiple bond IGNORE…

#### `g1-039` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** A student investigates the solubility of potassium nitrate in water. She measures the masses of potassium nitrate that dissolve in $ 2 5 \mathrm{c m}^{3} $ of water at different te…
> **Provenance:** anchor_code_non_spec=ING-4CH12CSUMMER2021 · rule=R1+R3 · source=qversion[4CH1/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1; selector=numeric-stem fill (quota amendment, command_word unpopulated)
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `669b7691ec…:4` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > 4 A student investigates the solubility of potassium nitrate in water. She measures the masses of potassium nitrate that dissolve in $ 2 5 \mathrm{c…
- **tier 1** (`R3-paper-cohort`) → `7649654514…:2` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > When examiners are in doubt regarding the application of the mark scheme to a candidate's response,the team leader must be consulted. Crossed out wor…
- **tier 1** (`R3-paper-cohort`) → `9a2262007b…:0` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > PMT Pearson Edexcel Mark Scheme (Results) November 2021 Pearson Edexcel International GCSE In Chemistry (4CH1) Paper 2C Edexcel and BTEC Qualificatio…
- **tier 1** (`R3-paper-cohort`) → `66a8d87f23…:3` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2(a)(i)(ii) | M1 oxygen | ALLOW air/O2 | 2 M2 water | ALLOW moisture/water vapour/H2O | painting/oiling/coat…

### Class 4 — Prerequisite questions (`prerequisite`, 12/12 sampled)

#### `g1-041` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Saturated solution before I can understand Solubility?
> **Gold spec points:** 4CH1-1.10 · 4CH1-1.4 · 4CH1-1.5C
> **Gold concepts:** 4CH1-CON-SATURATED-SOLUTION · 4CH1-CON-SOLUBILITY
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-SOLUBILITY->4CH1-CON-SATURATED-SOLUTION — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `d72903ee82…:1` · — QUESTION_PAPER p.1 · state SUGGESTED
  > 7 Li | 9 Be 3 Lithium | 4 Beryllium 23 Na Sodium | 24 Mg Magnesium 39 K Potassium | 40 Ca Calcium 86 Rb Rubidium | 88 Sr Strontium 133 Cs Caesium | 1…
- **tier 1** (`R2-term-cooccurrence`) → `914d583101…:4` · 4CH1/2C QUESTION_PAPER p.1 · state SUGGESTED
  > This is the equation for the reaction. \mathrm {P b} \left(\mathrm {N O} _ {3}\right) _ {2} (\mathrm {a q}) + \mathrm {N a} _ {2} \mathrm {S O} _ {4}…
- **tier 1** (`R2-term-cooccurrence`) → `babfe26bcb…:2` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `6a9a10e439…:3` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > add an excess of solid to some water in a boiling tube and stir measure the temperature of the saturated solution formed weigh an empty evaporating b…
- **tier 1** (`R2-term-cooccurrence`) → `29f3959669…:3` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) State the meaning of the term solvent. (b) Explain what is meant by a saturated solution. (c) A dark purple liquid is diluted by adding water. T…

#### `g1-042` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Ionic bonding before I can understand Electrolysis?
> **Gold spec points:** 4CH1-1.41 · 4CH1-1.58C
> **Gold concepts:** 4CH1-CON-ELECTROLYSIS · 4CH1-CON-IONIC-BOND
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-ELECTROLYSIS->4CH1-CON-IONIC-BOND — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `bd1bc88542…:5` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 4(d) | An planation linking the following five points M1water is covalently bonded/has a simple molecular st…
- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:22` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 15(a) | M1 break down/decomposition of a compoundM2 using electricity | ALLOW electrolyte/substance for comp…
- **tier 1** (`R2-term-cooccurrence`) → `268af62afb…:8` · 4CH1/1C MARK_SCHEME p.1 · state VALIDATED
  > (ii) | D yellow A is incorrect as sodium ions do not give a green flame B is incorrect as sodium ions do not give a lilac flame C is incorrect as sod…
- **tier 1** (`R2-term-cooccurrence`) → `9bb3e3d6ff…:9` · 4CH0/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c)i | all 9 points plotted correctly to nearest gridline | Deduct 1 mark for each error Award these marks…
- **tier 1** (`R2-term-cooccurrence`) → `be35905e00…:6` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Describe how the student can obtain pure, dry crystals of hydrated sodium sulfate from the solution. (c) Crystals of hydrated sodium sulfate decompos…

#### `g1-043` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Exothermic and endothermic reactions before I can understand Bond-breaking endothermic, bond-making exothermic?
> **Gold spec points:** 4CH1-3.1 · 4CH1-3.6C
> **Gold concepts:** 4CH1-CON-BOND-BREAKING-MAKING · 4CH1-CON-EXO-ENDO
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-BOND-BREAKING-MAKING->4CH1-CON-EXO-ENDO — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `c4e2178d93…:8` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 8 | M1- add (aqueous) bromine to (aqueous) KCl | | | 5 M2- no change | orange/ yellow/brown soluti…
- **tier 1** (`R2-term-cooccurrence`) → `c928be1d9d…:9` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7(a)(i) | M1 yield decreases AND reaction shifts towards the left hand side | ALLOW backward reaction | 2 M2…
- **tier 1** (`R2-term-cooccurrence`) → `295c56c31b…:13` · 4CH1/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 8(c)(i) | substitution into $ Q=mc\Delta T $ calculation of heat energy in Joules Example calculation M1 $ Q…
- **tier 1** (`R2-term-cooccurrence`) → `36f8d68e0f…:2` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > Answer ALL questions. 1 The diagram shows a Bunsen burner. (a) The Bunsen burner uses methane as a fuel. Methane has the formula $ \mathrm{C H_{4}} $…
- **tier 1** (`R2-term-cooccurrence`) → `2f11ca6ab8…:11` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7(a) | M1 breaking up/down of a compound/substance OWTTE | REJECT elements | 2 M2 by heat(ing) | REJECT any…

#### `g1-044` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Factors affecting the rate of reaction before I can understand 4CH1-PR-10?
> **Gold spec points:** 4CH1-3.10
> **Gold concepts:** 4CH1-CON-RATE-FACTORS
> **Provenance:** endpoint_non_concept=['4CH1-PR-10'] · rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-PR-10->4CH1-CON-RATE-FACTORS — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `e5556d9d8c…:13` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Is the zinc or the hydrochloric acid in excess? Explain your answer. (c) The student repeated the experiment with 0.0075 mol of magnesium powder with…
- **tier 1** (`R2-term-cooccurrence`) → `c8b8f0758b…:13` · 4CH0/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > Is the zinc or the hydrochloric acid in excess? Explain your answer. (c) The student repeated the experiment with 0.0075 mol of magnesium powder with…
- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:20` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 13(a) | | Initial | After1min | Penalise missing trailing zeroes and/or extra zeroes once onlye.g.16/16.00 |…
- **tier 1** (`R2-term-cooccurrence`) → `f67d0dfb4a…:3` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 3(c) | copper sulfate/copper ions completely reacted/been used up/run out IGNORE copper completely…
- **tier 1** (`R2-term-cooccurrence`) → `2f11ca6ab8…:13` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 8(d) | M1 magnesium(more reactive than zinc so)would make reaction faster/increase the rate | REJECTreferenc…

#### `g1-045` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Pure substance and fixed melting/boiling points before I can understand Interpreting chromatograms?
> **Gold spec points:** 4CH1-1.11 · 4CH1-1.9
> **Gold concepts:** 4CH1-CON-CHROMATOGRAM-INTERPRETATION · 4CH1-CON-PURE-SUBSTANCE
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-CHROMATOGRAM-INTERPRETATION->4CH1-CON-PURE-SUBSTANCE — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `0f3d75d3b6…:8` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) Give a reason why the mass of pure water that collects in the U-tube is less than 2.16 g. (iii) Give a physical test to show that the water that…
- **tier 1** (`R2-term-cooccurrence`) → `e8017889e5…:6` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (c) Substance X is also covalently bonded,but its structure is different from that of A and B. It has a boiling point of $ 2 2 3 0^{\circ} \mathrm{C}…
- **tier 1** (`R2-term-cooccurrence`) → `90f25c1401…:3` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > A B C D E □ □ □ □ □ (b) Complete these sentences by placing a cross ( $ \boxtimes $ ) in one box next to the correct answer. (i) The elements in the…
- **tier 1** (`R2-term-cooccurrence`) → `512af760e5…:3` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > $ ^{*} $ The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and…
- **tier 1** (`R2-term-cooccurrence`) → `295c56c31b…:4` · 4CH1/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2(a) | ice turns into water solid carbon dioxide turns directly into a gas a solute is stirred into a solven…

#### `g1-046` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Empirical formula before I can understand Molecular formula?
> **Gold spec points:** 4CH1-1.32 · 4CH1-1.33
> **Gold concepts:** 4CH1-CON-EMPIRICAL-FORMULA · 4CH1-CON-MOLECULAR-FORMULA
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-MOLECULAR-FORMULA->4CH1-CON-EMPIRICAL-FORMULA — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `0ec62ea717…:10` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > | Answer | Notes | Marks 6 b iii | (compounds / molecules / substances with) same molecular formula / same number of each type of atom | Ignore same…
- **tier 1** (`R2-term-cooccurrence`) → `96bdc4705e…:6` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > Complete the following equation by inserting the appropriate state symbols. \mathrm {L i} _ {3} \mathrm {N} (\mathrm {s}) + 3 \mathrm {H} _ {2} \math…
- **tier 1** (`R2-term-cooccurrence`) → `2c192320c2…:4` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 3(a) | molecular formula | C3H6 | ACCEPT propyleneACCEPT N or other letters e.g. x | 4 name of this alkene |…
- **tier 1** (`R2-term-cooccurrence`) → `5f9b96f76a…:6` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (f) Old refrigerators may contain substances that harm the ozone layer in the atmosphere. Many new refrigerators use 152a, an organic compound that d…
- **tier 1** (`R2-term-cooccurrence`) → `fa60642a0e…:8` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 5 | d | i | | but-1-ene | Accept butene Ignore mention of cis or trans | 1 | | ii | | C4H8 | | 1 | | iii |…

#### `g1-047` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Concentration of a solution before I can understand Factors affecting the rate of reaction?
> **Gold spec points:** 4CH1-1.34C · 4CH1-3.10
> **Gold concepts:** 4CH1-CON-CONCENTRATION · 4CH1-CON-RATE-FACTORS
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-RATE-FACTORS->4CH1-CON-CONCENTRATION — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `e5556d9d8c…:13` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Is the zinc or the hydrochloric acid in excess? Explain your answer. (c) The student repeated the experiment with 0.0075 mol of magnesium powder with…
- **tier 1** (`R2-term-cooccurrence`) → `c8b8f0758b…:13` · 4CH0/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > Is the zinc or the hydrochloric acid in excess? Explain your answer. (c) The student repeated the experiment with 0.0075 mol of magnesium powder with…
- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:20` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 13(a) | | Initial | After1min | Penalise missing trailing zeroes and/or extra zeroes once onlye.g.16/16.00 |…
- **tier 1** (`R2-term-cooccurrence`) → `2f11ca6ab8…:5` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2 | (a)(i) | (solute is) the substance/solid that dissolves(in a solvent) OWTTE | | 1 (ii) | (solvent is) th…
- **tier 1** (`R2-term-cooccurrence`) → `f67d0dfb4a…:3` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 3(c) | copper sulfate/copper ions completely reacted/been used up/run out IGNORE copper completely…

#### `g1-048` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Covalent bond before I can understand Bond energy calculations?
> **Gold spec points:** 4CH1-1.44 · 4CH1-1.45 · 4CH1-3.7C
> **Gold concepts:** 4CH1-CON-BOND-ENERGY-CALC · 4CH1-CON-COVALENT-BOND
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-BOND-ENERGY-CALC->4CH1-CON-COVALENT-BOND — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `de0d5a687a…:13` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c)(i) | M1 displayed formula of chloroethene C=CCl H H H | IGNORE bond angles IGNORE brackets/n | 3 | M2 c…
- **tier 1** (`R2-term-cooccurrence`) → `98c0133538…:8` · 4CH1/2CR QUESTION_PAPER p.1 · state SUGGESTED
  > \mathrm {C} _ {2} \mathrm {H} _ {4} (\mathrm {g}) + \mathrm {H} _ {2} \mathrm {O} (\mathrm {g}) \rightleftharpoons \mathrm {C} _ {2} \mathrm {H} _ {5…
- **tier 1** (`R2-term-cooccurrence`) → `034516a426…:7` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a) | M1 shared pair(s) of electronsM2 attracted to(two) nuclei | REJECT nucleus.Must be plural for M2M2 de…
- **tier 1** (`R2-term-cooccurrence`) → `56c67b2c2a…:8` · 4CH1/2C QUESTION_PAPER p.1 · state SUGGESTED
  > The student calculates that the heat energy absorbed by the water is 18.2 kJ. Show that the results of this experiment give an approximate value for…
- **tier 1** (`R2-term-cooccurrence`) → `da0b8fe107…:6` · 4CH1/2C QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) Draw the displayed formula of the ester that forms when propanoic acid reacts with ethanol. (iii) Esters have particular uses that depend on the…

#### `g1-049` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Anions and cations and their migration to cathode and anode before I can understand Electrolysis?
> **Gold spec points:** 4CH1-1.57C · 4CH1-1.58C
> **Gold concepts:** 4CH1-CON-ANODE-CATHODE · 4CH1-CON-ELECTROLYSIS
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-ELECTROLYSIS->4CH1-CON-ANODE-CATHODE — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:22` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 15(a) | M1 break down/decomposition of a compoundM2 using electricity | ALLOW electrolyte/substance for comp…
- **tier 1** (`R2-term-cooccurrence`) → `fa60642a0e…:6` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 4 | d | | M1 | galvanising / sacrificial (protection) | Ignore references to anode / cathode | 1 | | | M2…
- **tier 1** (`R2-term-cooccurrence`) → `9bb3e3d6ff…:9` · 4CH0/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c)i | all 9 points plotted correctly to nearest gridline | Deduct 1 mark for each error Award these marks…
- **tier 1** (`R2-term-cooccurrence`) → `be35905e00…:6` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Describe how the student can obtain pure, dry crystals of hydrated sodium sulfate from the solution. (c) Crystals of hydrated sodium sulfate decompos…
- **tier 1** (`R2-term-cooccurrence`) → `bd1bc88542…:6` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > (iii) | A hydrogen B is incorrect as oxygen is not formed at the cathode C is incorrect as sodium is not formed when graphite electrodes are used D i…

#### `g1-050` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Paper chromatography before I can understand 4CH1-PR-02?
> **Gold spec points:** 4CH1-1.10
> **Gold concepts:** 4CH1-CON-CHROMATOGRAPHY
> **Provenance:** endpoint_non_concept=['4CH1-PR-02'] · rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-PR-02->4CH1-CON-CHROMATOGRAPHY — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `136b500f07…:1` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > 7 Li | 9 Be 3 Lithium | 4 Beryllium 23 Na Sodium | 24 Mg Magnesium 39 K Potassium | 40 Ca Calcium 86 Rb Rubidium | 88 Sr Strontium 133 Cs Caesium | 1…
- **tier 1** (`R2-term-cooccurrence`) → `ae36e95e78…:2` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `ce65d4fd54…:3` · 4CH1/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `465b699921…:2` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `61abeb4e83…:1` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > 1 The box shows some methods that can be used in separating mixtures. crystallisation | dissolving | evaporation | filtration paper chromatography |…

#### `g1-051` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Covalent bond before I can understand Dot-and-cross diagrams for covalent substances?
> **Gold spec points:** 4CH1-1.44 · 4CH1-1.45 · 4CH1-1.46
> **Gold concepts:** 4CH1-CON-COVALENT-BOND · 4CH1-CON-DOT-CROSS-COVALENT
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-DOT-CROSS-COVALENT->4CH1-CON-COVALENT-BOND — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `de0d5a687a…:13` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c)(i) | M1 displayed formula of chloroethene C=CCl H H H | IGNORE bond angles IGNORE brackets/n | 3 | M2 c…
- **tier 1** (`R2-term-cooccurrence`) → `034516a426…:7` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a) | M1 shared pair(s) of electronsM2 attracted to(two) nuclei | REJECT nucleus.Must be plural for M2M2 de…
- **tier 1** (`R2-term-cooccurrence`) → `5f9b96f76a…:6` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (f) Old refrigerators may contain substances that harm the ozone layer in the atmosphere. Many new refrigerators use 152a, an organic compound that d…
- **tier 1** (`R2-term-cooccurrence`) → `fc38cf9a0b…:7` · 4CH0/1CR MARK_SCHEME p.1 · state SUGGESTED
  > | IGNORE light(er)/high strength to weight ratio/references to cost/lightweight/does not rust | | | | | Total Question number | Answer | Accept | Rej…
- **tier 1** (`R2-term-cooccurrence`) → `df8fd0f8c2…:1` · 4CH0/1C QUESTION_PAPER p.1 · state VALIDATED
  > (a) Which one of the three particles has a negative charge? (b) Which one of the three particles has the smallest mass? (c) Use words from the box to…

#### `g1-052` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Do I need to master Exothermic and endothermic reactions before I can understand Position of equilibrium?
> **Gold spec points:** 4CH1-3.1 · 4CH1-3.21C · 4CH1-3.22C
> **Gold concepts:** 4CH1-CON-EQ-POSITION · 4CH1-CON-EXO-ENDO
> **Provenance:** rule=R2 · source=edge:REQUIRES_PREREQUISITE:4CH1-CON-EQ-POSITION->4CH1-CON-EXO-ENDO — substrate `kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `c4e2178d93…:8` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 8 | M1- add (aqueous) bromine to (aqueous) KCl | | | 5 M2- no change | orange/ yellow/brown soluti…
- **tier 1** (`R2-term-cooccurrence`) → `c928be1d9d…:9` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7(a)(i) | M1 yield decreases AND reaction shifts towards the left hand side | ALLOW backward reaction | 2 M2…
- **tier 1** (`R2-term-cooccurrence`) → `5a98b7f5db…:15` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (i) Identify the concordant results by placing ticks ( $ \checkmark $ ) in the table where appropriate. (ii) Use your ticked results to calculate the…
- **tier 1** (`R2-term-cooccurrence`) → `e5285c8628…:11` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > 4 \mathrm {N H} _ {3} (\mathrm {g}) + 5 \mathrm {O} _ {2} (\mathrm {g}) \rightleftharpoons 4 \mathrm {N O} (\mathrm {g}) + 6 \mathrm {H} _ {2} \mathr…
- **tier 1** (`R2-term-cooccurrence`) → `e5556d9d8c…:14` · — QUESTION_PAPER p.1 · state SUGGESTED
  > (b) (i) Use the graph to state the effect on the percentage of ammonia at equilibrium of the following changes an increase in temperature at constant…

### Class 5 — Misconception questions (`misconception`, 10/10 sampled)

#### `g1-053` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'predicting that a pressure change shifts equilibrium to the side with…' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-3.21C · 4CH1-3.22C
> **Gold concepts:** 4CH1-CON-EQ-POSITION
> **Gold misconceptions:** 4CH1-MIS-EQ-PRESSURE-FEWER
> **Provenance:** rule=R2 · source=edge:WRONG_ANSWER_PATTERN:4CH1-MIS-EQ-PRESSURE-FEWER->4CH1-CON-EQ-POSITION — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `c4e2178d93…:8` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 8 | M1- add (aqueous) bromine to (aqueous) KCl | | | 5 M2- no change | orange/ yellow/brown soluti…
- **tier 1** (`R2-term-cooccurrence`) → `d7c4a09cd6…:15` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 8(a)(i)(ii) | 能量H2(g)+I2(g)Ecat△H2HI(g) | curve from reactant level to product level with peak below that of…
- **tier 1** (`R2-term-cooccurrence`) → `250fb27db9…:12` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 5 | d | (i) | M1 | reversible / can go in both directions / (both) forward and reverse reactions can occur…
- **tier 1** (`R2-term-cooccurrence`) → `cf90825ca8…:8` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a)(i) | M1 the equilibrium shifts to the left(as temperature increases) | ALLOW the reaction moves in the…
- **tier 1** (`R2-term-cooccurrence`) → `fa60642a0e…:17` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 8 | d | i | M1 | decreased | No ECF from increased / no effectAccept longer time for reactionIgnore refere…

#### `g1-054` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'saying covalent bonds are broken when simple molecular substances mel…' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.47 · 4CH1-1.48
> **Gold concepts:** 4CH1-CON-SIMPLE-MOLECULAR
> **Gold misconceptions:** 4CH1-MIS-COVALENT-BONDS-BROKEN
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-COVALENT-BONDS-BROKEN->4CH1-CON-SIMPLE-MOLECULAR — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `af3e685fd0…:9` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7 a | fractional distillation/fractionating column/tower (crude oil) heated/vaporised/boiled cooler at top/h…
- **tier 1** (`R2-term-cooccurrence`) → `f5b6cd140f…:4` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 3(a) | alkanes | | 1 (b)(i) | A boiling point is the correct answer because fractional distillation depends…
- **tier 1** (`R2-term-cooccurrence`) → `034516a426…:7` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a) | M1 shared pair(s) of electronsM2 attracted to(two) nuclei | REJECT nucleus.Must be plural for M2M2 de…
- **tier 1** (`R2-term-cooccurrence`) → `7758a51c10…:5` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 5(a) | M1 heatedM2(until it is) vaporised | ALLOW boiledALLOW raised to high temperature/temperature above35…
- **tier 1** (`R2-term-cooccurrence`) → `512af760e5…:3` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > $ ^{*} $ The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and…

#### `g1-055` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'explaining a catalyst's effect as particles gaining energy or moving …' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-3.12 · 4CH1-3.13
> **Gold concepts:** 4CH1-CON-CATALYST
> **Gold misconceptions:** 4CH1-MIS-CATALYST-PARTICLE-ENERGY
> **Provenance:** rule=R2 · source=edge:WRONG_ANSWER_PATTERN:4CH1-MIS-CATALYST-PARTICLE-ENERGY->4CH1-CON-CATALYST — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `7758a51c10…:3` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > | Question number | Answer | Notes | Marks 3 | (a) | M1(crystals)-get smaller | ACCEPT disappear IGNORE dissolve IGNORE reference to(incorrect) colou…
- **tier 1** (`R2-term-cooccurrence`) → `56b6c614ef…:13` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 8 | a | i | high / higher (temperature) because (forward) reaction is endothermic / absorbs heat | Accept re…

#### `g1-056` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'drawing gas particles touching each other or joined by bonds' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.1 · 4CH1-1.3
> **Gold concepts:** 4CH1-CON-STATE-PARTICLE-MODEL
> **Gold misconceptions:** 4CH1-MIS-GAS-PARTICLES-TOUCH
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-GAS-PARTICLES-TOUCH->4CH1-CON-STATE-PARTICLE-MODEL — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `ad168ca9fc…:3` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 1 a i | six circles separated from each other | Accept minimum of 4 complete circles Ignore size and shape o…

#### `g1-057` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'describing ionic bonding as attraction between atoms or molecules' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.41
> **Gold concepts:** 4CH1-CON-IONIC-BOND
> **Gold misconceptions:** 4CH1-MIS-IONIC-BOND-ATOMS
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-IONIC-BOND-ATOMS->4CH1-CON-IONIC-BOND — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `bd1bc88542…:5` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 4(d) | An planation linking the following five points M1water is covalently bonded/has a simple molecular st…
- **tier 1** (`R2-term-cooccurrence`) → `ad168ca9fc…:18` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 9 d ii | M1 layers/sheets/planes/rows AND(positive)ions/atoms/particles | | 2 M2 slide(over each other) | Al…
- **tier 1** (`R2-term-cooccurrence`) → `034516a426…:7` · 4CH1/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a) | M1 shared pair(s) of electronsM2 attracted to(two) nuclei | REJECT nucleus.Must be plural for M2M2 de…
- **tier 1** (`R2-term-cooccurrence`) → `d4dbfed8a0…:7` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a)(i) | H $ ^{x} $ H | ACCEPT any combination of dots and crosses | 1 NB H does not need to be shown if to…
- **tier 1** (`R2-term-cooccurrence`) → `95544412b9…:14` · 4CH0/1CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 9 | a | i | gains oxygen | Accept increase in oxidation number/state Ignore reference to loss of electrons |…

#### `g1-058` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'failing to convert cm3 to dm3 in concentration calculations' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.34C
> **Gold concepts:** 4CH1-CON-VOL-CONVERSION
> **Gold misconceptions:** 4CH1-MIS-CONC-UNIT
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-CONC-UNIT->4CH1-CON-VOL-CONVERSION — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `e02c65ad9f…:10` · — QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) The concentration of the hydrogen peroxide solution in experiment S was $ 0. 4 0 \mathrm{m o l} / \mathrm{d m}^{3}. $ Use the graph to deduce th…
- **tier 1** (`R2-term-cooccurrence`) → `93db3ed101…:10` · 4CH0/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) The concentration of the hydrogen peroxide solution in experiment S was $ 0. 4 0 \mathrm{m o l} / \mathrm{d m}^{3}. $ Use the graph to deduce th…
- **tier 1** (`R2-term-cooccurrence`) → `868a150c1a…:3` · 4CH1/2CR QUESTION_PAPER p.1 · state VALIDATED
  > (c) One of the hydrocarbons in crude oil is an alkane with this structural formula. \mathrm {C H} _ {3} \mathrm {C H} _ {2} \mathrm {C H} _ {2} \math…
- **tier 1** (`R2-term-cooccurrence`) → `103502ffda…:7` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > (c) In the future, it may be necessary to convert the ethanol (produced by reaction 2) into ethene. Write the equation for this reaction and state th…
- **tier 1** (`R2-term-cooccurrence`) → `d59ce7ec2c…:18` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > Volume of potassium hydroxide solution | 25.0cm3 Volume of sulfuric acid | 23.60cm3 Concentration of sulfuric acid | 0.0500mol/dm3 He used these resu…

#### `g1-059` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'believing isotopes of an element differ in their number of protons' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.16 · 4CH1-1.17
> **Gold concepts:** 4CH1-CON-ISOTOPES
> **Gold misconceptions:** 4CH1-MIS-ISOTOPES-DIFFER-PROTONS
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-ISOTOPES-DIFFER-PROTONS->4CH1-CON-ISOTOPES — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `20d8089be2…:2` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 1 | a | | | cross in box C (neutrons and protons) | | 1 | | | | | | | b | i | | 6 | | 1 | | |…
- **tier 1** (`R2-term-cooccurrence`) → `5131935830…:2` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > BLANK PAGE Answer ALL questions. 1 The diagram shows six pieces of apparatus that are used in the laboratory. A B C D E F The table lists the names o…
- **tier 1** (`R2-term-cooccurrence`) → `e5285c8628…:2` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > BLANK PAGE Answer ALL questions. 1 This question is about the element beryllium. (a) Use words from the box to complete the sentences about beryllium…
- **tier 1** (`R2-term-cooccurrence`) → `361de44773…:1` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Our aim is to help everyone progress in their lives through education. We believe in every kind of learning, for all kinds of people, wherever they a…
- **tier 1** (`R2-term-cooccurrence`) → `79bd80919c…:3` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > Answer ALL questions. 1 The table shows the numbers of particles in two atoms, L and M. | Atom L | Atom M number of electrons | 6 | 6 number of neutr…

#### `g1-060` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'quoting the molar enthalpy change as the unconverted joule value inst…' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-3.4
> **Gold concepts:** 4CH1-CON-MOLAR-ENTHALPY
> **Gold misconceptions:** 4CH1-MIS-ENTHALPY-UNIT-J
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-ENTHALPY-UNIT-J->4CH1-CON-MOLAR-ENTHALPY — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `682b67c880…:9` · 4CH0/2CR QUESTION_PAPER p.1 · state SUGGESTED
  > (iv) The student uses the results from experiment 3 to calculate the molar enthalpy change, in kJ/mol, for the combustion of methane. She compares he…
- **tier 1** (`R2-term-cooccurrence`) → `78d67bd9c0…:9` · — QUESTION_PAPER p.1 · state SUGGESTED
  > (iv) The student uses the results from experiment 3 to calculate the molar enthalpy change, in kJ/mol, for the combustion of methane. She compares he…
- **tier 1** (`R2-term-cooccurrence`) → `cbff9c92ef…:10` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (iii) In the reaction, 0.0500 mol of hydrochloric acid completely react. Calculate the molar enthalpy change, $ \Delta H $ , in kilojoules per mole o…
- **tier 1** (`R2-term-cooccurrence`) → `5a0d064fb5…:12` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) In this experiment the student uses 1.70g of the anhydrous copper(II) sulfate Calculate the molar enthalpy change $ (\Delta H) $ in kJ/mol. Incl…

#### `g1-061` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'calling the periodic table relative atomic mass the mass number' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-1.26 · 4CH1-1.28
> **Gold concepts:** 4CH1-CON-AR
> **Gold misconceptions:** 4CH1-MIS-RAM-MASS-NUMBER
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-RAM-MASS-NUMBER->4CH1-CON-AR — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `5131935830…:2` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > BLANK PAGE Answer ALL questions. 1 The diagram shows six pieces of apparatus that are used in the laboratory. A B C D E F The table lists the names o…
- **tier 1** (`R2-term-cooccurrence`) → `babfe26bcb…:2` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R2-term-cooccurrence`) → `05952b3ad6…:6` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 4(a) | C(elements) The only correct answer is C because the substances found in the Periodic Table are eleme…
- **tier 1** (`R2-term-cooccurrence`) → `90f25c1401…:3` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > A B C D E □ □ □ □ □ (b) Complete these sentences by placing a cross ( $ \boxtimes $ ) in one box next to the correct answer. (i) The elements in the…
- **tier 1** (`R2-term-cooccurrence`) → `a5eacc1113…:7` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > \mathrm {X C O} _ {3} (\mathrm {s}) + 2 \mathrm {H N O} _ {3} (\mathrm {a q}) \rightarrow \mathrm {X} \left(\mathrm {N O} _ {3}\right) _ {2} (\mathrm…

#### `g1-062` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Why is 'counting the wrong number or type of bonds in bond-energy calculations' a wrong idea, and what is the correct picture?
> **Gold spec points:** 4CH1-3.7C
> **Gold concepts:** 4CH1-CON-BOND-ENERGY-CALC
> **Gold misconceptions:** 4CH1-MIS-BOND-ENERGY-COUNT
> **Provenance:** rule=R2 · source=edge:REMEDIATED_BY:4CH1-MIS-BOND-ENERGY-COUNT->4CH1-CON-BOND-ENERGY-CALC — substrate `kg+chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `f2afa60dc1…:16` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 10 | b | i | M1 | green precipitate | Accept solid / suspension Ignore qualifiers such as pale / light / d…
- **tier 1** (`R2-term-cooccurrence`) → `e7ce0faf0e…:8` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 5(c)(i) | aluminium/it is more reactive/higher in the reactivity series than carbon ORA | ALLOW aluminium is…
- **tier 1** (`R2-term-cooccurrence`) → `fa60642a0e…:12` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | | Answer | Notes | Marks 7 | a | i | M1 | (A) reduced AND(B) oxidised | If first column blank,M1 can be scored from words in second…
- **tier 1** (`R2-term-cooccurrence`) → `c904de1e03…:8` · 4CH0/1C MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 8(a)(i) | CH4 | AcceptH4C | 1 C2H6 | AcceptH6C2 | 1 CH3CH2CH3 | AcceptCH3-CH2-CH3/H3C-CH2-CH3 | 1 H H H H |…
- **tier 1** (`R2-term-cooccurrence`) → `9a2262007b…:4` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 3 | (a)(i)(ii) | $2H_{2}S(g)+SO_{2}(g)\rightarrow 3S(s)+2H_{2}O(l)$ | | M1 all state symbols correct | ALLOW…

### Class 6 — Why did I get this wrong? (`why_wrong`, 10/10 sampled)

#### `g1-063` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'Oxides can be made by burning elements in air' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=4CH1-S2-g · rule=R1+R3 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `f06f808464…:2` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > (c) Which substance is an element that is a green gas at room temperature? (d) Which substance is used to sterilise water? (e) Which substance is a m…
- **tier 1** (`R3-paper-cohort`) → `20d8089be2…:7` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 4 | a | | M1 | concentration | Ignore from the same bottle | 1 | | | M2 | temperature/same tem…
- **tier 1** (`R3-paper-cohort`) → `790877f765…:2` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 2(a)(i)(ii) | D | d | | 1 A | a | | 1 (b) | M1-B | b | contains other colours | 1 M2- the spots do…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 4(a)(i) | Contains a (carbon to carbon) double bond / contains C=C / multiple bond IGNORE…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:10` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 8(a) | It (like water) is a colourless (liquid) Ignore it is clear / transparent Ignore r…

#### `g1-064` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'Magnesium chloride can be made by reacting excess magnesium carbonate with dilute hydrochloric acid' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=4CH1-S1-e · rule=R1+R3 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `f06f808464…:8` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > 7 Magnesium chloride can be made by reacting excess magnesium carbonate with dilute hydrochloric acid. The equation for the reaction is \mathrm {M g…
- **tier 1** (`R3-paper-cohort`) → `20d8089be2…:7` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 4 | a | | M1 | concentration | Ignore from the same bottle | 1 | | | M2 | temperature/same tem…
- **tier 1** (`R3-paper-cohort`) → `790877f765…:2` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 2(a)(i)(ii) | D | d | | 1 A | a | | 1 (b) | M1-B | b | contains other colours | 1 M2- the spots do…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 4(a)(i) | Contains a (carbon to carbon) double bond / contains C=C / multiple bond IGNORE…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:10` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 8(a) | It (like water) is a colourless (liquid) Ignore it is clear / transparent Ignore r…

#### `g1-065` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'This question is about carboxylic acids' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH12CJANUARY2021 · rule=R1+R3 · source=qversion[4CH1/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `13b8cded84…:3` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > (b) Describe the test for hydrogen gas. (Total for Question 2 = 5 marks) 3 This question is about carboxylic acids. Solutions of carboxylic acids rea…
- **tier 1** (`R3-paper-cohort`) → `7649654514…:2` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > When examiners are in doubt regarding the application of the mark scheme to a candidate's response,the team leader must be consulted. Crossed out wor…
- **tier 1** (`R3-paper-cohort`) → `9a2262007b…:0` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > PMT Pearson Edexcel Mark Scheme (Results) November 2021 Pearson Edexcel International GCSE In Chemistry (4CH1) Paper 2C Edexcel and BTEC Qualificatio…
- **tier 1** (`R3-paper-cohort`) → `66a8d87f23…:3` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2(a)(i)(ii) | M1 oxygen | ALLOW air/O2 | 2 M2 water | ALLOW moisture/water vapour/H2O | painting/oiling/coat…
- **tier 1** (`R3-paper-cohort`) → `cfae503ca6…:10` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c) | ethyl ethanoate | ALLOW ethyl acetate | 1 (d)(i)(ii) | condensation (polymerisation) C=C-CH2CH2-C-O-C…

#### `g1-066` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'This question is about Group 1 metals and their reactions.' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH12CRJANUARY2020 · rule=R1+R3 · source=qversion[4CH1/2CR] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `960bce5cd1…:6` · 4CH1/2CR QUESTION_PAPER p.1 · state VALIDATED
  > One of the products of this electrolysis is lead. (i) State why solid lead(II) bromide does not conduct electricity. (ii) Bromine is formed by the ox…
- **tier 1** (`R3-paper-cohort`) → `36455b0823…:11` · 4CH1/2CR MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 7(a)(i) | CO2 | | 1 (ii) | (otherwise) ethanoic acid will form | ALLOW(otherwise) ethanol will be oxidised o…
- **tier 1** (`R3-paper-cohort`) → `cda9b6c006…:5` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > (v) | (OH-ions/they) are present in/come from water OWTTE | ACCEPT(some) water molecules dissociate to give OH-ions OWTTE ALLOW because copper sulfat…
- **tier 1** (`R3-paper-cohort`) → `fdfa109ccf…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > January 2021 Publications Code 4CH1_2CR_2101_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Education Ltd 2021 All…
- **tier 1** (`R3-paper-cohort`) → `8a8c83c985…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question Paper Log Number P71953A Publications Code 4CH1_2CR_2306_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Ed…

#### `g1-067` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'Hydrogen is used as a fuel' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=4CH1-S3-a · rule=R1+R3 · source=qversion[4CH0/1C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `df8fd0f8c2…:12` · 4CH0/1C QUESTION_PAPER p.1 · state VALIDATED
  > (e) A student mixed together the acid and alkali to form sodium nitrate solution. She used the volumes needed for complete reaction found in the titr…
- **tier 1** (`R3-paper-cohort`) → `0ec62ea717…:15` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 8(c)i | all six points plotted to nearest gridline | Deduct 1 mark for each error up to max 2, including ext…
- **tier 1** (`R3-paper-cohort`) → `c377331412…:13` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > | | If any other incorrect reagent added e.g. barium chloride then only M1 can be scored | (d) clip(ii) | [208-(2x35.5)=]137 | | 1 A is barium/Ba | A…
- **tier 1** (`R3-paper-cohort`) → `c904de1e03…:6` · 4CH0/1C MARK_SCHEME p.1 · state VALIDATED
  > 6(b)(i) | barium sulfate/BaSO4 | | 1 (ii) | (dilute) hydrochloric acid/HCl | Accept other suitable acids(name or formula)such asHNO3/CH3COOHIgnore hy…
- **tier 1** (`R3-paper-cohort`) → `d4dbfed8a0…:15` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > (d)(i) | M1 positive ions/cations/nuclei and delocalised electrons M2 attract (one another) M2 dep on M1 | IGNORE metal ions ALLOW sea of electrons I…

#### `g1-068` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: '(a) Two substances are needed to cause iron to rust' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH12CRJANUARY2022 · rule=R1+R3 · source=qversion[4CH1/2CR] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `868a150c1a…:2` · 4CH1/2CR QUESTION_PAPER p.1 · state VALIDATED
  > The lanthanoids (atomic numbers 58-71) and the actinoids (atomic numbers 90-103) have been omitted. The relative atomic masses of copper and chlorine…
- **tier 1** (`R3-paper-cohort`) → `36455b0823…:11` · 4CH1/2CR MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 7(a)(i) | CO2 | | 1 (ii) | (otherwise) ethanoic acid will form | ALLOW(otherwise) ethanol will be oxidised o…
- **tier 1** (`R3-paper-cohort`) → `cda9b6c006…:5` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > (v) | (OH-ions/they) are present in/come from water OWTTE | ACCEPT(some) water molecules dissociate to give OH-ions OWTTE ALLOW because copper sulfat…
- **tier 1** (`R3-paper-cohort`) → `fdfa109ccf…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > January 2021 Publications Code 4CH1_2CR_2101_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Education Ltd 2021 All…
- **tier 1** (`R3-paper-cohort`) → `8a8c83c985…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question Paper Log Number P71953A Publications Code 4CH1_2CR_2306_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Ed…

#### `g1-069` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'The mineral nesquehonite is a form of hydrated magnesium carbonate' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH12CSPECIMEN2017 · rule=R1+R3 · source=qversion[4CH1/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `6a9a10e439…:7` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > 6 The mineral nesquehonite is a form of hydrated magnesium carbonate. The formula, $ \mathrm{M g C O_{3}. x H_{2} O} $ , shows that nesquehonite cont…
- **tier 1** (`R3-paper-cohort`) → `7649654514…:2` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > When examiners are in doubt regarding the application of the mark scheme to a candidate's response,the team leader must be consulted. Crossed out wor…
- **tier 1** (`R3-paper-cohort`) → `9a2262007b…:0` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > PMT Pearson Edexcel Mark Scheme (Results) November 2021 Pearson Edexcel International GCSE In Chemistry (4CH1) Paper 2C Edexcel and BTEC Qualificatio…
- **tier 1** (`R3-paper-cohort`) → `66a8d87f23…:3` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2(a)(i)(ii) | M1 oxygen | ALLOW air/O2 | 2 M2 water | ALLOW moisture/water vapour/H2O | painting/oiling/coat…
- **tier 1** (`R3-paper-cohort`) → `cfae503ca6…:10` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c) | ethyl ethanoate | ALLOW ethyl acetate | 1 (d)(i)(ii) | condensation (polymerisation) C=C-CH2CH2-C-O-C…

#### `g1-070` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'Crude oil is a complex mixture of organic compounds called hydrocarbons' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-SUMMER2016 · rule=R1+R3 · source=qversion[None] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `431606b12a…:6` · — QUESTION_PAPER p.1 · state VALIDATED
  > Use the diagram to complete the table. Give the readings to the nearest 0.05 $ \mathrm{c m}^{3}. $ Burette reading after adding the acid | Burette re…
- **tier 2** (`R1-stem-verbatim`) → `821c1d9f59…:6` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > (e) A second student did the experiment four times, using a different solution of potassium hydroxide. The table shows her results. Volume in $ \math…

#### `g1-071` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'The table shows the names of some substances' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH02CJANUARY2016 · rule=R1+R3 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `b8613965b7…:1` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > 7 Li | 9 Be 23 Na | 24 Mg 39 K | 40 Ca 86 Rb | 88 Sr 133 Cs | 137 Ba 223 Fr | 226 Ra Answer ALL questions. 1 The table shows the names of some common…
- **tier 1** (`R3-paper-cohort`) → `20d8089be2…:7` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 4 | a | | M1 | concentration | Ignore from the same bottle | 1 | | | M2 | temperature/same tem…
- **tier 1** (`R3-paper-cohort`) → `790877f765…:2` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 2(a)(i)(ii) | D | d | | 1 A | a | | 1 (b) | M1-B | b | contains other colours | 1 M2- the spots do…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 4(a)(i) | Contains a (carbon to carbon) double bond / contains C=C / multiple bond IGNORE…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:10` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 8(a) | It (like water) is a colourless (liquid) Ignore it is clear / transparent Ignore r…

#### `g1-072` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** For this exam question: 'A student investigates the temperature rise of water in a copper can placed above a spirit burner containing a flammable liquid' — what are the common mistakes students make?
> **Provenance:** anchor_code_non_spec=ING-4CH02CJANUARY2016 · rule=R1+R3 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `b8613965b7…:9` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > (Total for Question 6 = 13 marks) 7 A student investigates the temperature rise of water in a copper can placed above a spirit burner containing a fl…
- **tier 1** (`R3-paper-cohort`) → `20d8089be2…:7` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | | Answer | Notes | Marks | | | | | | 4 | a | | M1 | concentration | Ignore from the same bottle | 1 | | | M2 | temperature/same tem…
- **tier 1** (`R3-paper-cohort`) → `790877f765…:2` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Accept | Reject | Marks 2(a)(i)(ii) | D | d | | 1 A | a | | 1 (b) | M1-B | b | contains other colours | 1 M2- the spots do…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 4(a)(i) | Contains a (carbon to carbon) double bond / contains C=C / multiple bond IGNORE…
- **tier 1** (`R3-paper-cohort`) → `e50985bda8…:10` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Expected answer | Accept | Reject | Marks 8(a) | It (like water) is a colourless (liquid) Ignore it is clear / transparent Ignore r…

### Class 7 — Exam-question retrieval (`exam_question`, 2/10 sampled)

#### `g1-074` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** The diagram shows the industrial equipment used to separate crude oil into fractions.
> **Provenance:** anchor_code_non_spec=ING-4CH12CSUMMER2021 · rule=R1 · source=qversion[4CH1/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `669b7691ec…:3` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > 3 The diagram shows the industrial equipment used to separate crude oil into fractions. (a) (i) Give the name of the industrial equipment. (ii) Give…

#### `g1-075` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** A student is provided with a solution of dilute sulfuric acid and a solution of sodium hydroxide. The student does a titration using $ 2 5. 0 \mathrm{c m}^{3} $ of the sodium hydroxide solut…
> **Provenance:** anchor_code_non_spec=4CH1-S2-f · rule=R1 · source=qversion[4CH0/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 2** (`R1-stem-verbatim`) → `b2db6100bf…:2` · 4CH0/2C QUESTION_PAPER p.1 · state VALIDATED
  > (Total for Question 2 = 8 marks) 3 A student is provided with a solution of dilute sulfuric acid and a solution of sodium hydroxide. The student does…

### Class 8 — Mark-scheme retrieval (`mark_scheme`, 2/8 sampled)

#### `g1-086` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** What does the mark scheme accept for the 4CH1/2CR question: 'Substances can be classified as elements, mixtures or compounds.'?
> **Provenance:** anchor_code_non_spec=ING-4CH12CRJANUARY2020 · rule=R3 · source=qversion[4CH1/2CR] — substrate `chunks`
> **Generator notes:** auto-derived v1; selector=paper-linked (command_word unpopulated)
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R3-paper-cohort`) → `36455b0823…:11` · 4CH1/2CR MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 7(a)(i) | CO2 | | 1 (ii) | (otherwise) ethanoic acid will form | ALLOW(otherwise) ethanol will be oxidised o…
- **tier 1** (`R3-paper-cohort`) → `cda9b6c006…:5` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > (v) | (OH-ions/they) are present in/come from water OWTTE | ACCEPT(some) water molecules dissociate to give OH-ions OWTTE ALLOW because copper sulfat…
- **tier 1** (`R3-paper-cohort`) → `fdfa109ccf…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > January 2021 Publications Code 4CH1_2CR_2101_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Education Ltd 2021 All…
- **tier 1** (`R3-paper-cohort`) → `8a8c83c985…:1` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question Paper Log Number P71953A Publications Code 4CH1_2CR_2306_MS All the material in this publication is copyright $ \textcircled{c} $ Pearson Ed…
- **tier 1** (`R3-paper-cohort`) → `cda9b6c006…:3` · 4CH1/2CR MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 3(a)(i) | B $ C_{4}H_{10}$ A is incorrect as $ C_{2}H_{5} $ is not the molecular formula of an alkane C is i…

#### `g1-089` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** What does the mark scheme accept for the 4CH1/2C question: 'The diagram shows an atom of an element.'?
> **Provenance:** anchor_code_non_spec=ING-4CH12CJANUARY2021 · rule=R3 · source=qversion[4CH1/2C] — substrate `chunks`
> **Generator notes:** auto-derived v1; selector=paper-linked (command_word unpopulated)
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R3-paper-cohort`) → `7649654514…:2` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > When examiners are in doubt regarding the application of the mark scheme to a candidate's response,the team leader must be consulted. Crossed out wor…
- **tier 1** (`R3-paper-cohort`) → `9a2262007b…:0` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > PMT Pearson Edexcel Mark Scheme (Results) November 2021 Pearson Edexcel International GCSE In Chemistry (4CH1) Paper 2C Edexcel and BTEC Qualificatio…
- **tier 1** (`R3-paper-cohort`) → `66a8d87f23…:3` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 2(a)(i)(ii) | M1 oxygen | ALLOW air/O2 | 2 M2 water | ALLOW moisture/water vapour/H2O | painting/oiling/coat…
- **tier 1** (`R3-paper-cohort`) → `cfae503ca6…:10` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(c) | ethyl ethanoate | ALLOW ethyl acetate | 1 (d)(i)(ii) | condensation (polymerisation) C=C-CH2CH2-C-O-C…
- **tier 1** (`R3-paper-cohort`) → `0588a3f201…:4` · 4CH1/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Additional guidance | Mark 6(a) | All points plotted correctly(1)Best fit line drawn(1) | must be drawn with the aid of a…

### Class 9 — Revision-note retrieval (`revision_note`, 2/10 sampled)

#### `g1-091` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Give me quick revision notes covering know the general rules for predicting the solubility of ion….
> **Gold spec points:** 4CH1-2.34
> **Provenance:** rule=none-substrate-absent · source=spec_point:4CH1-2.34 — substrate `notes_mirror`
> **Generator notes:** substrate notes_mirror; per-class N/A at t0
> **Notes:** ________________________________________________________

_No gold evidence chunks for this record (spec-point-only anchor)._

#### `g1-093` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Give me quick revision notes covering know that condensation polymerisation, in which a dicarboxy….
> **Gold spec points:** 4CH1-4.48C
> **Provenance:** rule=none-substrate-absent · source=spec_point:4CH1-4.48C — substrate `notes_mirror`
> **Generator notes:** substrate notes_mirror; per-class N/A at t0
> **Notes:** ________________________________________________________

_No gold evidence chunks for this record (spec-point-only anchor)._

### Class 10 — Vague learner-language queries (`vague_learner`, 2/8 sampled)

#### `g1-101` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** I don't get understand how the formulae of simple compou… at all — help me understand it.
> **Gold spec points:** 4CH1-1.31
> **Provenance:** rule=R2 · source=spec_point:4CH1-1.31 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `4fc51e5c4a…:7` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (ii) The relative formula mass $ ( M_{\mathrm{r}}) $ of compound Z is 62 Deduce the molecular formula of compound Z. BLANK PAGE 7 This question is ab…
- **tier 1** (`R2-term-cooccurrence`) → `34dd2dabcf…:8` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (i) Explain one safety precaution that should be taken after adding the dilute sulfuric acid and before lighting the unreacted hydrogen gas. (ii) Sta…

#### `g1-104` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** can someone break down understand how to deduce the structure of a … for me please
> **Gold spec points:** 4CH1-4.46
> **Provenance:** rule=R2 · source=spec_point:4CH1-4.46 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `ede4cbebcd…:4` · 4CH0/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 5(a) | Mass of sodium hydrogencarbonate in g | Initial temperature in ℃ | Lowest temperature reached in ℃ |…
- **tier 1** (`R2-term-cooccurrence`) → `61abeb4e83…:3` · 4CH0/2C QUESTION_PAPER p.1 · state SUGGESTED
  > Draw a straight line through the first three points and another straight line through the last two points. Make sure that the two lines cross. (ii) U…
- **tier 1** (`R2-term-cooccurrence`) → `6a9a10e439…:10` · 4CH1/2C QUESTION_PAPER p.1 · state VALIDATED
  > \mathrm {H N O} _ {3} (\mathrm {a q}) + \mathrm {N H} _ {3} (\mathrm {a q}) \rightarrow \mathrm {N H} _ {4} \mathrm {N O} _ {3} (\mathrm {a q}) (i) S…
- **tier 1** (`R2-term-cooccurrence`) → `e094de544a…:12` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Corn starch from plants can also be used to make polymers for plastic bags. The table gives some information about poly(ethene) and polymers made fro…
- **tier 1** (`R2-term-cooccurrence`) → `f6ca23616e…:15` · 4CH0/1CR QUESTION_PAPER p.1 · state SUGGESTED
  > (a) Three of the fractions obtained from fractional distillation are fuel oil, gasoline and kerosene. (i) Identify which of these fractions has the d…

### Class 11 — Multi-SpecificationPoint questions (`multi_spec_point`, 2/7 sampled)

#### `g1-109` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** How do understand how to carry out calculations involving amount o… and describe the use of litmus, phenolphthalein and methyl oran… connect in this topic?
> **Gold spec points:** 4CH1-1.34C · 4CH1-2.28
> **Provenance:** rule=R2 · source=spec_points:4CH1-1.34C+4CH1-2.28 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `5a0d064fb5…:5` · 4CH1/1C QUESTION_PAPER p.1 · state SUGGESTED
  > (c) A mixture of zinc powder and copper(II) oxide is heated. The chemical equation for the reaction that takes place is (i) State how the reaction sh…
- **tier 1** (`R2-term-cooccurrence`) → `f20fe163e6…:8` · 4CH0/2C MARK_SCHEME p.1 · state VALIDATED
  > Question number | Answer | Notes | Marks 7(a)(i) | M10.080 mol of HCl react with 0.040 mol of MgCO3 | ACCEPT any method involving correct ratios of m…
- **tier 1** (`R2-term-cooccurrence`) → `f326b266dd…:7` · 4CH1/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 6(a)(i) | Any 2 from | | 2 M1 effervescence/bubbles/fizzing | | M2 moves | moves on surface scores | M3 floa…
- **tier 1** (`R2-term-cooccurrence`) → `af3e685fd0…:10` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7 b i | CnH2n+2 | Do not penalise inappropriate spaces or failure to show 2 and n as subscripts | 1 ii | sam…
- **tier 1** (`R2-term-cooccurrence`) → `5f9b96f76a…:8` · 4CH0/1C QUESTION_PAPER p.1 · state SUGGESTED
  > The formation of poly(ethene) can be represented as (a) What is the name of this type of reaction? A addition B decomposition substitution C reductio…

#### `g1-113` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** How do know that vinegar is an aqueous solution containing ethanoi… and explain why substances with a simple molecular structures a… connect in this topic?
> **Gold spec points:** 4CH1-1.47 · 4CH1-4.37C
> **Provenance:** rule=R2 · source=spec_points:4CH1-4.37C+4CH1-1.47 — substrate `chunks+kg`
> **Generator notes:** auto-derived v1
> **Notes:** ________________________________________________________

Gold evidence (tier → chunk):

- **tier 1** (`R2-term-cooccurrence`) → `0ec62ea717…:13` · 4CH0/1C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 7 d i | product formulae or names/products(word)above reactants | Horizontal line not needed Ignore formula…
- **tier 1** (`R2-term-cooccurrence`) → `df8fd0f8c2…:1` · 4CH0/1C QUESTION_PAPER p.1 · state VALIDATED
  > (a) Which one of the three particles has a negative charge? (b) Which one of the three particles has the smallest mass? (c) Use words from the box to…
- **tier 1** (`R2-term-cooccurrence`) → `66a8d87f23…:6` · 4CH1/2C MARK_SCHEME p.1 · state SUGGESTED
  > Question number | Answer | Notes | Marks 5(a) | Any two from | | 2 M1 same general formula | | M2 same functional group | | M3 similar chemical prope…
- **tier 1** (`R2-term-cooccurrence`) → `4c856f38b3…:9` · 4CH1/2C QUESTION_PAPER p.1 · state SUGGESTED
  > (b) Explain why the molar enthalpy change $ (\Delta H) $ for the reaction between ester A and water is 0 kJ/mol. In your answer, refer to the bonds b…
- **tier 1** (`R2-term-cooccurrence`) → `e094de544a…:12` · — QUESTION_PAPER p.1 · state SUGGESTED
  > Corn starch from plants can also be used to make polymers for plastic bags. The table gives some information about poly(ethene) and polymers made fro…

### Class 12 — Diagram/figure-dependent questions (`diagram_dependent`, 1/5 sampled)

#### `g1-116` — verdict: ☐ CORRECT ☐ INCORRECT

> **Query:** Draw / label the diagram required for: The diagram shows an atom of an element
> **Provenance:** anchor_code_non_spec=ING-4CH12CJANUARY2021 · rule=none-substrate-absent · source=qversion[4CH1/2C] selector=draw-cue-stem — substrate `figures`
> **Generator notes:** substrate figures; per-class N/A at t0
> **Notes:** ________________________________________________________

_No gold evidence chunks for this record (spec-point-only anchor)._

## Rollup (owner fills)

| Class | CORRECT | Sampled | Precision | ≥90%? |
|-------|--------:|--------:|----------:|-------|
| Direct factual questions | | 3 | | ☐ |
| Conceptual explanations | | 3 | | ☐ |
| Calculations | | 2 | | ☐ |
| Prerequisite questions | | 12 | | ☐ |
| Misconception questions | | 10 | | ☐ |
| Why did I get this wrong? | | 10 | | ☐ |
| Exam-question retrieval | | 2 | | ☐ |
| Mark-scheme retrieval | | 2 | | ☐ |
| Revision-note retrieval | | 2 | | ☐ |
| Vague learner-language queries | | 2 | | ☐ |
| Multi-SpecificationPoint questions | | 2 | | ☐ |
| Diagram/figure-dependent questions | | 1 | | ☐ |

Any class below 0.90 → manual re-author of that class before the next
recorded run (ruling 3). Record the outcome in TODO T-C13 + PROGRESS.
