from __future__ import annotations

from chart_conditioned_aspects.natal import compile_natal_structure

from conftest import make_chart, make_snapshot, make_structure


def test_same_saturn_has_different_chart_conditioned_role(profiles) -> None:
    taurus = make_structure(profiles, ascendant_sign="TAURUS")
    cancer = make_structure(profiles, ascendant_sign="CANCER")
    taurus_saturn = next(role for role in taurus.roles if role.planet == "SATURN")
    cancer_saturn = next(role for role in cancer.roles if role.planet == "SATURN")
    assert taurus_saturn.owned_houses == (9, 10)
    assert taurus_saturn.functional_class == "SUPPORTIVE"
    assert "YOGAKARAKA_CANDIDATE" in taurus_saturn.flags
    assert cancer_saturn.owned_houses == (7, 8)
    assert cancer_saturn.functional_class == "ADVERSE"


def test_date_only_chart_disables_house_lordship(profiles) -> None:
    chart = make_chart(chart_id="DATE-ONLY", time_accuracy="DATE_ONLY_STABLE_MOON")
    structure = compile_natal_structure(chart, make_snapshot(chart), profiles)
    assert all(role.functional_class == "UNKNOWN" for role in structure.roles)
    assert all(not role.owned_houses for role in structure.roles)
    assert (
        "FUNCTIONAL_LORDSHIP_AND_HOUSE_DOMAINS_DISABLED_BY_TIME_ACCURACY"
        in structure.unknowns
    )
