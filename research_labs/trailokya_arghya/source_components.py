"""Fail-closed, source-bounded Trailokya 1972 Argha arithmetic components.

This module deliberately does not select a ruler, generate Vedha, calculate a
price, or emit a market interpretation.  It only exposes source-closed table
lookups and arithmetic stages after their inputs have been supplied with their
own provenance.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Literal

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLE_CONTRACT_PATH = (
    PROJECT_ROOT / "configs" / "sbc" / "trailokya" / "trailokya_1972_argha_viswa_table_v1.yaml"
)
OPERATOR_READINESS_PATH = (
    PROJECT_ROOT / "configs" / "sbc" / "trailokya" / "trailokya_1972_argha_operator_v1.yaml"
)
COMPONENT_VERSION = "TRAILOKYA_1972_ARGHA_SOURCE_COMPONENTS_V1"


@dataclass(frozen=True)
class SourceComponentResult:
    state: Literal["KNOWN", "UNKNOWN", "INACTIVE_NO_REQUIRED_ASPECT"]
    value: Fraction | None
    unit: str
    source_verses: tuple[str, ...]
    source_pages: tuple[int, ...]
    source_status: str
    calculation_version: str
    input_provenance: tuple[str, ...]
    unknown_reasons: tuple[str, ...]
    prohibited_uses: tuple[str, ...] = (
        "PRICE_FORECAST", "FX_MAPPING", "POLARITY", "SCORE", "FIELDS_POLARITY",
        "AUTO_SUGGEST", "ML", "MT5", "EXECUTION",
    )


def _unknown(*reasons: str, unit: str = "SOURCE_UNIT") -> SourceComponentResult:
    return SourceComponentResult(
        state="UNKNOWN", value=None, unit=unit, source_verses=(), source_pages=(),
        source_status="UNKNOWN_DEPENDENCY", calculation_version=COMPONENT_VERSION,
        input_provenance=(), unknown_reasons=tuple(reasons),
    )


def _fraction_from_viswa_kala(token: str) -> Fraction:
    major, kala = token.split("|", 1)
    return Fraction(int(major), 1) + Fraction(int(kala), 60)


def _load_table_rows() -> dict[tuple[str, str, str], dict[str, str]]:
    contract = yaml.safe_load(TABLE_CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract["contractId"] != "TRAILOKYA_1972_ARGHA_VISWA_TABLE_SOURCE_V1":
        raise ValueError("Unexpected Trailokya Argha table contract")
    if contract["executionAllowed"] is not False:
        raise ValueError("Trailokya Argha source components must remain execution locked")
    path = PROJECT_ROOT / contract["source"]["primary"]["transcription"]["path"]
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 108:
        raise ValueError("Trailokya Argha table must contain exactly 108 literal rows")
    return {(row["table_id"], row["row_key"], row["column_key"]): row for row in rows}


def resolve_relationship_viswa(
    *, aspect_strength: str | None, nature: Literal["BENEFIC", "MALEFIC"] | None,
    relation: Literal["OWN", "FRIEND", "NEUTRAL", "ENEMY"] | None,
    vedha_hit: bool | None, required_zodiacal_aspect: bool | None,
) -> SourceComponentResult:
    """Resolve the literal relationship table after the verse-371 aspect gate."""
    if None in (aspect_strength, nature, relation, vedha_hit, required_zodiacal_aspect):
        return _unknown("RELATIONSHIP_OR_ASPECT_GATE_INPUT_MISSING", unit="VISWA_KALA")
    if not vedha_hit:
        return _unknown("VEDHA_HIT_ABSENT", unit="VISWA_KALA")
    if not required_zodiacal_aspect:
        return SourceComponentResult(
            state="INACTIVE_NO_REQUIRED_ASPECT", value=None, unit="VISWA_KALA",
            source_verses=("371",), source_pages=(84,),
            source_status="SOURCE_CLOSED_HARD_GATE", calculation_version=COMPONENT_VERSION,
            input_provenance=("GEOMETRIC_VEDHA", "ZODIACAL_ASPECT_GATE"), unknown_reasons=(),
        )
    row = _load_table_rows().get(
        ("relationship_vedha_viswa", aspect_strength, f"{nature.lower()}_{relation.lower()}")
    )
    if row is None:
        return _unknown("LITERAL_RELATIONSHIP_TABLE_CELL_MISSING", unit="VISWA_KALA")
    return SourceComponentResult(
        state="KNOWN", value=_fraction_from_viswa_kala(row["raw_token"]), unit="VISWA_KALA",
        source_verses=("362-364",), source_pages=(82,),
        source_status="SOURCE_CLOSED_LITERAL_TABLE", calculation_version=COMPONENT_VERSION,
        input_provenance=(row["raw_token"], row["source_id"], row["transcription_pass"]), unknown_reasons=(),
    )


def resolve_aspect_houses(*, aspect_strength: str | None, planet: str | None) -> SourceComponentResult:
    if aspect_strength is None or planet is None:
        return _unknown("ASPECT_TABLE_INPUT_MISSING", unit="WHOLE_SIGN_HOUSE_LIST")
    row = _load_table_rows().get(("planet_aspect_houses", aspect_strength, planet.lower()))
    if row is None:
        return _unknown("LITERAL_ASPECT_TABLE_CELL_MISSING", unit="WHOLE_SIGN_HOUSE_LIST")
    houses = tuple(int(value) for value in row["raw_token"].split("|") if value != "0")
    return SourceComponentResult(
        state="KNOWN", value=None, unit="WHOLE_SIGN_HOUSE_LIST",
        source_verses=("365-370",), source_pages=(83,),
        source_status="SOURCE_CLOSED_LITERAL_TABLE", calculation_version=COMPONENT_VERSION,
        input_provenance=(row["raw_token"], *tuple(str(house) for house in houses)), unknown_reasons=(),
    )


def resolve_five_category_viswa(
    *, aspect_strength: str | None, nature: Literal["BENEFIC", "MALEFIC"] | None,
    category_count: int | None,
) -> SourceComponentResult:
    """Resolve the literal five-category Viswa table without regularization."""
    if aspect_strength is None or nature is None or category_count is None:
        return _unknown("FIVE_CATEGORY_TABLE_INPUT_MISSING", unit="VISWA_KALA")
    if not 1 <= category_count <= 5:
        return _unknown("FIVE_CATEGORY_COUNT_OUT_OF_SOURCE_RANGE", unit="VISWA_KALA")
    row = _load_table_rows().get(
        ("five_class_vedha_viswa", aspect_strength, f"{nature.lower()}_{category_count}")
    )
    if row is None:
        return _unknown("LITERAL_FIVE_CATEGORY_TABLE_CELL_MISSING", unit="VISWA_KALA")
    return SourceComponentResult(
        state="KNOWN", value=_fraction_from_viswa_kala(row["raw_token"]), unit="VISWA_KALA",
        source_verses=("372-374",), source_pages=(85,),
        source_status="SOURCE_CLOSED_LITERAL_TABLE", calculation_version=COMPONENT_VERSION,
        input_provenance=(row["raw_token"], row["source_id"], row["transcription_pass"]), unknown_reasons=(),
    )


def net_viswa(
    benefic_viswa: SourceComponentResult | None, malefic_viswa: SourceComponentResult | None,
) -> SourceComponentResult:
    if benefic_viswa is None or malefic_viswa is None:
        return _unknown("BENEFIC_OR_MALEFIC_COMPONENT_MISSING", unit="VISWA_KALA")
    if benefic_viswa.state != "KNOWN" or malefic_viswa.state != "KNOWN":
        return _unknown("BENEFIC_OR_MALEFIC_COMPONENT_NOT_KNOWN", unit="VISWA_KALA")
    if benefic_viswa.value is None or malefic_viswa.value is None:
        return _unknown("BENEFIC_OR_MALEFIC_VALUE_MISSING", unit="VISWA_KALA")
    return SourceComponentResult(
        state="KNOWN", value=benefic_viswa.value - malefic_viswa.value, unit="VISWA_KALA",
        source_verses=("375",), source_pages=(85,), source_status="SOURCE_CLOSED_ARGHYA_ONLY_NETTING",
        calculation_version=COMPONENT_VERSION,
        input_provenance=benefic_viswa.input_provenance + malefic_viswa.input_provenance,
        unknown_reasons=(),
    )


def apply_twenty_part_basis(net_result: SourceComponentResult | None) -> SourceComponentResult:
    """Apply verse 376's commodity-basis arithmetic, never a price conversion."""
    if net_result is None or net_result.state != "KNOWN" or net_result.value is None:
        return _unknown("NET_VISWA_NOT_KNOWN", unit="CURRENT_COMMODITY_BASIS_PARTS")
    return SourceComponentResult(
        state="KNOWN", value=Fraction(20, 1) + net_result.value,
        unit="CURRENT_COMMODITY_BASIS_PARTS", source_verses=("376",), source_pages=(86,),
        source_status="SOURCE_CLOSED_COMMODITY_BASIS_ARITHMETIC_NOT_PRICE", calculation_version=COMPONENT_VERSION,
        input_provenance=net_result.input_provenance + ("BASE_20_PARTS",), unknown_reasons=(),
    )


def full_source_calculator_ready() -> bool:
    readiness = yaml.safe_load(OPERATOR_READINESS_PATH.read_text(encoding="utf-8"))
    return readiness["fullSourceCalculatorReady"] is True
