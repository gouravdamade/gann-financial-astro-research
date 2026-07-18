from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from instrument_relative_sbc import (
    InstrumentIdentity,
    RuleRecord,
    SourceCitation,
    UncertaintySummary,
    aggregate_component_score,
    build_currency_score,
    derive_fx_pair_score,
    load_experimental_profile,
    validate_currency_invariants,
    validate_rule_profile,
)


NOW = datetime(2026, 7, 18, tzinfo=timezone.utc)
PROFILE_PATH = Path(__file__).parents[1] / "profiles" / "fx_relative_experimental_v1.yaml"


def currency(code: str, score: float | None):
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


def pair(symbol: str, base: str, quote: str) -> InstrumentIdentity:
    return InstrumentIdentity(
        instrument_id=f"fx:{symbol}",
        symbol=symbol,
        asset_class="fx_pair",
        legal_name=symbol,
        base_currency=base,
        quote_currency=quote,
    )


def test_profile_is_execution_locked() -> None:
    profile = load_experimental_profile(PROFILE_PATH)
    assert profile.status == "experimental"
    assert profile.execution_allowed is False
    assert profile.promotion_allowed is False
    assert profile.component_weights["sbc_identity"] == 1.0


def test_aggregate_uses_enabled_available_components_only() -> None:
    value = aggregate_component_score(
        {"sbc_identity": 2.0, "currency_event": None, "country_mundane": 100.0},
        {"sbc_identity": 1.0, "currency_event": 1.0, "country_mundane": 0.0},
    )
    assert value == 2.0
    assert aggregate_component_score({"missing": None}, {"missing": 1.0}) is None


def test_pair_derivation_uses_metadata_and_preserves_unknown() -> None:
    usd = currency("USD", 2.0)
    jpy = currency("JPY", 0.5)
    result = derive_fx_pair_score(pair("USDJPY", "USD", "JPY"), usd, jpy, no_edge_threshold=0.35)
    assert result.differential == 1.5
    assert result.direction_hypothesis == "base_outperformance"
    assert result.execution_allowed is False

    missing = derive_fx_pair_score(
        pair("USDJPY", "USD", "JPY"),
        currency("USD", None),
        jpy,
        no_edge_threshold=0.35,
    )
    assert missing.differential is None
    assert missing.direction_hypothesis == "unknown"


def test_pair_rejects_ticker_guess_or_wrong_currency_order() -> None:
    with pytest.raises(ValueError, match="explicit pair metadata"):
        derive_fx_pair_score(
            pair("USDJPY", "JPY", "USD"),
            currency("USD", 2.0),
            currency("JPY", 0.5),
            no_edge_threshold=0.35,
        )


def test_latent_scores_satisfy_inversion_identity_and_triangle() -> None:
    scores = {
        "EUR": currency("EUR", 2.4),
        "USD": currency("USD", -1.1),
        "JPY": currency("JPY", 0.6),
    }
    assert validate_currency_invariants(scores) == []
    assert (2.4 - -1.1) + (-1.1 - 0.6) == pytest.approx(2.4 - 0.6)


def test_classical_profile_rejects_experimental_source() -> None:
    citation = SourceCitation(
        source_id="NOTE",
        title="Modern mapping",
        source_tier="experimental_note",
        locator="record 1",
    )
    rule = RuleRecord(
        rule_id="R1",
        rule_family="sbc_vedha",
        profile_id="classical",
        status="provisional",
        source_citations=(citation,),
        normalized_condition={},
        normalized_effect={},
        confidence=0.5,
    )
    with pytest.raises(ValueError, match="non-classical"):
        validate_rule_profile((rule,), profile_kind="classical")
