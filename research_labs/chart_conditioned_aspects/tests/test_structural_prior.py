from __future__ import annotations

from chart_conditioned_aspects.evaluation import compile_structural_prior

from conftest import make_structure


def test_same_transit_aspect_changes_with_chart_structure(profiles) -> None:
    taurus = make_structure(profiles, ascendant_sign="TAURUS")
    cancer = make_structure(profiles, ascendant_sign="CANCER")
    taurus_prior = compile_structural_prior(
        taurus,
        transit_body="SATURN",
        natal_target="MOON",
        aspect_type="square",
        profiles=profiles,
    )
    cancer_prior = compile_structural_prior(
        cancer,
        transit_body="SATURN",
        natal_target="MOON",
        aspect_type="square",
        profiles=profiles,
    )
    assert taurus_prior.directional_prior == "SUPPORTIVE"
    assert cancer_prior.directional_prior == "ADVERSE"
    assert taurus_prior.activation_prior == cancer_prior.activation_prior == "STRONG"
    assert taurus_prior.volatility_prior == cancer_prior.volatility_prior == "HIGH"
    assert taurus_prior.prior_hash != cancer_prior.prior_hash


def test_prior_preserves_missing_sources_and_never_executes(profiles) -> None:
    structure = make_structure(profiles)
    prior = compile_structural_prior(
        structure,
        transit_body="SATURN",
        natal_target="MOON",
        aspect_type="trine",
        profiles=profiles,
    )
    assert "TRAILOKYA_DIPIKA_1972_BLOCKED" in prior.unknowns
    assert "AGARWAL_FINANCIAL_COMPLETE_EDITION_BLOCKED" in prior.unknowns
    assert "TARGET_DOMAIN_TO_PRICE_POLARITY_NOT_CERTIFIED" in prior.unknowns
    assert prior.execution_allowed is False
    assert prior.automatic_order_placement is False
    aspect_entry = next(
        item for item in prior.explanation_ledger if item.entry_id == "ASPECT_GEOMETRY"
    )
    assert aspect_entry.directional_effect == "INDETERMINATE"
