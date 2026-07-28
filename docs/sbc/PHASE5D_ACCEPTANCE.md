# Phase 5D Acceptance: Reproducible Audit Comparison Packages

P4 is accepted only when all of the following are demonstrated:

- one canonical P3 audit is the sole evidence input;
- baseline and comparison interval IDs must exist in that audit;
- the baseline cannot also be a comparison interval;
- multiple comparison intervals replay in stable source order;
- total and per-axis/key deltas are candidate-minus-baseline and explicitly
  descriptive-only;
- absent axis/key cells stay visibly absent on that side of the comparison;
- P3 interval, cell, cluster, and source-lineage identities are unchanged;
- bookmarks can target only valid P3 identities or validation gates;
- bookmark text is marked manual research annotation only;
- canonical hashes seal the source projection, replay recipe, comparison rows,
  bookmarks, and complete package;
- JSON export and a readable escaped HTML report are available;
- import verification reruns Chakra -> P1 -> P2 -> P3 -> P4;
- tampered payloads, weakened locks, broken links, and replay drift fail closed;
- unknown evidence and missing financial or phase validation remain visible;
- comparison and bookmarks contribute no independent vote and `0.0`
  directional weight;
- FX subtraction, phase, confidence, market direction, Auto Suggest, live
  inference, official ML notes, shadow validation, trades, and MT5 remain
  blocked.
