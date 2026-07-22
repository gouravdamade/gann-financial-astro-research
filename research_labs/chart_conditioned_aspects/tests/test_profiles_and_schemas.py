from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_all_profiles_are_locked_and_missing_books_are_blocked(profiles) -> None:
    for raw in (
        profiles.lordship,
        profiles.domains,
        profiles.graph,
        profiles.aspects,
        profiles.manifest,
    ):
        assert raw["execution_allowed"] is False
        assert raw["promotion_allowed"] is False
    blocked = set(profiles.manifest["blocked_source_profiles"])
    assert {"TRAILOKYA_DIPIKA_1972", "AGARWAL_FINANCIAL_COMPLETE_EDITION"} <= blocked
    assert profiles.graph["configured_drishti_enabled"] is False
    assert profiles.graph["yoga_edges_enabled"] is False


def test_schema_files_are_strict_json_schema_documents() -> None:
    expected = {
        "organization_chart.schema.json",
        "planet_role.schema.json",
        "natal_structure.schema.json",
        "aspect_prior.schema.json",
        "event_evaluation.schema.json",
    }
    found = {path.name for path in (ROOT / "schemas").glob("*.json")}
    assert found == expected
    for path in sorted((ROOT / "schemas").glob("*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert schema["required"]
