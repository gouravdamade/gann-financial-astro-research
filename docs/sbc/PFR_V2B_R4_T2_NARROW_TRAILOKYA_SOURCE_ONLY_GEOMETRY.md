# PFR-V2B-R4-T2: Narrow Trailokya Source-Only Geometry

## Decision implemented

The immutable record `SBC_TRAILOKYA_1972_SOURCE_ONLY_GEOMETRY_V1` admits only
three Trailokya Dipika 1972 variables under the explicit profile selection
`SBC_TRAILOKYA_1972_V1`:

- Variable Mars-through-Saturn ray selection from an externally supplied
  `RETROGRADE`, `DIRECT_SWIFT`, or `MEAN` research state.
- Sun, Moon, Rahu and Ketu all-three figure-relative rays.
- Side and front ray extent with categorical target reach.

The record points to `PFR-V2B-R4-T1`, its packet IDs, and printed/PDF page
locators. It is read only and hashes into every geometry result/export.

## Product behavior

The dedicated backend/native route is
`/api/chakra-lab/trailokya-source-only-geometry`. It builds a score-free Chakra
snapshot: `guidance` is always `null`. The Board uses the returned rays to mark
target cells and reached targets. Its audit section exposes the source profile,
packet, founder decision, page locators, and any unavailable ray.

The export embeds the same approval/audit data. `LEFT`, `FRONT`, and `RIGHT`
remain figure-relative only; no cardinal/geographic binding is claimed.

## Fail-closed boundaries

- Mars, Mercury, Jupiter, Venus and Saturn require the explicit caller state;
  no speed threshold is derived.
- A missing or disputed source/target-cell mapping returns an unavailable ray;
  no approximate target is emitted.
- The current partial grid may still return such unavailable rays. This is
  intended evidence, not a fallback signal.
- Natural planet class, Moon/Mercury conditions, modifier factors and stacking
  remain outside this implementation.

No directional wave, polarity, pair mapping, magnitude, score aggregation,
price conversion, confidence, Auto Suggest, execution or package candidate is
generated. Mode 2 behavior and existing named profiles are unchanged.

## Verification

`pytest -q test_classical_oscillator_coverage.py
test_trailokya_dipika_vedha_page_certification.py
test_trailokya_source_only_geometry.py
gann-astro-desk/backend/test_chakra_lab_service.py` passed 40 tests.

Focused frontend tests passed 34 tests; the production frontend build and
`cargo check` for `gann-astro-desk/src-tauri` passed. No installer was created.
