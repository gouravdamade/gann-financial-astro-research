# PFR-V2B-6 FX Side Pilot Readiness

Date completed: 2026-08-02

## Purpose

V2B-6 adds a read-only status check for the first small, founder-reviewed FX
side pilot. It does not create, approve, or modify research evidence.

The checker reads the existing immutable evidence-packet registry and matching
polarity catalogue. For each primary side (`FX_CURRENCY:USD` and
`FX_CURRENCY:JPY`) it reports:

- reviewed packet count;
- matching catalogue-entry count;
- categorical states currently present;
- required states still missing (`SUPPORTIVE` and `ADVERSE`);
- explicit blockers; and
- the retained unknown-gap policy for unreviewed events.

## Current Product Result

Both production side registries are empty. The app therefore displays
`PILOT_EVIDENCE_PENDING` for USD and JPY and explains that both required
categorical examples are still missing. This is intentional and correct.

The check only reports `PILOT_EVIDENCE_PRESENT_RESEARCH_ONLY` when at least
one side has immutable reviewed records for both `SUPPORTIVE` and `ADVERSE`.
That status is not a pair direction, profitability claim, execution approval,
or automatic admission action.

## Desktop Surface

Open `Fields` in the Chakra workspace. The new **FX side pilot status** section
loads through the private desktop bridge alongside the three independent
fields. It shows the current status and lets the founder refresh it after a
separate evidence review has updated the immutable registry.

## Boundaries Retained

- No write route or client approval field exists.
- Client-side approval attempts are rejected.
- No pair direction, magnitude, fusion, SBC confirmation, ML, Auto Suggest,
  live inference, MT5 execution, or trade behavior is added.
- Unknown gaps remain visible for every side event without an admitted record.

## Verification

- Pilot service tests: production evidence pending; both required categorical
  states required before a side is eligible; unknown request fields rejected.
- Backend regression suite: `36 passed`.
- Desktop API/workspace tests: `14 passed`.
- Production TypeScript/Vite build and Rust `cargo check`: passed.

## Next Step

The product is ready for a real founder-reviewed side-chart pilot. To move
forward, supply a specific USD or JPY chart identity, chart hypothesis, natal
target, source references, profile hash, reviewer/timestamp, and two reviewed
categorical examples. Add their packet and exactly matching catalogue records
in one reviewed change; then refresh this panel and preserve unknown gaps.
