"""Synthetic-only contract tests for the independent Evaluator B."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from research_labs.candidate_c_reproduction.evaluator_b import (
    EvaluatorB,
    RealCandidateCExecutionBlocked,
    SyntheticEvent,
    SyntheticInputError,
    load_frozen_contracts,
)
from research_labs.candidate_c_reproduction.evaluator_b.evaluator import (
    evaluate_synthetic_event,
    validate_output_rows,
)


ROOT = Path(__file__).resolve().parents[3]
CONTRACTS = load_frozen_contracts(ROOT)


def _position(body: str, sign_index: int, speed: float = 1.0) -> dict[str, object]:
    return {
        "body": body,
        "siderealLongitudeDeg": float((sign_index - 1) * 30 + 4),
        "siderealLongitudeSpeedDegPerDay": speed,
        "sign": str(sign_index),
        "signIndex": sign_index,
    }


def _event(
    source: str = "SUN",
    target: str = "MARS",
    source_sign: int = 1,
    target_sign: int = 3,
    sun_sign: int = 5,
    **extra: object,
) -> dict[str, object]:
    return {
        "eventId": "SYNTHETIC_EVENT_001",
        "eventHash": "SYNTHETIC_HASH_001",
        "sideIdentity": "SYNTHETIC_SIDE",
        "chartIdentity": "SYNTHETIC_CHART",
        "exactUtc": "2025-01-01T00:00:00Z",
        "eventRoles": {"sourceBody": source, "targetBody": target},
        "transitPositionAtExactUtc": _position(source, source_sign),
        "natalTargetPositionAtFrozenChartUtc": _position(target, target_sign),
        "sunPositionAtExactUtc": _position("SUN", sun_sign),
        "moonPositionAtExactUtc": _position("MOON", 7),
        "planetaryPositionsAtExactUtc": {
            source: _position(source, source_sign),
            target: _position(target, target_sign),
            "SUN": _position("SUN", sun_sign),
            "MOON": _position("MOON", 7),
        },
        **extra,
    }


def _rows(event: dict[str, object] | SyntheticEvent) -> list[dict[str, object]]:
    return evaluate_synthetic_event(event, CONTRACTS)


def _row(rows: list[dict[str, object]], component: str, operator: str | None = None) -> dict[str, object]:
    for row in rows:
        if row["componentId"] == component and (operator is None or row["sourceContractId"] == operator):
            return row
    raise AssertionError(f"row not found: {component}/{operator}")


def test_frozen_contract_identities_validate_and_real_arrays_are_not_exposed() -> None:
    assert CONTRACTS.expected_row_count == 5160
    assert CONTRACTS.real_frozen_population_read is True
    assert CONTRACTS.real_frozen_population_artifact_read_for_validation is True
    assert CONTRACTS.real_frozen_population_exposed_to_evaluator is False
    assert CONTRACTS.real_frozen_population_arrays_exposed_to_evaluation_path is False
    assert CONTRACTS.real_frozen_population_evaluated is False
    assert "events" not in CONTRACTS.shared_astronomy_metadata
    assert "population" not in CONTRACTS.population_manifest_metadata
    assert "expectedRowKeyUniverse" not in CONTRACTS.bindings["outputCardinality"]
    assert CONTRACTS.execution_allowed is False


def test_synthetic_event_schema_rejects_malformed_input() -> None:
    malformed = _event()
    del malformed["eventRoles"]
    with pytest.raises(SyntheticInputError):
        SyntheticEvent.from_mapping(malformed)


def test_all_eight_template_rows_are_distinct_and_schema_valid() -> None:
    rows = _rows(_event())
    validate_output_rows(rows, CONTRACTS)
    assert len(rows) == 8
    assert len({
        (row["eventId"], row["sourceProfile"], row["componentId"], row["sourceContractId"], row["provenance"]["operatorId"])
        for row in rows
    }) == 8
    assert sum(row["componentId"] == "C05_ORDINARY_AND_SPECIAL_DRSTI" for row in rows) == 2


def test_c01_closed_body_is_categorical() -> None:
    assert _row(_rows(_event(source="SUN")), "C01_NATURAL_PLANET_CLASS")["sourceValue"] == "KRURA"


def test_c01_moon_is_mandatory_unknown() -> None:
    row = _row(_rows(_event(source="MOON", target="MARS")), "C01_NATURAL_PLANET_CLASS")
    assert row["outputStatus"] == "UNKNOWN"
    assert row["unknownReasonCode"] == "MOON_CONDITION_INPUT_UNAVAILABLE"


def test_c01_mercury_is_mandatory_unknown() -> None:
    row = _row(_rows(_event(source="MERCURY", target="MARS")), "C01_NATURAL_PLANET_CLASS")
    assert row["outputStatus"] == "UNKNOWN"
    assert row["unknownReasonCode"] == "MERCURY_ASSOCIATION_INPUT_UNAVAILABLE"


def test_c02_is_directional() -> None:
    forward = _row(_rows(_event(source="SUN", target="MERCURY")), "C02_NATURAL_RELATIONSHIP")
    reverse = _row(_rows(_event(source="MERCURY", target="SUN")), "C02_NATURAL_RELATIONSHIP")
    assert forward["sourceValue"] == "NEUTRAL"
    assert reverse["sourceValue"] == "FRIEND"


def test_c02_nodes_and_self_fail_closed() -> None:
    node = _row(_rows(_event(source="RAHU", target="SUN")), "C02_NATURAL_RELATIONSHIP")
    self_row = _row(_rows(_event(source="SUN", target="SUN")), "C02_NATURAL_RELATIONSHIP")
    assert node["unknownReasonCode"] == "RELATIONSHIP_INPUT_BODY_NOT_CLOSED_FOR_TRAILOKYA"
    assert self_row["unknownReasonCode"] == "UNKNOWN"


def test_c03_uses_inclusive_relative_place() -> None:
    row = _row(_rows(_event(source="SUN", target="MARS", source_sign=1, target_sign=2)), "C03_TEMPORARY_RELATIONSHIP")
    assert row["sourceValue"] == "TEMPORARY_FRIEND"


def test_c03_ignores_aspect_type() -> None:
    conjunction = _row(_rows(_event(aspectType="CONJUNCTION")), "C03_TEMPORARY_RELATIONSHIP")
    opposition = _row(_rows(_event(aspectType="OPPOSITION")), "C03_TEMPORARY_RELATIONSHIP")
    assert conjunction["sourceValue"] == opposition["sourceValue"]
    assert conjunction["inputIdentityHash"] == opposition["inputIdentityHash"]


def test_c04_uses_saravali_natural_relationship_not_trailokya() -> None:
    row = _row(_rows(_event(source="MERCURY", target="MARS", source_sign=1, target_sign=2)), "C04_COMPOUND_RELATIONSHIP")
    assert row["sourceValue"] == "NEUTRAL"


def test_c04_unresolved_input_is_unknown() -> None:
    row = _row(_rows(_event(source="RAHU", target="MARS")), "C04_COMPOUND_RELATIONSHIP")
    assert row["unknownReasonCode"] == "COMPOUND_RELATIONSHIP_INPUT_UNRESOLVED"


def test_c05_ordinary_and_special_rules_are_separate() -> None:
    rows = _rows(_event(source="MARS", target="MARS", source_sign=1, target_sign=4))
    ordinary = _row(rows, "C05_ORDINARY_AND_SPECIAL_DRSTI", "SARAVALI_4_32_ORDINARY_DRSTI_V1")
    special = _row(rows, "C05_ORDINARY_AND_SPECIAL_DRSTI", "CLASSICAL_SPECIAL_DRSTI_GEOMETRY_V1")
    assert ordinary["sourceValue"] == "3/4"
    assert special["sourceValue"] == "SPECIAL_FULL_DRSTI"


def test_c06_outer_motion_uses_stated_category() -> None:
    row = _row(_rows(_event(source="MARS", target="SUN", source_sign=1, target_sign=2, sun_sign=2)), "C06_STHULA_MOTION")
    assert row["sourceValue"] == "SHIGHRA"


def test_c06_inner_motion_uses_only_enumerated_places() -> None:
    enumerated = _row(_rows(_event(source="MERCURY", target="SUN", source_sign=1, target_sign=2, sun_sign=3)), "C06_STHULA_MOTION")
    unlisted = _row(_rows(_event(source="MERCURY", target="SUN", source_sign=1, target_sign=2, sun_sign=5)), "C06_STHULA_MOTION")
    assert enumerated["sourceValue"] == "SAMA"
    assert unlisted["unknownReasonCode"] == "MOTION_EXACT_THRESHOLD_EXTERNAL_OR_UNRESOLVED"


def test_c06_asta_and_speed_thresholds_fail_closed_without_modern_cutoff() -> None:
    asta = _row(_rows(_event(source="MARS", source_sign=2, sun_sign=2)), "C06_STHULA_MOTION")
    fast = _row(_rows(_event(source="MARS", source_sign=1, sun_sign=2, speed=999.0)), "C06_STHULA_MOTION")
    assert asta["unknownReasonCode"] == "ASTA_DIRECTION_UNKNOWN"
    assert fast["sourceValue"] == "SHIGHRA"


def test_c07_is_the_frozen_mandatory_unknown() -> None:
    row = _row(_rows(_event()), "C07_INDIVIDUAL_SOURCE_RECORDS_NO_STACKING")
    assert row["outputStatus"] == "UNKNOWN"
    assert row["unknownReasonCode"] == "UNKNOWN"


def test_unknown_reasons_belong_to_frozen_taxonomy() -> None:
    for row in _rows(_event(source="MOON", target="RAHU")):
        if row["outputStatus"] == "UNKNOWN":
            assert row["unknownReasonCode"] in CONTRACTS.unknown_reason_codes


def test_output_schema_rejects_market_field() -> None:
    rows = _rows(_event())
    rows[0]["price"] = 1
    with pytest.raises(ValueError):
        validate_output_rows(rows, CONTRACTS)


def test_real_population_entry_point_is_blocked() -> None:
    with pytest.raises(RealCandidateCExecutionBlocked):
        EvaluatorB(CONTRACTS).evaluate_population()


def test_no_prohibited_import_or_shortcut_dependency() -> None:
    package = Path(__file__).parent
    prohibited = {"evaluator_a", "decision_engine", "classical_source_operators", "swisseph", "yfinance"}
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.lower() for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                names = {(node.module or "").lower()}
            else:
                continue
            assert not any(any(token in name for token in prohibited) for name in names)
