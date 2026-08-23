# Multi Oscillator MO-P2-R1: Activity Integrity Hardening

Status: `IMPLEMENTED_FOR_CENTRAL_REVIEW`
Milestone: `MO-P2-R1`
Evidence mode: `EXPLORATORY_UNSIGNED`

## Scope

This is a bounded correction to the unsigned event-activity inspector. It does
not add polarity, magnitude, signed pair activity, smoothing, price input,
outcome reads, SBC/CGVO input, LLM inference, Auto Suggest, ML, MT5, or
execution.

The contribution contract remains `MO_ACTIVITY_CONTRIBUTION_V1`: event `i`
contributes one unit on the half-open interval
`[applyingStartUtc, separatingEndUtc)`. `rawActiveEventCount` remains an
integer event count, not a score, probability, confidence, magnitude, or
forecast.

## Coverage Semantics

The activity service delegates event construction to the canonical
chart-conditioned transit compiler. A rejected compiler candidate is classified
using only its supplied `observedSearchStartUtc` and
`observedSearchEndUtc`:

- if the observed interval is valid and completely outside the requested
  half-open visible range, it is `irrelevant` and does not poison visible
  coverage;
- if the observed interval overlaps the visible range, it is `relevant` and
  the side remains `UNKNOWN`;
- if the rejection is malformed, missing timestamps, or has reversed bounds, it
  is treated as relevant and coverage fails closed;
- any canonical `unknownReasons` entry keeps coverage `UNKNOWN`, even when all
  rejected candidates are irrelevant.

The response reports `rejectedEventCount`,
`relevantRejectedEventCount`, and `irrelevantRejectedEventCount`. A successful
empty compilation is still a known zero. An irrelevant rejection elsewhere is
not treated as a visible-range failure.

## Shared Raw-Count Display Axis

The response contract is now `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1` with
`schemaVersion: 2`; the side contract is
`MO_UNSIGNED_EVENT_ACTIVITY_SIDE_V1_1`. The event-universe hash is named
`eventUniverseHash` and remains separate from `eventUniverseProfileId`.

The Fields panel applies body/aspect filters locally. It recomputes one display
axis from the filtered visible interval counts:

`sharedAxisMax = max(USD filtered counts, JPY filtered counts)`

Both lanes use that same axis. If both sides have zero visible activity, the
label remains `0-0` in the logical display scale while pixel math safely uses
`max(1, sharedAxisMax)`. Filtering never mutates event records, event hashes,
coverage provenance, or canonical event-universe completeness.

The panel displays:

`Shared raw activity scale: 0-N active events`

with the current filtered count range. This is display-axis scaling only; data
normalization remains false. The guardrail contract retains the original
`normalizationUsed=false` field and adds:

```json
{
  "dataNormalizationUsed": false,
  "displayAxisScaling": {
    "mode": "SHARED_RAW_COUNT_AXIS",
    "derivedFrom": "CURRENT_FILTERED_VISIBLE_COUNTS",
    "changesDataValues": false
  }
}
```

## Provenance and Existing Locks

The event inspector still exposes event ID, event hash, exact UTC, applying
start, separating end, body, target, aspect, astronomy contract, generator,
chart identity, and chart hypothesis. Records remain labelled
`CANONICAL_COMPILER_EVENT`; arbitrary live-range events are not labelled
`SINGLE_PASS_VERIFIED`.

The following remain false: polarity assigned, magnitude assigned, price data
read, price outcome read, SBC read, LLM read, pair difference computed, data
normalization, smoothing, automatic order placement, and execution. The
activity panel remains read-only and non-predictive.

## Verification

Focused tests cover half-open boundaries, known zero, unknown compiler state,
irrelevant and relevant rejected candidates, malformed rejection metadata,
multiple-rejection classification, injected-universe rejection, signed and
magnitude-bearing compiler output, the shared frontend axis, filtered display
recomputation, zero-range pixel safety, provenance selection, and existing
Fields behavior.

Verification completed locally:

- focused backend: `15/15`;
- focused frontend/API: `30/30`;
- full backend: `319 passed, 1 skipped`;
- full frontend: `182 passed` across 42 files;
- Oxlint: passed with no warnings;
- production build: passed, with the existing large-chunk warning;
- `cargo fmt --check`: passed;
- `cargo check`: passed;
- Rust tests: `19 passed`;
- `git diff --check`: passed.

The real 14-day smoke from 2025-04-01 through 2025-04-15 produced USD 57
source/eligible events and 32 rejected candidates: 3 relevant and 29
irrelevant, leaving USD `UNKNOWN`. JPY produced 59 source/eligible events and
14 rejected candidates: 0 relevant and 14 irrelevant, leaving JPY `KNOWN`.

Windows packaging is intentionally not part of MO-P2-R1. The next action after
central review is the founder-inspection candidate.
