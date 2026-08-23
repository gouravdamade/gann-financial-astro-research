# MO-P2-R1A Exact Raw-Count Pixel Scaling

Status: implemented for central review

## Scope

MO-P2-R1A is a frontend-only geometry correction to the accepted MO-P2-R1
unsigned activity inspector. It does not change event compilation, coverage,
astronomy, event identity, filtering semantics, or any financial/execution
path.

## Corrected mapping

The former activity fill used a visible five-percent floor:

```text
max(5, rawActiveEventCount / max(1, sharedAxisMax) * 100)
```

That made a known-zero interval visibly non-zero and exaggerated a one-event
interval. The current pure helper uses the shared, currently filtered raw
count axis:

```text
if rawCount <= 0 or sharedAxisMax <= 0 or either value is non-finite:
    0
otherwise:
    clamp(100 * rawCount / sharedAxisMax, 0, 100)
```

Examples: with an axis of 100, counts 100, 25, 1 and 0 render as 100%, 25%,
1% and 0%. With an axis of 4, counts 4 and 1 render as 100% and 25%.

## Data geometry versus interaction geometry

Each count interval remains a full-lane keyboard/click target. Its visible
fill is a pseudo-element whose height is exactly the computed percentage. A
known-zero interval therefore remains selectable without drawing a bar. A
very small positive interval is not enlarged for clickability. Unknown
intervals retain their separate hatch treatment and do not become zero or a
fabricated activity amplitude.

## Unchanged contracts

- USD and JPY continue to use one shared raw-count axis derived after local
  body/aspect filtering.
- Filtering recomputes the shared axis and does not mutate backend records,
  event IDs, event hashes, coverage, or event-universe identity.
- MO-P2-R1 visible-range rejection classification is unchanged.
- `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`, schema version 2, and all
  provenance fields remain unchanged.
- `dataNormalizationUsed=false`, `smoothingUsed=false`,
  `executionAllowed=false`, and all non-predictive locks remain unchanged.

## Verification

The frontend tests cover exact proportional values, zero-axis behavior,
negative/non-finite input, clamping, known-zero rendered height, shared-axis
filter recomputation, and existing unknown-state behavior. Full frontend,
lint, production build, Rust formatting/check/tests, and diff checks are run
as local verification. No Windows package is produced in this microfix.
