# CGVO-S1A-R1 Central-Review Correction

Status: `READY_FOR_CENTRAL_REVIEW`

## Scope

This bounded correction preserves the CGVO-P1R1 local-eclipse engine and the
CGVO-S1A source contracts. It does not create a package, market interpretation,
score, field input, automated suggestion, model input, broker action, or
execution path.

## Four Corrections

### Lunar intercalation guard

The former full-moon Sun-sign-delta shortcut was removed as an intercalation
decision. The read-only purnimanta adapter now finds physical new-moon
conjunction boundaries, finds selected Chitra-180-frame solar rasi ingress
boundaries in every relevant new-moon interval, and accepts an ordinary month
only when every interval has exactly one ingress. The response preserves each
interval's start and end plus its ingress timestamps.

`2023-07-29` returns `UNKNOWN_INTERCALATION_PROFILE_NOT_CLOSED` with
`ADHIKA_OR_KSHAYA_GUARD_TRIGGERED`; it can no longer return `SHRAVANA`.
`2025-04-15` remains `VAISHAKHA` only after two relevant intervals each have
one documented ingress. This guard is calendar-mechanics evidence, not a
complete historical adhika/kshaya naming doctrine.

### Aspect semantics

The existing sign-relative fractions remain exact categorical geometry from
Brihat Jataka II.13. They are now nested under
`auditGeometryAtMaximum` with role `GEOMETRY_SNAPSHOT_ONLY`. The V.60-62 source
claims are exposed as source tokens, but the required commencement/conclusion
mapping is not source-closed. Therefore
`sourcePhaseActivation.status=UNKNOWN_SOURCE_PHASE_MAPPING_NOT_CLOSED`,
`effectActivated=null`, and `jupiterMitigationActivated=null`.

### Locality-safe Swiss state

`_topocentric_body_states` owns the existing re-entrant lock, ephemeris
configuration, `set_topo`, topocentric equatorial calculation, horizontal
coordinates, and local-hour-angle derivation. The observer and firmament paths
reuse that immutable result. Concurrent Ujjain/New York workbench tests match
their single-thread baselines and retain one physical causal event identity.

### Source-status wording

The UI now states that rasi/nakshatra partitions are root-source closed while
their absolute frame requires explicit selection; purnimanta is a
high-confidence source-internal inference while intercalation can remain
unknown; and firmament geometry is available while the classical section is
unknown due to commentary conflict.

## Remaining S1B Questions

- Chitra apparent-versus-true star, epoch, nutation, and alternate-anchor audit.
- Lunar commencement/conclusion mapping and solar C1/C4 source alignment.
- Firmament six-versus-seven source adjudication.
- A complete historical adhika/kshaya naming engine beyond this fail-closed guard.

## Invariants

`executionAllowed=false`. There is no price or outcome read, market direction,
polarity, score, Fields, SBC, Auto Suggest, ML, MT5, or execution path.
