# PFR-V2B-R5-F2A - Real Side Event Compiler and Blank Founder Pilot

## Purpose and stop gate

This bounded milestone replaces the former Fields UI placeholder event arrays
with a backend-owned transit-to-natal astronomy compiler. It produces exact,
immutable, reviewable event identities for the already accepted USD and JPY
research chart hypotheses. It does **not** assign polarity, generate a wave,
look at price, read SBC, call an LLM, create a catalogue entry, enable Auto
Suggest, package a candidate, or permit execution.

The compiler is an event-plumbing milestone only. A real event remains
`UNKNOWN` until a future, separately approved founder review and admission
process exists.

## Canonical identity source

The backend reads the immutable registry at
`research_labs/chart_conditioned_aspects/profiles/founder_chart_hypotheses_v1.json`.
No chart ID or chart-hypothesis ID is duplicated in the frontend request.

| Side | Instrument | Chart ID | Hypothesis ID |
| --- | --- | --- | --- |
| USD | `FX_CURRENCY:USD` | `FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1` | `USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1` |
| JPY | `FX_CURRENCY:JPY` | `FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1` | `JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1` |

The retained astronomy contract is
`RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1`: Swiss Ephemeris,
Raman sidereal, true-node Rahu with Ketu derived at 180 degrees, geocentric
coordinates, and the accepted historical civil-time `ZoneInfo` conversion
policy.

## Event range contract

`CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1` accepts only:

```text
sideIdentity: USD | JPY
rangeStartUtc
rangeEndUtc
aspectProfileId: ASPECT_STRENGTH_V0
```

The frontend cannot supply an event, chart ID, chart-hypothesis ID, transit
body, natal target, price result, SBC state, or LLM text. Such fields fail
closed. The backend loads the one accepted chart for the requested currency
side and evaluates the locked `ASPECT_STRENGTH_V0` geometry profile.

Each event includes: immutable `eventId` and `eventHash`, side/instrument,
chart/hypothesis, transit and natal bodies, aspect type, applying start, exact
moment, separating end, orb contract, astronomy contract, Swiss Ephemeris
version, Raman ayanamsha, node policy, generator version, and generator hash.
The range also reports rejected incomplete-boundary observations; those are
never silently clipped into founder review identities.

`FieldsWorkspace` now sends only `sideIdentities: ['USD', 'JPY']` and the
aspect profile. The existing empty target-aware catalogue therefore renders
segmented `UNKNOWN` side intervals containing the real event IDs. The derived
pair field remains `UNKNOWN_SIDE_EVIDENCE`; no decorative directional path is
introduced.

## Blank April 2025 founder packs

The selection interval is fixed before any price inspection:

```text
UTC: 2025-04-01T00:00:00Z through 2025-05-01T00:00:00Z
IST: 2025-04-01 05:30 through 2025-05-01 05:30
```

Complete events whose `exactUtc` falls in that interval are sorted by `exactUtc`
then immutable event ID. The first twelve are included per side. Price, SBC,
LLM text, expected polarity, and later outcome do not participate in selection.

| Side | Valid exact events in interval | Included blank review rows |
| --- | ---: | ---: |
| USD | 99 | 12 |
| JPY | 104 | 12 |

The versioned founder packets and immutable-output manifests are:

- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.manifest.json`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.manifest.json`

Every review row intentionally leaves reviewed polarity, evidence class,
sources, reasoning, reviewer, review timestamp, classification, and review
packet hash blank. Permitted future founder labels are:

```text
SUPPORTIVE
ADVERSE
MIXED
NEUTRAL
UNKNOWN_MORE_EVIDENCE_REQUIRED
REJECT_EVENT_IDENTITY
```

An evidence-class choice must also be made: either
`SOURCE_BACKED_CLASSICAL_CANDIDATE` (which still requires the separate R4
Mode 2-to-Mode 1 source-promotion gate), or
`FOUNDER_RESEARCH_HYPOTHESIS` (Calibrated Research only, non-classical and
financially unvalidated).

## Prepared but inactive validator

`research_labs/chart_conditioned_aspects/founder_review/FOUNDER_REVIEW_ADMISSION_VALIDATOR_PREPARATION_V1.json`
records the future exact-match contract. It is documentation/contract only in
F2A and is not connected to a catalogue, mode admission, pairing transform, or
execution. A review row may never mutate its event astronomy identity.

## Guardrails retained

- No automatic polarity from geometry, planet name, natural nature, dignity,
  price, SBC, Shadbala, Drik, Ashtakavarga, or an LLM.
- No Mode 1 admission, magnitude, directional pair field, curve fitting,
  smoothing, financial validation, Auto Suggest, order placement, or package.
- Unknown remains a visible gap rather than neutral or zero.
