# SBC Linked Audit Views P3

Date: 2026-07-28

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

Status: implemented in source, read-only, execution-locked

## Purpose

P3 turns the reconciled Phase 5B ledger into a linked manual-audit workspace.
It answers a narrow question: can a researcher inspect one immutable evidence
set across time, dimensions, rays, lineage, reconciliation, and validation
without creating extra votes or silently filling missing doctrine?

## Contract

- linked view: `SBC_LINKED_AUDIT_VIEW_V1`
- schema version: `1`
- policy: `LINKED_READ_ONLY_PROGRESSIVE_DISCLOSURE_V1`
- classification: `SOURCE_PROFILED_EXPERIMENTAL`
- validation states: `PASS`, `FAIL`, `UNKNOWN`

The six view IDs are:

- `TIMELINE`
- `LEDGER`
- `RAY_AUDIT`
- `SOURCE_LINEAGE`
- `RECONCILIATION`
- `VALIDATION`

## Deterministic Projection

The P3 compiler accepts one canonical Phase 5B series. It validates the P2
contract, schema, classification, and safety locks before projecting:

- interval rows linked to their canonical clusters and cells;
- ledger rows linked to the same primary cluster set;
- ray rows that preserve primary evidence and figure-relative Vedha direction;
- source-lineage rows with snapshot, profile, citation, and witness provenance;
- per-axis reconciliation rows;
- typed validation gates.

The canonical audit ID includes the complete linked projection. Replaying the
same evidence produces the same ID and serialization.

## Chakra Lab Integration

The existing Board remains the current-moment Chakra view. The new Audit mode
lets the user:

1. choose an opaque instrument identity;
2. capture explicit timestamped Chakra boundaries with a reason;
3. set one terminal end;
4. compile the linked audit;
5. move among Timeline, Ledger, Ray audit, Lineage, Reconciliation, and
   Validation while retaining the current interval, cell, and cluster context.

The browser does not submit precomputed evidence. The backend recomputes every
Chakra snapshot and compiles Phase 5A, Phase 5B, and Phase 5C. Native desktop
runtime uses a dedicated Tauri command and the supervised private sidecar.

## Visible Uncertainty

The audit deliberately shows:

- unresolved actor motion;
- explicit missing-evidence IDs;
- null unknown magnitude;
- incomplete coverage;
- absent financial validation;
- absent timing-phase doctrine;
- blocked execution consumers.

Ray direction is a Jyotisha figure relation. It is not a phase angle and not
an up/down market prediction.

## Deliberate Exclusions

P3 does not:

- discover boundaries from later prices or aspect outcomes;
- perform base-minus-quote FX subtraction;
- compute phase, confidence, or market direction;
- alter Auto Suggest or live inference;
- create or edit official ML notes;
- vote in shadow validation;
- create orders or call MT5;
- rebuild a Windows or Android package.

## Verification

Focused verification covers value preservation, cross-link integrity,
ray-versus-phase separation, visible unknown evidence, deterministic replay,
fail-closed guardrails, and a real Chakra Lab -> P1 -> P2 -> P3 flow.

The live development workspace was also exercised through the real browser
path: a boundary was captured, the audit compiled through the private backend,
and the Validation view displayed timestamp/reconciliation passes plus explicit
unknown financial, phase, and evidence gates with no browser errors.

Exact test totals and the canonical module hash are recorded in
`status/audits/sbc_linked_audit_views_p3_20260728.json`.

## Next Boundary

P4 may add comparison layouts or exportable audit packages, but it must remain
a projection over stable P3 identities unless a separately accepted ADR
changes the evidence contract.

FX subtraction remains blocked by P0-R6. Timing phase remains blocked until the
sector, boundary, loop, station, missing-state, confidence, and prospective
validation contracts are complete.
