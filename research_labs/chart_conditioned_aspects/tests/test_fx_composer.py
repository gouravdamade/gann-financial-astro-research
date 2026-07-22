from __future__ import annotations

from datetime import datetime, timezone

from chart_conditioned_aspects.fx_composer import compose_fx_pair_score
from instrument_relative_sbc import (
    InstrumentIdentity,
    UncertaintySummary,
    build_currency_score,
    validate_currency_invariants,
)


NOW = datetime(2026, 7, 22, tzinfo=timezone.utc)


def currency(code: str, score: float):
    return build_currency_score(
        currency=code,
        timestamp_utc=NOW,
        profile_id="fx_relative_experimental_v1",
        sbc_identity_score=score,
        currency_event_scores={},
        central_bank_scores={},
        country_scores={},
        mundane_domain_score=None,
        component_weights={"sbc_identity": 1.0},
        contributions=(),
        uncertainty=UncertaintySummary(),
    )


def identity(symbol: str, base: str, quote: str) -> InstrumentIdentity:
    return InstrumentIdentity(
        instrument_id=f"fx:{symbol}",
        symbol=symbol,
        asset_class="fx_pair",
        legal_name=symbol,
        base_currency=base,
        quote_currency=quote,
    )


def test_fx_bridge_reuses_base_minus_quote_and_invariants() -> None:
    scores = {
        "USD": currency("USD", 1.2),
        "JPY": currency("JPY", -0.4),
        "EUR": currency("EUR", 0.5),
    }
    result = compose_fx_pair_score(
        identity("USDJPY", "USD", "JPY"),
        scores["USD"],
        scores["JPY"],
        no_edge_threshold=0.1,
    )
    inverse = compose_fx_pair_score(
        identity("JPYUSD", "JPY", "USD"),
        scores["JPY"],
        scores["USD"],
        no_edge_threshold=0.1,
    )
    assert result.differential == 1.6
    assert inverse.differential == -1.6
    assert result.differential == -inverse.differential
    assert validate_currency_invariants(scores) == []
    assert result.execution_allowed is False
