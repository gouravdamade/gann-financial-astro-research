# PFR-V2B-5 Founder-Visible Independent Field Stack

Date completed: 2026-08-02

## What Is Visible

The Chakra workspace now has a `Fields` control. It opens a compact three-lane
stack aligned to one explicit UTC chart range:

1. USD aspect field - categorical side-chart context.
2. JPY aspect field - categorical side-chart context.
3. SBC atomic field - SBC guidance availability only.

Every block carries its own state and hover explanation. The displayed states
are categorical only: `SUPPORTIVE`, `ADVERSE`, `NEUTRAL`, `MIXED`, or
`UNKNOWN` for a currency side, and `AVAILABLE`, `PARTIAL`, or `UNKNOWN` for
SBC availability.

## Range and Desktop Path

The workspace derives the shared range from the currently rendered 110 chart
candles. `Load chart range` submits that exact start/end range through the
native private Rust bridge to `/api/independent-fields/synchronized-range`.
The backend rejects a mismatched field or late SBC boundary rather than making
the three fields look aligned when they are not.

## Important Current State

The USD and JPY lanes are intentionally `UNKNOWN` until reviewed immutable
side-chart evidence is admitted. Current pair-chart aspect events are not
copied into either side lane. This is correct: USDJPY is a derived pair view,
not an accepted USD or JPY natal chart.

The SBC lane is independently available from its existing atomic ledger. Its
availability does not confirm, negate, combine with, or change an aspect
state.

## Boundaries Retained

- The stack has no combined signal, score, amplitude, smoothing, calibration,
  curve fitting, or market-direction inference.
- The stack cannot reach Auto Suggest, ML, live inference, MT5, or execution.
- `MIXED` remains visibly mixed rather than being converted into a net value.
- Existing execution locks remain active.

## Verification

- Focused desktop tests: `13 passed`, including native IPC routing and three
  independent lane rendering.
- Production TypeScript/Vite build: passed.
- Rust `cargo check`: passed.
- Backend aspect/SBC/coordinator regression suite: `33 passed`.

## Next Bounded Step

V2B-6 may admit only a small founder-reviewed side-level pilot with immutable
evidence. It must include both positive and negative categorical intervals and
preserved unknown gaps. No package should be created before that founder
review is complete.
