# Phase 5C Linked Audit View Acceptance Gates

Phase 5C, which is P3 of the multidimensional SBC roadmap, is accepted in
source only when all of the following pass:

1. Input gate: the compiler accepts only the canonical Phase 5B ledger
   contract, schema, classification, and locked guardrails.
2. Projection gate: P3 reproduces Phase 5B values and identities without
   changing evidence weight.
3. Link gate: every interval cluster, interval cell, ledger-cell cluster,
   ray-row cell, lineage cluster, and reconciliation interval link resolves
   exactly.
4. Timeline gate: intervals preserve start, end, cutoff, duration, summary,
   duplicate count, cluster set, and cell set.
5. Ledger gate: every displayed ledger cell remains `DERIVED_AXIS`, has no
   vote, and contributes `0.0` market direction.
6. Ray gate: every ray row remains `PRIMARY_EVIDENCE` and preserves
   figure-relative Vedha direction only.
7. No-phase gate: all ray phase angles are null, phase-vector flags are false,
   and the audit guardrail reports phase absent.
8. Lineage gate: source IDs, citation IDs, snapshots, profile IDs and hashes,
   guidance model, witness set, and evidence status remain linked.
9. Reconciliation gate: all six Phase 5B axes remain reconciled. A broken axis
   or unknown link fails closed.
10. Unknown-evidence gate: unresolved and explicit missing evidence remain
    visible, counted, and null in magnitude.
11. Typed-validation gate: timestamp safety, reconciliation, unknown evidence,
    financial validation, phase profile, and execution lock use only `PASS`,
    `FAIL`, or `UNKNOWN`.
12. Replay gate: identical Phase 5B input produces identical P3 IDs and
    serialization.
13. Boundary gate: the service accepts only non-empty, timezone-aware explicit
    boundaries and a timezone-aware terminal end after the final boundary.
14. Recompute gate: the backend rebuilds Chakra snapshots, Phase 5A intervals,
    Phase 5B ledgers, and P3 views; it does not trust browser-computed evidence.
15. Transport gate: browser development and native Tauri IPC return the same
    read-only contract and keep execution locked.
16. User-interface gate: Board and Audit are distinct modes; Timeline, Ledger,
    Ray audit, Lineage, Reconciliation, and Validation remain linked and
    inspectable without overlapping controls.
17. Isolation gate: FX subtraction, phase, confidence, market direction, Auto
    Suggest, live inference, official ML notes, shadow validation votes, trade
    output, MT5 execution, and package promotion remain blocked.
18. Regression gate: earlier SBC, Chakra Lab, service, frontend, and status
    tests continue to pass.

Passing these gates certifies a deterministic read-only audit projection. It
does not certify Jyotisha doctrine, a timing-phase model, financial usefulness,
market direction, packaging, or execution.
