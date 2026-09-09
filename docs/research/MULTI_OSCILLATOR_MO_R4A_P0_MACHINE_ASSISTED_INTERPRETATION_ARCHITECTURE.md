# MO-R4A-P0 Machine-Assisted Interpretation Architecture

## Purpose

MO-R4A-P0 corrects the pilot workflow before any real April 2025 founder
decision was entered. The founder remains the product owner,
research-governance authority, source/witness approver, experimental-hypothesis
approver, usability judge, and final freeze/analysis authority. The founder is
no longer required to act as the astrology calculation engine.

The historical Founder Review workbench, append-only revision store, source
reference structure, and `FOUNDER_POLARITY_REVIEW_FREEZE_V1` verifier remain
valid infrastructure. This milestone does not rewrite their history, migrate
data, execute a freeze, or alter the accepted `0.10.64-pfr-v2b-mo-r3-r2-f1-r1`
candidate.

## Evidence-Bound Audit

| Surface | Current evidence | MO-R4A-P0 disposition |
| --- | --- | --- |
| Founder Review | `gann-astro-desk/backend/founder_review_workbench.py` verifies blank packet, manifest, and event-identity audit before durable review export. | Preserved; not read or written by this milestone. |
| Founder freeze | `gann-astro-desk/backend/founder_review_freeze.py` is a separately invoked, future-only verifier. | Preserved; no real freeze is created. A future machine contract must not silently reuse it. |
| Production polarity catalogue | `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_catalogue_v1.json` has `NO_ACCEPTED_PRODUCTION_ENTRIES`. | Unchanged and not consumed by the new interpreter. |
| Reviewed evidence registry | `research_labs/chart_conditioned_aspects/profiles/target_aware_polarity_evidence_packets_v1.json` has `NO_REVIEWED_PACKETS`. | Unchanged and not consumed by the new interpreter. |
| MO-P2/P3 activity | `gann-astro-desk/backend/multi_oscillator_activity_service.py` exposes `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` in `EXPLORATORY_UNSIGNED` mode. | Unchanged. Raw activity is not a sign, magnitude, score, or pair result. |
| Source-profile work | Existing Trailokya and SBC source adapters contain source-specific facts and explicit unresolved dependencies. | Kept separate. No existing committed contract closes an event-bound source operator for the 24 canonical April identities. |
| Fields explanation surface | Fields can display unsigned activity and independent source profiles. | No UI or Fields behavior changes in this milestone. |
| Accepted candidate | `status/acceptance/mo_r4_p0_founder_acceptance.json` preserves the `0.10.64` release hashes. | Read only by regression assertions; the candidate is not rebuilt or modified. |

The source/operator conclusion is deliberately narrow: existing source research
is not treated as a universal astrology-to-currency function. A source operator
can only be used after an explicit versioned contract closes its inputs,
doctrine, precedence, and scope for the event in question.

## Protocol Supersession

The authoritative machine-readable state is
`status/acceptance/mo_r4a_p0_machine_assisted_interpretation_protocol.json`.
It records:

- `FOUNDER_MANUAL_ASTROLOGY_POLARITY_AUTHORSHIP = SUPERSEDED_BEFORE_FIRST_REAL_DECISION`;
- the replacement pilot: `BLINDED_MACHINE_ASSISTED_INTERPRETATION`;
- zero real founder decisions, classifications, and source references at
  supersession;
- `OUTCOME_DATA_READ = false`;
- signed USD, JPY, and USDJPY runtimes as `NOT_AUTHORIZED`; and
- a design-only future contract name,
  `MACHINE_ASSISTED_POLARITY_HYPOTHESIS_FREEZE_V1`, which does not repurpose the
  historical Founder Review freeze schema.

## Layered Contract

`gann-astro-desk/backend/machine_assisted_interpretation.py` and
`configs/research/machine_interpretation/machine_assisted_astrological_interpretation_v1.schema.json`
define a typed, provenance-first packet. The layers are intentionally not
collapsed into a score.

| Layer | Contract object | Permitted role | Explicit non-role |
| --- | --- | --- | --- |
| Astronomy fact | `eventIdentity` | Identifies an interval, chart, bodies, and aspect. | Does not imply astrology or currency direction. |
| Source doctrine | `SourceOperatorEvidence` | Carries a versioned operator ID, exact locators, source status, literal measurement, and unresolved dependencies. | A bare benefic/malefic label, drishti geometry, or bala value cannot create currency pressure. |
| Astrology interpretation | `AstrologyInterpretation` | Holds `SUPPORTIVE_ASTRO_STATE`, `ADVERSE_ASTRO_STATE`, `MIXED_ASTRO_STATE`, `NEUTRAL_ASTRO_STATE`, or `UNKNOWN_ASTRO_STATE`. | Does not itself create a market sign. |
| Market bridge | `MarketBridge` | States whether a bridge is source-backed, a versioned experimental hypothesis, or absent. | An experimental bridge can never masquerade as `SOURCE_CERTIFIED`. |
| Currency-side state | `CurrencySideInterpretation` | Carries only a categorical state with `signedUnit = null`. | No signed active-event unit, magnitude, or pair resultant is produced. |
| Explanation | `PlainLanguageExplanation` | Explains what is known, what is experimental, and what remains unknown. | Does not forecast, recommend a trade, or hide missing dependencies. |

The current callable interpreter accepts only explicitly synthetic identities
whose ID begins `SYNTHETIC_`. This prevents a test fixture from being pointed at
a real canonical April row. Real identities have a separate, identity-only
coverage path described below.

## Modes

The three conceptual modes remain distinct from existing Fields visualization
labels.

| Mode | Allowed | Disallowed |
| --- | --- | --- |
| `SOURCE_CERTIFIED` | Source-closed astrology operator facts. | Experimental market hypotheses, unsigned facts becoming a currency sign, or a source-certified financial forecast without a source-backed bridge. |
| `EXPERIMENTAL_PROFILED` | A versioned, exact-input, approved blinded-test bridge. | Financial validation claims, a signed unit, magnitude, or a post-hoc rule. |
| `EXPLORATORY_UNSIGNED` | Unsigned source facts, unresolved operators, and raw activity. | Currency direction, a signed side wave, or a pair resultant. |

## Experimental Hypothesis Registry

`configs/research/machine_interpretation/experimental_market_hypothesis_registry_v1.json`
is intentionally empty. Its schema requires a hypothesis ID, version, author,
UTC creation time, exact source operator IDs, target side, categorical output,
source dependencies, experimental assumptions, prohibited generalizations,
approval status, validation status, and a deterministic hash over
decision-bearing content.

The registry does not contain a global sign table. It has no real
astrology-to-FX rule, reads no market data, and cannot create a signed unit,
magnitude, pair resultant, catalogue admission, evidence admission, Auto
Suggest path, ML path, MT5 path, or executable output.

## Real 24-Identity Dry Run

`status/audits/mo_r4a_p0_real_24_identity_only_coverage.json` is derived by a
read-only verifier from the immutable blank packets, their identity manifests,
and the accepted event-identity audit. It verifies packet/manifest hashes,
side bindings, the underlying audit contract/version, `SINGLE_PASS_VERIFIED`
records, and the applying/exact/separating ordering.

The verifier does not accept a review-store path and does not inspect founder
review fields. It reads no price, return, candle, PnL, market outcome, SBC
interpretation, or source-derived sign. The result is exactly 12 USD and 12
JPY canonical identities. Every row presently has:

- `SOURCE_OPERATOR_COVERAGE = OPERATOR_NOT_YET_AVAILABLE`;
- `UNRESOLVED_OPERATOR_COUNT = 1` for
  `NO_EVENT_BOUND_SOURCE_OPERATOR_CONTRACT`;
- `MARKET_BRIDGE_STATUS = NO_AUTHORIZED_MARKET_BRIDGE`;
- `CURRENT_DIRECTION_STATUS = UNKNOWN_MORE_EVIDENCE_REQUIRED`; and
- `MAGNITUDE_NOT_CONFIGURED` in `EXPLORATORY_UNSIGNED` mode.

That is a useful, honest pilot baseline: the event universe is integrity-bound,
but source/operator and bridge population have not begun.

## Boundary Locks

MO-R4A-P0 does not add or change any of the following:

- real founder decisions, review exports, classifications, or source references;
- production catalogue or reviewed-evidence admissions;
- price, outcome, return, candle, PnL, backtest, or market-reaction reads;
- SBC interpretation;
- signed USD/JPY waves, `W_USDJPY`, pair transforms, magnitude,
  normalization, smoothing, or kernels;
- Auto Suggest, LLM interpretation, ML, MT5, orders, or execution; or
- the accepted `0.10.64` candidate and its immutable resource-tree hash.

`executionAllowed` remains `false` throughout this architecture.

## Next Authorized Direction

The next central source step may admit a versioned source/operator contract
only after the relevant Brhat Jataka, Saravali, BPHS, or Trailokya evidence
closes its exact inputs, scope, conflict handling, and unresolved states. A
separate directive would then be required to define the first explicit blinded
experimental market hypothesis. Neither step is performed here.
