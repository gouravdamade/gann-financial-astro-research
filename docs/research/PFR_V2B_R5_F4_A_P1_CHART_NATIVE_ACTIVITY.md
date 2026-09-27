# PFR-V2B-R5-F4-A-P1 Chart-Native Unsigned Activity

## Disposition

The chart-native unsigned activity indicator is implemented on the isolated
branch `research/pfr-v2b-r5-f4-a-p1-chart-native-activity`, starting from
`5ae4df13b042b1eaa309a7ac0ab6c36850bd50e9`. The implementation commit is
recorded by Git history and bound in the machine status record's successor
metadata update.

Only the F4-A unsigned activity phase is implemented. There is no directional
USD, JPY, or pair chart pane. F4-B and F4-C remain unauthorized.

## Chart Architecture

- Price, RSI, and unsigned activity share the existing single Lightweight
  Charts `IChartApi` and its time scale.
- The chart-only `ChartPaneRegistry` maps `PRICE`, `RSI`, and
  `FIELDS_ACTIVITY` to owned series and resolves runtime pane ownership from
  the actual pane/series identity. Numeric pane positions are not persisted or
  used as indicator identities.
- The activity pane contains USD and JPY native stepped lines on one shared
  raw integer count scale. It does not normalize, smooth, interpolate, combine,
  or subtract the sides.
- Activity can be enabled independently of RSI. Both lower panes reflow using
  native chart panes; activity height is stored as display configuration only.
- Exact-event markers are grouped by side and UTC second, bounded to 500
  visible groups, and rendered as native series markers. Hover/crosshair and
  click selection expose side, transit, natal target, aspect, exact UTC, and
  applying/separating timestamps in the event detail panel. Selecting a marker
  may pin the shared research time and open the existing Fields workspace; it
  never assigns polarity.
- Price drawing tools remain bound to the price pane; existing supported RSI
  drawing behavior is retained. The activity pane rejects price drawing tools.
- Existing chart capture continues to capture the root containing all native
  panes; no second chart or screenshot compositor was added.

## Activity Contract and Requests

The frontend consumes the existing `MO_UNSIGNED_EVENT_ACTIVITY_RANGE_V1_1`
request/response contract through the existing API client. No backend endpoint
or backend code changed.

Visible ranges map to fixed, half-open 14-day UTC chunks. The controller
debounces visible-range changes by 180 ms, loads only chunks intersecting the
visible range, bounds a request to at most 12 chunks, deduplicates in-flight
requests, merges immutable event/interval identities, and uses a 12-entry LRU
cache. Adjacent prefetch is intentionally disabled. Crosshair movement, marker
hover/click, mode changes, and marker visibility changes do not request data;
only entering uncached visible chunks can do so. This controller does not
trigger provider ingestion, MT5 capture, price snapshots, outcome reads, or
Candidate C.

## Coverage Semantics

- `KNOWN` with raw count `0` is rendered and labelled as `0 observed | coverage
  known`.
- `KNOWN` with a positive count reports the observed raw count and known
  coverage.
- `UNKNOWN` with a positive count preserves the observed count and explicitly
  labels coverage incomplete.
- `UNKNOWN` with count `0` is labelled `Coverage incomplete | no confirmed
  events`, never as an established zero.
- Incomplete ranges receive a distinct hatch over the observed step line. The
  hatch describes activity coverage only, not directional/polarity state.

The compact chart status says USD and JPY have no admitted polarity entries and
the pair is unavailable. The Fields tab remains the detailed research surface
and is not replaced or migrated.

## Layout and Compatibility

Chart layout state adds only `fieldsWaves.activityVisible`,
`fieldsWaves.activityMarkersVisible`, and `fieldsWaves.activityPaneHeight`.
New and legacy layouts default activity visibility to false; height is
normalized to 110-240 pixels. Data, events, coverage, cached chunks, and
crosshair state are not persisted. Existing RSI settings retain their prior
semantics.

## Verification

- Focused chart/layout/activity/Fields tests: 54 passed across 5 files.
- Full frontend: 229 passed across 47 files.
- TypeScript project build: passed through `npm run build` (`tsc -b`).
- Oxlint: passed.
- Vite production build: passed. The existing advisory about the 594.42 kB
  main chunk remains.
- Browser review used a local synthetic fixture only: price + activity,
  price + RSI + activity, activity hidden, known-zero, and incomplete-coverage
  states were inspected. USD/JPY count and coverage labels remained distinct;
  the shared chart crosshair and time axis aligned across panes.
- The existing `MarketChart.capture()` path was exercised on the same synthetic
  multi-pane chart and returned a non-empty PNG data URL; the captured preview
  includes the native chart composition without a separate compositor.
- No backend or Rust/Tauri tests were run because neither backend nor native
  source changed.
- `git diff --check`: recorded at finalization.

The visual fixture was temporary and removed before the final build. It used
synthetic candles and activity records and did not request backend data.

## Locks

No polarity catalogue, evidence registry, pair math, source doctrine, backend,
Candidate C, or EMP3 artifact changed. F4-C is not authorized. No provider was
accessed; no market data was captured or read; no outcomes were analyzed; no
empirical execution or MT5 order was invoked. `executionAllowed=false`.
