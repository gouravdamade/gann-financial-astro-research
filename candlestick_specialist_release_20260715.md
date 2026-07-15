# Gann Astro Desk 0.10.0 Candlestick Specialist Release

Date: 2026-07-15

## Decision

Candlestick analysis is implemented as a separate specialist, not as additional
Jyotish prompt material. It has its own deterministic evidence packet, corpus,
retrieval policy, prompt, model setting, verifier, API contract, and Analyze Aspect
tab. It shares the installed Ollama process and defaults to the same lightweight
`qwen2.5:3b` model only to avoid duplicating GPU memory on this laptop.

This boundary prevents candle vocabulary from becoming astrology doctrine and
prevents either local model from silently blending evidence. A future coordinator
may compare the specialists after each has independent out-of-sample validation;
it must not merge their source corpora or promote agreement into proof.

## Deterministic Evidence

- Contract: `GANN_CANDLESTICK_EVIDENCE_V1`.
- Method: `transparent_ohlc_geometry_v1`.
- Invalid OHLC rows are rejected before analysis.
- Only bars fully closed by the selected timestamp cutoff are evidence.
- A selected chart annotation can supply the cutoff; otherwise the event end is
  used.
- The packet records raw open/high/low/close, range and body in pips, body fraction,
  upper/lower wick fraction, close location, ATR14, and a five-bar prior trend.
- Transparent geometry labels cover doji, spinning top, marubozu-like, long-body,
  long-wick context, body engulfing, inside bar, and outside bar. The exact formula
  basis accompanies each label.
- Up to six bars after the cutoff are placed in a separately labeled retrospective
  object and cannot masquerade as information available at the decision time.
- Every packet locks consumption by live inference, Auto Suggest, the shadow ledger,
  official ML notes, and execution.

The implementation intentionally does not claim TA-Lib parity. TA-Lib remains a
method-name and implementation reference, while Gann Astro Desk exposes its own
thresholds so every classification can be audited.

## Local Specialist

- Draft contract: `GANN_LOCAL_CANDLE_RAG_DRAFT_V1`.
- Independent configuration:
  - `GANN_ASTRO_CANDLE_LLM_MODEL` selects the candle model;
  - `GANN_ASTRO_CANDLE_CORPUS` selects the candle corpus.
- Packaged corpus: three locally authored chunks covering transparent methods,
  mixed empirical evidence, and source/copyright provenance.
- Copyrighted books remain registry-only until the user supplies a lawful local
  copy. No unofficial copy is downloaded or committed.
- The prompt prohibits invented OHLC, certainty, execution language, TA-Lib parity,
  and unlabelled hindsight.
- The verifier checks source IDs, focus-bar pattern drift, unsupported certainty,
  execution-like language, and method claims. If the small local model omits source
  IDs, code appends a visible deterministic citation footer and reports that repair.
- Deterministic evidence still renders when Ollama is unavailable.

## Source Review

Primary and publisher sources reviewed for this release:

- TA-Lib pattern-recognition functions:
  https://ta-lib.org/functions/
- Steve Nison, *Japanese Candlestick Charting Techniques*, publisher record:
  https://www.penguinrandomhouse.com/books/350650/japanese-candlestick-charting-techniques-by-steve-nison/
- Marshall, Young, and Rose, negative DJIA-stock test:
  https://doi.org/10.1016/j.jbankfin.2005.08.001
- Lu, Chen, and Hsu, holding-strategy/trend-definition sensitivity:
  https://doi.org/10.1016/j.jbankfin.2015.09.009
- Author working-paper copy for the Lu, Chen, and Hsu study:
  https://www.econ.sinica.edu.tw/~econ/pdfPaper/14-A010.pdf

The research record is deliberately mixed. One peer-reviewed study found no value
for its tested DJIA strategies, while another showed that reported results change
materially with trend and holding definitions. Therefore named patterns are feature
hypotheses, not universal bullish/bearish signals, and USDJPY must be tested with
purged chronological splits, costs, and explicit holding rules.

## Native UI

Analyze Aspect now contains five compact inspector tabs: Evidence, Notes, Candles,
Local Jyotish, and Codex. The Candles tab displays the cutoff, closed-bar count,
focus-bar OHLC and geometry, ATR/prior trend, named geometry with formula basis,
event-window summary, collapsed retrospective bars, local-model composer, citations,
verifier issues, and deterministic repairs.

Native visual QA confirmed that the tabs and evidence fit the Tauri analysis window
without overlap. A real USDJPY event loaded a bearish focus bar with doji and
spinning-top geometry, and the local specialist action was available independently
of the Jyotish tab.

## Verification

- Candlestick-focused Python tests: 10 passed.
- Full backend suite: 55 passed. The real-generator test deadline is 90 seconds so
  normal Windows load does not turn a completed 34-second generator run into a false
  timeout; production generation behavior is unchanged.
- Frontend Vitest suite: 18 passed.
- Oxlint, TypeScript/Vite build, Ruff, and Python byte compilation passed.
- PowerShell packaging scripts parsed successfully.
- Rust formatting, `cargo check`, Rust tests, and Clippy with warnings denied passed.
- Real repository event evidence smoke passed.
- Real Flask plus Ollama smoke passed with `qwen2.5:3b`; the final draft verifier
  passed after the deterministic citation-footer repair.
- Full native crash/recovery soak passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.0_20260715_143548\logs\native_soak_report.json`.
- Stable-path native smoke passed:
  `D:\GannFinancialAstro\soak\tauri_0.10.0_20260715_143913\logs\native_soak_report.json`.
- Both soaks confirmed `tradeAllowed=false`, candlestick corpus/evidence contracts,
  closed-bar-only evidence, all live/shadow/execution locks, and no surviving child
  processes.

## Release Artifacts

- Stable executable:
  `D:\GannFinancialAstro\release\GannAstroDesk\GannAstroDesk.exe`
- Executable SHA-256:
  `8E3545DA8E9176088C08D25E7323D808F0A3FA99FEAC7D0830BC5E6486E2D161`
- NSIS installer:
  `D:\GannFinancialAstro\release\GannAstroDesk\Gann Astro Desk_0.10.0_x64-setup.exe`
- Installer SHA-256:
  `A0CA5A58722F4C8D270EED09344381EF2F87414539CECDD5A7BC47F221B4212E`
- Immediate pre-final-verifier rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.10.0_pre_final_verifier_20260715_200811`
- Previous-release rollback archive:
  `D:\GannFinancialAstro\release_archive\GannAstroDesk_0.9.2_20260715_113545`
- Pre-promotion live-state backup:
  `D:\GannFinancialAstro\state_backups\pre_0.10.0_promotion_20260715_113545`

The promoted tree contains 1,453 files including the manifest. The executable and
installer hashes match the candidate and promoted manifest. The installer is not
code-signed.

## Next Gate

Build a timestamp-safe USDJPY candle evaluation dataset before any coordinator is
allowed to use this specialist. Compare raw OHLC geometry, named-pattern features,
and simple price-only baselines on purged chronological splits; freeze trend,
confirmation, holding, and cost definitions before measuring results. Only stable
out-of-sample improvement may justify a coordinator-facing candle feature. No
candlestick draft or pattern currently changes a trade decision.
