# Chat Session Backup - 2026-05-16 03:54 IST

- User flagged that `aspect_review_case_11_chart.html` had no candles near the selected March 7 event and only showed price candles around March 10.
- Confirmed this was not merely a non-trading-day gap: March 7, 2025 was Friday, but the M30 parquet starts at `2025-03-10 05:30 IST`.
- Confirmed the full H1 parquet covers the chart window and has 99 H1 bars from `2025-03-04 11:30 IST` through `2025-03-10 13:30 IST`.
- Updated `build_repeatation_review_pack.py` to check price coverage and fall back from M30 to H1 when M30 does not cover the case window/chart context.
- Regenerated the current served case 11 repeatation pack in place. Case `11` now uses H1 chart data and `price_timeframe=h1` in the marker template/annotation command.
- Browser verification showed March 5-7 candles visible around the selected case window after reload.
