# PFR-U1 Founder Acceptance Record

## Frozen Candidate

- Candidate: `0.10.31-pfr-c2f`
- Exact packaged source: `b8ae06fa775b152e4782157e44c9b8be47676c82`
- Portable: `D:\PycharmProjects\releases\GannAstroDesk-0.10.31-pfr-c2f\GannAstroDesk.exe`
- Current release verification: 2026-08-02 06:11 IST
- Preflight machine: `SURBHI`, Windows 11 Home Single Language, build 26200
- Founder acceptance: `PENDING`

## Artifact Identity

| Artifact | SHA-256 |
| --- | --- |
| Portable `GannAstroDesk.exe` | `5DEF199321271B95EBCA9E866D8A35E99E975BC3632EBC39A9F08C65CE618AD8` |
| Installer `Gann Astro Desk_0.10.31_x64-setup.exe` | `340C5EA66F73F989C79B850B4B7A8AE73FB3D870408EDC2694FAC99ADF7DF5CA` |
| Backend `backend\GannAstroBackend.exe` | `BC2A62134784BECEFA2FEF5DB8CB327C490B4475FA6E256147D79A9478F3E55B` |
| Release manifest `release.manifest.json` | `AAA8BF79D28CD8B65626C4AC60C9E9C74AC945072173C7B3A3EE371B213908FA` |

## Before Testing

- [ ] Start the portable candidate above. Do not use a rebuilt, patched, or newer copy.
- [ ] Record display scaling: `________________`.
- [ ] Record acceptance start/end time in IST: `________________`.
- [ ] Keep the candidate folder unchanged during this run.
- [ ] Note any external data availability restriction separately from a product defect.

## Founder Workflow

- [ ] Launch, close normally, and launch again.
- [ ] Open the product-first SBC/phase workspace and a known USDJPY historical period.
- [ ] Pan and zoom without blanking, crashing, or losing the selected time.
- [ ] Move the selected candle with mouse and keyboard; price, event lanes, Chakra, fixed wheel, Phase Lab, Compare, and Why stay aligned.
- [ ] Switch all three modes and restart; mode persistence is correct.
- [ ] `SOURCE_ONLY_BASELINE` visibly says source-profiled partial baseline and founder approval pending.
- [ ] `CALIBRATED_RESEARCH` visibly says unconfigured/source-missing and invents no fitted values.
- [ ] `VISUAL_ONLY_NO_SCORE` and unconfigured calibrated mode reveal no score through text, color, line length, radius, tooltip, title, bookmark, or export.
- [ ] Phase Lab shows lifecycle only and withholds Re, Im, resultant, gross, coherence, conflict, and collective phase while the link profile is missing.
- [ ] USDJPY pair direction, common activation, and joint net strength are separate and clearly labelled.
- [ ] Export one state from each mode; each export identifies mode, profile, approval state, source gaps, timestamp, cutoff, calculation version, source SHA, and execution locks.
- [ ] Optional candlestick specialist visibly says not configured rather than fabricating evidence.
- [ ] No order, buy/sell, position-size, Auto Suggest, official ML, live inference, or execution control is present.

## Result

Choose exactly one: `ACCEPTED` | `ACCEPTED_WITH_DEFECTS` | `REJECTED`

- Result: `________________`
- Founder comment: `________________`
- Screenshots / exports / log paths: `________________`
- Defects, severity, and exact reproduction steps: `________________`
- Founder name: `________________`
- Completed at (IST): `________________`

Do not change the product during acceptance. A rejection or defect report must be reproduced and recorded before any code is changed.

## Known Acceptance Defect

### U1-S1-001: Zoom removes research overlays

- Reported: 2026-08-02 during founder acceptance of the exact frozen portable.
- Severity: `S1` - navigation blocker.
- Steps: open a historical chart with aspects and Live SR planetary lines visible,
  then use the mouse wheel to zoom into the chart.
- Expected: candlesticks, active/overlapping aspect lanes, and the enabled
  planetary lines remain visible and aligned to the same viewport.
- Observed: candlesticks remain, while aspect lanes and planetary lines disappear.
- Evidence: founder report in the PFR-U1 acceptance session.
- Original source finding: the aspect-band renderer requires an on-screen coordinate for
  an aspect's start or end boundary. When zooming inside a long active aspect,
  both boundaries may be off-screen even though the aspect covers the whole
  viewport, causing the band to be incorrectly omitted. The planetary-line
  disappearance shares the viewport-refresh path.
- Status: `FOUNDER_TARGETED_CHECK_PASSED`.

### Approved Bounded Correction

- Approval: founder approved U1-S1 hotfix implementation on 2026-08-02.
- Aspect correction: active aspect intervals are clipped to the viewport before
  coordinates are calculated, so an aspect remains visible when its start and
  end boundaries are both off-screen.
- Live SR correction: a viewport request includes sparse whole-chart anchors
  plus dense visible-range samples. A fast zoom therefore retains a line
  segment while the denser viewport calculation catches up.
- Guard: this change affects rendering continuity only. It does not change
  aspect detection, SR values, source profiles, scores, inference, ML, orders,
  or execution permissions.
- Source validation: 32 frontend test files / 127 tests passed; lint and the production frontend build passed. The isolated native soak passed, including backend health, restart recovery, chart contracts, and execution locks.
- Hotfix candidate: `0.10.32-pfr-u1-s1`, source `5d61fd42739603ec5e05c4e4e0d7e7a15127c557`, at `D:\PycharmProjects\releases\GannAstroDesk-0.10.32-pfr-u1-s1\`. Its manifest records `source_git_dirty=false`.
- Portable SHA-256: `91DAF5C9011A6A064BD5E688114EFCA47E71582ED08BE134BB369E9406F881BF`. Installer SHA-256: `6B8944BE06D6F07786C2755638B0C289043B5CA5790A8323A519777C34C124D1`.
- Founder result: on 2026-08-02 at 20:40 IST, the founder confirmed that aspect
  lanes and Live SR lines remained visible during repeated zoom. The targeted
  U1-S1 rendering check therefore passed.
- Scope note: this records the targeted hotfix acceptance only. The original
  `0.10.31-pfr-c2f` artifact remains the historical C2F candidate and is never
  replaced; no calculation, execution, or polarity behavior was changed by
  this confirmation.

This record does not alter the historical C2F candidate. Under PFR-U1, only
this approved S1 rendering repair may proceed before the corrected candidate
is physically inspected.

## What Follows Acceptance

Use `PFR_U1_OBSERVATION_LOG_TEMPLATE.csv` for at least five normal research sessions. During observation, do not tune constants, weights, phase spans, thresholds, sources, colors, profiles, or any execution-related behavior. Record negative, ambiguous, and unknown results as faithfully as good-looking ones.
