# Evidence Accumulation Pilot — Round 001 (2026-09-17, Session 77)

**Commission:** the operator's Track-2 directive — proceed with the actual
pilot while preserving the frozen r3/t0 baseline; produce NEW learner
evidence, not a re-run of the synthetic/r3 monitor transition.

**Status: EXECUTED (learner-side round complete in production; the teacher
marking round is handed to the operator).** All inputs are honestly labeled
controlled inputs from a documented simulated-learner profile (mid-ability:
solid particulate basics, competent single-step mole arithmetic, a
multi-step ratio slip, two deliberately expressed misconceptions, naive on
molecular shape). No organic student is claimed; the teacher's marking
judgment remains the operator's alone.

## 0. Reconciliation with the concurrent lanes (recorded post-authoring)

This round was planned against the session-76 state (r3/t0 PREPARED, CI
BLOCKED, pilot 4/5 gates). While it was being prepared and executed, the
concurrent lanes landed (sessions 90–95): **r3 EXECUTED — VERDICT PASS**
(monitor 3→6 attempts / 2→4 correct / v3→v6; Smart Lesson ADVANCE_TOPIC at
decay-adjusted 0.77; the fix chain app-level PRODUCTION VERIFIED), **the
Phase-4 t0 CAPTURED** (integrity CLEAN, before and after r3), **Actions
restored** (the r3 vehicle's workflow runs + core-ci PR runs all green),
and the **Phase-5 pilot-readiness review DECIDED: PILOT READY,
PASS-WITH-NOTES** (session 92). Consequences for this record:

- the "frozen r3/t0 baseline" this round preserved is now the **captured
  t0 artifact** (session 90's S3 capture); this round's evidence
  (14:02–14:03 UTC) is POST-t0 — exactly the pilot position the t0
  procedure defines (t0 → pilot evidence → t1), so t1 will attribute this
  round's cells as pilot delta; every row is attributable by account
  (pilot.learner01) regardless.
- the freeze verification below remains valid as executed: none of this
  round's 12 attempted questions maps to any frozen topic's servable
  list, and the monitor account was never used (r3's post-round state is
  the concurrent lane's, untouched by this round).
- this round is therefore **pilot round 001 post-readiness** — the first
  learner-side evidence accumulation of the pilot proper.

## What ran (production, real product surfaces)

1. **Provisioning** — `pilot.learner01@syllabai-test.dev` via the public
   register API (STUDENT, TEST convention; the session-58 monitor pattern).
   Credentials delivered to the operator (0600 file,
   `download/s77-pilot/PILOT_LEARNER01_CREDENTIALS.txt`).
2. **Discovery (read-only)** — 5 candidate zero-evidence topics verified
   live INSUFFICIENT_COVERAGE; servable landscape: 4CH1 = 34 STRUCTURED,
   CHM seed = 8 MCQ_SINGLE (the only auto-evidence path).
3. **MCQ practice round** — 8 auto-graded attempts (4 correct / 4 incorrect)
   → **immediate BKT evidence on 6 fresh topic cells** (5 primary + 1 via a
   secondary mapping).
4. **Structured round** — 4 past-paper questions × 26 part answers → PENDING
   in the teacher marking queue on fresh cells (4CH1-S1-c ×2, 4CH1-S2-e ×1,
   4CH1-S1-f ×1 — note: selected from the S1-e/S1-c practice lists, whose
   secondary mappings place their primary cells elsewhere; all zero-evidence
   cells, none frozen). **The operator's per-point marking of these answers
   is the first legitimate mixed-award κ sample** (r1 was all-zero
   placeholders; r2/r3 are answer-key inputs).
5. **Tutor leg** — the Smart Lesson's own ASK_TUTOR recommendation followed:
   one grounded answer (4 evidence items, model openai/gpt-oss-120b via
   groq, 17.0 s) correctly remediating the active ionic-lattice
   misconception, cited to 4CH1-1.42/1.43. **First live tutor remediation
   of an active misconception.** (All 4 citations are KG-side spec topics;
   zero document-side evidence — the Track-3 corpus finding, live.)

## What the loop did (the round's measurements)

Five Smart Lesson transitions, all INSUFFICIENT_COVERAGE at the start:

| Cell | Before → After | Action |
|---|---|---|
| WCH11-T1.1 mole calculations | → PREREQUISITE_WEAK | REMEDIATE_PREREQUISITE (T2.1 measured 0.16 over 2 attempts) |
| WCH11-T1.2 empirical formulae | → TOPIC_MASTERED | ADVANCE_TOPIC (decay-adjusted 0.36 — 1/1 correct) |
| WCH11-T2.1 isotopes | → PREREQUISITE_WEAK | REMEDIATE_PREREQUISITE (T2.2 at 0.11 via secondary-mapped evidence) |
| WCH11-T3.1 ionic lattice | → MISCONCEPTION_SUSPECTED | ASK_TUTOR — **first misconception evidence in production** ("Ionic compounds form discrete molecule pairs", p=0.75) |
| WCH11-T3.2 covalent | → MISCONCEPTION_SUSPECTED | ASK_TUTOR ("The octet rule is an absolute law", p=0.75) |

The misconception leg closed end-to-end: distractor choice → expressed
misconception evidence → misconception state → ASK_TUTOR → grounded cited
tutor answer. At t0 this path had ZERO data.

## Freeze verification (the directive's constraint — held)

- The **monitor account was never used** (no credentials touched; all writes
  came from pilot.learner01's own token).
- **4CH1-S2-f and the 8 r1-measured topics were never attempted** — verified
  live post-round: zero overlap between the round's 12 attempted questions
  and any frozen topic's servable list; 4CH1-S2-f's list is still exactly
  the r2 trio (96ae4235 / ac5045d7 / ddf30066).
- r3's preconditions (monitor state version 3, no PENDING on the monitor
  account, 3 servable questions on S2-f) are structurally intact; the r3
  spec and t0 procedure remain PREPARED/FROZEN exactly as committed
  (tracker d6b7001).
- The frozen baseline remains `EVIDENCE-ACCUMULATION-BASELINE-2026-09-15.md`;
  this round's evidence is attributable by account, so any later global t0
  capture separates pilot rows exactly.

## Handed to the operator

- `TEACHER_MARKING_RUNBOOK.md` (in `download/s77-pilot/`) — the 4 PENDING
  attempts, all 26 part answers, the marking order (Smart Mark assist
  first), and the closed-loop verification steps.
- The DB-level t0/t1 instrument remains committed (web d0fc4d9) — runnable
  by the operator via the Neon path at any time; recommended AFTER r3
  closes per the procedure, with pilot rows separable by account either way.

## Honest status

EXECUTED: provisioning, discovery, MCQ round (evidence fired), structured
submissions (PENDING), tutor leg, before/after/final captures, freeze
verification. NOT EXECUTED (operator/CI): the teacher marking round (κ +
the structured cells' evidence), the DB-level t0/t1 capture, r3 itself
(frozen; Actions quota sentinel window opens 2026-09-27). NOT CLAIMED: κ
evaluated, pilot t1 measured, CI verified.

Raw artifacts: `download/s77-pilot/` (phase A/B/C JSON, freeze
verification, subject landscape, credentials) — machine record
`PILOT_ROUND_001_RECORD.json`.
