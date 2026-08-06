# PFR-V2B-R5-F1: Dedicated Fields Workspace and Pair-Relative Field

## Purpose

This milestone moves the founder-visible categorical field product out of the
Chakra workspace and into the top-level **Fields** workspace. It is a bounded
visualization and transparent-data-transform change. It adds no Jyotish
doctrine, evidence, polarity catalogue records, score, price conversion,
prediction, Auto Suggest behavior, or execution path.

The Fields workspace reuses the loaded chart, active symbol/timeframe, visible
UTC range, selected candle, shared crosshair, `RESEARCH_TIME_CONTROLLER_V1`,
visualization mode, source profile, and founder-approved side-chart identities.
It does not independently refetch market chart data.

## Product layout

The Fields page is one normal vertically scrolling workspace, in this order:

1. Instrument and source-profile context.
2. The existing synchronized market chart.
3. USD/base categorical field for an FX instrument.
4. JPY/quote categorical field for an FX instrument.
5. A transparent derived `USDJPY pair-relative field`.
6. An independent SBC availability/geometry field.
7. Coverage, activity, conflict, source-gap, chart-identity, and interval-audit details.

Each field shares the exact UTC range and crosshair with the price chart.
Selecting any USD, JPY, pair, or SBC interval stores its canonical `startUtc`
in the research time controller. Pair selection also stores
`selectedPairIntervalId`; it is not inferred from SVG pixels.

Chakra now retains its board, audit, and a compact **Open in Fields** hand-off.
It is not the primary oscillator workstation.

## FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1

`FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1` is a **modern engineering research
transform**. It is not a classical doctrine, a market forecast, a confidence
value, or SBC confirmation.

### Input and boundary contract

For an FX instrument, the compiler reads only the already stored independent
base and quote categorical intervals. Its output boundaries are the sorted
union of:

- the requested range start and end;
- every USD/base stored interval start and end;
- every JPY/quote stored interval start and end.

The compiler never samples, stretches, smooths, interpolates, fits a curve, or
looks at market price/outcomes. Every derived interval includes the exact source
interval IDs that produced it.

### Calculation

For each known side interval:

```text
supportive component = +1 when active
adverse component    = -1 when active
sideGross            = active known supportive + adverse component count
sideNet              = supportive component count - adverse component count
sideBalance          = sideNet / sideGross, when sideGross > 0
```

An explicit `NEUTRAL` state may yield `0`. A `MIXED` state preserves its
supportive activity, adverse activity, gross activity, and conflict even where
its balance is `0` or close to it.

For USDJPY:

```text
base    = USD
quote   = JPY
pairRaw = baseBalance - quoteBalance
pairDisplay = clamp(pairRaw / 2, -1, +1)
```

If either side is unknown, the pair result is:

```text
pairDisplay = null
state       = UNKNOWN_SIDE_EVIDENCE
```

The UI renders that as a visible patterned gap. Unknown evidence is never
silently converted to zero, neutral, or a decorative flat wave.

### Generic instrument behavior

- **FX**: base field, quote field, transparent pair-relative field, and
  independent SBC field.
- **Single stock**: one chart-conditioned stock field and independent SBC;
  there is no automatic subtraction.
- **Multiple stocks**: one pane for each explicitly selected stock. A relative
  field requires an explicit comparison configuration and is not created here.

## Visualization mode behavior

### SOURCE_ONLY_BASELINE

Only known source-backed categorical side paths are shown. Pair intervals appear
only when both side inputs are known. Magnitude remains explicitly unconfigured.

### CALIBRATED_RESEARCH

The source baseline remains intact. This milestone configures no new calibrated
values.

### VISUAL_ONLY_NO_SCORE

The chart, interval boundaries, coverage, and availability lanes remain visible.
USD, JPY, and pair directional paths are suppressed and the page states:

`DIRECTIONAL FIELD SUPPRESSED BY VISUAL-ONLY MODE`

Suppression is deliberate and must not resemble a failed request.

## SBC separation

SBC remains independent from USD, JPY, and pair derivation.

- The existing Phaladeepika atomic/availability behavior is unchanged.
- Trailokya source-only geometry continues to expose
  `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` until its independent range compiler
  exists.
- Trailokya keeps all seven unresolved source gaps visible and never falls back
  to a score, polarity state, guidance unit, or wave.

## Current empty-evidence state

When no admitted side catalogue event is active, Fields still renders the
permanent USD and JPY lanes, the accepted chart identities, shared UTC scale,
and patterned gaps. It identifies the reason as
`POLARITY_CATALOGUE_MISSING` or `NO_ACTIVE_REVIEWED_SIDE_EVENT`. The pair lane
is `UNKNOWN_SIDE_EVIDENCE`; magnitude is `MAGNITUDE_NOT_CONFIGURED`.

## Explicit guardrails

This milestone does **not**:

- invent or admit polarity evidence;
- infer polarity from aspect geometry, planet nature, Shadbala, Drik, or price;
- use SBC as confirmation;
- use price outcomes;
- add curve fitting, smoothing, interpolation, sine waves, or price conversion;
- enable Auto Suggest, trade placement, execution, or packaging promotion.

## Verification

Focused field/product tests cover exact union boundaries, side-balance math,
mixed-state preservation, unknown gaps, visual-only suppression, Trailokya
score-free behavior, profile refresh, interval selection, stock behavior, and
the Chakra hand-off. Responsive visual checks cover 1920 x 1080 and 1366 x 768
with the chart and first field lanes visible without a nested field scroll box.

Founder physical acceptance remains pending. The next package is a separate,
immutable founder-inspection candidate and is not a stable promotion.
