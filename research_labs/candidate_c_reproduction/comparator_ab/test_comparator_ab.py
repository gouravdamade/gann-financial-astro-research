"""Comparator-only tests.  These never execute A and B together."""

from __future__ import annotations

from copy import deepcopy

from research_labs.candidate_c_reproduction.comparator_ab.adapters import adapt_fixture_for_a, adapt_fixture_for_b
from research_labs.candidate_c_reproduction.comparator_ab.comparator import MISMATCH_TAXONOMY, compare_projected_batches
from research_labs.candidate_c_reproduction.comparator_ab.fixtures import build_fixture_corpus, generate_neutral_fixtures
from research_labs.candidate_c_reproduction.comparator_ab.models import NeutralFixture, SemanticRow
from research_labs.candidate_c_reproduction.comparator_ab.projection import project_rows


def _fixture() -> NeutralFixture:
    return generate_neutral_fixtures()[0]


def _row(
    fixture: NeutralFixture,
    *,
    value: object = "FRIEND",
    status: str = "VALUE",
    reason: str = "UNKNOWN",
    operator: str = "OPERATOR_A",
    profile: str = "PROFILE_A",
    contract: str | None = None,
    version: str | None = "1",
) -> SemanticRow:
    return SemanticRow(
        fixture_id=fixture.fixture_id,
        semantic_fixture_identity_hash=fixture.semantic_fixture_identity_hash,
        fixture_family=fixture.fixture_family,
        coverage_tags=fixture.coverage_tags,
        source_profile=profile,
        component_id="C01_NATURAL_PLANET_CLASS",
        source_contract_id=contract or operator,
        operator_id=operator,
        operator_version=version,
        output_status=status,
        source_value=value if status == "VALUE" else None,
        unknown_reason_code=reason if status == "UNKNOWN" else None,
        source_status="SOURCE_CLOSED_CATEGORICAL",
        original_row={},
    )


def _classes(mismatches: list[dict[str, object]]) -> set[str]:
    return {item for mismatch in mismatches for item in mismatch["mismatchClassifications"]}


def test_corpus_generation_is_deterministic_and_complete() -> None:
    first = build_fixture_corpus()
    second = build_fixture_corpus()
    assert first["corpusHash"] == second["corpusHash"]
    assert first["fixtureCount"] == 1040
    assert first["fixtureFamilyCounts"] == {
        "RELATIONSHIP_POSITION_MATRIX": 972,
        "MOTION_MATRIX": 64,
        "REPRESENTATION_INVARIANCE_CANARIES": 4,
    }
    assert all(item["semanticFixtureIdentityHash"] for item in first["fixtures"])


def test_adapters_preserve_neutral_scientific_inputs_but_not_schema_shape() -> None:
    fixture = _fixture()
    a = adapt_fixture_for_a(fixture)
    b = adapt_fixture_for_b(fixture)
    assert a["eventId"] == b["eventId"]
    assert a["eventId"].startswith("SYNTHETIC_AB_")
    assert a["eventRoles"]["sourceBody"] == b["eventRoles"]["sourceBody"] == fixture.source_body
    assert a["eventRoles"]["targetBody"] == b["eventRoles"]["targetBody"] == fixture.target_body
    assert a["transitPositionAtExactUtc"]["signIndex"] == b["transitPositionAtExactUtc"]["signIndex"] == fixture.source_sign_index
    assert a["natalTargetPositionAtFrozenChartUtc"]["signIndex"] == b["natalTargetPositionAtFrozenChartUtc"]["signIndex"] == fixture.target_sign_index
    assert a["eventRoles"]["sourceRole"] == "TRANSIT_BODY"
    assert set(b["eventRoles"]) == {"sourceBody", "targetBody"}


def test_identical_semantic_rows_compare_equal() -> None:
    fixture = _fixture()
    assert compare_projected_batches(fixture, [_row(fixture)], [_row(fixture)]) == []


def test_value_unknown_and_unknown_reason_mismatches_are_frozen() -> None:
    fixture = _fixture()
    value_mismatch = compare_projected_batches(fixture, [_row(fixture, value="FRIEND")], [_row(fixture, value="ENEMY")])
    unknown_status_mismatch = compare_projected_batches(fixture, [_row(fixture)], [_row(fixture, status="UNKNOWN")])
    unknown_reason_mismatch = compare_projected_batches(
        fixture,
        [_row(fixture, status="UNKNOWN", reason="UNKNOWN")],
        [_row(fixture, status="UNKNOWN", reason="ASTA_DIRECTION_UNKNOWN")],
    )
    assert "SOURCE_VALUE_MISMATCH" in _classes(value_mismatch)
    assert "OUTPUT_STATUS_MISMATCH" in _classes(unknown_status_mismatch)
    assert "UNKNOWN_REASON_MISMATCH" in _classes(unknown_reason_mismatch)


def test_missing_duplicate_and_operator_mismatches_are_detected() -> None:
    fixture = _fixture()
    base = _row(fixture)
    missing = compare_projected_batches(fixture, [base], [])
    duplicate = compare_projected_batches(fixture, [base, base], [base])
    operator = compare_projected_batches(fixture, [base], [_row(fixture, operator="OPERATOR_B")])
    assert "ROW_MISSING_B" in _classes(missing)
    assert "ROW_DUPLICATE_A" in _classes(duplicate)
    assert "OPERATOR_MISMATCH" in _classes(operator)


def test_irrelevant_provenance_format_is_excluded_but_semantic_change_is_not() -> None:
    fixture = _fixture()
    raw = {
        "sourceProfile": "PROFILE_A",
        "componentId": "C01_NATURAL_PLANET_CLASS",
        "sourceContractId": "OPERATOR_A",
        "outputStatus": "VALUE",
        "sourceValue": "FRIEND",
        "provenance": {"operatorId": "OPERATOR_A", "operatorVersion": "1", "sourceStatus": "SOURCE_CLOSED_CATEGORICAL", "sourceArtifact": {"path": "one"}},
    }
    alternate = deepcopy(raw)
    alternate["provenance"]["sourceArtifact"] = "one"
    assert compare_projected_batches(fixture, project_rows(fixture, [raw]), project_rows(fixture, [alternate])) == []
    alternate["sourceValue"] = "ENEMY"
    assert "SOURCE_VALUE_MISMATCH" in _classes(compare_projected_batches(fixture, project_rows(fixture, [raw]), project_rows(fixture, [alternate])))


def test_ordinary_drsti_representation_aliases_are_closed_and_source_justified() -> None:
    fixture = _fixture()
    row = {
        "sourceProfile": "BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES",
        "componentId": "C05_ORDINARY_AND_SPECIAL_DRSTI",
        "sourceContractId": "SARAVALI_4_32_ORDINARY_DRSTI_V1",
        "outputStatus": "VALUE",
        "sourceValue": "DRSTI_3_4",
        "provenance": {"operatorId": "SARAVALI_4_32_ORDINARY_DRSTI_V1", "operatorVersion": "1", "sourceStatus": "SOURCE_CLOSED_CATEGORICAL"},
    }
    for alias, literal in (("DRSTI_1_4", "1/4"), ("DRSTI_1_2", "1/2"), ("DRSTI_3_4", "3/4"), ("DRSTI_FULL", "FULL")):
        aliased = deepcopy(row)
        literal_row = deepcopy(row)
        aliased["sourceValue"] = alias
        literal_row["sourceValue"] = literal
        assert compare_projected_batches(fixture, project_rows(fixture, [aliased]), project_rows(fixture, [literal_row])) == []


def test_ordinary_drsti_non_admitted_alias_is_not_silently_normalized() -> None:
    fixture = _fixture()
    row = {
        "sourceProfile": "BJ_SARAVALI_CROSS_TEXT_CONTRACTS_AS_SEPARATE_PROFILES",
        "componentId": "C05_ORDINARY_AND_SPECIAL_DRSTI",
        "sourceContractId": "SARAVALI_4_32_ORDINARY_DRSTI_V1",
        "outputStatus": "VALUE",
        "sourceValue": "DRSTI_UNKNOWN_LABEL",
        "provenance": {"operatorId": "SARAVALI_4_32_ORDINARY_DRSTI_V1", "operatorVersion": "1", "sourceStatus": "SOURCE_CLOSED_CATEGORICAL"},
    }
    alternate = deepcopy(row)
    alternate["sourceValue"] = "UNKNOWN_LABEL"
    assert "SOURCE_VALUE_MISMATCH" in _classes(compare_projected_batches(fixture, project_rows(fixture, [row]), project_rows(fixture, [alternate])))


def test_mismatch_taxonomy_and_fixtures_exclude_market_and_real_population_fields() -> None:
    assert "SOURCE_VALUE_MISMATCH" in MISMATCH_TAXONOMY
    rendered = str(build_fixture_corpus()).lower()
    for prohibited in ("price", "return", "marketoutcome", "bullish", "bearish", "usd", "jpy"):
        assert prohibited not in rendered
