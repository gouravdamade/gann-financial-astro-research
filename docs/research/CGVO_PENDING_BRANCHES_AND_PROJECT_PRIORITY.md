# CGVO Pending Branches and Project Priority

Last central review: 2026-08-23 IST

Reference baseline: `023f6e67ddd8dd9679649dc8c7f8fb15adf58e9e`

Accepted state at baseline: `CGVO-G3-S1-R1 = CENTRAL ACCEPTED — SOURCE CORRECTION COMPLETE`.

## Governing project priority

The primary product goal is a **working, inspectable Multi Oscillator / wave visualizer**.

CGVO and other signal/source-research streams are secondary unless they directly unblock, validate, or improve the Multi Oscillator. Do not let optional CGVO research delay the working oscillator product.

## CGVO-G3 status

`CGVO-G3` is **FROZEN** after `CGVO-G3-S1-R1`.

Do **not** open `CGVO-G3-R2` unless a future, explicit Multi Oscillator requirement or new source evidence creates a necessary bounded question.

Current frozen G3 conclusions:

- V.11 local differential solar visibility: `SOURCE_CLOSED_SOLAR_LOCAL_DIFFERENTIAL_VISIBILITY`
- V.42 root Kūrma reference: `SOURCE_CLOSED_ROOT_KURMA_REFERENCE`
- Chapter XIV directional/nakshatra geography: `SOURCE_CLOSED_CONTEXTUAL_MAPPING`
- Site -> historical region: `SOURCE_SILENT_SITE_TO_REGION_OPERATOR`
- Site visibility -> region visibility: `NOT_AUTHORIZED`
- `regionVisibility = null`
- `sourceEffectActivation = null`
- Market, Fields, SBC, Auto Suggest, ML, MT5, scoring, polarity, and execution remain disconnected/locked.

## Remaining core CGVO completion branches

There are **three planned core closure branches** before the core CGVO source architecture should be considered complete.

### 1. CGVO-S1B-PHASE-R1 — Historical eclipse phase mapping

**Status:** mandatory core closure; currently unresolved.

Current blocker:

`UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED`

Goal:

Source-close, or formally fail-close, the mapping between the historical source's eclipse commencement/conclusion/phase language and modern event phases exposed by the astronomy engine.

Examples of modern phases that must not be mapped by assumption:

- solar: `C1 / C2 / MAX / C3 / C4`
- lunar: `P1 / U1 / U2 / MAX / U3 / U4 / P4`

Until this is source-closed:

- `sourceEffectActivation` remains `null`
- no phase multiplier, effect boolean, mitigation coefficient, weight, polarity, oscillator input, or market use may be created from the unresolved historical phase language.

Recommended model: **Terra High** for source/architecture research; **Luna Max** only for a later bounded implementation once the mapping is centrally approved.

### 2. CGVO-CALENDAR-R1 — Historical lunar-month/intercalation closure

**Status:** mandatory core closure for reliable month-based historical rules.

Current accepted basis:

- `VARAHAMIHIRA_LUNAR_MONTH_BASE = PURNIMANTA`
- confidence: `HIGH_CONFIDENCE_SOURCE_INTERNAL_INFERENCE`

Remaining gap:

The complete historical treatment of `adhika` / `kshaya` months and edge cases is not source-closed.

Goal:

Define a source-faithful historical lunar-month/intercalation contract or explicitly preserve unresolved edge cases as `UNKNOWN`.

Do not replace source uncertainty with a convenient modern calendar heuristic.

Recommended model: **Terra High**.

### 3. CGVO-FRAME-R1 — Absolute stellar/rasi frame closure

**Status:** mandatory core closure for a source-certified absolute frame.

Current state:

- the active Chitra/Spica reconstruction remains non-default/experimental
- the acquired *Panchasiddhantika* records Chitra polar longitude at `180°50′`, not an exact source proof of modern ecliptic Chitra = `180°`
- Magha/Chitra historical table data are acquired, but the transformation into a modern ecliptic frame remains unresolved
- no averaging or invented modern-star transformation is authorized.

Goal:

Either:

1. source-close a defensible historical -> modern astronomical frame transformation, or
2. formally classify the existing reconstruction as experimental/non-Mode-1 and define the source-certified CGVO behavior when no absolute transform can be closed.

Recommended model: **Terra High**.

## Dormant / nonblocking CGVO question

### CGVO-FIRMAMENT — V.28-31 section classifier

Current state:

`COMMENTARY_CONFLICT_NOT_SOURCE_CLOSED`

The held commentary evidence conflicts on a six-versus-seven visible-sky division. Raw modern diurnal geometry does not itself establish the historical classifier.

This is **not currently a mandatory fourth core branch**.

Default disposition:

- keep the historical firmament section `UNKNOWN`
- retain raw modern geometry only as modern geometry
- do not invent six/seven section boundaries
- reopen only if a concrete, source-required CGVO or Multi Oscillator feature actually depends on this classifier.

## Completion definition

Core CGVO may be called complete after the three mandatory branches above are centrally resolved, provided the following remain true:

- unknown source states remain `UNKNOWN`, not synthetic zero/neutral
- source facts are kept separate from experimental transforms and market hypotheses
- no geometry-only relation is treated as bullish/bearish
- cross-source composition occurs only when explicitly source-authorized
- unresolved source operators remain null/fail-closed
- no market or execution path is activated by CGVO completion itself.

## Execution order / priority rule

Do **not** execute the three CGVO branches consecutively merely to finish CGVO.

Preferred project order:

1. Audit and finish the **Multi Oscillator / wave visualizer** first.
2. Use the oscillator completion ledger to identify which CGVO gap, if any, actually blocks a usable/source-certified oscillator input.
3. Close CGVO gaps one at a time in dependency order.
4. Keep dormant/optional CGVO research frozen unless a product requirement justifies reopening it.

## Future-session instruction

When recovering this project in a future ChatGPT/Codex session, treat this file as the concise CGVO pending-work ledger. Re-check the live repository before implementation because later accepted commits may supersede this baseline.
