# Multi Oscillator MO-P2: Unsigned Event Activity V0

Status: `IMPLEMENTED_FOR_CENTRAL_REVIEW`
Milestone: `MO-P2`
Evidence mode: `EXPLORATORY_UNSIGNED`

> MO-P2-R1 hardening supersedes the response-shape and coverage wording below.
> The current implementation uses `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` /
> `MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1`, classifies rejected candidates by
> visible-range relevance, and renders both sides on one filtered raw-count
> display axis. The V0 record is retained as implementation history.

## Purpose

This milestone adds a founder-inspectable event-activity surface to the existing
Fields workspace. It is a descriptive view of backend-owned chart-conditioned
transit events for the accepted USD and JPY currency hypotheses. It is not a
directional oscillator, forecast, score, magnitude model, or execution input.

The existing USD, JPY, pair-relative categorical, SBC, and BPHS surfaces remain
separate and unchanged. The new panel does not replace or fuse those fields.

## Backend Contract

Endpoint: `POST /api/multi-oscillator/activity-range`

Tauri command: `multi_oscillator_activity_range`

Contract: `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1`

Contribution contract: `MO_ACTIVITY_CONTRIBUTION_V1`

The request accepts only:

- `rangeStartUtc`;
- `rangeEndUtc`;
- `sideIdentities`, exactly `USD` and `JPY`;
- `aspectProfileId`, exactly `ASPECT_STRENGTH_V0`.

Chart identities, body lists, aspect lists, event IDs, polarity, magnitude, and
pair-relative values cannot be supplied by the frontend. The service delegates
event construction to the existing canonical chart-conditioned transit event
compiler, which loads the accepted backend chart registry and astronomy
contract.

The response includes, independently for USD and JPY:

- accepted chart and hypothesis identities;
- complete immutable event records and event hashes;
- applying start, exact timestamp, and separating end;
- event-universe profile, body universe, aspect profile, and generator hash;
- astronomy provider, ephemeris, ayanamsha, node policy, and generator data;
- exact half-open activity intervals;
- contributing event IDs and raw active-event counts;
- deterministic body/aspect occurrence counts;
- coverage and unknown reason;
- read-only guardrails.

## Activity Semantics

For event `i`, the contribution is one unit on:

`[applyingStartUtc, separatingEndUtc)`

The exact timestamp is an inspection marker, not a sampled value or a weight.
The backend forms interval boundaries from the union of the requested range
boundaries and every clipped event boundary. It evaluates active membership at
each interval start; it does not sample, interpolate, smooth, normalize, fit, or
render a continuous waveform.

`rawActiveEventCount` is an integer event count only. It is not a score,
probability, signed magnitude, confidence value, or market strength.

If compilation succeeds with no active event, the interval is `KNOWN` with count
zero. If the compiler reports unknown or rejected coverage, the interval remains
`UNKNOWN`; unknown coverage is never silently converted into zero.

## Founder UI

Fields now contains a separate `Multi Oscillator / Event Activity` section below
the existing independent categorical fields. It provides:

- USD unsigned activity lane;
- JPY unsigned activity lane;
- applying-to-separating event spans;
- exact event markers;
- rectangular raw active-event count intervals;
- local transit-body and aspect filters;
- shared crosshair updates when an event or interval is selected;
- selected-event provenance including event hash, exact UTC, chart identity,
  body, target, aspect, and explicit `NOT ASSIGNED` / `NOT CONFIGURED` states.

The inspector identifies records as `CANONICAL_COMPILER_EVENT`. It does not
claim `SINGLE_PASS_VERIFIED` for arbitrary live ranges; that status belongs to
the separately audited founder packets and is not present in this activity
response.

The panel is labelled `EXPLORATORY_UNSIGNED`, `UNSIGNED`,
`NON-PREDICTIVE`, and `MAGNITUDE NOT CONFIGURED`. There is no USD-minus-JPY
unsigned difference field.

## Guardrails

The response and frontend transport assert:

- `polarityAssigned=false`;
- `magnitudeAssigned=false`;
- `priceDataRead=false`;
- `priceOutcomeRead=false`;
- `sbcRead=false`;
- `llmRead=false`;
- `pairDifferenceComputed=false`;
- `normalizationUsed=false`;
- `smoothingUsed=false`;
- `executionAllowed=false`.

SBC, CGVO, Auto Suggest, ML, MT5, order placement, and execution are not
connected to this panel.

## Verification

Focused backend tests cover exact boundary segmentation, half-open membership,
known zero versus unknown coverage, request-injection rejection, and structured
JSON route behavior. Frontend Fields tests cover default rendering, exact event
inspection, crosshair callback, existing categorical lanes, profile isolation,
BPHS behavior, and page guards. The production TypeScript/Vite build and Oxlint
pass.

A real 14-day backend smoke produced 57 USD events and 59 JPY events with 79
and 78 exact boundary intervals. The compiler also reported rejected boundary
records, so the side coverage state remained `UNKNOWN`; those records were not
converted into a false zero.

This source milestone is not a packaged Windows candidate. Central review must
decide whether a founder-inspection candidate should be built next.
