# PFR-V2B-1 FX Side Contract

Date: 2026-08-02

## Result

V2B-1 is complete as a research-only identity correction. The immutable
chart-conditioned polarity path now accepts only these primary chart
identities:

- `FX_CURRENCY:USD`
- `FX_CURRENCY:JPY`

`FX_PAIR:USDJPY` is now explicit `PAIR_DERIVATION_ONLY`. It cannot resolve a
primary catalogue entry, even if an event has been selected. The pair view can
only be constructed later from separately reviewed side-chart contexts.

## Minimum Evidence Shape

Every future reviewed packet and matching catalogue entry must carry:

- `sideIdentity` (`USD` or `JPY`), matching `instrumentId`
- `chartId`
- `chartHypothesisId`
- transit, side-chart natal target, aspect type, categorical reviewed state,
  reviewed evidence, and immutable packet hash

The selected USDJPY pair event is preserved only as `reviewScope` in a
downloaded candidate worksheet. Its natal target is intentionally left blank
in both side candidates. Candidate defaults are
`PENDING_REVIEW` and `PENDING_FOUNDER_REVIEW`; they remain
`CANDIDATE_NOT_ADMISSIBLE`.

## Desktop Surface

The chart-conditioned aspect panel now displays independent USD and JPY
lookup states and creates separate **USD candidate** and **JPY candidate**
worksheets. It does not display a derived pair direction, magnitude, signal,
or execution action.

## Verification

- Polarity catalogue tests: `7 passed`
- Backend lookup tests: `4 passed`
- Focused desktop tests: `21 passed`
- Frontend API test: `8 passed`
- Lint and production frontend build: passed

## Preserved Boundaries

No range oscillator, magnitude, fusion with SBC, source admission, financial
validation, ML, Auto Suggest, live inference, MT5 execution, or installer was
added in this milestone.
