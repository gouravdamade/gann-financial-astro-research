# MO-R4A CONT-1 P1 Bounded Hidden-Premise Containment

Status: IMPLEMENTED_PENDING_CENTRAL_REVIEW
Starting branch: `research/mo-r4a-astra-a1-r2-final-audit-freeze`
Starting commit: `74a018a482d1ef95236ec036dd0719cee589ab35`
Implementation branch: `research/mo-r4a-cont-1-p1-bounded-containment`

## Scope

This record documents the bounded CONT-1 P1 containment implementation. It
does not reopen the Astra A1-R2 audit, add source doctrine, create a market
model, validate a forecast, or authorize execution. Candidate C scientific
closure and EMP3 authorization state are unchanged.

The four contained surfaces are:

1. an explicit-only experimental directional diagnostic;
2. missing and partial evidence states;
3. mandatory two-sided USD/JPY evidence completeness before pair direction;
4. separate Swiss Ephemeris UT identity and civil UTC display values for CGVO.

## Directional Diagnostic

Loading a family, changing the selected event, or changing the evidence cutoff
no longer invokes `/api/decisions`. The existing diagnostic route and scorer
remain available behind the explicit `Run diagnostic` command.

Before a run, the UI displays `EXPERIMENTAL`, `UNCERTIFIED`, `NOT
FORECAST-VALIDATED`, and `EXECUTION DISABLED`. After a run, the product-facing
result is `bullish`, `bearish`, or `abstain`; the historical `WATCH_LONG` or
`WATCH_SHORT` token remains an audit detail only. Diagnostic state is cleared
when the event or detail changes, so a prior event result cannot remain visible
for a newly selected event.

Live packets now carry additive guardrails:

```text
experimentalDirectionalDiagnostic = true
forecastValidated = false
directionCertification = UNCERTIFIED
executionAllowed = false
```

## Evidence States

The containment parser distinguishes `ABSENT`, `MALFORMED`, `VALID_EMPTY`, and
`VALID_NONEMPTY` without changing the legacy `safe_json_list` behavior.
Required side evidence is classified as:

| State | Meaning |
| --- | --- |
| `KNOWN` | Required factual fields are resolved and no conflict is present. |
| `MIXED` | Required factual fields are resolved and conflict is explicitly present. |
| `PARTIAL` | Some evidence exists but a required factual or scoring field is unresolved or malformed. |
| `UNKNOWN` | No sufficient usable evidence exists. |
| `BLOCKED_MAPPING` | The required side identity/reference mapping is absent. |

Finite zero evidence remains a real observed value. It is not converted to
missing evidence merely because the legacy scorer skips non-positive strength
for its hit total. Malformed, nonfinite, or absent mandatory fields remain
visible through state and reason fields.

Pair direction is eligible only when both sides are `KNOWN` or `MIXED`.
Otherwise the pair is `UNKNOWN`, `fx_pair_direction_eligible` is false, the
decision engine adds `pair_evidence_incomplete`, and the action is `ABSTAIN`.
`MIXED + KNOWN` and `KNOWN + MIXED` remain eligible for the existing frozen
scorer; no weights, thresholds, or formulas changed.

The inspector and source-first Fields panel expose side state and pair
eligibility so `PARTIAL`, `UNKNOWN`, and `BLOCKED_MAPPING` cannot look like a
resolved directional call.

## Drik and Shadbala Missingness

Missing Mercury longitude no longer implies observed-alone benefic Mercury.
Missing Sun or Moon phase inputs no longer manufacture a benefic lunar phase.
An aspector without longitude produces an unavailable contribution with null
numeric contribution fields and explicit unresolved coverage rather than a
numeric-looking zero.

Drik results expose `coverage_state`, expected and known contributor counts,
and unresolved contributors. Saptavargaja exposes required/known varga counts
and is not complete when a constituent is unresolved. Yuddha missing candidate
data remains unresolved rather than being interpreted as observed no-war.
`AVG(ALL)` exposes population coverage. Fully populated fixture calculations
retain their existing numeric values; the focused exact-value tests remain
green.

## Fields Dignity

The Fields frontend no longer sends `dignity: ORDINARY` by default. Chakra
actor selection accepts omitted dignity, and the backend preserves omission.
Readiness reports `DIGNITY_REQUIRED` with `dignityStatus: UNSPECIFIED` when a
selected routine requires a factual dignity that was not supplied. An explicit
caller-provided `ORDINARY` remains a valid explicit value.

## CGVO Identity and Display

The Swiss Ephemeris UT Julian-day values remain the source for the immutable
`globalMaxSwissUt`, identity hash, and `causalEventId`. The legacy
`globalMaxUtc` and `globalContacts` aliases remain readable but are labelled as
Swiss-UT compatibility aliases.

The new display fields use the original Julian-day values and
`swe.jdut1_to_utc(...)`:

- `globalMaxUtcDisplay` is civil UTC display time;
- `globalContactsSwissUt` preserves identity/calendar representations;
- `globalContactsUtcDisplay` is separately converted civil UTC display;
- metadata declares `identityTimeScale: SWISSEPH_UT` and
  `displayTimeScale: UTC`.

The frontend renders Swiss UT identity without appending a false UTC label.
Older payloads without display fields remain readable and are explicitly shown
as legacy Swiss-UT aliases rather than newly certified civil UTC.

## Frozen Evidence Integrity

The A1-R2 audit files and report were compared before and after implementation.
Their SHA-256 values remained unchanged:

| Artifact | SHA-256 |
| --- | --- |
| `docs/research/MO_R4A_ASTRA_A1_R2_FINAL_BOUNDED_COVERAGE_CLOSURE.md` | `A43A9F216A45260CB00E419386C462CD477FEB4FBD88EE69F7CDC074485A9D00` |
| `status/audits/mo_r4a_astra_a1_r2_active_path_and_missingness.json` | `E9260E8A74006FFE8D00B2BE82492B30A781F6923C99CDBBC4B29F41EA6B95F5` |
| `status/audits/mo_r4a_astra_a1_r2_coverage_manifest.json` | `067DA1EA6754735DF251965DFAF0171ACACCE2B6DB957DE957C65B4B5328BAFB` |
| `status/audits/mo_r4a_astra_a1_r2_dependency_graph.json` | `EFC29C23C94714F96FD5799866D2D0188083AC2F8F143E0B79D2C67AE22009B6` |
| `status/audits/mo_r4a_astra_a1_r2_final_audit_freeze.json` | `A436223E73FE48818B85FC8FBEE1BBB0DC09D33B0F9CB4847A98143BD7A5E327` |
| `status/audits/mo_r4a_astra_a1_r2_high_impact_numeric_classification.json` | `AA69EF53414EC6CA44EEFFC88DE4C33708FCCA7B80FE56B36C68B27A3544ED2E` |
| `status/audits/mo_r4a_astra_a1_r2_historical_branch_review.json` | `B4556DBAA7285CD8181F99E2E881FCD5FA3B9A9FDEFC15C19937B4BECB4047E8` |
| `status/audits/mo_r4a_astra_a1_r2_master_assumption_ledger.json` | `1A0A91471F485F9E2F09547A0079E7E007C0F7E73117E12D83DA54C688E4D4EB` |
| `status/audits/mo_r4a_astra_a1_r2_source_witness_manifest.json` | `C1498F097D6A399FBEEEDC9117B9A14F824ACE572EC4DE568BF676609A655CBE` |
| `status/audits/mo_r4a_astra_a1_r2_summary.json` | `D91FFE35EBCE6BE963573B0BE740C2A6F38B7905AE85495D7877994CAB4490EE` |
| `status/audits/mo_r4a_astra_a1_r2_test_assumption_mapping.json` | `99A175FBD40F02D1EBE1CBA88F8BC1B9154CC8A74C01AA56C8E6F2B56EFA8423` |

The key Candidate C preregistration, population, EMP2 result/closure, and
Astra post-outcome audit files were also hash-checked and unchanged. No source
audit bytes were rewritten.

## Verification

Focused Python coverage: `57 passed`.
Focused backend unittest coverage: `66 passed`.
Frontend: `44` files, `203 passed`.
TypeScript and Vite production build: passed.
Oxlint: passed.
`git diff --check`: passed.

The full repository pytest command was attempted. It stops during collection
at the pre-existing immutable Candidate C Evaluator B raw source-ledger hash
mismatch (`expected 4C7D0C4C1A366287A05DD70E9638A27585516240B24C3AEEBFA91889F22E86E8`,
`got 979B194E5045B104E3DB3CC203B46AC62C65BE541DB993C3F7CA0C2B2303BE3F`). The
mismatch is outside this branch's changes and was not repaired. A broad
non-Evaluator-B run was allowed to continue through data-heavy tests but was
stopped after the bounded regression evidence was established; no additional
source or result artifact was modified.

No provider, market, outcome, or empirical execution path was accessed by this
milestone. The product locks remain:

```text
providerAccessed = false
marketDataAccessed = false
outcomeAnalysisPerformed = false
empiricalExecutionPerformed = false
mt5Invoked = false
executionAllowed = false
automaticOrderPlacement = false
EMP3 = unauthorized
```

Next gate: `CENTRAL_REVIEW_MO_R4A_CONT_1_P1_BOUNDED_CONTAINMENT`.
