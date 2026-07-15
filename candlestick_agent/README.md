# Candlestick Specialist

This is a separate, research-only specialist for OHLC candlestick analysis.

The specialist has three boundaries:

1. `candlestick_analysis.py` computes versioned deterministic geometry from closed
   bars and keeps hindsight fields separate from evidence available at the cutoff.
2. The local RAG service explains that packet using this dedicated corpus. Its raw
   text is untrusted and never becomes an official note automatically.
3. A future coordinator may compare candlestick evidence with Jyotish, SR, and Gann
   evidence. The candlestick specialist cannot alter Auto Suggest, the prospective
   ledger, or MT5 execution.

Build the local chunk file with:

```powershell
python candlestick_agent\build_corpus_index.py
```

Run the frozen USDJPY H1 retrospective evaluation with:

```powershell
python candlestick_agent\usdjpy_walk_forward.py
```

The study contract is `usdjpy_evaluation_contract_v1.json`. It locks the source
hash, decision and fill timing, holding period, spread/slippage costs,
chronological folds, purge/embargo rule, model thresholds, primary candidate,
and promotion gate before results are inspected. Generated datasets and reports
are written below `D:\GannFinancialAstro\validation` and remain uncommitted.

Even a passing retrospective gate leaves coordinator, Auto Suggest, shadow,
official-note, and execution authorization disabled.

The frozen V1 run on 2026-07-15 failed its retrospective gate. The primary
named-pattern model made zero trades because every out-of-sample probability
remained inside the predeclared abstention band. See
`candlestick_usdjpy_walk_forward_20260715.md`; this result is evidence against
promoting named patterns, not permission to retune V1 on the same folds.

Copyrighted books are registry references only unless the user supplies a lawful
local copy. No unofficial downloadable copy is fetched or committed.
