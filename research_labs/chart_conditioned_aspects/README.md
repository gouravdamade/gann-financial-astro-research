# Chart-Conditioned Planetary Aspect Research Lab

This package implements Milestone 1 of the chart-conditioned aspect-polarity
specification as an isolated, execution-locked research layer. It does not
modify production Auto Suggest, MT5 execution, support/resistance logic, or the
existing SBC runtime.

## Implemented

- Versioned organization-chart hypotheses with source provenance, effective
  dates, explicit human acceptance, and exact/date-only/unknown time gates.
- Provisional Parashari functional-lordship roles derived from a locked profile.
- Modern financial-domain translations stored separately from classical rules.
- Immutable natal graphs containing only configured conjunction geometry,
  dispositors, lordship, and house occupancy.
- Static aspect priors with separate direction, activation, and volatility.
- An explicit transit-to-natal event adapter that rejects ambiguous role
  recovery, transit-to-transit events, outcome fields, future-return fields,
  and out-of-profile orbs.
- Bounded graph activation and timestamp-safe dynamic evaluation that preserves
  conflicts instead of forcing a single answer.
- An FX bridge that delegates numeric base-minus-quote composition and invariant
  checks to `research_labs/instrument_relative_sbc`.
- Strict JSON schemas and adversarial tests.

## Deliberately Blocked

- Any executable rules attributed to the missing complete Agarwal financial
  edition.
- Any executable rules attributed to the missing *Trailokya Dipika* source.
- Configured special drishti, yoga edges, full dignity/friendship tables, and a
  financial-domain-to-price polarity map until page-level doctrine is certified.
- Numeric fitting, market-label learning, UI integration, live trading, and
  automatic promotion.

Unknown means unknown. Missing evidence is never converted to zero, neutral, or
a hidden directional weight.

## Run

```powershell
python -m pytest research_labs\chart_conditioned_aspects\tests -q
python -m ruff check research_labs\chart_conditioned_aspects
```

The root `pytest.ini` includes this lab in normal repository test discovery.
