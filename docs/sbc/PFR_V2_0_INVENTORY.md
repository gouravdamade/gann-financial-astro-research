# PFR-V2-0 Focused Contract Inventory

Date: 2026-08-02

Scope: a bounded inventory for PFR-V2/V2A only. This document adds no
calibration, source research, certification, new doctrine, oscillator values,
market inference, or execution capability.

## Decision

The repository has a reusable chart-conditioned research framework and a
usable numeric SBC ledger, but it does **not** yet have a usable immutable,
target-aware polarity catalogue for a selected production instrument. The
aspect panel must therefore retain `UNKNOWN / POLARITY_CATALOGUE_MISSING` for
missing entries. It must not turn an aspect type, a natural planet nature, or
the current transit functional-role label into a market sign.

When a future accepted chart/profile supplies a target-aware static polarity
but no declared aspect magnitude, PFR-V2 may render the requested categorical
step state under the explicit label
`CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED`:

- `SUPPORTIVE`: above zero.
- `ADVERSE`: below zero.
- `NEUTRAL`: zero.
- `MIXED`: separate supportive and adverse activity, never a silent zero.
- `UNKNOWN`: a gap with the blocking reason.

This is a display state, not a price prediction, calibration, or validation
claim. SBC remains an independent synchronized comparison field; agreement or
disagreement is descriptive only.

## Inventory

| Required question | Evidence found | Verdict |
| --- | --- | --- |
| Target-aware polarity catalogue | `research_labs/chart_conditioned_aspects` has a chart-keyed `AspectPriorRecord` for transit body, natal target, and aspect type. It is compiled in memory, has no persistent immutable catalogue store, and its static direction is taken from the transit functional role. The compiler explicitly records `TARGET_DOMAIN_TO_PRICE_POLARITY_NOT_CERTIFIED`. | `NOT_USABLE_FOR_V2A_SIGN` |
| Natal-target context | The prior records the target, natal condition, target functional role, graph context, financial-domain links, source/profile hashes, and unknowns. Target context is explanatory only and is deliberately not mapped to price direction. | `PRESENT_CONTEXT_ONLY` |
| Evidence status and provenance | Chart hypotheses include provenance, time accuracy, acceptance status, astronomy contract, effective dates, and hashes. Priors include doctrine status, explanation ledger, profile hash, and prior hash. Existing status is `SOURCE_ALIGNED_PROVISIONAL_EXPERIMENTAL_LOCKED`; it does not provide the V2A catalogue's required static entry states or a production USD/JPY record. | `PARTIAL_PROVISIONAL` |
| Accepted production USD/JPY chart data | The tracked chart-conditioned lab contains registry/test fixtures, not an accepted persistent USD or JPY chart hypothesis or per-target catalogue. Existing USDJPY displays use separate experimental SBC arithmetic, not chart-conditioned aspect polarity. | `MISSING` |
| Aspect activation / magnitude | The chart-conditioned lab supplies categorical activation and volatility labels (`WEAK` through `EXCEPTIONAL`, `LOW` through `HIGH`) but no numeric magnitude contract. It rejects hidden numeric conversion. | `MAGNITUDE_NOT_CONFIGURED` |
| SBC interval / magnitude contract | `SBC_ATOMIC_INTERVAL_SERIES_V1` and `SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1` preserve favorable, adverse, net, gross activation, scored/unknown counts, unknown magnitude, coverage, boundaries, lineage, profiles, and cutoffs. | `USABLE_AS_INDEPENDENT_SBC_FIELD` |
| Time-range compiler and API | SBC compiler accepts explicit timestamp-safe boundaries and has audit projection endpoints. The desktop currently fetches a single Chakra snapshot and optional fixed phasor for one selected instant; no visible-range oscillator-series API or shared range/crosshair controller exists. | `MISSING_FOR_V2_RANGE_PRODUCT` |
| Current product surface | `ChakraLabWorkspace` and `ProductFirstSbcWorkspace` provide a selected moment, Chakra, scalar summary, fixed 0/pi display, and chart context. They do not provide a range-based stepped SBC panel, chart-conditioned aspect oscillator, canonical selected interval, or synchronized oscillator panes. | `FOUNDATION_ONLY` |

## Reuse Map

- Chart structure and timestamp-safe event guardrails:
  `research_labs/chart_conditioned_aspects/chart_conditioned_aspects/`.
- Existing structural-prior limitation:
  `evaluation/structural_prior.py` deliberately keeps natal target context out
  of price polarity.
- Canonical SBC intervals:
  `sbc/atomic_intervals.py` (`SBC_ATOMIC_INTERVAL_SERIES_V1`).
- Canonical reconciled SBC ledger:
  `sbc/multidimensional_ledger.py`
  (`SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1`).
- Existing read-only desktop API bridge:
  `gann-astro-desk/backend/chakra_lab_service.py`.
- Existing selected-moment desktop workspace:
  `gann-astro-desk/src/views/ChakraLabWorkspace.tsx` and
  `gann-astro-desk/src/views/ProductFirstSbcWorkspace.tsx`.

## V2A-1 Entry Criteria

The next implementation is allowed to add a single lookup contract and
missing-state surface. It must:

1. Reuse the existing chart, event, and profile identities; do not create a
   second polarity engine.
2. Return a static, immutable entry only when an accepted chart/profile
   contains an explicit target-aware polarity.
3. Return `POLARITY_CATALOGUE_MISSING` or
   `TARGET_CONTEXT_INCOMPLETE` otherwise.
4. Preserve static polarity, runtime interpretation, and runtime conflict as
   separate fields.
5. Support the categorical stepped rendering above only for an accepted static
   polarity with no aspect magnitude contract.
6. Keep SBC values in their own synchronized series. No aspect/SBC fusion,
   calibration, curve fitting, trading, Auto Suggest, official ML, live
   inference promotion, or order capability is permitted.

## Verification Performed

- Chart-conditioned research lab plus SBC interval/ledger tests: `41 passed`.
- Desktop Chakra/API focused tests: `25 passed`.
- The bundled Python runtime lacks `pytest`; the repository Python runtime was
  used for the 41-test run.

## V2-0 Result

`COMPLETE`. The focused inventory does not authorize V2A-1 code until the
founder explicitly approves that next bounded implementation step.
