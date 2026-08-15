"""Integrity gates for the TD1R Trailokya-native source artifacts.

These tests validate source-record structure and fail-closed boundaries only.
They do not instantiate the legacy guidance engine or any market behavior.
"""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
TRAILOKYA = ROOT / "configs" / "sbc" / "trailokya"
PRIMARY_HASH = "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"


def _load(name: str) -> dict:
    data = yaml.safe_load((TRAILOKYA / name).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _assert_primary_source(data: dict) -> None:
    assert data["source"]["sourceId"] == "TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN"
    assert data["source"]["sha256"] == PRIMARY_HASH
    assert data["source"]["citationAuthority"] == "ORIGINAL_1972_PAGE_IMAGE_ONLY"
    assert data["readingWitness"]["role"] == "SAME_LINEAGE_READING_WITNESS_NOT_CONTROLLING"
    assert data["executionAllowed"] is False


def test_native_board_is_an_81_cell_cardinally_bound_trailokya_projection() -> None:
    board = _load("trailokya_1972_chakra_construction_v1.yaml")
    _assert_primary_source(board)
    projection = board["cellProjection"]
    assert len(projection) == 9
    assert all(len(row) == 9 for row in projection)
    assert board["orientation"]["authorVisible"] == {
        "east": "TOP", "west": "BOTTOM", "north": "LEFT", "south": "RIGHT"
    }
    assert "ABHIJIT" in {cell for row in projection for cell in row}
    assert board["sourceStatus"] == "SOURCE_CLOSED"


def test_enumerated_target_rows_are_complete_native_and_front_is_one_nakshatra() -> None:
    target_map = _load("trailokya_1972_vedha_target_map_v1.yaml")
    _assert_primary_source(target_map)
    rows = target_map["rows"]
    assert len(rows) == 28
    assert len({row["source"] for row in rows}) == 28
    assert {row["source"] for row in rows} >= {"ABHIJIT", "KRITTIKA", "BHARANI"}
    for row in rows:
        assert row["front"].startswith("NAKSHATRA:")
        assert row["left"] or row["right"]
        assert row["scanPage"] in range(22, 28)
    assert target_map["invariants"] == [
        "DIRECT_AND_EXPANDED_TARGETS_SHARE_ONE_CAUSAL_VEDHA_EVENT_ID",
        "NO_PHALADEEPIKA_OR_AGARWAL_TARGET_ROW_MAY_FILL_A_TRAILOKYA_GAP",
    ]


def test_expansions_are_semantic_cohits_not_extra_votes() -> None:
    expansions = _load("trailokya_1972_special_expansion_rules_v1.yaml")
    _assert_primary_source(expansions)
    assert len(expansions["rules"]) == 4
    assert len(expansions["rules"][1]["triplets"]) == 4
    assert len(expansions["rules"][2]["vowelPairs"]) == 7
    assert len(expansions["rules"][3]["cornerCases"]) == 4
    assert expansions["causalDeduplication"]["directTargetAndAllExpansions"] == "ONE_CAUSAL_VEDHA_EVENT"


def test_conditional_nature_is_categorical_and_moon_overlap_remains_fail_closed() -> None:
    nature = _load("trailokya_1972_planet_nature_conditions_v1.yaml")
    _assert_primary_source(nature)
    assert set(nature["baseClasses"]["krura"]) == {"SATURN", "SUN", "RAHU", "KETU", "MARS"}
    assert set(nature["baseClasses"]["saumya"]) == {"MOON", "MERCURY", "JUPITER", "VENUS"}
    moon = nature["conditionalRules"][0]
    assert moon["failClosedResult"] == "UNKNOWN_AT_OVERLAP_BOUNDARY"
    assert nature["conditionalRules"][1]["forbiddenSubstitute"] == "MODERN_ANGULAR_CONJUNCTION_ORB"
    assert nature["categoricalIntensification"]["numericMultiplier"] == "NOT_SOURCE_AUTHORIZED"


def test_sthula_motion_is_closed_only_at_source_granularity() -> None:
    motion = _load("trailokya_1972_sthula_motion_classifier_v1.yaml")
    _assert_primary_source(motion)
    assert motion["families"]["VAKRA"]["vedhaDirection"] == "RIGHT"
    assert motion["families"]["SHIGHRA"]["vedhaDirection"] == "LEFT"
    assert motion["families"]["SAMA"]["vedhaDirection"] == "FRONT"
    assert motion["mercuryVenusRelativeSun"]["unlistedCases"] == "UNKNOWN_DO_NOT_INHERIT_OUTER_PLANET_TABLE"
    assert motion["exactMotionBoundaries"] == {
        "continuousSwiftMeanThreshold": "NOT_SOURCE_CLOSED",
        "stationaryState": "SOURCE_SILENT_UNRESOLVED",
        "exactAstronomy": "EXTERNAL_GANITA_DELEGATED",
        "residenceTimeTables": "DESCRIPTIVE_STHULA_TABLES_NOT_EPHEMERIS_ENGINE",
    }


def test_readiness_retires_only_trailokya_target_dependencies_and_preserves_locks() -> None:
    readiness = _load("trailokya_1972_td1_readiness.yaml")
    assert readiness["sourceContract"]["contractId"] == "TRAILOKYA_1972_STHULA_VEDHA_SOURCE_V1"
    assert readiness["readiness"]["TD1972_CORE_BOARD_GEOMETRY_SOURCE_CLOSED"] is True
    assert readiness["readiness"]["TD1972_ENUMERATED_TARGET_MAP_SOURCE_CLOSED"] is True
    assert readiness["readiness"]["TD1972_EXACT_CONTINUOUS_SWIFT_MEAN_SPEED_THRESHOLD_SOURCE_CLOSED"] is False
    assert readiness["readiness"]["TD1972_STATIONARY_STATE_SOURCE_CLOSED"] is False
    assert readiness["readiness"]["TD1972_COMPLETE_VEDHA_OPERATOR_SOURCE_CLOSED"] is False
    assert readiness["phaladeepikaDependencyAudit"][0]["classification"] == "NO_LONGER_NEEDED_SOURCE_NATIVE_TD1_REPLACEMENT_AVAILABLE"
    assert all(value is False for value in readiness["globalLocks"].values())
