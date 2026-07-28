# ADR-0008: Reproducible SBC Audit Comparison Packages

Date: 2026-07-28

Status: accepted for P4 implementation

## Context

P3 projects one reconciled Phase 5B evidence ledger into six linked, read-only
views. Researchers can inspect stable interval, cell, causal-cluster, and
source-lineage identities, but cannot yet compare selected intervals in one
bounded workspace or preserve that review as a replayable artifact.

P4 must add those capabilities without changing the evidence contract or
turning descriptive differences into market inference.

## Decision

P4 introduces `SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1`, schema `1`, under
`READ_ONLY_COMPARISON_EXPORT_REPLAY_V1`.

One package:

- embeds one complete canonical P3 projection;
- embeds the explicit Chakra Lab capture request needed to recompute it;
- selects one baseline interval and one or more comparison intervals from that
  same P3 projection;
- computes candidate-minus-baseline descriptive deltas for the interval total
  and every existing P2 axis/key;
- preserves the original P3 interval, cell, cluster, source-lineage, snapshot,
  profile, citation, and witness identities;
- may contain manual research bookmarks linked to an audit, interval, cell,
  cluster, or validation gate;
- is sealed by canonical SHA-256 identities for the source projection, replay
  recipe, comparisons, bookmarks, and complete package;
- can be imported and verified by rerunning Chakra -> P1 -> P2 -> P3 -> P4
  from its embedded replay recipe.

Comparison rows use `DESCRIPTIVE_COMPARISON_ONLY`. Bookmark rows use
`MANUAL_RESEARCH_ANNOTATION_ONLY`.

## Interpretation Boundary

A positive or negative delta means only that the comparison interval contains
more or less of that already-defined ledger quantity than the baseline. It is
not favorable/unfavorable market direction, performance, confidence, phase,
prediction, or a trade instruction.

Manual bookmarks are untrusted researcher annotations. They are not Jyotisha
doctrine, evidence, official ML notes, shadow-validation votes, or training
labels.

## Replay Verification

Import verification must:

1. validate the package contract, schema, policy, classification, hashes,
   links, and guardrails;
2. reject unknown package fields;
3. rebuild the P3 audit from the embedded explicit capture request;
4. rebuild P4 with the sealed interval selections, bookmarks, and timestamp;
5. require exact source-audit, source-projection, replay-recipe, and package
   identity matches.

A file hash by itself is not sufficient replay verification.

## Guardrails

P4 remains:

- research-only;
- read-only;
- timestamp-safe and no-lookahead;
- source-profiled experimental;
- financially unvalidated;
- non-voting with directional contribution `0.0`;
- disconnected from FX subtraction, phase, confidence, market direction,
  Auto Suggest, live inference, official ML notes, shadow validation, trade
  output, and MT5 execution.

## Deliberate Non-Goals

P4 does not compare different P3 audits, instruments, profile versions, or
evidence cutoffs arithmetically. It does not certify P0-R6 comparable FX
subtraction. It does not add timing phase or prospective financial validation.

Those require separate accepted contracts.
