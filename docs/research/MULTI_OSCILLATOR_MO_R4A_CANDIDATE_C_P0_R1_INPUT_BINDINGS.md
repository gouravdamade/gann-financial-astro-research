# MO-R4A Candidate C P0-R1 Shared Astronomy Inputs and Component Bindings

**Milestone:** MO-R4A-CANDIDATE-C-P0-R1
**Starting commit:** `30138691d79c4ea3f543e9cb4f3a74f16c8a82fb`
**Status:** FROZEN BEFORE EVALUATOR IMPLEMENTATION
**Stop gate:** `CENTRAL_REVIEW_CANDIDATE_C_P0_R1_BEFORE_EVALUATOR_IMPLEMENTATION`

## Scope

P0-R1 completes the non-runtime input contract for Candidate C. It preserves
the P0 population exactly and freezes shared astronomy facts plus the
event-to-operator bindings that future clean-room evaluators must consume.
Neither Evaluator A nor Evaluator B, a comparator, a source-output fixture, or
Candidate C execution exists in this milestone.

The immutable P0 population remains **645** events in canonical
`exactUtc,eventId` order. Its exact population hash remains
`A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6` and
the population manifest hash remains
`0B384FF0131BF19EFB842A3D4AEE4F7D1F9A923469281A65D6326B76CC39A092`.

The historical P0 preregistration hash remains
`1FB698C6420CF5D8F6E950849BF53B9D7BD35AF67DD9EE157DE08161427BD719`.
The updated P0-R1 preregistration hash is
`5A15DA738B4C349E3C251F0C000960955D955E370F51CC313E52F8D5851C1961`.

## Shared Astronomy Snapshot

The snapshot is
`status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json` with
self-hash `F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915`.
It contains each event's immutable identity, chart identity, established
source/target roles, exact UTC, sidereal longitude and longitude speed,
sign/index, frozen natal-target position, Sun and Moon positions, and the
nine-body exact-time position set.

It uses only
`RAMAN_SIDEREAL_SWISSEPH_TRUE_NODE_GEOCENTRIC_V1`: Swiss Ephemeris `2.10.03`,
`UTC/JD_UT`, true-node Rahu/Ketu opposition, and
`FLG_SWIEPH|FLG_SPEED|FLG_SIDEREAL`. The deterministic generator specification
hash is `1E3E46230999B6450A1C7B7675C44063CB06CEB8C655E35970CB38E52CFB2751`.
It reads the frozen P0 population without calling the event compiler or any
source operator, and it cannot read price, returns, outcomes, S4 results, or
provider data.

`aspectType` is deliberately excluded from the shared input snapshot. It is
part of immutable event identity but is angular geometry, not a classical
relative-place input. The snapshot also excludes source-category outputs,
relationship labels, Drsti fractions, motion labels, modifier outputs,
UNKNOWN decisions, and expected evaluator answers.

## Accepted Event Roles

The accepted event-bound adapter establishes `sourceBody=transitBody` and
`targetBody=natalTarget`; this is not inferred merely from the field names.
The machine binding cites:

- `CHART_CONDITIONED_TRANSIT_EVENT_RANGE_V1` and its frozen compiler source;
- `MO_R4A_S1R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1`; and
- the accepted `_event_astronomy_snapshot` and `_event_operator_outputs`
  mapping in `gann-astro-desk/backend/classical_source_operators.py`.

`relativePlace` is always counted inclusively from transit-source sign to
natal-target sign:

```text
((targetSignIndex - sourceSignIndex) mod 12) + 1
```

`relativeSunPlace` uses the same formula from transit-source sign to Sun sign
at exact UTC. Neither calculation may use or derive from
conjunction/sextile/square/trine/opposition.

## Component Bindings

| Component | Frozen binding and abstention boundary |
| --- | --- |
| C01 natural class | Evaluates the transit source body. Moon condition and Mercury krura-association have no admitted mapper, so they remain deterministic UNKNOWN paths. C06 may supply a verbatim motion state only through the accepted adapter; no VAKRA-to-RETROGRADE alias or speed threshold is licensed. |
| C02 natural relationship | Directed `transitBody -> natalTarget` Trailokya lookup. Nodes remain source-unclosed. Unstated self cells use P0 generic UNKNOWN and retain their precise source dependency in binding metadata. |
| C03 temporary relationship | Uses transit and natal-target signs plus the frozen inclusive relative-place rule. |
| C04 compound relationship | Uses **Saravali** natural relationship plus BJ/Saravali temporary relationship. Trailokya natural relationship is expressly prohibited as a C04 input. Any unresolved upstream relationship emits `COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED`. |
| C05 ordinary and special Drsti | Emits separate ordinary and special rows from the frozen sign-derived relative place. Event aspect type is prohibited. A stated absence of fraction/override remains a source value, not an UNKNOWN shortcut. |
| C06 Sthula motion | Uses the transit source body and sign-derived relative-Sun place only. Raw speed is audit evidence and cannot introduce modern thresholds. Asta, unlisted inner cases, unsupported bodies, stationary, and direct-slow attempts remain deterministic UNKNOWN paths. |
| C07 verse-166 records | Emits one UNKNOWN row per event. No typed Trailokya Sthana-Phala measurement is admitted, so no modifier and no factor is manufactured. Multiple modifier stacking remains prohibited. |

## Profile and UNKNOWN Controls

C04's required natural input is independently closed as
`SARAVALI_NATURAL_RELATIONSHIP_V1` in the adjudicated S2R1-R1 Saravali ledger
(`985DA1ECD2FF6631D9624541CEA27F69AC4620207EFE4C6CD79790263E3FAF01`).
This is a supporting input contract only; it does not merge Trailokya into the
BJ/Saravali profile.

The binding contract self-hash is
`D3219C1E6A8B7C791064F50E2CF23C211D4DE859AA73978B689C97E650DF5985` and
the applicability-matrix hash is
`5C0E627294579FA9C41C5E19B791ED489FFDE2D2700D21AC7AE4C3530C91F4B4`.
No UNKNOWN reason code was invented. Where P0 already admits a specific code,
it is mandatory. For C02 self-cell and C07 absent-Sthana-Phala cases, P0's
frozen generic `UNKNOWN` code is mandatory while the more specific existing
operator dependency remains recorded in binding metadata.

## Output Universe and Clean Room

The binding freezes **8** contract rows per event: one each for C01, C02,
C03, C04, C06, and C07, plus two distinct C05 rows. The resulting **5160**
row-key universe has hash
`6AC975EE4DA32A3872399C68F514BA19E63FFAC5F565018A2DF15CECA27A4580`.
It contains only event/profile/component/contract/operator identities and no
output values.

Both future evaluators must consume the P0-R1 snapshot. They must not query
Swiss Ephemeris during the frozen run, import each other's code, share business
helpers, inspect each other's output, or use an expected-output fixture. A
mismatch fails the run; any correction requires a new preregistered run.

## Locks

This is source-operator reproducibility infrastructure only. No price, return,
outcome, provider, polarity, score, magnitude, wave, market forecast, Fields
polarity, Auto Suggest, ML, MT5, execution, runtime code, or Candidate C run
was created or accessed. `executionAllowed=false` remains immutable.
