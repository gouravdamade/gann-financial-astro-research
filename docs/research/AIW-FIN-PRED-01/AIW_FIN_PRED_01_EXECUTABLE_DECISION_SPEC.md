# Deterministic research decision procedure

**Two outputs can be independently reproduced.** Given the printed Chart 44, return the natal relationships, the author's financial attribution and the exact interval relative to his birth balance. Given a personal chart, an active ruler and complete, edition-specific testimony for BPHS XLII.13, return the passage's conditional financial judgment. These are distinct rule IDs. A query for a *new* native matching Chart 44's Ketu placement cannot inherit Raman's case conclusion or amount.

### 1. Identify subject and question

Require subject ID, chart ID, chart type (natal, divisional or annual), question, witness and rule. For XLII.13 require a human native and personal financial harm. Return NOT_APPLICABLE on domain mismatch. Unknown identity produces UNKNOWN. Record even an early exit.

### 2. Evaluate natal conditions

Use the indicated chart and reference. Compute house as 1 + floorMod(bodySign − referenceSign,12). Classical domicile owners in Aries–Pisces order are Mars, Venus, Mercury, Moon, Sun, Mercury, Venus, Mars, Jupiter, Saturn, Saturn, Jupiter. Retain separate predicate records for each house, owner and relation. Evaluate three-valued AND and OR. For AND any known false decides false, otherwise a missing operand decides unknown. For OR any known true decides true, otherwise a missing operand decides unknown. For presence tests on a set, all-false requires complete coverage. Keep all eight contributors on any upstream Aṣṭakavarga record in its own convention.

### 3. Evaluate specified qualifications

Fix the direction of each aspect, chart, geometry and universe of eligible aspectors. For full graha aspects compute d = 1 + floorMod(targetSign − sourceSign,12) and compare to the permitted places for the **source**. Keep the individual checks, even when the resulting existence predicate is false. Apply a dignity, D9 or strength qualification only to a clause that names it. A missing quantitative cutoff in a qualitative source yields a qualitative or unresolved qualification.

### 4. Reconstruct the period

Select the star-based system for the Raman case. Read the versioned balance (printed, longitude replay, or passage-time replay). First subtract elapsed time within the opening major period. For full subsequent majors accumulate allotments in source order. Within a major start with that ruler and accumulate child durations from the **full parent start**. Use left-closed, right-open membership. For the printed case measure in 360 integer parts per conventional period-year. Preserve fractions if a child subdivision needs them. Civil projection requires its own convention and origin. No source-specific pratyantardaśā judgment is available for R44.

**Raman's independent topic selector.** Let W be the union of the six participant sets on pp. 91–92 of *How to Judge a Horoscope*, as enumerated in the worked report. Evaluate parent ∈ W and child ∈ W. Both true → emphasized second-house results. Child only → limited. Parent only → feeble. Both false → no selection by these channels. Missing coverage → preserve the possible categories. Each planet counts once for eligibility regardless of how many channels it satisfies. The strength labels describe relevance to second-house affairs, with no sign or amount attached. Chart 38 supplies the author's own lookup control. Chart 44 proves Venus membership through conjunction even if other channels have incomplete coverage.

### 5. Evaluate dynamic premises

R44 and P42.13 require no live transit stream. Where a different rule names a transit and obstruction, require the source's origin and complete coverage during the queried interval. Split only at an actual state boundary. Keep natal and annual IDs on the two-chart Hāyanaratna rule. Store lack of a required observation as unknown.

### 6. Interpret

~~~text
assess_XLII_13(subject, P, gate, chart, profile):
    if subject outside personal-finance scope: return NOT_APPLICABLE
    if domain or P unknown: return UNKNOWN
    assoc = exists(distinct lord of 6,8,12 joined to P)
    guard = exists(eligible trinal lord aspecting P)
    condition = AND(gate.inOwnPeriod(P), assoc, NOT(guard))
    if condition is true:  return CONDITION_PRESENT, UNFAVORABLE
    if condition is false: return CONDITION_ABSENT, NO_JUDGMENT
    return UNKNOWN, UNKNOWN

replay_R44(case, queryAge):
    use printed facts and separately identified birth balance
    emit natal evidence and its author's assessments
    selected = interval(Ketu, Venus, balance)
    attach the author's debt attribution to selected
    if queryAge is supplied: report membership in selected
    a different case ID has no R44 attribution
~~~

The existential tests retain their input sets and completeness flags. Unknown coverage can coexist with an already proved aspect or conjunction. For a known false period gate there is no active judgment even when some natal premises are missing. For a civil time outside the supported clock return timing unknown. A source-attributed observation is never a computed consequence for a new subject.

### 7. Resolve interactions

Match subject, question, chart, period system, matter, graha and source operator. Group semantic aliases by canonical proof identity, while retaining their citations. Equal opposing effects for a single planet may cancel under J8.23. Numerical predominance uses the Aiyar profile only. Preserve different planets' separate periods. Mark an unresolved conflict only when the known statements actually conflict on the same target. An annual mixed judgment has its own rule ID. A source's local obstruction operates on its named target. For an explicitly authorized dynamic rule, intersect supported intervals before judging simultaneous truth.

### 8. Emit a record

The JSON contains the field contract and populated records. Carry source ID/locator, subject, horoscope, question, graha and house identities, evidence IDs, parent/child lineage, balance profile, original calendar, optional UTC endpoints or event, predicate and interpretation, exceptions, conflicts, missing evidence, provenance and reconstruction confidence. Unknown is different from absent. Use null for unavailable times and give the reason. Maintain executionAllowed, financiallyValidated and marketDirectionAssigned as false. Inspectors can trace a judgment to its source and individual inputs. Grouping records at another display timeframe preserves their original intervals.

**Acceptance boundary.** The consumer can replay all expected predicates and period ages in the [fixtures](AIW_FIN_PRED_01_TEST_FIXTURES.json) independently of software platform. A complete financial predictor would additionally need a source-backed rule to select this child period, resolve the birth balance and qualify competing promises. None is inferred from the reported loss.
