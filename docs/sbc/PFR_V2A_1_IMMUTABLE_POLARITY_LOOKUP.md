# PFR-V2A-1 Immutable Polarity Lookup

Date: 2026-08-02

Scope: one read-only lookup and status surface. This closes the V2A-1
entry gate identified by `PFR_V2_0_INVENTORY.md`; it does not implement an
oscillator, financial model, calibration, source admission, execution path,
or automatic inference.

## Delivered Contract

- Catalogue: `CHART_CONDITIONED_POLARITY_CATALOGUE_V1`.
- Seed manifest:
  `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_catalogue_v1.json`.
- The seed catalogue is deliberately empty and declares
  `NO_ACCEPTED_PRODUCTION_ENTRIES`.
- Backend lookup:
  `POST /api/chart-conditioned-polarity/lookup`.
- Desktop workspace status: **Chart-conditioned aspect pressure**.

The lookup accepts an instrument identity and optionally the complete event
identity: chart id, transit body, natal target, and aspect type. Partial event
identity returns `TARGET_CONTEXT_INCOMPLETE`; missing or unmatched accepted
entries return `POLARITY_CATALOGUE_MISSING`.

## Non-negotiable Boundary

For current USDJPY use, the product returns
`POLARITY_CATALOGUE_MISSING`. It does not derive a sign from:

- the aspect geometry;
- a planet's natural benefic/malefic label;
- a transit functional-role label;
- SBC guidance, agreement, or disagreement.

SBC remains a separate synchronized comparison field. Neither field confirms
the other, and neither can change Auto Suggest, live inference, ML notes,
shadow validation, or MT5 execution.

## Future Ready-State Rendering

Only a specific immutable entry carrying a reviewed evidence packet can return
`READY`. It contains one categorical polarity only: `SUPPORTIVE`, `ADVERSE`,
`NEUTRAL`, or `MIXED`. The panel always labels it:

`CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED`

There is intentionally no smooth amplitude, confidence, strength score,
calibration, or order instruction. `MIXED` must remain split activity in the
eventual stepped visual, never a quiet zero.

## Verification

- `research_labs/chart_conditioned_aspects/tests/test_polarity_catalogue.py`:
  `4 passed`.
- `gann-astro-desk/backend/test_chart_conditioned_polarity_service.py`:
  `3 passed`.
- Focused desktop API/workspace tests: `25 passed`.
- Desktop lint and production TypeScript/Vite build: passed.

## Next Bound

Do not add entries merely to make a chart colorful. The next permitted work is
to admit a concrete, separately reviewed chart/profile evidence packet, then
add exactly the matching immutable entry and test it. A visible range oscillator
remains a later product milestone, not an implication of this lookup.
