# PFR-V2B-CGVO-P1R1: Founder Inspection Corrections

Status: `FOUNDER_INSPECTION_CANDIDATE`

This bounded correction preserves candidate `0.10.57-pfr-v2b-cgvo-p1` and
does not change its historical artifacts. It repairs the following observable
contracts for the next immutable candidate:

## Astronomy

- Sun and Moon horizontal coordinates are explicitly topocentric: the backend
  calls `swe.set_topo()` and calculates with `FLG_TOPOCTR`.
- Swiss Ephemeris' raw azimuth convention is
  `SWISSEPH_SOUTH_CLOCKWISE_TO_WEST`. The API retains `sourceAzimuthDeg` and
  exposes `azimuthDeg` under `NORTH_CLOCKWISE_0N_90E_180S_270W`.
- Solar and lunar local visibility is a three-state result. `RISE_SET_CLIPPED`
  means the event is visible at the locality but the maximum is not visible;
  the response includes horizon boundaries and a clipped visible interval.
  If there is no matching local eclipse, horizon fields remain null rather than
  borrowing a timestamp from another event.
- Lunar `umbralMagnitude` and `penumbralMagnitude` are separately sourced from
  Swiss Ephemeris `lun_eclipse_how`; the response identifies that reference.

## Identity and API integrity

`globalMaxSwissUt` and `globalContactsSwissUt` are the identity-side fields.
`globalMaxUtcDisplay` and `globalContactsUtcDisplay` are explicit UTC display
fields. Existing `globalMaxUtc`/`globalContacts` aliases remain for compatibility.
The causal ID is hashed from event type, global type, and Swiss UT maximum.
The frontend sends both the canonical Swiss-UT identity and the immutable
`causalEventId`; the sidecar reconstructs the event and rejects mismatches with
typed JSON errors.

## Kurma seed boundary

The seed includes the raw historical name lists and verse ranges for the nine
Kūrma Vibhāga groups. It deliberately does not turn those names into modern
countries or coordinates. Mapping remains `UNKNOWN`, and the UI exposes the
lists only as source names. The Chapter XIV source describes the ninefold
division and its directional groups; this implementation preserves the raw
source layer without importing a modern geography hypothesis. See the
[Bṛhat Saṃhitā Chapter XIV source translation](https://www.wisdomlib.org/hinduism/book/brihat-samhita/d/doc228914.html).

## Tests and locks

Focused tests cover topocentric coordinates and azimuth normalization,
rise/set clipping, no cross-event horizon leakage, lunar magnitude references,
causal URL identity validation, and raw Kurma names. The implementation has
no dependency on price, outcomes, Fields, SBC, Auto Suggest, ML, MT5, or
execution. `executionAllowed=false` remains invariant.
