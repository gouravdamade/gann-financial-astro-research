# PFR-V2B-R4-T2P-U1 — Founder-Visible Oscillator and Toolbar Correction

Status: IMPLEMENTED_PENDING_FOUNDER_INSPECTION
Date: 2026-08-05 IST

## Scope

This bounded correction changes only the founder-facing workspace layout and
integration. It does not add doctrine, polarity, evidence, magnitude,
Trailokya range compilation, smoothing, curve fitting, financial
interpretation, Auto Suggest, execution, or packaging promotion.

## Implemented

- The existing `IndependentFieldStack` now renders inside the left price
  context column, immediately below the visible-aspect legend.
- The order in that column is aspect ribbons, price chart, visible-aspect
  legend, then the independent USD, JPY, and SBC fields.
- The field stack is expanded by default when the workspace is opened. A
  founder may collapse it with the existing `Fields` control; that preference
  is stored locally and does not affect the field response.
- The existing synchronized response remains authoritative. USD and JPY keep
  their independent categorical states and unknown gaps. Trailokya continues
  to display `GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED` without a scored fallback.
- The workspace view controls now occupy a full-width wrapping toolbar row.
  Previous candle, Time, Profile, Wheel, Phase lab, Compare, Fields, and next
  candle remain in the DOM, keyboard reachable, and visibly focusable.
- The oscillator group has a bounded height so the price chart remains usable
  and the left column can scroll rather than silently clip content.

## Verification

- `npm.cmd run lint`: passed (Oxlint)
- `npm.cmd test`: 32 files, 139 tests passed
- `npm.cmd exec -- vitest run --pool=threads --no-file-parallelism --maxWorkers=1 src/productFirstSbcWorkspace.test.tsx`: 1 file, 7 tests passed
- `npm.cmd run build`: passed (TypeScript and Vite production build)

Focused coverage proves default expansion, left-column placement, explicit
unknown gaps, Trailokya geometry-only unavailability without a scored
fallback, collapse/restore behavior, and toolbar control reachability.

No Playwright or native viewport harness is configured in the frontend
repository, so the required 1920x1080 (100/125/150%) and 1366x768 physical
Tauri checks remain founder inspection items. No packaged candidate was
produced by this source correction.

## Founder inspection checklist

Pending physical screenshots:

- [ ] 1920x1080 Workspace with price, legend, USD, JPY, and SBC visible together
- [ ] Full toolbar with Phase lab, Compare, and Fields reachable
- [ ] Trailokya source-only geometry with explicit SBC unavailable lane
- [ ] Phaladeepika independent SBC range unchanged
- [ ] 1366x768 responsive layout with no silent clipping

