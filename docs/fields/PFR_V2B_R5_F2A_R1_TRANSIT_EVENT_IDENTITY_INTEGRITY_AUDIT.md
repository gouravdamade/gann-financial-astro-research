# PFR-V2B-R5-F2A-R1: Transit Event Identity Integrity and Multi-Pass Audit

## Scope and stop gate

This milestone audits the astronomy identity of the F2A transit-to-natal
events. It does not assign founder polarity, inspect price, read SBC or an LLM,
admit a catalogue entry, draw a directional field, tune a parameter, package a
candidate, or enable Auto Suggest or execution.

The canonical founder packets remain blank. The audit answers only one question:
does a packet row represent one unambiguous exact astronomical pass?

## Current F2A compiler assumptions

`chart_conditioned_event_compiler.py` performs fast candidate discovery with a
body-specific sampling grid. For each transit body, natal target, and approved
aspect it:

1. finds samples inside the configured three-degree orb;
2. groups one contiguous inside-orb run into one candidate window;
3. bisects the outside-to-inside and inside-to-outside edges to refine applying
   and separating boundaries;
4. uses `_refine_exact`, a ternary minimum search over the whole run, to select
   one exact timestamp; and
5. hashes the immutable event seed: chart/hypothesis identity, named transit
   and natal bodies, aspect, the three timestamps, orb contract, astronomy
   contract, ayanamsha, node policy, and generator version.

The ternary search is valid only when the orb curve in that continuous run has
one usable minimum. F2A did not prove that condition. In particular, a
retrograde or station loop can keep a transit inside one orb window while
creating more than one exact pass or no exact pass at all.

## Independent verifier

`event_identity_audit.py` is deliberately separate from the production ternary
search. It uses the same allowed Swiss Ephemeris/Raman/true-node provider but a
different method:

1. builds exact-angle branches from the natal longitude, including correct
   circular treatment around 0/360 degrees;
2. scans every compiler window more densely than F2A discovery;
3. calculates signed angular residuals for each valid exact-angle branch;
4. refines every sign-bracketed root independently;
5. runs a separate golden-section local-minimum search to detect a station
   touch that does not cross a signed root;
6. numerically scans transit motion for direct/retrograde changes and station
   timestamps;
7. tests whether the orb moves monotonically toward one exact point and then
   away; and
8. reproduces the immutable F2A hash from its identity fields.

The verifier never calls `_refine_exact` as its evidence path.

### Fail-closed statuses

- `SINGLE_PASS_VERIFIED`: exactly one independently detected exact candidate,
  valid configured-orb boundaries, monotonic approach/recession, correct
  immutable hash, and accepted chart identity.
- `MULTI_PASS_EVENT_IDENTITY_UNRESOLVED`: more than one exact candidate, or a
  non-monotonic continuous run that cannot safely be treated as one pass.
- `BOUNDARY_VERIFICATION_FAILED`: no independently verified exact point,
  boundary mismatch, hash/identity mismatch, or another required check failed.

Unresolved or failed windows are not eligible for later founder-review
admission. They are not split, discarded silently, or converted into a
convenient exact timestamp.

## April 2025 audit results

Audit interval: `2025-04-01T00:00:00Z` through `2025-05-01T00:00:00Z`
(`2025-04-01 05:30 IST` through `2025-05-01 05:30 IST`).

| Side | Overlapping complete windows | Single pass verified | Multi-pass unresolved | Boundary verification failed | Exact moments inside April | Exact moments outside April while interval overlaps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| USD | 111 | 104 | 6 | 1 | 99 | 12 |
| JPY | 117 | 105 | 5 | 7 | 104 | 13 |

No incomplete search-horizon window overlaps the April founder pilot interval.
The full affected-event list, exact candidates, residuals, station/reversal
timestamps, boundary measurements, and hash checks live in
`status/audits/pfr_v2b_r5_f2a_r1_event_identity_integrity.json`.

Rahu/Ketu identities were checked separately. Geometry can be symmetric under
the true-node opposition, but the immutable identity includes the named transit
and natal bodies. No accidental duplicate event ID or event hash was found.

## Founder packet outcome

All 12 USD V1 rows and all 12 JPY V1 rows are `SINGLE_PASS_VERIFIED`. Therefore
the existing immutable V1 packets remain unchanged. No V2 replacement pack was
created.

Verification manifests:

- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json`

Non-authoritative readable renderings, still entirely blank for founder fields:

- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.md`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.md`

If a future audit finds a V1 row unresolved, the audit tool writes a V2 packet
only from the first twelve `SINGLE_PASS_VERIFIED` records ordered by
`exactUtc`, then `eventId`. It records every excluded V1 ID. Price, expected
polarity, SBC, LLM output, chart appearance, and prospective wave coverage are
explicitly prohibited selection inputs.

## Future event-family metadata proposal: not active

The following are engineering metadata for future founder approval. They are
not classical doctrine, financial meaning, or current production fields:

| Proposed field | Proposed deterministic definition | Status |
| --- | --- | --- |
| `eventFamilyId` | Stable hash of chart ID, hypothesis ID, named transit/natal pair, aspect type, orb-profile ID/hash, astronomy contract, and node policy; timestamps excluded. | Proposal only |
| `exactPassIndex` | One-based chronological index among independently verified exact candidates inside one audited continuous orb window. | Proposal only |
| `motionPhaseAtExact` | `DIRECT`, `RETROGRADE`, or `STATION` from the audit's numerical Swiss-Ephemeris motion probe. | Proposal only |
| `stationAssociation` | Explicit list of audited motion-reversal timestamps inside the continuous orb window. | Proposal only |
| `previousExactPassReference` / `nextExactPassReference` | Immutable references to the adjacent independently detected exact candidate when a founder-approved multi-pass identity convention exists. | Proposal only |

No production event contract changes, event re-hashing, catalogue admission, or
review-row classification result from this proposal. Founder approval is needed
before any such metadata is activated.

## Verification

Focused tests cover a simple direct pass, angular wrap, two-pass retrograde
geometry, three-pass station-loop geometry, station without exactness, exactness
near a range boundary, reproducible event hashes, and deterministic V2
replacement ordering. The audit output itself is regenerated from Swiss
Ephemeris and contains no market, SBC, LLM, polarity, or execution input.
