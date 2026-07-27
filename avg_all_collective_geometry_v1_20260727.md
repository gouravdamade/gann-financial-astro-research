# AVG(ALL) Collective Geometry V1

Date: 2026-07-27

## Purpose

The legacy `AVG(ALL)` planetary line is a synthetic, equal-weight circular
mean of ten geocentric Raman-sidereal longitudes:

- Sun
- Moon
- Mercury
- Venus
- Mars
- Jupiter
- Saturn
- Uranus
- Neptune
- Pluto

Rahu and Ketu remain excluded. This is a workspace research profile, not a
classical Jyotisha doctrine and not a certified market signal.

The V1 collective-geometry layer makes the mathematical quality of that
synthetic mean visible without changing the legacy line values.

## Calculations

For each exact chart-bar timestamp and longitude theta_i:

```text
C1 = mean(cos(theta_i))
S1 = mean(sin(theta_i))
R1 = sqrt(C1^2 + S1^2)
mean longitude = atan2(S1, C1)

C2 = mean(cos(2 * theta_i))
S2 = mean(sin(2 * theta_i))
R2 = sqrt(C2^2 + S2^2)
polarisation axis = atan2(S2, C2) / 2
```

- `R1` reports first-harmonic concentration. A high value means the ten
  bodies occupy a comparatively concentrated circular field. A low value
  means the mean longitude is weakly defined.
- `R2` reports second-harmonic or two-pole geometry. It can be high when
  bodies form opposing groups even though `R1` is near zero.
- Circular variance is `1 - R1`.
- Circular standard deviation is reported only when the first resultant is
  stable enough to define it.

## Versioned Display Classification

`AVG_ALL_DISPLAY_RELIABILITY_V1` uses these UI-only thresholds:

- unstable first resultant: `R1 < 1e-8`
- low coherence: `R1 < 0.20`
- concentrated: `R1 >= 0.65`
- bipolar evidence: `R2 >= 0.55` when first-harmonic coherence is weak

These thresholds are descriptive research heuristics. They do not change the
line, create a direction, or contribute a financial coefficient.

## Compatibility

- The original circular-mean function is retained as
  `legacy_circular_mean`.
- Regression coverage compares it directly with the former vector formula.
- Existing direct and mirror planetary-line formulas are unchanged.
- Reliability does not hide or alter legacy line values.

## Evidence Contract

The backend exposes:

- `GANN_PLANETARY_COLLECTIVE_FIELD_V1`
- `AVG_ALL_CIRCULAR_GEOMETRY_V1`
- `GANN_RESEARCH_EVIDENCE_PACKET_V1`

The evidence packet always contains explicit direction, activation, conflict,
and confidence channels. For AVG(ALL) V1 all four are
`NOT_APPLICABLE`, because no certified mapping from collective geometry to
market behavior exists.

Every response records:

- exact observation timestamp;
- profile identity and deterministic profile hash;
- ten profile members and equal weights;
- R1, R2, mean longitude, polarisation axis, state, and reliability;
- sample-level and summary evidence;
- an empirical coefficient of exactly `0.0`.

## Safety Boundary

The source and frontend contracts require:

- research only;
- context only;
- timestamp safe;
- not consumed by live inference;
- not consumed by Auto Suggest;
- not consumed by official ML notes;
- not consumed by execution.

No installed package was rebuilt for this source milestone. Promotion requires
separate packaging evidence and financial validation.

## Verification

Focused verification on 2026-07-27:

- backend evidence, geometry, and planetary-line tests: `12/12`;
- frontend planetary-line tests: `7/7`;
- complete desktop backend suite: `127/127`;
- complete desktop frontend suite: `72/72`;
- complete repository Python suite: `370/370`;
- frontend lint: passed;
- TypeScript and Vite production build: passed;
- native-size browser inspection at `1280 x 720`: passed with no overlap or
  browser-console errors;
- legacy formula identity regression: passed;
- exact opposed-group bipolar regression: passed;
- research-only contract validation: passed.
