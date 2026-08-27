# Multi Oscillator MO-R2 Polarity Admission Readiness

Status: `READINESS_AUDIT_COMPLETE_NO_SIGN_ADMISSIONS`

Audit date: `2026-08-27`

Starting documentation baseline: `c5e0cfa5401ad9be2403f495f2353024122c9738`

## Scope

This is a documentation-only audit of the existing target-aware polarity
catalogue, reviewed-evidence registry, April 2025 founder-review packets,
identity manifests and admission-preparation contract. It makes no runtime,
API, Python, TypeScript, Rust, polarity-catalogue, reviewed-evidence, package
or Windows candidate change.

The accepted MO-P3A unsigned baseline remains
`0.10.61-pfr-v2b-mo-p3a-f1`. It remains unsigned, non-predictive and execution
locked.

## Current Admission State

| Item | Current state | Audit result |
| --- | --- | --- |
| Target-aware polarity catalogue | `NO_ACCEPTED_PRODUCTION_ENTRIES` | `0` accepted entries |
| Reviewed-evidence packet registry | `NO_REVIEWED_PACKETS` | `0` registered reviewed packets |
| USD reviewed export | `REVIEW_NOT_STARTED` | 12 eligible, 12 incomplete |
| JPY reviewed export | `REVIEW_NOT_STARTED` | 12 eligible, 12 incomplete |
| Catalogue admission validator | `PREPARED_NOT_RUN_NOT_CONNECTED_TO_CATALOGUE` | Not activated |

`SOURCE_BACKED_SIGN_ADMISSIONS_READY=0`.

No currently held source record maps a specific accepted USD or JPY
transit-to-natal event identity to a financial `SUPPORTIVE` or `ADVERSE`
contribution. A planet name, a natural planet classification, an aspect shape,
or a price movement is not a replacement for that missing source mapping.

## Verified Pilot Inventory

The bounded founder-review universe is the non-outcome-selected April 2025
window:

```text
UTC: 2025-04-01T00:00:00Z through 2025-05-01T00:00:00Z
IST: 2025-04-01 05:30 through 2025-05-01 05:30
```

| Side | Accepted chart identity | Hypothesis identity | Valid events in window | Pilot rows |
| --- | --- | --- | ---: | ---: |
| USD | `FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1` | `USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1` | 99 | 12 |
| JPY | `FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1` | `JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1` | 104 | 12 |

The 24 pilot rows are the first 12 complete identities per side ordered by
`exactUtc` and event ID. They were not selected using price movement, later
outcomes, SBC, expected polarity or LLM preference.

All 12 USD and all 12 JPY rows are `SINGLE_PASS_VERIFIED`. Each carries a
deterministic event ID and hash, side and instrument identity, accepted chart
and hypothesis ID, transit body, natal target, aspect, applying/exact/separating
UTC bounds, orb contract, node policy, astronomy contract, ephemeris version,
ayanamsha and generator version.

The immutable/read-only identity inputs are:

- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- the corresponding `.identity_integrity.manifest.json` files.

The current reviewed exports are identity-bound and content-hashed, but are
not yet frozen admitted evidence packets: a later founder export may replace
them before an admission record is made. The future admission process must bind
the chosen reviewed-export hash as well as the original blank-packet and
integrity-manifest hashes.

## Outcome-Leakage Audit

The packet generation metadata is `nonOutcomeSelected=true`, `priceRead=false`,
`sbcRead=false` and `llmUsed=false`. Packet rows contain astronomy and identity
facts only; they do not contain candles, returns, P/L, later price movement,
SBC state or AI interpretation. The review-workbench contract explicitly hides
market-facing information and starts every decision and classification field
blank.

Result: `OUTCOME_LEAKAGE_AUDIT=PASS_FOR_CURRENT_PACKET_PAYLOAD_AND_WORKBENCH_CONTRACT`.

This is not financial validation. It records only that the current review input
is structurally outcome-blind. No price or outcome read was added by this
audit.

## Evidence Classes and Founder Decisions

Allowed founder decisions remain:

```text
SUPPORTIVE
ADVERSE
MIXED
NEUTRAL
UNKNOWN_MORE_EVIDENCE_REQUIRED
REJECT_EVENT_IDENTITY
```

Every non-rejected row must also have exactly one evidence class:

| Evidence class | Future permitted location | Required conditions |
| --- | --- | --- |
| `SOURCE_BACKED_CLASSICAL_CANDIDATE` | Pending a separate Mode 2-to-Mode 1 promotion gate | Exact source ID, edition, page/verse/chapter/table locator and an explanation linking that source to this exact event identity |
| `FOUNDER_RESEARCH_HYPOTHESIS` | A separately versioned Calibrated Research profile only | Founder decision, reasoning, reviewer, UTC timestamp, exact reviewed/export hashes and outcome-blind declaration |

`UNKNOWN_MORE_EVIDENCE_REQUIRED` remains an unknown gap; it is never changed to
neutral. `MIXED` must retain supportive and adverse component activity and
conflict metadata. `REJECT_EVENT_IDENTITY` requires a reason and can never
become a catalogue entry.

No founder polarity decision has been made in this audit.

## Proposed Future Admission Record

This is a documentation-only proposal. It is not a new runtime schema and it
does not admit an event.

```text
ContributionPolarityReviewRecordV1
  recordId
  sideIdentity
  instrumentIdentity
  eventId
  eventHash
  chartId
  chartHypothesisId
  transitBody
  natalTarget
  aspectType
  applyingStartUtc
  exactUtc
  separatingEndUtc
  astronomyContract
  orbContract
  identityStatus = SINGLE_PASS_VERIFIED
  blankPacketId
  blankPacketHash
  identityIntegrityManifestId
  identityIntegrityManifestHash
  reviewedPacketHash
  founderDecision
  evidenceClassification
  sourceReferences[]
  founderReasoning
  reviewer
  reviewedAtUtc
  outcomeBlindDeclaration = true
  priceOrOutcomeRead = false
  admissionState
```

For `SOURCE_BACKED_CLASSICAL_CANDIDATE`, `sourceReferences[]` must be non-empty
and exact. For `FOUNDER_RESEARCH_HYPOTHESIS`, the record remains explicitly
non-classical and financially unvalidated. In both cases, all astronomy identity
fields must reproduce exactly from the blank packet and integrity manifest.

## Future-Only Signed Activity Contract

No signed activity is implemented or rendered. If a future separately approved
admission milestone supplies a valid sign record, its initial categorical
contribution contract is proposed as:

```text
s_i in {+1, -1}
a_i(t) = 1 on [applyingStartUtc, separatingEndUtc), otherwise 0
W_side(t) = sum_i s_i * a_i(t)
```

`SUPPORTIVE` maps to `+1`; `ADVERSE` maps to `-1`. This is one signed active
event unit, not a magnitude. It has no kernel, weighting, smoothing,
interpolation, amplitude calibration or normalization. The proposed interval is
the existing half-open applying-to-separating span only.

`MAGNITUDE_NOT_CONFIGURED` remains true. No sign contribution may be inferred
from an unsigned event count, geometry, body name, aspect label, price outcome,
SBC, Shadbala, Drik Bala, Ashtakavarga or LLM text.

## Unknown, Conflict and Pair Gates

Future signed compilation must preserve these non-numeric states:

| State | Required behavior |
| --- | --- |
| `UNKNOWN_SOURCE_ABSENT` | Visible gap; do not substitute zero |
| `UNKNOWN_COMPILER_COVERAGE` | Visible gap while preserving observed activity separately |
| `FOUNDER_REVIEW_REQUIRED` | Visible gap until a valid founder decision is admitted |
| `CONFLICT_SOURCE_PROFILES` | Preserve competing components and conflict; do not vote or average |
| `MIXED` | Preserve supportive count, adverse count, gross activity and conflict |
| `REJECT_EVENT_IDENTITY` | Exclude from admission and retain audit reason |

An FX pair-relative signed field is blocked. It can be considered only after
both independently compiled side fields are compatible and known for the same
canonical interval. Its future-only form would be:

```text
pairRaw = baseSignedActivity - quoteSignedActivity
pairDisplay = clamp(pairRaw / 2, -1, +1)
```

For USDJPY, USD is base and JPY is quote. If either side is unknown or in an
unresolved conflict, `pairDisplay=null` with `UNKNOWN_SIDE_EVIDENCE`. SBC is
not an input to that calculation and cannot confirm it.

## Mode Boundaries

| Mode | Current MO-R2 position |
| --- | --- |
| `SOURCE_ONLY_BASELINE` | No side sign appears automatically. A source-backed candidate still requires its separate promotion gate. |
| `CALIBRATED_RESEARCH` | No signed record currently exists. A founder-research hypothesis could appear only after explicit founder decision, integrity-bound admission and separate implementation authorization. |
| `VISUAL_ONLY_NO_SCORE` | Remains unsigned geometry/activity only; directional fields remain suppressed. |

There is no Mode 1 admission, Mode 2 signed wave, pair resultant, price
conversion or execution path in the current product.

## Readiness Decision

| Decision | Result |
| --- | --- |
| Source-backed sign admissions ready | `0` |
| Existing founder-review identity infrastructure | `READY_FOR_FOUNDER_DECISION` |
| Existing review decisions | `0`; all 24 are blank |
| Founder-research sign pilot | `NOT_STARTED` |
| Runtime sign implementation | `BLOCKED` |
| Pair-relative signed field | `BLOCKED` |
| Magnitude, kernel and normalization | `NOT_CONFIGURED` |

## Required Founder Decision

The recommended next step is one of two mutually exclusive paths:

1. **Founder polarity review pilot.** Use the existing outcome-blind 24-row
   USD/JPY packet set. The founder makes every individual decision in the
   existing Founder Review workbench and explicitly classifies each reviewed
   row as a `FOUNDER_RESEARCH_HYPOTHESIS` or a source-backed candidate with
   exact source references. Codex must not supply decisions.
2. **Source-evidence closure first.** Keep all rows blank and seek exact source
   locators that map a particular chart-conditioned event identity to a sign.
   This is the only path that could later pursue Source Only/Mode 1 promotion.

Given the audit, the practical next milestone is a **bounded founder polarity
review pilot**, not a sign-wave implementation: the 24 identities are complete
and outcome-blind, while source-backed sign admissions remain zero. That
recommendation does not authorize reviewing, admission or runtime work by
itself.

## Locks Preserved

This audit did not change and does not authorize:

```text
NO POLARITY ADMISSION
NO SIGNED WAVE
NO PAIR RESULTANT
NO MAGNITUDE
NO NORMALIZATION
NO SMOOTHING
NO PRICE OR OUTCOME READ
NO SBC, CGVO OR BPHS FUSION
NO LLM OR ML INFERENCE
NO AUTO SUGGEST
NO MT5 SIGNAL OR ORDER LOGIC
executionAllowed = false
```
