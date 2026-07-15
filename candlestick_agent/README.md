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

Copyrighted books are registry references only unless the user supplies a lawful
local copy. No unofficial downloadable copy is fetched or committed.
