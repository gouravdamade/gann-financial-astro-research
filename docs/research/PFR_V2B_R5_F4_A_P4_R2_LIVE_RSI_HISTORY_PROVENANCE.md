# PFR-V2B-R5-F4-A-P4-R2 Live RSI History Source-Provenance Correction

Milestone: `PFR-V2B-R5-F4-A-P4-R2`

Starting commit: `b126714387085e8cb1047f9c0c70c89d6735d7ec`

Implementation commit: `136e42c6f473146bae24c3654e8df150622189df`

Branch: `research/pfr-v2b-r5-f4-a-p4-r2-live-rsi-history-provenance`

## Disposition

R1 correctly repaired the research chart path by adding bounded historical OHLC
context for RSI initialization. R1 did not close the live-source contract:
the live route replaced only `candles` with MT5 bars after obtaining a USDJPY
payload from `AstroRepository`, leaving repository-derived `indicatorHistory`
in the response. That mixed MT5 visible price data with corrected research
warm-up data.

R2 supersedes that live-path finding only. The research path remains accepted;
the R1 record is retained with status
`REQUIRES_LIVE_SOURCE_PROVENANCE_CORRECTION`.

## Root Cause

`GET /api/chart?source=live` previously called `gateway.bars(...)`, then used
`repository.chart_payload(...)` for USDJPY overlays and overwrote only
`payload["candles"]`. Because the repository payload also contained
`indicatorHistory`, RSI could be initialized from a different source family
than the visible MT5 candles.

## Correction Contract

The live route now makes one bounded MT5 bar request:

```text
requested count = visible_count + INDICATOR_HISTORY_MAX_BARS
visible_count   = clamp(requested liveBarCount, 1, 5000)
INDICATOR_HISTORY_MAX_BARS = 1000
```

The returned sequence is split without a second data request:

- the final `visible_count` bars are the visible price candles;
- only the immediately preceding bars are eligible for RSI history;
- history is capped at the latest 1,000 preceding bars;
- history ends strictly before the first visible candle;
- if fewer than `visible_count` bars are returned, all returned bars remain
  visible and history is empty;
- no bar is duplicated across the two channels.

The response always publishes `dataSource=mt5_live` and replaces both
`candles` and `indicatorHistory.candles`. The latest MT5 bar is preserved as
returned; R2 does not change open-bar or closed-bar semantics.

For USDJPY, the repository may still provide astronomy/aspect and support/
resistance overlay data, but repository candles and repository RSI history
cannot survive into the live payload. For non-USDJPY, no repository chart
payload is requested at all. Live RSI input therefore remains MT5-originated
for every supported symbol and timeframe.

The research path continues to use the R1 corrected research source and its
existing replay cutoff contract. R2 does not alter the RSI formula, levels,
warm-up policy, visible range, or chart layout.

## Verification Coverage

The R2 backend tests prove:

- exactly one gateway fetch for a live chart and the requested bounded count;
- USDJPY visible candles and RSI history both come from the MT5 response;
- repository overlay candles cannot leak into either live channel;
- strict history/visible timestamp separation and no duplicate boundary;
- the 1,000-bar history cap;
- limited and insufficient history behavior;
- non-USDJPY live charts skip the research repository overlay;
- H1, H4, D1, and W1 preserve the same source boundary.

Focused live-route backend result: **6/6 passed**. The focused chart/RSI,
repository, layout, timeframe, market-synthesis, gateway, and live-route
backend set passed **47/47**.

The R1 frontend RSI/chart regression remains the prior accepted result, and was
re-run unchanged: focused frontend **75/75** and full frontend **254/254**
across 49 files. TypeScript, Oxlint, Vite production build, `cargo fmt
--check`, and `cargo check --release` passed. R2 does not change frontend
source code; the frontend uses the existing optional history channel.

The native development build passed from the R2 source commit using the
inherited package metadata version `0.10.67-pfr-v2b-r5-f4-a-p3-r2`:

- portable: `D:\Rust\targets\release\gann-astro-desk.exe`, SHA-256
  `612D2A64741950E5676CBEFC40C80EFA4690C6BD2BF5C248CCF7C3018E66DD46`;
- installer: `D:\Rust\targets\release\bundle\nsis\Gann Astro Desk_0.10.67-pfr-v2b-r5-f4-a-p3-r2_x64-setup.exe`,
  SHA-256
  `E9F1BBDF9743554CC80F094D4485ABE9074DDF8C665C3B31F1E27C97A14EB72E`.

This is a development verification artifact, not a new immutable Windows
candidate. Native visual control remained unavailable.

Native visual control was unavailable for this source-only correction, so no
founder visual acceptance is claimed. The immutable P4 candidate was not
overwritten.

## Preserved Locks

`rsiFormulaChanged=false`

`closedBarSemanticsChanged=false`

`lookAheadAllowed=false`

`visibleRangeChanged=false`

`fieldsWavesChanged=false`

`activityMathChanged=false`

`pairMathChanged=false`

`polarityCatalogueChanged=false`

`evidenceRegistryChanged=false`

`f4bImplemented=false`

`f4cImplemented=false`

`candidateCChanged=false`

`emp3Authorized=false`

`providerAccess=false`

`outcomeAnalysis=false`

`mt5OrderInvocation=false`

`executionAllowed=false`

No Fields/Waves/activity, pair, polarity, Candidate C, EMP3, outcome, order,
or execution behavior is changed by R2.

## Next Gate

`CENTRAL_REVIEW_PFR_V2B_R5_F4_A_P4_R2_LIVE_RSI_HISTORY_PROVENANCE`
