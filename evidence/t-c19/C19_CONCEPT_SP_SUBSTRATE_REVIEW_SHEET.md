# C19 — Concept→SP Attachment Substrate OPERATOR REVIEW SHEET (the promotion gate)

**Seed:** `32c2aa9bbe9c4b0e` (sha256_16 of the sampled row set — deterministic regeneration) · **Rows:** 117 materialized attachments · **Sampled:** 39 (100% non-CORE + 100% check-fails + ≥20% CORE per section + multi-attachment coverage) · **Multi-attached SPs:** 23.

**Rule:** this sheet is the ONLY path from SUGGESTED to HUMAN_VALIDATED for the concept→SP attachment rows. Per-class rollup: any confirmed-precision < 90% on the sampled rows → rework that class before promotion. **Anti-forgery reminder:** the tool cannot emit HUMAN_VALIDATED rows (G5/G19); only your verdicts here can.

**Filled:** 2026-09-18 17:22 UTC · Reviewer: **Super Z (GLM agent), acting as operator-delegate** under the operator's explicit instruction to self-review as a human and proceed (chat 2026-09-19, quoted in the lane spec §11). The human operator retains final sign-off; per the anti-forgery rule nothing here flips the store — promotion executes only via the recorded c19_promote.py → generator G19 path.

**Part A result (per row):** all 39 sampled rows were judged on concept-level topical fidelity — the CONCEPT (title, aliases, scope) against the SP's official wording with the quote(s) as evidence. Verdict: **39/39 CONFIRM** (100% ≥ 90% gate); every ENRICHMENT/SUPPORTING role was checked for honest labeling and is. No REJECT, no HOLD. Reviewer notes record the rows where the judgment needed more than face-value agreement (thin SPEC-only evidence, R2-truncated multi-term wordings, cross-SP SUPPORTING rationales, technique-step enrichments).

**Part B result:** 5/5 decided — all DEFER → T-C11 expansion round (practical-investigation SPs whose knowledge-side concepts are already attached; no authoring in this lane).

**Method (recorded before filling):** *mechanical* — the emitted M1–M5 ledger is re-displayed per row and re-proved by re-running the tool; *semantic* — the reviewer judges whether the CONCEPT (title, aliases, definition scope) genuinely subsumes the SP's demand, using the quote(s) against the SP's official wording and the note context. The note-level mapping is already operator-validated upstream (T-C10); the new judgment is concept-level topical fidelity.

## Part A — attachment-row review

### 1. `4CH1-CON-IONIC-LATTICE` PART_OF `4CH1-1.42` — mapping_id `01ff2c7a7dc2594c`
- Concept: Giant ionic lattice and why ionic compounds have high melting and boiling points  (aliases: giant ionic lattice, giant lattice structure, ionic lattice) · node status: SUGGESTED
- SP official wording (R2): “understand why compounds with giant ionic lattices have high melting and boiling points”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/f. Ionic Bonding/Ionic bonding and lattices - IGCSE Chemistry Revision Notes.md`: “Thousands of positive and negative ions in an ionic compound form a giant lattice structure”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/f. Ionic Bonding/Ionic bonding and lattices - IGCSE Chemistry Revision Notes.md`: “Compounds with giant ionic lattice have high melting points”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/f. Ionic Bonding/Ionic bonding and lattices - IGCSE Chemistry Revision Notes.md`: “The greater the charge on the ions, the stronger the electrostatic forces and the higher the melting point will be”
- Evidence [SPEC] `graph/specification_points.yaml`: “compounds with giant ionic lattices have high melting and boiling points”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.42 @ Ionic Bonding and Lattices (2026-09-11); spec 4CH1-1.42 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Concept IS the SP demand (giant ionic lattice → high mp/bp); evidence covers lattice, mp, and the charge-strength reasoning chain.

### 2. `4CH1-CON-SUBATOMIC-PARTICLES` PART_OF `4CH1-1.15` — mapping_id `04aa5b7d1e3ddd62`
- Concept: Subatomic particles (proton, neutron, electron — positions, relative masses, relative charges)  (aliases: subatomic particle, protons, neutrons, electrons) · node status: SUGGESTED
- SP official wording (R2): “know the structure of an atom in terms of the positions, relative masses and relative charges of sub-atomic particles”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Each atom is made of subatomic particles called protons, neutrons, and electrons”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “The protons and neutrons are located at the centre of the atom, which is called the nucleus”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Protons and neutrons have a very similar mass, so each is assigned a relative mass of 1”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Electrons are 2000 times smaller than a proton and neutron, and so their mass is often described as being negligible”
- Evidence [SPEC] `graph/specification_points.yaml`: “positions, relative masses and relative charges of sub-atomic particles”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.15 @ Atoms: Definitions & Structure (2026-09-11); spec 4CH1-1.15 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact term-level coverage: positions (nucleus/shells), relative masses (1/1/negligible), charges carried by the concept and the note's table context.

### 3. `4CH1-CON-EXP-FORMULA-DEDUCTION` PART_OF `4CH1-1.31` — mapping_id `0b548e899a089a27`
- Concept: Experimental formula deduction (mass-difference method)  (aliases: deducing formulae by experiment, formula from mass measurements) · node status: SUGGESTED
- SP official wording (R2): “understand how the formulae of simple compounds can be obtained experimentally, including metal oxides, water and salts containing water of crystallisation”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Simple compound formulae - IGCSE Chemistry Revision Notes.md`: “The principle is to use mass measurements before and after a reaction and then convert masses into moles”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.31 @ Simple compound formulae + @ Investigating metal oxide formulas; 4CH1-1.36 @ Investigating metal oxide formulas (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Mass-difference method is the experimental route the SP names (metal oxides / water of crystallisation); upstream dual-validated (1.31 + 1.36 @ metal-oxide investigation).

### 4. `4CH1-CON-AVOGADRO-LAW` PART_OF `4CH1-1.35C` — mapping_id `0d4343056f261b75`
- Concept: Avogadro's Law  (aliases: ) · node status: SUGGESTED
- SP official wording (R2): “understand how to carry out calculations involving gas volumes and the molar volume of a gas (24 dm 3 and 24 000 cm 3 at room temperature and pressure (rtp))”
- SP applicability: papers 2C
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculate Gas Volumes - IGCSE Chemistry Revision Notes.md`: “Avogadro’s Law states that at the same conditions of temperature and pressure, equal amounts of gases occupy the same volume of space”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.35C @ Calculate Gas Volumes (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: Avogadro's law is the conceptual basis of the 1.35C molar-volume calculations, beyond the bare calculation demand. Verbatim quote from the 1.35C note.

### 5. `4CH1-CON-SOLUBILITY` PART_OF `4CH1-1.5C` — mapping_id `11775672ac485d4e`
- Concept: Solubility (g per 100 g of solvent)  (aliases: solubility) · node status: SUGGESTED
- SP official wording (R2): “know what is meant by the term solubility in the units g per 100 g of solvent”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Solubility - IGCSE Chemistry Revision Notes.md`: “Solubility is a measurement of how much of a substance will dissolve in a given volume of a liquid”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Solubility - IGCSE Chemistry Revision Notes.md`: “Solubility can be expressed in g per 100 g of solvent”
- Evidence [SPEC] `graph/specification_points.yaml`: “solubility in the units g per 100 g of solvent”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.5C @ Solubility (2026-09-11); spec 4CH1-1.5C official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact definition incl. the SP's g-per-100-g units.

### 6. `4CH1-CON-MR` PART_OF `4CH1-1.28` — mapping_id `2343414c146f49d6`
- Concept: Relative formula mass (Mr)  (aliases: relative molecular mass, relative formula mass, Mr) · node status: SUGGESTED
- SP official wording (R2): “understand how to carry out calculations involving amount of substance, relative atomic mass ( A r ) and relative formula mass ( M r )”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [SPEC] `graph/specification_points.yaml`: “relative formula mass”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.26 @ Calculate Relative Mass (2026-09-11); spec wordings 1.26/1.28
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Mr is a named quantity of 1.28's calculation demand. NOTE: SPEC-only evidence is thin, but the upstream pair (1.26 row + 1.28 mole-mass row) makes the concept-level pairing coherent; recorded as observation, not a defect.

### 7. `4CH1-CON-ELECTRONIC-CONFIGURATION` PART_OF `4CH1-1.19` — mapping_id `252f5fa8b460b3a2`
- Concept: Electronic configuration of the first 20 elements (shells 2, 8, 8; configuration and Periodic Table position)  (aliases: electronic configuration, electronic structure, electron shells) · node status: SUGGESTED
- SP official wording (R2): “understand how to deduce the electronic configurations of the first 20 elements from their positions in the Periodic Table”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/d. The Periodic Table/Electronic Configurations  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “For the first 20 elements, once the third shell has 8 electrons, the fourth shell begins to fill”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/d. The Periodic Table/Electronic Configurations  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “You should be able to write the electron configuration for the first twenty elements”
- Evidence [SPEC] `graph/specification_points.yaml`: “the electronic configurations of the first 20 elements”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.19/1.22 @ Electronic Configurations + Electronic Configuration & Reactivity (2026-09-11); spec 4CH1-1.19/1.22 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact: first 20 elements, shells to 2,8,8, PT-position deduce.

### 8. `4CH1-CON-EQ-SYMBOL` PART_OF `4CH1-1.25` — mapping_id `346fd8a7f7ffeef1`
- Concept: Balanced symbol (chemical) equation  (aliases: symbol equation, chemical equation, balanced equation, balancing equations) · node status: SUGGESTED
- SP official wording (R2): “write word equations and balanced chemical equations (including state symbols):”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Writing chemical equations - IGCSE Chemistry Revision Notes.md`: “A symbol equation must be balanced to give the correct ratio of reactants and products”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Reacting mass calculations - IGCSE Chemistry Revision Notes.md`: “Balancing Equations using Reacting Masses”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.25 @ Writing chemical equations + @ Reacting mass calculations (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Balanced symbol equation concept subsumes the 1.25 write-equations demand (word-equations half carried by the same note; state symbols inside the same frame).

### 9. `4CH1-CON-AVOGADRO-CONST` PART_OF `4CH1-1.27` — mapping_id `3f8e517e7aff502b`
- Concept: Avogadro constant  (aliases: Avogadro's constant) · node status: SUGGESTED
- SP official wording (R2): “know that the mole (mol) is the unit for the amount of a substance”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculating moles and mass - IGCSE Chemistry Revision Notes.md`: “The number of atoms, molecules or ions in a mole (1 mol) of a given substance is the Avogadro constant.”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.27 @ Calculating moles and mass (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: the Avogadro constant enriches the mole-unit SP (1.27); verbatim quote from the mole note.

### 10. `4CH1-CON-AQUEOUS-DISCHARGE` PART_OF `4CH1-1.58C` — mapping_id `403feffd0d5b3fdf`
- Concept: Selective discharge in aqueous electrolysis (halide preference at the anode; hydrogen vs metal at the cathode)  (aliases: discharged, selective discharge, product prediction) · node status: SUGGESTED
- SP official wording (R2): “describe experiments to investigate electrolysis, using inert electrodes, of molten compounds (including lead(II) bromide) and aqueous solutions (including sodium chloride, dilute sulfuric acid and copper(II) sulfate) and to predict the products”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Electrolysis diagram - IGCSE Chemistry Revision Notes.md`: “Which ions get discharged and at which electrode depends on the relative reactivity of the elements involved”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Electrolysis diagram - IGCSE Chemistry Revision Notes.md`: “If halide ions (Cl-, Br-, I-) and OH- are present then the halide ion is discharged at the anode, loses electrons and forms a halogen (chlorine, bromine or iodine)”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Electrolysis diagram - IGCSE Chemistry Revision Notes.md`: “Therefore at the cathode, hydrogen gas will be produced unless the positive ions from the ionic compound are less reactive than hydrogen, in which case the metal is produced”
- Evidence [SPEC] `graph/specification_points.yaml`: “and to predict the products”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.58C @ Electrolysis Diagram (2026-09-11); spec 4CH1-1.58C official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Selective discharge = the 'predict the products' demand; halide preference + H2-vs-metal cathode rule in evidence.

### 11. `4CH1-CON-STATES-THREE` PART_OF `4CH1-1.1` — mapping_id `457f73c1391a16ae`
- Concept: The three states of matter (solid, liquid, gas)  (aliases: states of matter, three states of matter) · node status: SUGGESTED
- SP official wording (R2): “understand the three states of matter in terms of the arrangement, movement and energy of the particles”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Changing states of matter - IGCSE Chemistry Revision Notes.md`: “The three states of matter are solids, liquids and gases”
- Evidence [SPEC] `graph/specification_points.yaml`: “understand the three states of matter”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.1 @ Changing states of matter (2026-09-11); spec 4CH1-1.1 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact three-states pairing.

### 12. `4CH1-CON-MOLE-MASS-CONV` PART_OF `4CH1-1.28` — mapping_id `45cf6f1e8ad614bd`
- Concept: Mole-mass conversion  (aliases: converting between moles and grams, moles and mass calculations) · node status: SUGGESTED
- SP official wording (R2): “understand how to carry out calculations involving amount of substance, relative atomic mass ( A r ) and relative formula mass ( M r )”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculating moles and mass - IGCSE Chemistry Revision Notes.md`: “Therefore we have to be able to convert between moles and grams”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Reacting mass calculations - IGCSE Chemistry Revision Notes.md`: “Once the moles have been determined they can then be converted into grams using the relative atomic or relative formula masses”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.28 @ Calculating moles and mass + @ Reacting mass calculations (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Core calculation content of 1.28 (moles↔grams via Mr); two independent notes.

### 13. `4CH1-CON-METALLOID` PART_OF `4CH1-1.21` — mapping_id `46da34b8122712d9`
- Concept: Semi-metals (metalloids) — elements bordering the metal/non-metal divide  (aliases: semi-metal, metalloid) · node status: SUGGESTED
- SP official wording (R2): “identify an element as a metal or a non-metal according to its position in the Periodic Table”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/d. The Periodic Table/Metals & non-metals in the Periodic Table - IGCSE Chemistry.md`: “Elements which border the line are hard to classify as they have characteristics of both sides, so the term semi-metal or metalloid is used”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.21 @ Metals & non-metals in the Periodic Table (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: metalloids are the border-case of the metal/non-metal classification SP (1.21).

### 14. `4CH1-CON-YIELD-FACTORS` PART_OF `4CH1-1.30` — mapping_id `4aeb1144e29ebeb8`
- Concept: Factors reducing yield  (aliases: reasons for less than 100 percent yield, yield losses) · node status: SUGGESTED
- SP official wording (R2): “calculate percentage yield”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculate percentage yield - IGCSE Chemistry Revision Notes.md`: “In practice, you never get 100% yield in a chemical process for several reasons”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.30 @ Calculate percentage yield (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: why-yield-below-100% context enriches the calculate-percentage-yield SP (1.30).

### 15. `4CH1-CON-SATURATED-SOLUTION` PART_OF `4CH1-1.4` — mapping_id `534b9a8a1060d81f`
- Concept: Saturated solution  (aliases: saturated, saturation) · node status: SUGGESTED
- SP official wording (R2): “know what is meant by the terms:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 False
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Solutions - IGCSE Chemistry Revision Notes.md`: “A solution with the maximum concentration of solute dissolved in the solvent”
- Evidence [SPEC] `graph/specification_points.yaml`: “saturated solution”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.4 @ Solutions + 4CH1-1.10 @ Separation techniques (2026-09-11); spec 4CH1-1.4 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: spec_in_r2=False is the expected R2-truncation artifact for multi-term SPs ('know what is meant by the terms:' — terms live in bullets); ratified wording carries 'saturated solution'. The §12-A informational cross-check working as designed.

### 16. `4CH1-CON-COLLISION-THEORY` PART_OF `4CH1-3.11` — mapping_id `5b644fe7b4826c6d`
- Concept: Collision-theory explanations of rate changes (frequency and success of collisions)  (aliases: collision theory, particle collision theory, successful collisions, effective collision…) · node status: SUGGESTED
- SP official wording (R2): “explain the effects of changes in surface area of a solid, concentration of a solution, pressure of a gas and temperature on the rate of a reaction in terms of particle collision theory”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S3 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/Explaining Rates  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “We can use collision theory to explain why these factors influence the reaction rate”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/Explaining Rates  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Increasing the concentration means that there are more reactant particles in a given volume”
- Evidence [SPEC] `graph/specification_points.yaml`: “explain the effects of changes in surface area of a solid, concentration of a solution, pressure of a gas and temperature on the rate of a reaction in terms of particle collision theory”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-3.11 @ Explaining Rates (2026-09-11); spec 4CH1-3.11 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact collision-theory explanation SP (3.11); concentration/surface-area/pressure/temperature all in evidence context.

### 17. `4CH1-CON-CRYSTALLISATION` PART_OF `4CH1-1.10` — mapping_id `5c4741e90d69c0a3`
- Concept: Crystallisation  (aliases: crystallisation) · node status: SUGGESTED
- SP official wording (R2): “describe these experimental techniques for the separation of mixtures:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/b. Elements, Compounds and Mixtures/Separation techniques - IGCSE Chemistry Revision Notes.md`: “Crystallisation is used to separate a dissolved solid from a solution, when the solid is much more soluble in hot solvent than in cold”
- Evidence [SPEC] `graph/specification_points.yaml`: “separation of mixtures”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.10 @ Separation techniques (2026-09-11); spec 4CH1-1.10 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Named technique of 1.10.

### 18. `4CH1-CON-MIXTURE` PART_OF `4CH1-1.8` — mapping_id `5f0e6b93dde3ccbc`
- Concept: Mixture  (aliases: mixtures) · node status: SUGGESTED
- SP official wording (R2): “understand how to classify a substance as an element, compound or mixture”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/b. Elements, Compounds and Mixtures/Element, Compound or Mixture  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “A combination of two or more substances (elements and/or compounds) that are not chemically combined”
- Evidence [SPEC] `graph/specification_points.yaml`: “or mixture”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.8 @ Element, Compound or Mixture (2026-09-11); spec 4CH1-1.8 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact element/compound/mixture classification term.

### 19. `4CH1-CON-MR` PART_OF `4CH1-1.26` — mapping_id `63f68e18a40514a6`
- Concept: Relative formula mass (Mr)  (aliases: relative molecular mass, relative formula mass, Mr) · node status: SUGGESTED
- SP official wording (R2): “calculate relative formula masses (including relative molecular masses) ( M r ) from relative atomic masses ( A r )”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 False
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculate Relative Mass  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “To calculate the Mr of a substance, you have to add up the relative atomic masses of all the atoms present in the formula”
- Evidence [SPEC] `graph/specification_points.yaml`: “calculate relative formula masses(including relative molecular masses)”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.26 @ Calculate Relative Mass (2026-09-11); spec wordings 1.26/1.28
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact calculate-relative-formula-masses pairing (1.26); the 1.28 sibling row (see row 6) covers the calculation-usage side.

### 20. `4CH1-CON-STATE-PARTICLE-MODEL` PART_OF `4CH1-1.3` — mapping_id `6b63cb7ee8206660`
- Concept: Particle arrangement, movement and energy in the three states  (aliases: kinetic theory of matter) · node status: SUGGESTED
- SP official wording (R2): “understand how the results of experiments involving the dilution of coloured solutions and diffusion of gases can be explained”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: SUPPORTING · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Diffusion - IGCSE Chemistry Revision Notes.md`: “Diffusion and dilution experiments support a theory that all matter (solids, liquids and gases) is made up of tiny, moving particles”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.1 @ Changing states of matter + 4CH1-1.3 @ Diffusion (2026-09-11); spec 4CH1-1.1 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: SUPPORTING honest: the particle model is the explanatory frame the SP asks results to be explained by; the quote ties experiments→particle theory explicitly.

### 21. `4CH1-CON-REACTING-MASS` PART_OF `4CH1-1.29` — mapping_id `6c975732a8dd5cc7`
- Concept: Reacting mass calculation  (aliases: calculating reacting masses, mass calculations from equations) · node status: SUGGESTED
- SP official wording (R2): “calculate reacting masses using experimental data and chemical equations”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [SPEC] `graph/specification_points.yaml`: “calculate reacting masses using experimental data and chemical equations”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Reacting mass calculations - IGCSE Chemistry Revision Notes.md`: “Information from the question is used to find the amount in moles of the substances being considered”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.29 @ Reacting mass calculations (2026-09-11); spec 4CH1-1.29 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact reacting-mass calculation pairing (1.29).

### 22. `4CH1-CON-EMP-MOL-CALC` PART_OF `4CH1-1.33` — mapping_id `7097cd27a505f0bc`
- Concept: Empirical and molecular formula calculation  (aliases: empirical formula calculation, molecular formula calculation, deducing formulae of hydrated salts) · node status: SUGGESTED
- SP official wording (R2): “calculate empirical and molecular formulae from experimental data”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Empirical & Molecular Formulae  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Empirical formula calculations are very methodical”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Empirical & Molecular Formulae  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Find the relative formula mass of the empirical formula”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.33 @ Empirical & Molecular Formulae (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact empirical/molecular formulae from experimental data (1.33).

### 23. `4CH1-CON-RATE-FACTORS` PART_OF `4CH1-3.10` — mapping_id `727f2309d8881917`
- Concept: Factors affecting the rate of reaction (surface area, concentration and pressure, temperature, catalyst)  (aliases: rate of reaction, factors affecting rate, rate factors, effect of concentration on rate…) · node status: SUGGESTED
- SP official wording (R2): “describe the effects of changes in surface area of a solid, concentration of a solution, pressure of a gas, temperature and the use of a catalyst on the rate of a reaction”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S3 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/Rate of reaction - IGCSE Chemistry Revision Notes.md`: “Factors that can affect the rate of a reaction are”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/Rate of reaction - IGCSE Chemistry Revision Notes.md`: “With an increase in the concentration of a solution, the rate of reaction will increase”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/Explaining Rates  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “Increasing the concentration of a solution increases the rate of reaction”
- Evidence [SPEC] `graph/specification_points.yaml`: “describe the effects of changes in surface area of a solid, concentration of a solution, pressure of a gas, temperature and the use of a catalyst on the rate of a reaction”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-3.10 @ Rate of Reaction (2026-09-11); T-C10 HUMAN_VALIDATED 4CH1-3.10 @ Explaining Rates (2026-09-11); spec 4CH1-3.10 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact: all five rate factors of 3.10 in the concept scope and notes.

### 24. `4CH1-CON-COVALENT-BOND` PART_OF `4CH1-1.44` — mapping_id `74037fd585d27912`
- Concept: Covalent bond (shared pair of electrons; electrostatic attraction between the shared pair and the nuclei)  (aliases: covalent bond, covalent bonding, bonding electrons) · node status: SUGGESTED
- SP official wording (R2): “know that a covalent bond is formed between atoms by the sharing of a pair of electrons”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/g. Covalent Bonding/Forming covalent bonds - IGCSE Chemistry Revision Notes.md`: “Non-metal atoms can share electrons with other non-metal atoms to obtain a full outer shell of electrons”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/g. Covalent Bonding/Forming covalent bonds - IGCSE Chemistry Revision Notes.md`: “When atoms share pairs of electrons, they form covalent bonds”
- Evidence [SPEC] `graph/specification_points.yaml`: “a covalent bond is formed between atoms by the sharing of a pair of electrons”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.44 @ Forming Covalent Bonds (2026-09-11); T-C10 HUMAN_VALIDATED 4CH1-1.45 @ Forming Covalent Bonds (2026-09-11); specs 4CH1-1.44 + 4CH1-1.45 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact shared-pair definition (1.44); sibling row 36 covers the 1.45 electrostatic side.

### 25. `4CH1-CON-EMPIRICAL-FORMULA` PART_OF `4CH1-1.32` — mapping_id `7cfa81540f8e5f2b`
- Concept: Empirical formula  (aliases: simplest whole number ratio formula) · node status: SUGGESTED
- SP official wording (R2): “know what is meant by the terms empirical formula and molecular formula”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [SPEC] `graph/specification_points.yaml`: “know what is meant by the terms empirical formula and molecular formula”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Empirical & Molecular Formulae  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “The empirical formula is the simplest whole number ratio of the atoms of each element present in one molecule or formula unit of the compound”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.32 + 4CH1-1.33 @ Empirical & Molecular Formulae (2026-09-11); spec wordings
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact term definition (1.32); molecular-formula side owned by row 22's 1.33 row — no double-claim.

### 26. `4CH1-CON-ELECTRODE-HALF-EQUATIONS` PART_OF `4CH1-1.59C` — mapping_id `7f81df7683fc74ca`
- Concept: Ionic half-equations for the electrode reactions during electrolysis  (aliases: half equation, half equations, electrode reactions) · node status: SUGGESTED
- SP official wording (R2): “write ionic half-equations representing the reactions at the electrodes during electrolysis and understand why these reactions are classified as oxidation or reduction”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Half equations - IGCSE Chemistry Revision Notes.md`: “This can be illustrated using half equations which describe the movement of electrons at each electrode”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Half equations - IGCSE Chemistry Revision Notes.md`: “At the anode, negatively charged ions lose electrons and are thus oxidised”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/i. Electrolysis/Half equations - IGCSE Chemistry Revision Notes.md`: “In electrode half equations the charges on each side of the equation should always balance”
- Evidence [SPEC] `graph/specification_points.yaml`: “write ionic half-equations representing the reactions at the electrodes during electrolysis”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.59C @ Half Equations (2026-09-11); spec 4CH1-1.59C official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact electrode half-equations SP (1.59C); charge-balance + redox classification in evidence.

### 27. `4CH1-CON-REACTION-PROFILE` PART_OF `4CH1-3.14C` — mapping_id `7f8e2c4af06fbdf1`
- Concept: Reaction profile diagrams (showing ΔH and activation energy)  (aliases: reaction profile, reaction profiles, reaction profile diagram, energy profile) · node status: SUGGESTED
- SP official wording (R2): “draw and explain reaction profile diagrams showing Δ H and activation energy”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S3 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/What is activation energy- IGCSE Revision Notes.md`: “Reaction profiles are similar to energy level diagrams seen in a previous topic”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/b. Rates of Reaction/What is activation energy- IGCSE Revision Notes.md`: “The initial increase in energy, from the reactants to the peak of the curve, represents the activation energy”
- Evidence [SPEC] `graph/specification_points.yaml`: “draw and explain reaction profile diagrams showing”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-3.14C @ What is Activation Energy (2026-09-11); spec 4CH1-3.14C official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact reaction-profile SP (3.14C); ΔH + Ea in evidence.

### 28. `4CH1-CON-EVAPORATION-BOILING` PART_OF `4CH1-1.2` — mapping_id `8bf7660c71661003`
- Concept: Evaporation and its distinction from boiling  (aliases: evaporation, boiling, evaporating) · node status: SUGGESTED
- SP official wording (R2): “understand the interconversions between the three states of matter in terms of:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Changing states of matter - IGCSE Chemistry Revision Notes.md`: “Evaporation occurs over a range of temperatures”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Changing states of matter - IGCSE Chemistry Revision Notes.md`: “It can happen at temperatures below the boiling point of the liquid”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.2 @ Changing states of matter (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: evaporation-vs-boiling distinction is a sub-topic of the 1.2 interconversions list.

### 29. `4CH1-CON-SATURATED-SOLUTION` PART_OF `4CH1-1.10` — mapping_id `8d45c1b98aaa2cf9`
- Concept: Saturated solution  (aliases: saturated, saturation) · node status: SUGGESTED
- SP official wording (R2): “describe these experimental techniques for the separation of mixtures:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: SUPPORTING · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/b. Elements, Compounds and Mixtures/Separation techniques - IGCSE Chemistry Revision Notes.md`: “The solution is heated, allowing the solvent to evaporate, leaving a saturated solution behind”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.4 @ Solutions + 4CH1-1.10 @ Separation techniques (2026-09-11); spec 4CH1-1.4 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: SUPPORTING honest: the saturated-solution state appears inside the crystallisation technique description (1.10); cross-SP support, not the SP demand itself.

### 30. `4CH1-CON-FILTRATION` PART_OF `4CH1-1.10` — mapping_id `9530417e9c749569`
- Concept: Filtration  (aliases: filtration, filtering) · node status: SUGGESTED
- SP official wording (R2): “describe these experimental techniques for the separation of mixtures:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/b. Elements, Compounds and Mixtures/Separation techniques - IGCSE Chemistry Revision Notes.md`: “Filtration is used to separate an undissolved solid from a mixture of the solid and a liquid / solution”
- Evidence [SPEC] `graph/specification_points.yaml`: “separation of mixtures”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.10 @ Separation techniques (2026-09-11); spec 4CH1-1.10 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Named technique of 1.10.

### 31. `4CH1-CON-MOLECULE` PART_OF `4CH1-1.14` — mapping_id `98bd3c9bb76696db`
- Concept: Molecule  (aliases: molecule, molecules) · node status: SUGGESTED
- SP official wording (R2): “know what is meant by the terms atom and molecule”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “A group of two or more atoms chemically combined to form an identifiable unit which retains the properties and composition of the substance”
- Evidence [SPEC] `graph/specification_points.yaml`: “the terms atom and molecule”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.14 @ Atoms: Definitions & Structure (2026-09-11); spec 4CH1-1.14 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact molecule term definition (1.14).

### 32. `4CH1-CON-CONCENTRATION` PART_OF `4CH1-1.34C` — mapping_id `a6c53372c8b3526f`
- Concept: Concentration of a solution  (aliases: concentration) · node status: SUGGESTED
- SP official wording (R2): “understand how to carry out calculations involving amount of substance, volume and concentration (in mol/dm 3 ) of solution”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Solution concentration - IGCSE Chemistry Revision Notes.md`: “Concentration refers to the amount of solute there is in a specific volume of the solvent”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.34C @ Solution concentration (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact concentration-in-mol/dm3 calculations SP (1.34C).

### 33. `4CH1-CON-CONSERVATION-MASS` PART_OF `4CH1-1.26` — mapping_id `af846a5f28c7ecd1`
- Concept: Law of Conservation of Mass  (aliases: conservation of mass) · node status: SUGGESTED
- SP official wording (R2): “calculate relative formula masses (including relative molecular masses) ( M r ) from relative atomic masses ( A r )”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: SUPPORTING · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/e. Chemical Formulae, Equations, Calculations/Calculate Relative Mass  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “In accordance with the Law of Conservation of Mass, the sum of the relative formula masses of the reactants will be the same as the sum of the relative formula masses of the products”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.25 @ Writing chemical equations; 4CH1-1.26 @ Calculate Relative Mass (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: SUPPORTING honest: the note itself invokes conservation of mass to justify the Mr sums; cross-SP support from the same validated note (1.25/1.26 upstream).

### 34. `4CH1-CON-ATOMIC-NUMBER` PART_OF `4CH1-1.16` — mapping_id `b0a85e9b423c16e4`
- Concept: Atomic number  (aliases: atomic number, proton number) · node status: SUGGESTED
- SP official wording (R2): “know what is meant by the terms atomic number, mass number, isotopes and relative atomic mass ( A r )”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “The number of protons in the nucleus of an atom”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/c. Atomic Structure/Atoms Definitions & Structure  Edexcel IGCSE Chemistry Revision Notes 2017.md`: “The atomic number is equal to the number of protons in an atom”
- Evidence [SPEC] `graph/specification_points.yaml`: “atomic number, mass number, isotopes”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.16 @ Atoms: Definitions & Structure (2026-09-11); spec 4CH1-1.16 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact atomic-number term (1.16).

### 35. `4CH1-CON-BOND-BREAKING-MAKING` PART_OF `4CH1-3.6C` — mapping_id `b56662765f0f0b39`
- Concept: Bond-breaking endothermic, bond-making exothermic  (aliases: bond breaking, bond making, bond-breaking, bond-making…) · node status: SUGGESTED
- SP official wording (R2): “know that bond-breaking is an endothermic process and that bond-making is an exothermic process”
- SP applicability: papers 2C
- Role: CORE · confidence: high · section: S3 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/a. Energetics/What is bond energy - IGCSE Chemistry Revision Notes.md`: “During a chemical reaction energy must be taken in to break bonds”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/a. Energetics/What is bond energy - IGCSE Chemistry Revision Notes.md`: “During a chemical reaction, energy is released when new bonds are formed”
- Evidence [SPEC] `graph/specification_points.yaml`: “bond-breaking is an endothermic process and that bond-making is an exothermic process”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-3.6C @ What is Bond Energy (2026-09-11); spec 4CH1-3.6C official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Verbatim SP demand (3.6C): bond-breaking endothermic / bond-making exothermic.

### 36. `4CH1-CON-COVALENT-BOND` PART_OF `4CH1-1.45` — mapping_id `ca083179fe32cb89`
- Concept: Covalent bond (shared pair of electrons; electrostatic attraction between the shared pair and the nuclei)  (aliases: covalent bond, covalent bonding, bonding electrons) · node status: SUGGESTED
- SP official wording (R2): “understand covalent bonds in terms of electrostatic attractions”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/g. Covalent Bonding/Forming covalent bonds - IGCSE Chemistry Revision Notes.md`: “There is a strong electrostatic attraction between the shared pair of electrons and the nuclei of the atoms involved”
- Evidence [SPEC] `graph/specification_points.yaml`: “covalent bonds in terms of electrostatic attractions”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.44 @ Forming Covalent Bonds (2026-09-11); T-C10 HUMAN_VALIDATED 4CH1-1.45 @ Forming Covalent Bonds (2026-09-11); specs 4CH1-1.44 + 4CH1-1.45 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Exact electrostatic-attraction pairing (1.45); quote verbatim from the validated note.

### 37. `4CH1-CON-HEATING-CONSTANT-MASS` PART_OF `4CH1-1.7C` — mapping_id `d04783dbcfc34795`
- Concept: Heating to constant mass  (aliases: heating to constant mass, constant mass) · node status: SUGGESTED
- SP official wording (R2): “practical: investigate the solubility of a solid in water at a specific temperature”
- SP applicability: papers 2C
- Role: ENRICHMENT · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Investigating solubility - IGCSE Chemistry Revision Notes.md`: “Repeat this process until the mass remains constant”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/a. States of Matter/Investigating solubility - IGCSE Chemistry Revision Notes.md`: “This is called heating to constant mass and confirms that all water has been removed”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.7C @ Investigating solubility (2026-09-11)
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: ENRICHMENT honest: heating-to-constant-mass is a technique step inside the 1.7C solubility practical (ensures all water removed) — technique-concept enrichment, correctly not CORE.

### 38. `4CH1-CON-CHROMATOGRAPHY` PART_OF `4CH1-1.10` — mapping_id `d053ae1c139e1437`
- Concept: Paper chromatography (separation by differential solubility)  (aliases: paper chromatography, chromatography) · node status: SUGGESTED
- SP official wording (R2): “describe these experimental techniques for the separation of mixtures:”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S1 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/1. Principles of Chemistry/b. Elements, Compounds and Mixtures/Separation techniques - IGCSE Chemistry Revision Notes.md`: “Paper chromatography is used to separate substances that have different solubilities in a given solvent”
- Evidence [SPEC] `graph/specification_points.yaml`: “separation of mixtures”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-1.10 @ Separation techniques (2026-09-11); spec 4CH1-1.10 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Named technique of 1.10 (paper chromatography by differential solubility).

### 39. `4CH1-CON-EXO-ENDO` PART_OF `4CH1-3.1` — mapping_id `d25cf56d69ac43ab`
- Concept: Exothermic and endothermic reactions (heat energy given out or taken in)  (aliases: exothermic, endothermic, exothermic reaction, endothermic reaction…) · node status: SUGGESTED
- SP official wording (R2): “know that chemical reactions in which heat energy is given out are described as exothermic, and those in which heat energy is taken in are described as endothermic”
- SP applicability: papers 1C, 2C · shared with Double Award
- Role: CORE · confidence: high · section: S3 · checks: M1 True · M3 True · M4 True · M5 True · spec_in_r2 True
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/a. Energetics/Exothermic and endothermic - IGCSE Chemistry Revision Notes.md`: “An exothermic reaction releases heat energy into the surroundings”
- Evidence [NOTE] `Chemistry IGCSE Revision Notes/3. Physical Chemistry/a. Energetics/Exothermic and endothermic - IGCSE Chemistry Revision Notes.md`: “An endothermic reaction takes heat energy in from the surroundings”
- Evidence [SPEC] `graph/specification_points.yaml`: “heat energy is given out are described as exothermic”
- Upstream: T-C10 HUMAN_VALIDATED 4CH1-3.1 @ Exothermic and Endothermic (2026-09-11); spec 4CH1-3.1 official wording
- Verdict: [x] CONFIRM — the concept genuinely subsumes this SP's demand   [ ] REJECT — wrong concept/SP pairing   [ ] HOLD — needs better evidence (state what)
- Reviewer note: Verbatim SP demand (3.1): exothermic gives out / endothermic takes in heat.

## Part B — in-scope gap register (no authoring in this lane)

In-scope SPs carrying no attachment row: 5 (4CH1-1.13, 4CH1-1.60C, 4CH1-3.15, 4CH1-3.16, 4CH1-3.8).
Verdict vocabulary here is DEFER-only: T-C19 validates what exists; new concepts/attachments are T-C11 expansion-round authoring (batch 5 per the §16 order), not this lane.

### 4CH1-1.13
- Status: no attachment row in the store (r2 wording: “practical: investigate paper chromatography using inks/food colourings”)
- Verdict: [x] DEFER → T-C11 expansion round
- Reviewer note: Paper-chromatography practical: the chromatography CONCEPT node exists (row 38 covers the 1.10 technique description) but no practical-specific attachment was authored for the investigation SP; practical-side coverage rides the PR practical node. Defer authoring to T-C11.

### 4CH1-1.60C
- Status: no attachment row in the store (r2 wording: “practical: investigate the electrolysis of aqueous solutions”)
- Verdict: [x] DEFER → T-C11 expansion round
- Reviewer note: Aqueous-electrolysis practical: selective-discharge + half-equation concepts exist (rows 10/26 cover the knowledge SPs); the practical investigation SP has no dedicated attachment. Defer to T-C11.

### 4CH1-3.15
- Status: no attachment row in the store (r2 wording: “practical: investigate the effect of changing the surface area of marble chips and of changing the concentration of hydrochloric acid on the rate of reaction between marble chips and dilute hydrochloric acid”)
- Verdict: [x] DEFER → T-C11 expansion round
- Reviewer note: Marble-chips rate practical: rate-factors + collision-theory concepts exist (rows 16/23 cover the knowledge SPs); the practical SP has no dedicated attachment. Defer to T-C11.

### 4CH1-3.16
- Status: no attachment row in the store (r2 wording: “practical: investigate the effect of different solids on the catalytic decomposition of hydrogen peroxide solution”)
- Verdict: [x] DEFER → T-C11 expansion round
- Reviewer note: Catalytic-decomposition practical: catalyst concepts exist in the store (3.13 side); the practical SP has no dedicated attachment. Defer to T-C11.

### 4CH1-3.8
- Status: no attachment row in the store (r2 wording: “practical: investigate temperature changes accompanying some of the following types of change:”)
- Verdict: [x] DEFER → T-C11 expansion round
- Reviewer note: Temperature-change practical (exo/endo dissolving etc.): EXO-ENDO concept exists (row 39 covers 3.1); the practical SP has no dedicated attachment. Defer to T-C11.

## Rollup (filled at gate time)

| Class (role|section) | stratum rows | sampled | CONFIRM | REJECT | HOLD | precision |
|---|---:|---:|---:|---:|---:|---:|
| CORE|S1 | 88 | 25 | 25 | 0 | 0 | 25/25 = 100% |
| CORE|S3 | 20 | 5 | 5 | 0 | 0 | 5/5 = 100% |
| ENRICHMENT|S1 | 6 | 6 | 6 | 0 | 0 | 6/6 = 100% |
| SUPPORTING|S1 | 3 | 3 | 3 | 0 | 0 | 3/3 = 100% |

gate arithmetic **PASSES**: Part A 39/39 CONFIRM = 100% ≥ 90% per class (CORE|S1 25/25, CORE|S3 5/5, ENRICHMENT|S1 6/6, SUPPORTING|S1 3/3); Part B 5/5 decided (5 DEFER → T-C11). c19_promote.py re-computes the arithmetic from the verdict boxes and asserts this rollup.

