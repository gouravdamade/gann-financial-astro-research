# AVG(ALL) Collective Field Inspector M5

Date: 2026-07-27

## Scope

This milestone gives the existing ten-body synthetic `AVG(ALL)` source a
dedicated desktop research surface. It adds:

- synchronized diagnostic lanes for wrapped collective longitude, R1
  coherence, R2 polarisation, circular variance, and velocity;
- reliability bands and explicit broken segments where the collective
  longitude is unstable;
- sampled research-event markers;
- hover synchronization with the main price-chart crosshair and OHLC/RSI
  legends;
- click-to-pin synchronization from either the price chart or the inspector;
- a deterministic leave-one-out audit of each member's geometric influence;
- responsive inspector layout and accessible timestamp controls.

The inspector is an explanation and audit surface. It does not promote
`AVG(ALL)` into Jyotisha doctrine or a market predictor.

## Member Influence Audit

The response contract is:

```text
GANN_PLANETARY_COLLECTIVE_INFLUENCE_V1
AVG_ALL_LEAVE_ONE_OUT_AUDIT_V1
```

For each member and each exact source-bar timestamp, the engine calculates:

- the member longitude and configured weight;
- angular distance from the full collective mean;
- mean-longitude leverage: the absolute circular shift between the full mean
  and the mean recalculated without that member;
- R1 coherence leverage: full R1 minus leave-one-out R1;
- fast- or slow-moving display class;
- a deterministic display role and influence rank.

Positive R1 leverage means the member is concentrating the current geometry:
removing it reduces R1. Negative R1 leverage means the member is dispersing
the geometry: removing it increases R1.

The role names are compact UI descriptions, not classical astrological
judgments, market direction, causal proof, or independent votes. If the full
mean is unreliable, longitude and coherence leverage remain unavailable
rather than being invented.

## Inspector Behavior

The lower inspector contains four aligned lanes:

1. wrapped mean longitude;
2. R1 coherence;
3. R2 polarisation and circular variance;
4. reliability-safe velocity.

Background bands show the reliability state. Mean and velocity paths break at
unreliable samples and never bridge a gap. Event glyphs use their existing
sampled timing contract and remain explicitly approximate.

Moving across the inspector updates the main chart crosshair, OHLC legend,
and RSI legend at the nearest exact bar. Moving across the price chart updates
the inspector. Clicking either surface pins the timestamp; the pin control
clears it. The timestamp slider provides keyboard-accessible inspection.

Opening the inspector temporarily collapses the existing bottom Events dock
to preserve useful chart height. Closing it restores the prior dock state.
At narrower widths, the plot and audit table stack instead of overlapping.

## Visual Semantics

- The collective source uses a hollow synthetic glyph.
- Reliable, low-coherence, unstable, and undefined samples have separate
  background treatments.
- Unstable longitude has no selected mean marker.
- Broken reliability segments have no connected mean or velocity trace.
- Member roles remain visible as text rather than color-only meaning.

## Safety Boundary

Backend contracts, TypeScript types, and runtime validation require:

- research and UI-audit use only;
- no traditional-authority claim;
- no independent directional vote;
- directional contribution exactly `0.0`;
- no live-inference consumption;
- no Auto Suggest consumption;
- no shadow-ledger consumption;
- no official ML-note consumption;
- no SBC Vedha;
- no execution.

The desktop rejects an influence payload that weakens these locks or contains
malformed per-sample member audits.

## Verification

Verification completed on 2026-07-27:

- focused backend collective tests: `23/23`;
- focused frontend inspector and response-contract tests: `9/9`;
- complete desktop backend suite: `140/140`;
- complete desktop frontend suite: `80/80`;
- complete repository Python suite: `383/383`;
- Python Ruff for changed backend files: passed;
- frontend Oxlint: passed;
- project status validation: passed;
- TypeScript and Vite production build: passed.

Native-size browser inspection at `1280 x 720` passed against the live
USDJPY H1 workspace. Inspector-to-chart hover changed the matching OHLC and
RSI timestamp, chart-to-inspector click pinned the same bar, the bottom dock
restored correctly, and the browser console remained free of errors after the
final lifecycle correction.

The existing Vite main-chunk advisory remains non-blocking. The inspector is
already a separate lazy-loaded chunk; further main-workspace code splitting
is a later performance task.

## Known Limitations

- This is source-only; no Windows installer or Android package was rebuilt.
- The event markers remain bar-sampled estimates, not ephemeris-refined exact
  event times.
- Reliability thresholds and display roles are versioned research
  heuristics, not certified Jyotisha doctrine.
- Leave-one-out influence describes current circular geometry only. It does
  not establish price causality or market direction.
- No financial or prospective validation is claimed.

## Next Milestone

M6 should add only separately justified work, with the same safety boundary:

- refined event timing where an exact ephemeris root can be proven;
- optional visual studies such as Gann/SBC overlays without allowing them to
  become duplicate votes;
- explicit persistence/export for pinned collective audit snapshots;
- further code splitting and rendering performance measurement;
- prospective, frozen-policy validation before any inference promotion.
