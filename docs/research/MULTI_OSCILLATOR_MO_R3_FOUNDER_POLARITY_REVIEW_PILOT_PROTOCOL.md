# Multi Oscillator MO-R3 Founder Polarity Review Pilot Protocol

Status: `FROZEN_PROTOCOL_REVIEW_INFRASTRUCTURE_GAP`

Protocol date: `2026-08-27`

Governing documentation baseline: `d3b5162725f68467af05f4b1e9120622413147c0`

## Purpose

MO-R3 freezes the protocol for a small founder-only, outcome-blind polarity
review pilot. It does not classify an event, admit a catalogue record, produce
a signed side wave, produce a pair resultant, inspect price outcomes or change
runtime code.

The scientific question is what the founder records before seeing the market
outcome, not what sign would make a later USDJPY chart look persuasive.

## Frozen Event Universe

The only eligible pilot universe is the existing April 2025 selection:

```text
UTC: 2025-04-01T00:00:00Z through 2025-05-01T00:00:00Z
Selection: first 12 complete verified identities per side, exactUtc/eventId order
USD: 12 rows from 99 valid events in the window
JPY: 12 rows from 104 valid events in the window
Total: 24 rows
```

No new event may be selected. No existing event may be reordered, replaced or
excluded because of perceived astrological quality, convenience, a future price
movement or desired wave coverage.

The source identity files are read-only:

- `research_labs/chart_conditioned_aspects/founder_review/USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- `research_labs/chart_conditioned_aspects/founder_review/JPY_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json`
- the corresponding identity-integrity manifests.

## Identity Audit

All 24 candidate rows are currently `SINGLE_PASS_VERIFIED` and have unique
event IDs and hashes. The audit confirmed presence of side and instrument
identity, chart and chart-hypothesis identity, transit body, natal target,
aspect type, applying/exact/separating UTC bounds, orb contract, node policy,
astronomy contract, ayanamsha and generator version.

There is one provenance gap: `ephemerisVersion` is absent from every stored
event identity, for all 12 USD and 12 JPY rows. It must not be reconstructed
from `generatorVersion`, inferred from a local installation, or entered by the
founder. A separately authorized identity-safe metadata correction must supply
and reverify it before this pilot starts.

| Identity status | USD | JPY | Total |
| --- | ---: | ---: | ---: |
| `SINGLE_PASS_VERIFIED` | 12 | 12 | 24 |
| Rows missing explicit `ephemerisVersion` | 12 | 12 | 24 |
| Other required identity-field omissions found | 0 | 0 | 0 |

## Outcome-Blind Firewall

The review may use only the immutable event identity and approved source/evidence
material. It must not expose or consult:

- USDJPY candles, price levels, returns, P/L or later movement;
- technical indicators, backtests or forecast scores;
- SBC, CGVO or BPHS results;
- existing pair-relative directional field output;
- MT5 price reaction or execution state;
- LLM or ML sign suggestions;
- internet commentary about the event outcome.

Before the first decision, the pilot-level declaration is:

```text
outcomeBlindDeclaration = true
priceOrOutcomeRead = false
sbcRead = false
llmDecisionUsed = false
mlDecisionUsed = false
```

The existing packet metadata and workbench guards are structurally
outcome-blind: `priceDataRead=false`, `sbcRead=false`, `llmRead=false`, no
catalogue admission and no directional wave. This does not itself prove a
person did not look elsewhere; the founder makes the declaration above.

## Allowed Decisions

The only permitted founder decisions are:

```text
SUPPORTIVE
ADVERSE
NEUTRAL
MIXED
UNKNOWN_MORE_EVIDENCE_REQUIRED
REJECT_EVENT_IDENTITY
```

Only `SUPPORTIVE` and `ADVERSE` could eventually become numeric sign
contributions, and only after a separate admission and implementation
authorization:

```text
SUPPORTIVE -> +1
ADVERSE    -> -1
```

`NEUTRAL` is an explicit finding, not missing evidence or a non-event.
`MIXED` retains supportive and adverse considerations, gross activity and
conflict; it is never converted to zero. `UNKNOWN_MORE_EVIDENCE_REQUIRED`
remains an evidence gap and is encouraged when a defensible outcome-blind sign
does not exist. `REJECT_EVENT_IDENTITY` is only for an identity defect, requires
a reason, and cannot contribute unless separately repaired, reverified and
reviewed.

No completeness target exists. A valid pilot may end with zero sign-eligible
records.

## Evidence Classes and Reasoning

Every non-rejected decision requires exactly one class:

| Class | Protocol meaning |
| --- | --- |
| `FOUNDER_RESEARCH_HYPOTHESIS` | Experimental, non-classical, non-financially-validated and future Mode 2 research only. It cannot enter Source Only/Mode 1. |
| `SOURCE_BACKED_CLASSICAL_CANDIDATE` | Requires source ID, title, edition/witness, author/tradition where applicable, exact page/verse/chapter/table locator, proposition, scope/conditions and an explanation that maps the source to this exact side, chart, natal target, transit-to-natal relation and sign. It is still not automatically Mode 1. |

Every `SUPPORTIVE` or `ADVERSE` decision requires concise founder reasoning
that explains the sign for this exact side/chart/target without using market
outcome. It is not a request for a long essay.

Codex must never fill, suggest, rank or default a decision. No LLM-generated
sign, autocomplete, planet-name heuristic or aspect-shape heuristic is allowed.

## No Generalization

The pilot decisions are event-specific frozen research hypotheses. A decision
on one event does not establish a reusable rule for another occurrence with the
same bodies or aspect. Any later mapping such as
`(transitBody, natalTarget, aspectType, side) -> sign` requires a separately
preregistered generalization contract with scope, retained/ignored identity
fields, evidence basis, conflict handling and validation design.

## Reviewed Record Contract

This is a protocol-only proposed record. It does not change the existing export
schema or create an admission.

```text
ContributionPolarityReviewRecordV1
  recordId, recordHash, pilotId, pilotVersion
  sideIdentity, instrumentIdentity
  eventId, eventHash, chartId, chartHypothesisId
  transitBody, natalTarget, aspectType
  applyingStartUtc, exactUtc, separatingEndUtc
  astronomyContract, orbContract, generatorVersion, ephemerisVersion
  identityStatus
  blankPacketId, blankPacketHash
  identityIntegrityManifestId, identityIntegrityManifestHash
  founderDecision, evidenceClassification, sourceReferences[]
  founderReasoning, reviewer, reviewedAtUtc
  outcomeBlindDeclaration, priceOrOutcomeRead, sbcRead
  llmDecisionUsed, mlDecisionUsed
  admissionState, futureContributionEligibility
```

Before anyone inspects price outcomes, a completed reviewed packet must be
frozen with its packet ID/version/content hash, per-side reviewed-export hash,
original blank-packet hash, integrity-manifest hash, completion timestamp,
reviewer identity label and pilot-level outcome-blind declaration.

## Future-Only Eligibility and Mathematics

Future eligibility is not current admission:

| Reviewed state | Future eligibility |
| --- | --- |
| `SUPPORTIVE` or `ADVERSE` plus valid `FOUNDER_RESEARCH_HYPOTHESIS` | Could be considered only for a separately authorized Mode 2 sign-only profile |
| `SOURCE_BACKED_CLASSICAL_CANDIDATE` | Still requires a separate source-certification/promotion gate |
| `NEUTRAL` | No signed contribution; retain provenance |
| `MIXED` | Not reducible to one sign |
| `UNKNOWN_MORE_EVIDENCE_REQUIRED` | No signed contribution; visible evidence gap |
| `REJECT_EVENT_IDENTITY` | Excluded |

No signed wave is implemented. Its future side contract is only:

```text
a_i(t) = 1 for applyingStartUtc <= t < separatingEndUtc, otherwise 0
W_side(t) = sum_i s_i * a_i(t)
```

Unit: `SIGNED_ACTIVE_EVENT_COUNT`, meaning net signed activity count, not
strength, probability, confidence, expected return or forecast magnitude.

The future pair contract is raw subtraction only:

```text
W_BASEQUOTE(t) = W_BASE(t) - W_QUOTE(t)
W_USDJPY(t) = W_USD(t) - W_JPY(t)
```

No normalization, clamp, scaling to `[-1,+1]`, smoothing, kernel beyond
`RECTANGULAR_ACTIVITY_PRESENCE_ONLY`, weighting or magnitude is configured.
Both sides must be known and conflict-free on the same canonical interval. Any
unknown or conflict produces `UNKNOWN_SIDE_EVIDENCE`, not a zero substitution.

The existing categorical `FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1` is a separate
engineering contract and is unaffected by this raw signed-pair protocol.

## Mode Boundaries

- `SOURCE_ONLY_BASELINE`: no founder or source candidate enters automatically.
- `CALIBRATED_RESEARCH`: a founder-research hypothesis could appear only after
  an explicit future admission and implementation authorization.
- `VISUAL_ONLY_NO_SCORE`: stays unsigned; directional paths are suppressed.

No source-backed or founder-research admission is created by this protocol.

## Founder Review UI Audit

Result: `FOUNDER_REVIEW_UI_GAP`.

The existing navigation is **Fields -> Founder Review**. It safely displays
neutral astronomy facts, UTC/IST timestamps, chart identities, event hash,
astronomy/orb facts and `SINGLE_PASS_VERIFIED` status. It exposes all permitted
decision values, both evidence classes, source-reference fields, rejection
reason, reviewer and export-generated UTC timestamp. It hides price, SBC, LLM,
catalogue admission, directional wave and execution data.

However, it does not yet satisfy this frozen protocol because:

1. The visible founder-reasoning field says `Optional founder reasoning`.
2. The export validator accepts blank `founderReasoning` for `SUPPORTIVE` and
   `ADVERSE` decisions.
3. The 24 stored event identities lack the required `ephemerisVersion` field.

Do not begin review until a separately authorized correction enforces required
reasoning for `SUPPORTIVE`/`ADVERSE`, adds/reverifies the missing immutable
ephemeris provenance, and is independently checked against all 24 identities.

## Founder Workflow After the Gaps Are Repaired

1. Open **Fields**, then **Founder Review**.
2. Confirm the fixed USD April 2025 packet and its integrity status.
3. Read the first event identity and approved evidence only; do not inspect a
   market outcome.
4. Choose exactly one allowed decision, or leave it blank.
5. For `SUPPORTIVE`/`ADVERSE`, enter concise founder reasoning.
6. For every non-rejected decision, choose its evidence class.
7. For `SOURCE_BACKED_CLASSICAL_CANDIDATE`, provide all exact source locators
   and the connection to this event.
8. Save the review state; do not alter event identity fields.
9. Continue in canonical USD order, then canonical JPY order.
10. Stop after the 24th row. Do not inspect outcomes.
11. Ask Codex only to verify and freeze/hash the completed packet. Codex must
    not make or suggest any founder decision.

## Stop Gate

```text
NO FOUNDER DECISIONS CREATED
NO CATALOGUE ADMISSIONS CREATED
NO REVIEWED-REGISTRY ADMISSIONS CREATED
NO SIGNED WAVES CREATED
NO PAIR RESULTANT CREATED
NO MAGNITUDE OR KERNEL ADDED
NO NORMALIZATION ADDED
NO PRICE OR OUTCOME READ
NO PACKAGE CREATED
executionAllowed = false
```

This protocol stops at the documented gaps. It does not start MO-P3B, MO-P4,
outcome validation, backtesting, magnitude research, kernel research or
normalization research.
