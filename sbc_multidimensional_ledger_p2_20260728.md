# SBC Multidimensional Ledger P2

Date: 2026-07-28

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

Status: implemented in source, research-only, execution-locked

## Purpose

P2 adds a versioned multidimensional evidence ledger over the timestamp-safe
Phase 5A atomic intervals. It answers a narrow question: can the same
source-backed SBC evidence be inspected by actor, target layer, nature,
figure-relative Vedha direction, and source lineage without multiplying that
evidence into extra votes?

The answer is now enforced by stable causal-cluster identities and full
reconciliation.

## Contracts

- series: `SBC_MULTIDIMENSIONAL_LEDGER_SERIES_V1`
- causal cluster: `SBC_CAUSAL_CLUSTER_V1`
- dimension cell: `SBC_LEDGER_DIMENSION_CELL_V1`
- missing-evidence lineage: `SBC_MISSING_EVIDENCE_LINEAGE_V1`
- classification: `SOURCE_PROFILED_EXPERIMENTAL`

The exact role vocabulary is:

- `PRIMARY_EVIDENCE`
- `DERIVED_AXIS`
- `VISUALIZATION_ONLY`
- `NON_VOTING_CONTEXT`

## Causal Cluster Identity

The canonical cluster hash contains the opaque instrument identity, atomic
interval, evidence cutoff, snapshot, profile IDs and hashes, interval source
IDs, evidence kind, source lineage, actor, source nakshatra, target identity,
and exact derivation role.

Evaluated magnitude is deliberately separate. The existing Phase 5A
`contribution_id` continues to seal the evaluated nature, multiplier, signed
units, status, explanation, and unknown reason.

Inside one interval:

- an exact repeated contribution sharing one source lineage is deduplicated;
- two different evaluated contribution IDs sharing one lineage are rejected;
- repeated identical missing-evidence IDs are deduplicated;
- missing evidence gets a deterministic lineage and remains unknown.

## Ledger Views

Every interval exposes linked cells for:

- total;
- actor/body;
- target layer;
- nature;
- Vedha ray direction;
- source lineage.

Vedha direction here means the figure-relative Jyotisha ray direction. It is
not bullish or bearish market direction.

Missing evidence has no invented actor, target, nature, or direction. Those
cells use the explicit `UNAVAILABLE` key.

## Reconciliation

Every cluster must appear exactly once in every axis. Each axis separately
reconciles to the Phase 5A scalar total for:

- favorable guidance units;
- negative adverse guidance units;
- net guidance units;
- true gross activation as the sum of absolute scored units;
- scored count;
- unknown count;
- missing-evidence count;
- total evidence count;
- coverage and unknown-magnitude semantics.

The compiler fails closed if deduplicated clusters do not reproduce the Phase
5A scalar ledger or if any axis fails reconciliation.

## Deliberate Exclusions

P2 does not:

- perform base-minus-quote FX subtraction;
- calculate timing phase or confidence;
- emit market direction;
- alter Auto Suggest or live inference;
- create official ML notes;
- vote in shadow validation;
- create orders or call MT5;
- package a Windows or Android candidate.

The instrument identity is provenance only. Comparable FX arithmetic still
requires the separate P0-R6 gate.

## Verification

Focused tests cover:

- mixed favorable and adverse values;
- unknown and explicit missing evidence;
- exact-repeat deduplication;
- conflicting-evaluation rejection;
- instrument identity isolation;
- order-independent replay and serialization;
- weakened guardrail rejection;
- scalar-ledger mismatch rejection;
- empty intervals;
- non-voting role enforcement;
- real Chakra Lab -> Phase 5A -> Phase 5B flow.

The acceptance contract is
`docs/sbc/PHASE5B_ACCEPTANCE.md`. The causal-cluster decision is
`docs/sbc/ADR-0006-causal-cluster-and-ledger-deduplication.md`.

## Next Boundary

P3 may build linked audit visualization over cluster IDs, cells, intervals,
lineage, and reconciliation. It must not alter evidence weight.

FX subtraction remains blocked until P0-R6 freezes common timestamps, cutoff,
profile version, units, normalization, lineage policy, and bilateral coverage.
Phase remains blocked until P0-R1 through P0-R4 define and validate a complete
timing profile and typed confidence gates.
