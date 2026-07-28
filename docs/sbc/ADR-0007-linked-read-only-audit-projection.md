# ADR-0007: Linked Read-Only SBC Audit Projection

Status: accepted for P3 source implementation

Date: 2026-07-28

## Context

Phase 5A produces timestamp-safe atomic intervals. Phase 5B organizes each
interval into primary causal clusters and reconciled ledger axes. Those
contracts are machine-auditable, but they are difficult to inspect manually
without a linked view across time, actor, target, nature, Vedha direction, and
source lineage.

P3 must make that evidence inspectable without creating a new calculation,
vote, phase vector, market opinion, or trading consumer.

## Decision

1. P3 is a deterministic projection of the canonical Phase 5B ledger. It does
   not accept ad hoc display facts or recalculate evidence weight.
2. The projection contract is `SBC_LINKED_AUDIT_VIEW_V1`, schema version `1`,
   under policy `LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1`.
3. One audit contains six linked views:
   - `TIMELINE`
   - `LEDGER`
   - `RAY_AUDIT`
   - `SOURCE_LINEAGE`
   - `RECONCILIATION`
   - `VALIDATION`
4. Interval, cell, cluster, and lineage links use the canonical Phase 5B
   identities. Unknown links, duplicate links, or an unreconciled interval
   fail closed.
5. The timeline reproduces each half-open interval, evidence cutoff, duration,
   scalar total, cluster set, cell set, and duplicate-primary-evidence count.
6. The ledger view reproduces each Phase 5B axis cell and remains
   `DERIVED_AXIS`, non-voting, and directionally weightless.
7. The ray audit reproduces figure-relative Vedha direction from primary
   evidence. It has no phase angle or phase vector and is not a market
   direction.
8. The lineage view preserves source, citation, snapshot, foundation, grid,
   Vedha, guidance-model, witness, and evidence-status provenance.
9. Reconciliation reproduces the Phase 5B axis results. P3 refuses to display
   an unreconciled axis as valid.
10. Validation uses typed `PASS`, `FAIL`, or `UNKNOWN` gates. Missing
    financial validation and missing timing-phase doctrine are `UNKNOWN`, not
    implied passes.
11. Explicit missing evidence remains visible with null magnitude. It is not
    converted to zero or omitted from coverage.
12. The Chakra Lab audit service accepts explicit timezone-aware boundaries
    and one terminal end, recomputes each immutable snapshot, then compiles
    Phase 5A, Phase 5B, and Phase 5C in order.
13. The existing Chakra board remains the single-moment view. Audit is a
    separate mode in the same workspace, with explicit capture and compile
    actions.
14. Browser development may use the private HTTP endpoint. Packaged desktop
    builds must use native Tauri IPC to the supervised private backend.
15. P3 remains `SOURCE_PROFILED_EXPERIMENTAL`, read-only, has directional
    contribution `0.0`, and cannot feed FX subtraction, phase, confidence,
    market direction, Auto Suggest, live inference, official ML notes, shadow
    validation, trade output, or MT5 execution.

## Consequences

- A researcher can move between time, ledger, ray, lineage, reconciliation,
  and validation without losing the underlying evidence identity.
- Unknown doctrine and missing actor motion stay prominent instead of being
  hidden by a polished visualization.
- Stable links make screenshots and manual audits reproducible.
- The projection can be rebuilt from the same inputs and compared by canonical
  audit hash.
- A future phase engine cannot silently reuse the ray audit as a phase signal.
- No Windows or Android candidate is produced by this source milestone.

## Rejected Alternatives

- Counting each displayed dimension as another evidence vote.
- Treating left, front, or right Vedha rays as bullish or bearish direction.
- Filling absent phase angles with zero.
- Hiding unresolved evidence to simplify the interface.
- Letting the browser supply precomputed snapshots or ledger rows.
- Compiling implicit boundaries from chart extrema, aspect edges, or later
  market outcomes.
