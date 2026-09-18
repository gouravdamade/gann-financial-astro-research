"""Focused R3R2A tests: provenance closure and a zero-science real boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from .admission import EXPECTED_EVENT_COUNT, EXPECTED_POPULATION_HASH, EXPECTED_ROW_COUNT, load_and_validate_real_population
from .authorization_record_r3r2 import ExternalAuthorizationError, validate_external_authorization
from .contract_bundle_r3r2 import (
    ADMISSION_POLICY, APPROVED_TRANSFORM, BundleVerificationError, discover_dependency_inventory,
    lf_to_crlf_rendering, materialize_bundle, verify_bundle, verify_frozen_loader_acceptance,
)
from .controller_r3r2 import REAL_READ_SCOPE, structural_real_preflight
from .real_context_a_r3r2 import build_real_a_context
from .real_v2_bridge_r3r2 import bridge_event


ROOT = Path(__file__).resolve().parents[3]
RUNTIMES = {
    "EVALUATOR_A": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r2-a-runtime"),
    "EVALUATOR_B": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r2-b-runtime"),
}


def _position(body: str, sign: str, sign_index: int, speed: float) -> dict[str, object]:
    return {"body": body, "sign": sign, "signIndex": sign_index, "siderealLongitudeDeg": float(sign_index), "siderealLongitudeSpeedDegPerDay": speed}


def _fake_real_event() -> dict[str, object]:
    positions = [
        _position("SUN", "ARIES", 1, 1.0), _position("MOON", "TAURUS", 2, 13.0),
        _position("MARS", "GEMINI", 3, 0.5), _position("MERCURY", "CANCER", 4, 1.1),
        _position("JUPITER", "LEO", 5, 0.2), _position("VENUS", "VIRGO", 6, 1.0),
        _position("SATURN", "LIBRA", 7, 0.1), _position("RAHU", "SCORPIO", 8, -0.1), _position("KETU", "PISCES", 12, -0.1),
    ]
    return {"eventId": "FAKE_REAL_RUN1_R3R2_001", "eventHash": "FAKE_EVENT_HASH", "sideIdentity": "USD", "chartIdentity": {"chartId": "FAKE_CHART"}, "exactUtc": "2099-01-01T00:00:00Z", "eventRoles": {"sourceBody": "MARS", "targetBody": "JUPITER", "sourceRole": "TRANSIT_BODY", "targetRole": "NATAL_TARGET"}, "transitPositionAtExactUtc": positions[2], "natalTargetPositionAtFrozenChartUtc": positions[4], "sunPositionAtExactUtc": positions[0], "moonPositionAtExactUtc": positions[1], "planetaryPositionsAtExactUtc": positions}


def test_complete_dependency_inventory_and_derived_rendered_paths() -> None:
    inventory = discover_dependency_inventory(ROOT)
    assert len(inventory) == 12
    assert all(item["sourceGitBlobSha"] and item["canonicalLfCount"] > 0 for item in inventory)
    assert not any(item["representationDisposition"] == "BLOCKED_REPRESENTATION_MISMATCH" for item in inventory)
    rendered = [item for item in inventory if item["representationDisposition"] == APPROVED_TRANSFORM]
    assert len(rendered) == 7
    fourth = next(item for item in inventory if item["logicalPath"].endswith("planet_nature_conditions_v1.yaml"))
    assert fourth["canonicalGitBlobSha256"] == "5E875CD279270DF7B2264C71BD39741AE9D0C3820FD4A27EDBBE9D3F431AFDB1"
    assert fourth["candidateLfToCrlfSha256"] == fourth["historicalExpectedSha256"] == "9F6D7C637A4FF75E5C5C169785B108278CAB622E1ED02CE27D093F1DC58DB99B"


def test_bundle_round_trips_and_unchanged_loaders_accept() -> None:
    bundle = materialize_bundle(ROOT)
    assert bundle["admissionPolicy"] == ADMISSION_POLICY
    assert bundle["renderedPaths"] == sorted(bundle["renderedPaths"])
    verified = verify_bundle(ROOT)
    assert verified["bundleManifestHash"] == bundle["bundleManifestHash"]
    assert verify_frozen_loader_acceptance(verified, RUNTIMES) == {"EVALUATOR_A": True, "EVALUATOR_B": True}


def test_transform_refuses_non_lf_input_and_arbitrary_unreferenced_file() -> None:
    with pytest.raises(BundleVerificationError):
        lf_to_crlf_rendering(b"one\r\ntwo\r\n")
    assert all(item["logicalPath"] != "README.md" for item in discover_dependency_inventory(ROOT))


def test_truthful_a_context_and_v2_bridge_are_fake_only() -> None:
    class FrozenShape:
        EVENT_BODIES = frozenset({"SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU"})
        SIGN_NAMES = {1: "ARIES", 2: "TAURUS", 3: "GEMINI", 4: "CANCER", 5: "LEO", 6: "VIRGO", 7: "LIBRA", 8: "SCORPIO", 9: "SAGITTARIUS", 10: "CAPRICORN", 11: "AQUARIUS", 12: "PISCES"}
    event = _fake_real_event()
    context = build_real_a_context(event, FrozenShape)
    assert context["event"] is event and "_evaluatorInputKind" not in event
    bridge = bridge_event(event)
    assert bridge["fixtureId"] == event["eventId"] and bridge["semanticFixtureIdentityHash"] == event["eventHash"]


def test_structural_real_read_is_not_scientific_execution() -> None:
    bundle = materialize_bundle(ROOT)
    population = load_and_validate_real_population(Path(bundle["loaderView"]))
    preflight = structural_real_preflight(ROOT, population)
    assert preflight["populationCount"] == EXPECTED_EVENT_COUNT
    assert preflight["populationHash"] == EXPECTED_POPULATION_HASH
    assert preflight["realFrozenPopulationReadScope"] == REAL_READ_SCOPE
    assert preflight["realFrozenPopulationEvaluated"] is False
    assert preflight["realCandidateCOutputProduced"] is False
    assert preflight["realCandidateCOutputRowCount"] == 0
    assert preflight["realComparisonExecuted"] is False
    assert EXPECTED_ROW_COUNT == 5160


def test_external_authorization_is_absent_and_fail_closed() -> None:
    with pytest.raises(ExternalAuthorizationError):
        validate_external_authorization(None, {})
