# PFR-V2B-2 Categorical Visible-Range Compiler

Date: 2026-08-02

## Result

V2B-2 adds the research-only backend compiler
`CHART_CONDITIONED_CATEGORICAL_RANGE_V1` and its private API route:

`POST /api/chart-conditioned-polarity/range`

It receives a single primary side-chart identity, an accepted chart context,
a bounded UTC range, and timestamped aspect events. It produces contiguous
atomic intervals across the whole requested range.

## Interval Rules

- No active side-chart event: `UNKNOWN` gap.
- Any active event without a matching accepted immutable catalogue entry:
  `UNKNOWN` gap, even if another active event is known.
- Only supportive entries: `SUPPORTIVE`.
- Only adverse entries: `ADVERSE`.
- Supportive and adverse entries together: `MIXED`, with independent
  `supportiveActive=true` and `adverseActive=true` fields.
- Only neutral entries: `NEUTRAL`.

There is no numerical amplitude, smoothing, aggregation to a USDJPY pair,
SBC confirmation, trading instruction, ML input, Auto Suggest input, live
inference use, or execution behavior.

## Context Correction

`chartHypothesisId` is now part of the event-level lookup context as well as
the stored packet and catalogue record. A lookup must supply chart id,
hypothesis id, transit, natal target, and aspect together; partial context
fails closed.

## Verification

- Catalogue and range compiler tests: `9 passed`
- Backend lookup/range tests: `5 passed`
- Focused desktop/API tests: `29 passed` when run individually
- Lint and production frontend build: passed

The combined browser-suite command had one worker-start timeout under local
resource pressure. Each same focused suite subsequently passed individually;
the compiler and backend validation are independent of that runner startup
condition.

## Next Boundary

V2B-3 may expose the existing SBC atomic intervals through an equally bounded
read-only range contract. It must remain a separate synchronized comparison
field; no fusion or calibration is permitted.
