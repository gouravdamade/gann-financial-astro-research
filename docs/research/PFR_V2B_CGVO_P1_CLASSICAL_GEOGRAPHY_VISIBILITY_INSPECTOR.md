# PFR-V2B-CGVO-P1: Classical Geography & Visibility Inspector

Status: `IMPLEMENTED_FOUNDER_INSPECTION_CANDIDATE`

This milestone adds a read-only research inspector to Gann Astro Desk. It
keeps modern eclipse astronomy factual and separates the two held classical
source profiles from that calculation. It does not create a market signal,
score, forecast, polarity, or execution input.

## Contracts

- Observatory: `CLASSICAL_GEOGRAPHY_VISIBILITY_OBSERVATORY_V1`
- Event identity: `CGVO_CAUSAL_ECLIPSE_EVENT_V1`
- Modern astronomy: `MODERN_ASTRONOMY_VISIBILITY_V1`
- Varahamihira: `VARAHAMIHIRA_BS_ECLIPSE_V1`
- Trailokya: `TRAILOKYA_1972_GEOGRAPHY_ARGHA_V1`
- Kurma seed: `VARAHAMIHIRA_KURMA_REGION_SEED_V1`

One physical eclipse has one causal event ID derived from event type, global
maximum in UT, and global eclipse type. A locality changes only local
circumstances; it never creates a second causal event. UT is the identity time
scale. IANA timezone is display metadata only.

## Product Surface

Open `Experiments` and choose `CGVO classical geography & visibility`. The
inspector supports solar and lunar event ranges, a selected event, and
locality-specific circumstances for Ujjain, New York, London, or an explicit
future API locality. It shows contacts, local visibility/type, magnitude and
obscuration as separate modern facts, topocentric altitude/azimuth, and a
compact phase timeline.

The source panels remain parallel:

- Varahamihira displays typed claim locators and eligibility/status fields.
- Trailokya displays the exact geography/Argha context banner and remains
  source-silent for eclipse visibility in the held witness.
- Kurma displays raw nine-region nakshatra groups only; modern geography
  mapping is not built.

No claim from one source is used to complete another source. The inspector
does not calculate a live Trailokya eclipse rule.

## Explicit Unknowns

The event audit exposes unresolved source dependencies, including the
Varahamihira rasi frame, nakshatra/ayanamsha frame, lunar-month convention,
firmament interpretation, morphology mapping, colour observation, and the
Trailokya eclipse-visibility source gap. These remain `UNKNOWN`,
`MAPPING_UNRESOLVED`, `SOURCE_SILENT`, or `OBSERVATION_REQUIRED` as
appropriate. No missing field is replaced by neutral, zero, or a modern
astrology assumption.

The Varahamihira fixture is deliberately marked
`WORKING_WITNESS_METADATA_PENDING`; no fully certified 1946 witness is claimed
by this milestone. `SHOBHANA DHANYARGHA` remains a lexical lock with null
normalized market direction.

## API

The backend routes use the central runtime/API transport and return structured
JSON errors:

- `GET /api/experiments/cgvo/status`
- `GET /api/experiments/cgvo/source-profiles`
- `GET /api/experiments/cgvo/kurma-gazetteer-seed`
- `GET /api/experiments/cgvo/eclipse-search`
- `GET /api/experiments/cgvo/event/<causal-event-id>/local-circumstances`
- `GET /api/experiments/cgvo/workbench`

The sidecar packages the three source fixtures under
`configs/research/cgvo`. Packaging tests fail if any fixture is absent.

## Guardrails

The CGVO guardrail contract keeps all of these false: price data, price
outcome, Fields, SBC, Auto Suggest, ML, MT5, score aggregation, market
direction, and execution. `executionAllowed` is always `false`.

This is a founder-inspection candidate only. Physical founder review of the
packaged candidate remains pending.

## P1R1 Corrections

The immutable `0.10.57-pfr-v2b-cgvo-p1` candidate remains preserved as the
historical CGVO candidate. The P1R1 correction keeps its event and source
contracts unchanged while closing inspection gaps:

- Sun and Moon horizontal coordinates now use Swiss Ephemeris topocentric
  calculation with `FLG_TOPOCTR` and `set_topo`.
- Swiss Ephemeris' source azimuth (South-origin, clockwise toward West) is
  retained for audit and normalized to `0° North, clockwise` for display.
- Visibility reports `VISIBLE`, `NOT_VISIBLE`, or `RISE_SET_CLIPPED`, with
  horizon events, clipped boundaries, and the visible window. A locality with
  no matching local event cannot leak horizon times from a later event.
- Lunar umbral and penumbral magnitudes are calculated through
  `lun_eclipse_how` at the reconstructed event maximum and are rendered as
  separate fields.
- `globalMaxSwissUt` and Swiss-UT contact records are the identity fields;
  `globalMaxUtcDisplay` and UTC contact records are display aliases. The
  causal event hash uses Swiss UT identity, never a localized display value.
- Workbench/local-circumstance requests carry `causalEventId`; the backend
  reconstructs the event and rejects a mismatched URL or query identity.
- The Kurma seed now carries raw Chapter XIV historical names and verse ranges
  only. Modern geographic inference remains explicitly disabled and mapping
  status remains `UNKNOWN`.

No price, outcome, market direction, score, Fields, SBC, Auto Suggest, ML,
MT5, or execution path was added. `executionAllowed` remains `false`.
