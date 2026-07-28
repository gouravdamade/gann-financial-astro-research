# SBC Atomic Intervals P1

Date: 2026-07-28

Status: implemented in source; research-only; not packaged or financially
validated

## Result

P1 adds `SBC_ATOMIC_INTERVAL_SERIES_V1` in `sbc/atomic_intervals.py`.
The compiler converts explicit SBC state boundaries into ordered,
non-overlapping half-open intervals. It does not discover event boundaries and
does not generate phase, confidence, market direction, or trading output.

## Contracts

- series: `SBC_ATOMIC_INTERVAL_SERIES_V1`;
- policy: `EXPLICIT_BOUNDARY_STATES_V1`;
- contribution evaluation: `SBC_ATOMIC_CONTRIBUTION_V1`;
- source lineage: `SBC_ATOMIC_SOURCE_LINEAGE_V1`;
- classification: `SOURCE_PROFILED_EXPERIMENTAL`.

## Boundary Semantics

Each boundary contains:

- `starts_at_utc`;
- one `evidence_cutoff_utc`, which must be at or before the start;
- a deterministic snapshot identity and boundary reason;
- foundation, grid, Vedha, and guidance profile identities;
- source IDs;
- evaluated contributions;
- explicit missing-evidence IDs.

The compiler sorts boundaries before processing. Duplicate timestamps,
lookahead cutoffs, non-positive terminal intervals, and mixed profile
identities fail closed. Every emitted interval uses `[startUtc, endUtc)`.

## Transparent Accounting

For scored signed contribution units `u_i`:

- favorable units are `sum(u_i where u_i > 0)`;
- adverse units preserve their negative sign:
  `sum(u_i where u_i < 0)`;
- net units are `sum(u_i)`;
- gross activation is `sum(abs(u_i))`.

This means cancellation can no longer masquerade as low activity. P1 does not
yet assign a cancellation band or threshold.

Unresolved contribution count and missing-evidence count are preserved.
Unknown magnitude is null whenever either exists; it is `0.0` only when the
ledger has no unknown evidence. Coverage is scored evidence divided by total
scored, unresolved, and missing evidence rows.

## Chakra Adapter

`boundary_from_chakra_snapshot` converts an existing timestamp-safe Chakra Lab
snapshot without changing the snapshot contract. It:

- verifies all read-only, no-lookahead, no-market, and no-execution locks;
- preserves foundation, grid, Vedha, guidance, witness, and citation lineage;
- converts every matched Vedha contribution;
- records requested actors that were not ready, such as
  `MOTION_REQUIRED`, as missing evidence;
- requires explicit unavailable-profile metadata when no guidance ledger
  exists, rather than guessing which Vedha profile was selected.

## Deterministic Identity

Contribution, source-lineage, boundary, interval, and series IDs are canonical
SHA-256 hashes. Contribution order and source-ID order are normalized. Reversed
boundary input therefore produces the same payload and series identity.

P1 deliberately does not create the P0-R5 multidimensional causal-cluster
contract. Source lineage and evaluated contribution identity are kept separate
so P2 can deduplicate them without rewriting P1 evidence.

## Guardrails

The series carries:

- research-only and timestamp-safe status;
- `SOURCE_PROFILED_EXPERIMENTAL`;
- no independent vote;
- directional contribution `0.0`;
- execution disabled;
- explicit blocks for phase, confidence, market direction, Auto Suggest, live
  inference, official ML notes, shadow-validation votes, trades, and MT5.

## Limitations And Next Step

P1 is only as complete as its explicit boundary list. It does not yet scan an
ephemeris range to discover every state transition. It also does not:

- combine dimensions into one multidimensional ledger;
- classify safe/unsafe timing sectors;
- compute confidence;
- aggregate daily, weekly, or monthly duration;
- draw the interval series in the desktop app;
- register a prospective financial trial.

P2 should add a versioned multidimensional ledger over these intervals. Before
P2 uses FX arithmetic, P0-R5 and P0-R6 must freeze causal-cluster
deduplication, comparable units, shared cutoff/profile requirements, and true
gross activation.
