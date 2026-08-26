# Multi Oscillator MO-P3A Unsigned Step Wave

Status: `IMPLEMENTED_FOR_CENTRAL_REVIEW`

Date: `2026-08-26 IST`

Parent acceptance commit: `95a624d7270bb0a6ac3d9f62423a0d2172ce584a`

## Scope

MO-P3A productizes the founder-accepted discrete unsigned event activity from
MO-P2 as an exact time-domain display. It does not assign direction, polarity,
financial meaning or pair-relative behavior.

The two independent side fields are:

```text
U_USD(t) = A_USD(t)
U_JPY(t) = A_JPY(t)
```

There is no `U_USD - U_JPY` calculation and no pair resultant in this
milestone.

## Contract

The UI contract is `MO_UNSIGNED_ACTIVITY_STEP_WAVE_V1`.

Each wave segment is copied from the accepted backend activity interval and
retains:

- `startUtc` and `endUtc`;
- `rawActiveEventCount`;
- `coverage` and `unknownReason`;
- `contributingEventIds`;
- semantic unit `ACTIVE_EVENT_COUNT`.

Intervals are half-open: `[startUtc, endUtc)`. The renderer uses a zero-order
hold: the raw count is constant throughout the interval and changes only at an
exact interval boundary. Non-contiguous intervals start a new SVG path, so a
missing interval is never drawn as an interpolated diagonal.

The display Y coordinate is a presentation mapping only:

```text
height = clamp(rawActiveEventCount / sharedFilteredAxisMax, 0, 1)
```

The shared filtered axis is the maximum raw active count across the visible USD
and JPY intervals, with a zero baseline. It is not normalization of event
data, magnitude, scoring or calibration.

## Product Surface

`Unsigned Activity Waves` is rendered inside the existing Multi Oscillator /
Event Activity panel, before the per-side raster/count detail. It contains:

- one USD step-wave lane;
- one JPY step-wave lane;
- one shared UTC time axis;
- the same filtered raw-count maximum for both lanes;
- exact event markers and selectable interval hitboxes;
- visible UNKNOWN coverage overlays and the observed count retained beneath
  them.

Selecting an event marker opens the existing immutable event provenance
inspector and updates the shared research time controller at `exactUtc`.
Selecting an interval updates the shared controller at that interval's stored
`startUtc`. The existing event filters remain authoritative: changing a body
or aspect filter recomputes the visible intervals, step paths and shared axis
without changing backend event identities or hashes.

## Coverage Semantics

`KNOWN` and `UNKNOWN` remain independent from activity count. A known zero is
drawn at the zero baseline. An unknown interval retains its observed count,
uses a dashed trace/top overlay, and exposes its unknown reason. An unknown
interval is never converted to zero, a full-height fill or a directional state.

The compact legend states:

- `Raw activity: 0-N events`;
- `Fill/trace = observed count`;
- `Hatch = incomplete coverage`;
- `Baseline = 0`.

## Implementation Paths

- `gann-astro-desk/src/views/MultiOscillatorActivityWave.ts` contains the
  contract, interval projection, exact step-path construction, Y mapping and
  marker positioning.
- `gann-astro-desk/src/views/MultiOscillatorActivityPanel.tsx` renders both
  synchronized lanes, the shared axis, filters, event selection and
  provenance interactions.
- `gann-astro-desk/src/App.css` contains the bounded wave layout, marker
  hitboxes, unknown overlay and responsive dense-event treatment.
- `gann-astro-desk/src/views/MultiOscillatorActivityWave.test.ts` and
  `gann-astro-desk/src/fieldsWorkspace.test.tsx` cover the pure contract and
  integrated UI behavior.

The frontend does not compile astronomy events. The accepted backend
`MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` response remains the source of event
and interval data.

## Verification

Focused frontend command:

```text
npm exec -- vitest run src/views/MultiOscillatorActivityWave.test.ts src/fieldsWorkspace.test.tsx --pool=forks --maxWorkers=1 --reporter=dot
```

Result: `2` files passed, `28/28` tests passed.

Full frontend command:

```text
npm run test -- --pool=forks --reporter=dot
```

Result: `43` files passed, `195/195` tests passed.

Additional verification:

- `npm run lint`: passed;
- `npm run build`: passed, 1,878 modules transformed;
- `npm run test:backend`: 319 passed, 1 skipped;
- `cargo fmt --check`: passed;
- `cargo check`: passed;
- `cargo test`: 19 passed, 0 failed;
- `git diff --check`: passed.

## Explicit Limits

This milestone does not add or enable:

- signed activity, polarity, supportive/adverse states or bullish/bearish
  labels;
- USD-JPY subtraction, pair-relative output or a pair resultant;
- magnitude, weights, kernels, moving averages, normalization, calibration,
  smoothing or interpolation;
- price, outcome, SBC, CGVO, BPHS, RSI or financial interpretation;
- LLM, ML, Auto Suggest, MT5, order placement or execution.

`executionAllowed = false` remains unchanged. No backend contract, event
identity, source profile, package or installer was changed. No Windows
candidate is produced by MO-P3A; the implementation stops here for central
review.
