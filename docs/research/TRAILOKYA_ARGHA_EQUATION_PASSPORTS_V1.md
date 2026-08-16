# Trailokya Argha Equation Passports V1

All notation below is modern formalization for auditable engineering. It is not claimed to be literal algebra printed in the 1972 source.

## Kshetra Bala

- **Source:** verse 358, printed p.80.
- **Literal record:** own/friend/neutral/enemy are `4/4`, `3/4`, `2/4`, `1/4`; strength diminishes proportionally away from a sign midpoint.
- **Modern formalization:** `K = base(relation) * m`, where `m` is a proposed linear midpoint factor.
- **Range:** `0 <= K <= 1` only after an explicit longitude convention is supplied.
- **Engineering dependencies:** exact sign midpoint and distance normalization.
- **Unknown behavior:** no supplied convention means `UNKNOWN`.
- **Status:** partial for timestamped computation.
- **Prohibited uses:** ruler selection runtime, price/FX/polarity/score/execution.

## Vakra and Udaya Bala

- **Source:** verse 359, printed p.80.
- **Literal record:** full at the middle of the condition; zero at its beginning/end; use trairashika.
- **Modern formalization:** `V = maximum * triangular(progress)`.
- **Boundary:** 0 at progress 0 and 1, maximum at 1/2.
- **Unknown behavior:** absence of source-closed begin/end timestamps or midpoint policy means `UNKNOWN`.
- **Status:** mathematical form recorded; astronomy event provider unresolved.

## Uccha Bala

- **Source:** verse 360, printed p.80.
- **Literal record:** maximum exaltation is full, maximum debilitation is half; intermediate cases use trairashika.
- **Modern formalization:** source-dependent interpolation between the stated extremes.
- **Unknown behavior:** no source-closed paramocca location table in the TD3 scope means `UNKNOWN`.
- **Status:** partial.

## Relationship and Aspect Viswa

- **Source:** verses 362-371, printed pp.82-84.
- **Modern formalization:** `W_relation = literal_table(aspect_pada, nature, relation)` after `Vedha AND required_aspect`.
- **Unit:** exact `VISWA_KALA`; internal representation is a rational number.
- **Boundary:** no required aspect returns `INACTIVE_NO_REQUIRED_ASPECT`, never zero.
- **Status:** source-closed literal tables and gate.

## Five-category Viswa

- **Source:** verses 372-374, printed p.85.
- **Modern formalization:** table lookup only; no implied table regularization.
- **Unit:** exact `VISWA_KALA`.
- **Status:** source-closed literal table, with two marked source anomalies.

## Argha Residual

- **Source:** verse 375, printed p.85.
- **Modern formalization:** `R = V_benefic - V_malefic`.
- **Unit:** `VISWA_KALA`.
- **Scope:** Argha only, not a generic SBC cancellation operator.
- **Unknown behavior:** any unknown component propagates `UNKNOWN`.

## Twenty-part Commodity Basis

- **Source:** verse 376, printed p.86.
- **Modern formalization:** `A = 20 + R`.
- **Unit:** `CURRENT_COMMODITY_BASIS_PARTS`, not money, percent, return or price.
- **Source semantics:** above/below the basis concerns historical abundance/scarcity and cheapness/dearness in commodity context.
- **Falsification/reproduction:** a complete historical source example containing every upstream input is required; none was located in the held witnesses.
- **Prohibited uses:** direct price conversion, FX/equity mapping, polarity, score, Auto Suggest, ML, MT5 and execution.
