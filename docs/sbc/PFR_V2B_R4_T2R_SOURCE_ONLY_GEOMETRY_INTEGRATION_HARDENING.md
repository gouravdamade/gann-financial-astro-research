# PFR-V2B-R4-T2R - Source-Only Geometry Integration Hardening

## Scope

This bounded correction hardens only the approved Trailokya 1972 source-only
geometry path. It adds no doctrine, polarity, magnitude, score, price
conversion, Auto Suggest, execution, package, or polarity event.

## Synchronized field behavior

When `SBC_TRAILOKYA_1972_V1` is explicitly selected, synchronized refresh now
compiles the USD and JPY chart-conditioned fields normally, but returns the SBC
field as:

`GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED`

The returned SBC object is score-free and contains no intervals. It is not an
error and does not replace either currency field. The branch deliberately does
not construct `ChakraLabEngine`, `VedhaGuidanceEngine`, a regular atomic ledger,
or a substitute Phaladeepika/Trailokya scored profile. A separate score-free
Trailokya range compiler remains a future, separately admitted task.

## Target reach contract

Ray summaries now retain mapping uncertainty:

- `REACHED`: at least one known target is reached and none are unknown.
- `NOT_REACHED`: all target mappings are known and none is reached.
- `UNKNOWN`: all target mappings are unknown or unavailable.
- `PARTIAL_UNKNOWN`: known and unknown target mappings are mixed.

An unknown mapping never collapses to `NOT_REACHED`.

## Restored source gaps

The source-only user interface and synchronized unavailable state explicitly
show that classical completeness is false, including:

- `SBC_TD1972_BASE_NATURAL_PLANET_CLASS_PENDING`
- `SBC_TD1972_ISOLATED_RESULT_FACTORS_PENDING`
- `SBC_TD1972_SWIFT_MEAN_THRESHOLD_SOURCE_MISSING`
- `SBC_TD1972_MODIFIER_STACKING_SOURCE_MISSING`
- `SBC_TD1972_MOON_MERCURY_CONDITIONS_PENDING`
- `SBC_ABSOLUTE_ORIENTATION_UNRESOLVED`
- `SBC_TD1972_GEOMETRY_RANGE_NOT_COMPILED`

## R3 identity wiring

Founder-visible synchronized requests now use the accepted immutable research
records directly, with no polarity events admitted:

- USD chart: `FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1`
- USD hypothesis: `USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1`
- JPY chart: `FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1`
- JPY hypothesis: `JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1`

The previous provisional `UNCONFIGURED_*` and `PENDING_FOUNDER_REVIEW` request
identities are no longer emitted from this founder-facing workspace. This is
identity wiring only; no chart-conditioned polarity data was created or used.

## Verification reconciliation

The original R4-T2 handoff recorded a focused frontend run of **34** tests. A
later R4-T2 verification run collected **35** after the final pre-existing test
was added. The exact expanded T2R frontend command below now collects and passes
**39** tests; it supersedes neither historical count, but records the current
test surface after integration-hardening coverage was added.

```text
npm test -- --run src/api.test.ts src/chakraLabWorkspace.test.tsx src/visualizationModes.test.ts src/visualizationSourceGaps.test.ts
```

The focused Python command passed **44** tests:

```text
pytest -q test_classical_oscillator_coverage.py test_trailokya_dipika_vedha_page_certification.py test_trailokya_source_only_geometry.py gann-astro-desk/backend/test_chakra_lab_service.py gann-astro-desk/backend/test_synchronized_range_service.py
```

The production frontend build plus native `cargo fmt --check` and `cargo check`
also passed.

## Physical UI verification

1. Open Chakra Board from a chart with at least two visible timestamps.
2. Choose `Trailokya 1972 source-only geometry` under Vedha source profile.
3. Confirm the board refreshes and renders only source-only rays; no guidance
   score appears.
4. Open the integrated workspace and wait for its automatic range refresh.
5. Confirm USD and JPY lanes remain visible. The SBC lane must say
   `GEOMETRY ONLY RANGE NOT IMPLEMENTED` and must not show a score or a request
   error.
6. Expand `Source gaps` and confirm all seven named unresolved gaps are listed.
7. Switch back to the Phaladeepika editor profile and confirm its existing
   atomic range behavior is unchanged.

All execution, Auto Suggest, financial-validation, scoring, and packaging locks
remain false.
