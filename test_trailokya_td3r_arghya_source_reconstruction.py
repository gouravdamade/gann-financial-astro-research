"""Golden tests for TD3R's fail-closed Trailokya Argha source components."""
from __future__ import annotations

import csv
import hashlib
from fractions import Fraction
from pathlib import Path

import yaml

from research_labs.trailokya_arghya.source_components import (
    apply_twenty_part_basis,
    full_source_calculator_ready,
    net_viswa,
    resolve_aspect_houses,
    resolve_five_category_viswa,
    resolve_relationship_viswa,
)


ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "configs/sbc/arghya/trailokya_1972_arghya_pass1_td3r_page_corrected.csv"
READINESS = ROOT / "configs/sbc/trailokya/trailokya_1972_td3r_readiness.yaml"


def test_td3r_table_is_literal_complete_and_has_corrected_1972_locators() -> None:
    assert hashlib.sha256(TABLE.read_bytes()).hexdigest().upper() == (
        "2BCAF0465A96DE7423A63A0EFA6F18D49815F7B5EB924C2C82DBC12A24E31360"
    )
    with TABLE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 108
    assert sum(row["table_id"] == "relationship_vedha_viswa" and row["pdf_page"] == "98" and row["printed_page"] == "82" for row in rows) == 32
    assert sum(row["table_id"] == "planet_aspect_houses" and row["pdf_page"] == "99" and row["printed_page"] == "83" for row in rows) == 36
    assert sum(row["table_id"] == "five_class_vedha_viswa" and row["pdf_page"] == "101" and row["printed_page"] == "85" for row in rows) == 40


def test_literal_anomalies_are_exact_and_never_regularized() -> None:
    known = resolve_relationship_viswa(
        aspect_strength="three_quarter", nature="MALEFIC", relation="NEUTRAL",
        vedha_hit=True, required_zodiacal_aspect=True,
    )
    assert known.state == "KNOWN"
    assert known.value == Fraction(47, 4)  # Literal 11|45, not the expected 11|15.
    repeated = resolve_five_category_viswa(
        aspect_strength="three_quarter", nature="MALEFIC", category_count=4,
    )
    assert repeated.state == "KNOWN"
    assert repeated.value == Fraction(23, 10)  # Literal 2|18, not the expected 2|24.


def test_verse_371_requires_aspect_and_never_substitutes_zero() -> None:
    blocked = resolve_relationship_viswa(
        aspect_strength="full", nature="BENEFIC", relation="OWN",
        vedha_hit=True, required_zodiacal_aspect=False,
    )
    assert blocked.state == "INACTIVE_NO_REQUIRED_ASPECT"
    assert blocked.value is None
    unknown = resolve_relationship_viswa(
        aspect_strength="full", nature="BENEFIC", relation="OWN",
        vedha_hit=True, required_zodiacal_aspect=None,
    )
    assert unknown.state == "UNKNOWN"
    assert unknown.value is None


def test_aspect_table_and_td2_separation_are_literal_and_profile_isolated() -> None:
    mars = resolve_aspect_houses(aspect_strength="full", planet="MARS")
    assert mars.state == "KNOWN"
    assert mars.input_provenance[0] == "4|8|7"
    assert mars.source_verses == ("365-370",)
    assert "TD2" not in " ".join(mars.input_provenance)


def test_netting_and_twenty_part_basis_keep_exact_fraction_units() -> None:
    benefic = resolve_relationship_viswa(
        aspect_strength="full", nature="BENEFIC", relation="OWN",
        vedha_hit=True, required_zodiacal_aspect=True,
    )
    malefic = resolve_relationship_viswa(
        aspect_strength="half", nature="MALEFIC", relation="FRIEND",
        vedha_hit=True, required_zodiacal_aspect=True,
    )
    net = net_viswa(benefic, malefic)
    assert net.value == Fraction(15, 1)
    basis = apply_twenty_part_basis(net)
    assert basis.value == Fraction(35, 1)
    assert basis.unit == "CURRENT_COMMODITY_BASIS_PARTS"
    assert "PRICE_FORECAST" in basis.prohibited_uses


def test_unknown_propagates_and_full_calculator_stays_fail_closed() -> None:
    assert net_viswa(None, None).state == "UNKNOWN"
    assert apply_twenty_part_basis(None).state == "UNKNOWN"
    assert full_source_calculator_ready() is False
    readiness = yaml.safe_load(READINESS.read_text(encoding="utf-8"))
    assert readiness["TD3R_ARGHA_SOURCE_CALCULATOR_READY"] is False
    assert all(value is False for value in readiness["locks"].values())
