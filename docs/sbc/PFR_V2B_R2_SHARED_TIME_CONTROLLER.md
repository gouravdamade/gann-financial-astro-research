# PFR-V2B-R2 Shared Time Controller

Date completed: 2026-08-02

## Purpose

Give the price chart, the Chakra workspace, and the independent USD, JPY, and
SBC fields one explicit research timestamp and canonical interval selection.
This is review navigation only. It creates no evidence, magnitude, pair
polarity, confirmation, recommendation, or execution path.

## Delivered

### ResearchTimeControllerV1

`ResearchTimeControllerV1` records the current price viewport plus:

- a non-persistent chart crosshair timestamp;
- a selected timestamp and selected candle timestamp;
- the selected canonical USD, JPY, or SBC interval id;
- a null pair interval id because pair derivation is not part of R2;
- update source and a monotonically increasing in-memory sequence number.

Price crosshair movement updates only the shared cursor. A price-chart click
selects the nearest real candle. Chakra moment selection and interval selection
select exact UTC timestamps. The state never estimates a timestamp from a
decimated SVG point.

### Canonical field intervals

- Every USD and JPY field interval, including `UNKNOWN` gaps, is keyboard and
  pointer selectable.
- Every SBC availability interval is selectable in its own independent lane.
- Selecting an interval uses its stored `startUtc` and retains its stored
  `endUtc` and id. It does not stretch, resample, join, or reinterpret the
  interval.
- The selected interval is visibly outlined. A shared cursor line is shown in
  each categorical panel when a chart crosshair timestamp is available.

### Chakra synchronization

The selected UTC timestamp is converted to the Chakra form's IST moment and
loads the normal snapshot through the existing request path. Selection from the
Chakra controls returns the canonical UTC moment to the main controller.
The existing visible-range sequence guard remains responsible for stale range
responses.

## Guardrails

- `CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED` remains visible.
- `UNKNOWN` remains an explicit gap and is selectable only for inspection.
- SBC is an availability field, independent of aspect pressure, and is not
  confirmation.
- No `FX_PAIR_CATEGORICAL_RANGE_V1`, pair direction, source admission,
  smoothing, fusion, calibration, ML, Auto Suggest, live inference, MT5
  execution, or order capability was added.

## Verification

| Gate | Result |
| --- | --- |
| Oxlint | Passed |
| Focused Chakra and field interaction tests | 2 files / 24 tests passed |
| TypeScript/Vite production build | Passed |

## Next Bounded Milestone

PFR-V2B-R3 may derive a pair categorical range only after independently
accepted USD and JPY side evidence exists. It is not part of this navigation
milestone.
