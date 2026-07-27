# AVG(ALL) Gann And SBC Visual Study Freeze Candidate M7

Date: 2026-07-27

## Purpose

Milestone M7 adds an export-only evidence dossier for inspecting the synthetic
`AVG(ALL)` collective field beside user-authored Gann geometry and a
timestamp-matched Sarvatobhadra Chakra snapshot. It is a visual research aid,
not a forecast, vote, trading rule, ML label, or prospective result.

The dossier contract is:

- `GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1`;
- Gann child contract `GANN_AVG_ALL_GANN_VISUAL_STUDY_V1`;
- SBC child contract `GANN_AVG_ALL_SBC_VISUAL_STUDY_V1`;
- freeze-candidate contract
  `GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1`.

## Evidence Join

The user selects an exact source bar in the Planetary Collective Field
inspector and asks the app to build the study. The app then joins:

1. the immutable M6 `GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1` for that
   exact chart bar;
2. every currently visible, user-authored Gann fan in the active named chart
   layout, up to a fail-closed limit of 32;
3. an SBC Chakra Lab snapshot requested for the same instant and the active
   chart's reference latitude and longitude.

The SBC request asks for all nine classical/node body positions needed by the
existing snapshot contract. Only `SUN`, `MOON`, `RAHU`, and `KETU` are passed
as Vedha actors because the current certified profile can resolve those fixed
motion classes without inventing speed classifications for the other bodies.
`AVG(ALL)` itself does not cast Vedha.

The response is rejected unless it is read-only, timestamp-safe,
no-lookahead, guidance-only, not financially validated, and barred from
execution. Its `as_of_utc` must match the selected source bar within one
second, and its evidence cutoff cannot be later than that bar.

## Gann Scope

Only visible drawings with the existing research-only
`GANN_RESEARCH_CHART_DRAWING_V1` contract and type `gann_fan` are copied.
Anchors, positive finite ratios, and display style are preserved. The
dossier does not infer direction from the fan, score a touch, or read an
outcome.

If the chart, date range, reference location, or drawing set changes while an
SBC request is in flight, the request is invalidated and its stale result is
discarded.

## Seal And Freeze Semantics

The completed dossier is canonicalized and sealed with SHA-256. It includes:

- the exact immutable AVG audit;
- the copied Gann geometry;
- the complete timestamp-matched SBC snapshot;
- explicit child and top-level guardrails;
- a freeze-candidate section with the evidence cutoff and registration
  prerequisites.

`packetFrozen=true` means that downloaded packet is an immutable candidate
record. It does **not** mean a prospective trial has been registered.

The embedded status remains:

- `EXPORT_ONLY_NOT_REGISTERED`;
- `trialRegistered=false`;
- `outcomeLabelsIncluded=false`;
- `existingShadowTrialModified=false`.

## Guardrails

The UI, TypeScript contract, normalizer checks, package manifest, and tests
require:

- research use only;
- no independent vote;
- directional contribution exactly `0`;
- no live inference;
- no Auto Suggest;
- no shadow ledger;
- no official ML notes;
- no execution.

M7 makes no claim that Gann fans, SBC context, or `AVG(ALL)` predict price.
It provides a reproducible packet from which a separate future observer
protocol could be predeclared.

## Requirements Before Prospective Registration

A later trial must be separate from the existing frozen USDJPY shadow cohort
and must predeclare, before its untouched future start:

1. exact outcome labels and observation horizons;
2. entry/exclusion/missing-data rules;
3. pass/fail thresholds and minimum cohort size;
4. an immutable manifest identity;
5. how Gann and SBC observations are measured without looking at outcomes;
6. a prohibition on changing the observer after outcome inspection.

Until that work is complete, M7 stays an exportable visual-study candidate.

## Verification

Verification completed on 2026-07-27:

- M7 focused frontend tests: `8/8`;
- complete desktop frontend suite: `91/91`;
- complete desktop backend suite: `147/147`;
- complete repository Python suite: `390/390`;
- Rust suite: `18/18`;
- status validation: `6/6`;
- frontend Oxlint: passed;
- Python Ruff for the changed packaging test: passed;
- TypeScript and Vite production build: passed.

The existing main-workspace production chunk remains approximately 534 KiB
minified and emits the known chunk-size advisory. Further code splitting is a
separate performance milestone.

Windows artifact hashes and native soak evidence are recorded separately
after the clean `0.10.24` source commit is packaged.
