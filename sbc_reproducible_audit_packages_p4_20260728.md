# SBC Reproducible Audit Packages P4

Date: 2026-07-28

Classification: `SOURCE_PROFILED_EXPERIMENTAL`

Status: implemented in source, read-only, execution-locked

## Purpose

P4 turns one canonical P3 linked audit into a reproducible research package.
It lets a researcher compare explicit intervals, attach manual observations,
export the result, and later replay the complete evidence chain without
turning those comparisons or notes into market predictions.

## Contract

- package: `SBC_REPRODUCIBLE_AUDIT_PACKAGE_V1`
- verification: `SBC_AUDIT_PACKAGE_VERIFICATION_V1`
- schema version: `1`
- policy: `READ_ONLY_COMPARISON_EXPORT_REPLAY_V1`
- classification: `SOURCE_PROFILED_EXPERIMENTAL`
- validation states: `PASS`, `FAIL`, `UNKNOWN`

## Reproducible Comparison

The package accepts one P3 audit, one baseline interval, and one or more
comparison intervals. Comparison intervals are placed in canonical source
order and every delta means comparison minus baseline. Total and
multidimensional rows retain their P3 interval, cell, cluster, and source
lineage links.

The comparison is deliberately descriptive. A positive or negative delta is
not bullish, bearish, confidence, performance, or a trade signal.

## Manual Bookmarks

Bookmarks may target only the complete audit, a known interval, ledger cell,
primary evidence cluster, or validation gate. Every bookmark is sealed as a
manual research annotation. It contributes no evidence weight, no vote, no
market direction, and cannot become an official ML note.

## Export And Replay

The package provides:

- canonical JSON export;
- a self-contained, escaped HTML report;
- portable SHA-256 seals that survive Python-to-browser JSON numeric
  representation changes;
- an embedded replay recipe;
- full Chakra -> P1 -> P2 -> P3 -> P4 replay verification.

Unknown evidence, missing doctrine, and absent financial validation remain
visible in both the interface and the exported report. Tampering, weakened
locks, invalid links, and replay drift fail closed.

## Chakra Lab Integration

Audit mode now keeps boundary capture inside the audit workspace, including an
explicit IST timestamp control. Capturing a boundary advances the next moment
by one hour, duplicate moments are rejected, and the terminal end advances
when required.

After compilation the user can:

1. select a baseline and multiple comparison intervals;
2. inspect candidate-minus-baseline totals and per-axis rows;
3. open a comparison row at the correct linked interval and evidence cell;
4. add or remove linked manual bookmarks;
5. build and download JSON or HTML;
6. import a JSON package and replay it;
7. see a plain PASS or FAIL result for the complete chain.

The compact desktop layout keeps the linked inspector visible at a 900-pixel
viewport. Smaller screens move to a two-column research layout.

## Deliberate Exclusions

P4 does not:

- compare unrelated P3 audits;
- infer bullish or bearish direction;
- calculate confidence or performance;
- alter Auto Suggest or live inference;
- create or edit official ML notes;
- vote in shadow validation;
- create trades or call MT5;
- claim source certification or prospective financial validation;
- rebuild a Windows or Android package.

## Verification

Engine tests cover stable multi-interval ordering, linked manual bookmarks,
deterministic replay, tampering, weakened P3 locks, invalid selections, and
escaped HTML. Service tests include a browser-style numeric JSON round trip.
Frontend tests cover two explicit boundaries, comparison packaging, exports,
replay, and the execution lock.

The real in-app browser acceptance flow captured two explicit IST boundaries,
compiled the P3 audit, added a linked bookmark, built the sealed package,
displayed descriptive comparison metrics without bullish or bearish language,
and returned:

`PASS - Full Chakra to P1 to P2 to P3 to P4 replay matched`

Exact test totals and the canonical module hash are recorded in
`status/audits/sbc_reproducible_audit_packages_p4_20260728.json`.

## Next Boundary

P5 may add a catalog for multiple sealed packages or independently signed
exchange bundles. It must not perform cross-audit arithmetic, voting, market
direction, or financial promotion without a separate accepted contract and
prospective validation.

FX subtraction and directional phase remain blocked by the earlier P0 gates.
