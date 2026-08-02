# PFR-V2B-R1 Live Range and Stepped Fields

Date completed: 2026-08-02

## Purpose

Turn the previously manual compact Fields request into a truthful, visible
research instrument without adding evidence, numerical magnitude, pair
direction, fusion, or execution behavior.

## Delivered

### Live visible-range binding

- `MarketChart` already persists its settled logical visible range after
  pan/zoom through `ChartLayoutState.visibleStartUtc` and `visibleEndUtc`.
- `MainWorkspace` now passes that authoritative range into `ChakraLabWorkspace`.
- Chakra clamps the range to the loaded chart extent and requests the strict
  synchronized coordinator using the resulting exact UTC boundary pair.
- The old `chart.candles.slice(-110)` request source has been removed.
- A 240 ms debounce prevents request storms during viewport movement.
- Each request carries an in-memory sequence. A response only updates the UI
  when it is still the most recent requested viewport.
- The explicit button is now **Refresh now**, for recovery/retry only; the
  current viewport loads automatically when the Chakra workspace is opened or
  receives a new persisted chart range.

### Categorical stepped panes

- USD and JPY render as separate SVG stepped fields over the same UTC range.
- `SUPPORTIVE` is plotted above the always-visible zero axis.
- `ADVERSE` is plotted below the zero axis.
- `NEUTRAL` is zero only when the immutable reviewed state is explicitly
  neutral.
- `MIXED` has separate supportive and adverse dashed activity. It does not
  masquerade as neutral or produce a synthetic combined sign.
- `UNKNOWN` has no continuous balance line and is shown as a patterned gap.
- Every field is labelled `MAGNITUDE_NOT_CONFIGURED`; the step heights are
  categorical states, not financial strength, confidence, probability, or
  calibration.
- SBC remains a separate availability lane because the current SBC contract
  does not supply a chart-conditioned categorical polarity. It retains its
  `NOT_AUTOMATIC_CONFIRMATION` relationship.

## Source Changes

- `gann-astro-desk/src/views/MainWorkspace.tsx`
  - forwards the persisted price-chart visible range to Chakra.
- `gann-astro-desk/src/views/ChakraLabWorkspace.tsx`
  - clamps and debounces the current chart viewport, sequence-guards range
    requests, and stops using a trailing candle slice.
- `gann-astro-desk/src/views/ProductFirstSbcWorkspace.tsx`
  - presents the synchronized chart range instead of a fixed 110-candle view.
- `gann-astro-desk/src/views/IndependentFieldStack.tsx`
  - adds the independent USD/JPY categorical stepped panes and explicit gap
    grammar.
- `gann-astro-desk/src/App.css`
  - adds the minimal field-panel visual grammar.
- `gann-astro-desk/src/chakraLabWorkspace.test.tsx`
  - proves that the exact provided viewport boundaries reach the range
    coordinator.

## Verification

| Gate | Result |
| --- | --- |
| Oxlint | Passed |
| Focused field/range tests | 32 tests passed |
| Full desktop frontend suite | 32 files / 133 tests passed |
| TypeScript/Vite production build | Passed |

The existing Vite >500 kB main-chunk warning remains recorded as a later
performance concern. No package was produced in R1.

## Intentionally Not Implemented

- No shared crosshair, selected interval, or keyboard boundary navigation yet.
- No derived `FX_PAIR_CATEGORICAL_RANGE_V1` contract or USDJPY pair field.
- No positive/negative production plot exists while the immutable USD and JPY
  evidence registries are empty; the production panes correctly remain gaps.
- No packet admission, classification, approval, numerical magnitude,
  smoothing, calibration, fusion, Auto Suggest, ML, live inference, trading,
  or order capability.

## Next Bounded Milestone

PFR-V2B-R2: one visible selection/crosshair timestamp across price, USD, JPY,
SBC, Chakra, and Why. It must work from canonical interval boundaries and must
not use decimated display points as evidence.
