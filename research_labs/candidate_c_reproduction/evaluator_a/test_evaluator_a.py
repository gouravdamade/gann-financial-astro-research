from __future__ import annotations

from copy import deepcopy

import pytest

from research_labs.candidate_c_reproduction.evaluator_a import (
    RealCandidateCExecutionBlocked,
    evaluate_frozen_population,
    evaluate_synthetic_event,
    load_frozen_contracts,
)
from research_labs.candidate_c_reproduction.evaluator_a.evaluator import row_keys_for_event
from research_labs.candidate_c_reproduction.evaluator_a.schema import OutputSchemaError, validate_rows


SIGNS = {
    1: "ARIES",
    2: "TAURUS",
    3: "GEMINI",
    4: "CANCER",
    5: "LEO",
    6: "VIRGO",
    7: "LIBRA",
    8: "SCORPIO",
    9: "SAGITTARIUS",
    10: "CAPRICORN",
    11: "AQUARIUS",
    12: "PISCES",
}
BODIES = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU")


def _position(body: str, sign_index: int, speed: float = 0.1) -> dict[str, object]:
    return {
        "body": body,
        "siderealLongitudeDeg": float((sign_index - 1) * 30 + 1),
        "siderealLongitudeSpeedDegPerDay": speed,
        "sign": SIGNS[sign_index],
        "signIndex": sign_index,
    }


def _event(source: str = "MARS", target: str = "JUPITER", source_sign: int = 2, target_sign: int = 5, sun_sign: int = 3) -> dict[str, object]:
    signs = {
        "SUN": sun_sign,
        "MOON": 6,
        "MARS": source_sign,
        "MERCURY": 12,
        "JUPITER": target_sign,
        "VENUS": 7,
        "SATURN": 10,
        "RAHU": 8,
        "KETU": 2,
    }
    return {
        "_evaluatorInputKind": "SYNTHETIC_ONLY",
        "eventId": "SYNTHETIC_EVENT_001",
        "eventHash": "SYNTHETIC_EVENT_HASH_001",
        "sideIdentity": "USD",
        "chartIdentity": {"chartId": "SYNTHETIC_CHART"},
        "exactUtc": "2025-05-01T00:00:00Z",
        "eventRoles": {
            "sourceBody": source,
            "targetBody": target,
            "sourceRole": "TRANSIT_BODY",
            "targetRole": "NATAL_TARGET",
        },
        "transitPositionAtExactUtc": _position(source, source_sign, 0.5),
        "natalTargetPositionAtFrozenChartUtc": _position(target, target_sign, 0.2),
        "sunPositionAtExactUtc": _position("SUN", sun_sign, 0.9),
        "moonPositionAtExactUtc": _position("MOON", signs["MOON"], 14.4),
        "planetaryPositionsAtExactUtc": [_position(body, signs[body], 0.1) for body in BODIES],
    }


@pytest.fixture(scope="module")
def contracts():
    return load_frozen_contracts()


def _rows(contracts, event=None):
    return evaluate_synthetic_event(event or _event(), contracts)


def test_frozen_contracts_validate_without_exposing_real_arrays(contracts):
    assert len(contracts.expected_row_keys) == 5160
    assert "events" not in contracts.snapshot_metadata
    assert "population" not in contracts.population_metadata
    assert contracts.dependency_hashes["configs/research/machine_interpretation/source_operators/classical_source_operator_ledger_s1r1_v1.json"].startswith("4C7D")


def test_synthetic_rows_follow_the_eight_template_order_and_schema(contracts):
    rows = _rows(contracts)
    assert len(rows) == 8
    assert [(row["componentId"], row["sourceContractId"]) for row in rows] == [
        ("C01_NATURAL_PLANET_CLASS", "TRAILOKYA_1972_NATURAL_PLANET_CLASS_V1"),
        ("C02_NATURAL_RELATIONSHIP", "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1"),
        ("C03_TEMPORARY_RELATIONSHIP", "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1"),
        ("C04_COMPOUND_RELATIONSHIP", "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"),
        ("C05_ORDINARY_AND_SPECIAL_DRSTI", "SARAVALI_4_32_ORDINARY_DRSTI_V1"),
        ("C05_ORDINARY_AND_SPECIAL_DRSTI", "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1"),
        ("C06_STHULA_MOTION", "TRAILOKYA_1972_STHULA_MOTION_CLASS_V1"),
        ("C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING", "TRAILOKYA_1972_V166_INDIVIDUAL_MODIFIER_V1"),
    ]
    validate_rows(rows, row_keys_for_event("SYNTHETIC_EVENT_001", contracts), contracts.allowed_unknown_codes)


def test_synthetic_source_closed_values_are_local_contract_results(contracts):
    rows = _rows(contracts)
    assert [row.get("sourceValue") for row in rows] == [
        "KRURA",
        "FRIEND",
        "TEMPORARY_FRIEND",
        "GREAT_FRIEND",
        "DRSTI_3_4",
        "SPECIAL_FULL_DRSTI",
        "SHIGHRA",
        None,
    ]
    assert rows[-1]["unknownReasonCode"] == "UNKNOWN"
    assert rows[-1]["provenance"]["operatorDependencies"][-1] == "TRAILOKYA_V166_REQUIRES_STHANA_PHALA_INPUT"


@pytest.mark.parametrize(
    ("body", "reason"),
    [("MOON", "MOON_CONDITION_INPUT_UNAVAILABLE"), ("MERCURY", "MERCURY_ASSOCIATION_INPUT_UNAVAILABLE")],
)
def test_conditional_nature_inputs_remain_unknown(contracts, body, reason):
    rows = _rows(contracts, _event(source=body, target="MARS", source_sign=2, target_sign=5))
    nature = rows[0]
    assert nature["outputStatus"] == "UNKNOWN"
    assert nature["unknownReasonCode"] == reason
    assert "sourceValue" not in nature


def test_trailokya_node_relationship_and_self_cell_fail_closed(contracts):
    node_rows = _rows(contracts, _event(source="RAHU", target="MARS", source_sign=2, target_sign=5))
    assert node_rows[1]["unknownReasonCode"] == "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA"
    self_rows = _rows(contracts, _event(source="MARS", target="MARS", source_sign=2, target_sign=5))
    assert self_rows[1]["unknownReasonCode"] == "UNKNOWN"
    assert "TRAILOKYA_RELATIONSHIP_CELL_NOT_SOURCE_CLOSED" in self_rows[1]["provenance"]["operatorDependencies"]


def test_compound_uses_saravali_natural_relationship_only(contracts):
    rows = _rows(contracts, _event(source="MERCURY", target="MARS", source_sign=2, target_sign=5))
    compound = rows[3]
    assert compound["outputStatus"] == "VALUE"
    assert compound["sourceValue"] == "NEUTRAL"
    assert compound["provenance"]["supportingInputContract"]["operatorId"] == "SARAVALI_NATURAL_RELATIONSHIP_V1"
    assert compound["provenance"]["supportingInputContract"]["path"].endswith("classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json")


def test_compound_node_input_does_not_fall_back_to_trailokya(contracts):
    rows = _rows(contracts, _event(source="RAHU", target="MARS", source_sign=2, target_sign=5))
    compound = rows[3]
    assert compound["outputStatus"] == "UNKNOWN"
    assert compound["unknownReasonCode"] == "COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED"
    assert compound["provenance"]["supportingInputContract"]["operatorId"] == "SARAVALI_NATURAL_RELATIONSHIP_V1"


def test_relative_place_is_sign_derived_and_does_not_use_aspect_label(contracts):
    event = _event(source_sign=2, target_sign=5)
    event["aspectType"] = "CONJUNCTION"
    rows = _rows(contracts, event)
    assert rows[2]["sourceValue"] == "TEMPORARY_FRIEND"
    assert rows[2]["inputIdentity"]["consumedInputs"]["relativePlace"] == 4


def test_motion_is_enumerated_and_speed_does_not_create_a_modern_threshold(contracts):
    fast = _event(source="MARS", target="JUPITER", source_sign=2, target_sign=5, sun_sign=3)
    slow = deepcopy(fast)
    slow["transitPositionAtExactUtc"]["siderealLongitudeSpeedDegPerDay"] = 999.0
    fast_rows = _rows(contracts, fast)
    slow_rows = _rows(contracts, slow)
    assert fast_rows[6]["sourceValue"] == slow_rows[6]["sourceValue"] == "SHIGHRA"
    assert fast_rows[6]["inputIdentityHash"] != slow_rows[6]["inputIdentityHash"]
    asta_rows = _rows(contracts, _event(source="MARS", target="JUPITER", source_sign=2, target_sign=5, sun_sign=2))
    assert asta_rows[6]["unknownReasonCode"] == "ASTA_DIRECTION_UNKNOWN"
    inner_rows = _rows(contracts, _event(source="VENUS", target="JUPITER", source_sign=1, target_sign=5, sun_sign=1))
    assert inner_rows[6]["unknownReasonCode"] == "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED"


def test_c07_is_always_generic_unknown_without_modifier_composition(contracts):
    row = _rows(contracts)[7]
    assert row["outputStatus"] == "UNKNOWN"
    assert row["unknownReasonCode"] == "UNKNOWN"
    assert row["inputIdentity"]["consumedInputs"] == {"sourceMeasurement": None, "modifiers": []}


def test_schema_guards_cardinality_and_input_hash(contracts):
    rows = _rows(contracts)
    with pytest.raises(OutputSchemaError, match="row count mismatch"):
        validate_rows(rows[:-1], row_keys_for_event("SYNTHETIC_EVENT_001", contracts), contracts.allowed_unknown_codes)
    tampered = deepcopy(rows)
    tampered[0]["inputIdentityHash"] = "0" * 64
    with pytest.raises(OutputSchemaError, match="inputIdentityHash"):
        validate_rows(tampered, row_keys_for_event("SYNTHETIC_EVENT_001", contracts), contracts.allowed_unknown_codes)


def test_real_frozen_population_entry_point_is_unconditionally_blocked():
    with pytest.raises(RealCandidateCExecutionBlocked):
        evaluate_frozen_population("status/research/mo_r4a_candidate_c_p0_shared_astronomy_inputs_v1.json")


def test_clean_room_source_does_not_import_historical_operator_or_create_b():
    source = open(__file__.replace("test_evaluator_a.py", "evaluator.py"), encoding="utf-8").read()
    assert "classical_source_operators" not in source
    assert not open(__file__.replace("test_evaluator_a.py", "evaluator.py"), encoding="utf-8").read().find("evaluator_b") >= 0
