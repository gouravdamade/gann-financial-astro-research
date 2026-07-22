from __future__ import annotations

from instrument_relative_sbc.models import (
    CurrencyScore,
    FxPairScore,
    InstrumentIdentity,
)
from instrument_relative_sbc.scoring import (
    derive_fx_pair_score,
    validate_currency_invariants,
)


def compose_fx_pair_score(
    identity: InstrumentIdentity,
    base: CurrencyScore,
    quote: CurrencyScore,
    *,
    no_edge_threshold: float,
) -> FxPairScore:
    """Delegate numeric FX composition to the certified experimental FX foundation.

    Chart-conditioned categorical priors are intentionally not converted to hidden
    numbers here. Any future mapping must be registered and validated separately.
    """

    return derive_fx_pair_score(
        identity,
        base,
        quote,
        no_edge_threshold=no_edge_threshold,
    )


__all__ = ["compose_fx_pair_score", "validate_currency_invariants"]
