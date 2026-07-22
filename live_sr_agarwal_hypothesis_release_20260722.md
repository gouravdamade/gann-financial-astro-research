# Live SR Lab and Agarwal Hypothesis Source

Date: 2026-07-22
Source version: 0.10.21

## Live SR Status

The planetary-line overlay is implemented end to end in the native desktop
source. Open it from the chart context bar with **Live SR**. This is separate
from the adjacent **SR** toggle, which shows the corrected artifact's existing
precomputed support/resistance lines.

Live SR Lab supports per-planet enablement, direct/mirror/both modes, multiple
`n`, `f`, and degree values, per-planet colors, and a 300/600/900/1200 visible
bar-time sample limit. It recalculates after a symbol/timeframe artifact
change, a new chart-bar payload, visible-range change, or parameter change.
Version 0.10.21 also adds an explicit recalculate icon and the response's
generated time.

The backend uses exact UTC bar timestamps and the Raman sidereal Swiss
Ephemeris contract. It fails closed above 96 lines, 1,200 timestamps, or
100,000 plotted points. The response contract explicitly prevents consumption
by Auto Suggest, live inference, the shadow ledger, and execution. This remains
an exploratory curve-fitting overlay, not a certified trading signal.

## Agarwal Source Decision

Three private files were audited:

- the 191-page image scan, SHA-256 `5644DFC4...`, is the incomplete underlying
  page-image source;
- the 94-page January 2012 ChiStaBo PDF, SHA-256 `8AF0045A...`, is an earlier
  edited derivative with explicit missing-page placeholders;
- the 95-page 2013 ChiStaBo v3 PDF, SHA-256 `D93B9B97...`, is another edited
  derivative with documented terminology changes, redrawn figures, and
  bracketed additions.

The derivatives are not independent witnesses and cannot repair the image
scan's missing printed pages 46-47, 54-55, 62-63, 133, and 144.

One bounded section is usable for private retrieval: image-scan PDF pages
177-191 are consecutive printed pages 180-194, Chapter 20, `Astrological Norms
for Financial Gain in Share Market`. All fifteen page images were visually
checked. A page-marked extract is stored outside Git at:

`D:\GannFinancialAstro\sources\private\derived\AGARWAL_FINANCIAL_CHAPTER20_PDF_PAGES_177_191_5644DFC4.txt`

The local RAG system classifies it as
`AGARWAL_FINANCIAL_CHAPTER20_HYPOTHESIS_20260722` in the
`hypothesis_reference` layer. Retrieval is opt-in for questions naming
Agarwal, Sarvatobhadra, financial astrology, share markets, or bullish/bearish
market hypotheses. It is never doctrine, source certification, deterministic
SBC scoring, official ML truth, Auto Suggest evidence, live inference input,
prospective-ledger input, or execution permission.

## Verification

- frontend lint: pass;
- frontend tests: all 71 tests executed and passed across the resource-bounded
  suite plus focused Chakra rerun;
- production TypeScript/Vite build: pass;
- backend tests: 117 passed;
- corpus/source tests: 13 passed;
- Rust tests: 18 passed;
- private corpus rebuild: 5,193 chunks; Agarwal hypothesis smoke query returns
  the page-marked chapter first;
- JSON/YAML/CSV source metadata validation: pass.

The existing Vite warning for a 524 KB main chunk is a performance follow-up,
not a functional or source-integrity failure.
