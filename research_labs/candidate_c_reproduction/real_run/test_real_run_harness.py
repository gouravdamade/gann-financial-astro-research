"""Pre-run harness tests; no test evaluates a real Candidate C event."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from research_labs.candidate_c_reproduction.real_run.adapter_a import adapt_real_event_for_a, validate_adapter_a
from research_labs.candidate_c_reproduction.real_run.adapter_b import adapt_real_event_for_b
from research_labs.candidate_c_reproduction.real_run.admission import (
    EXPECTED_EVENT_COUNT,
    EXPECTED_POPULATION_HASH,
    EXPECTED_ROW_COUNT,
    REAL_ADMISSION_MARKER,
    RealPopulationAdmissionError,
    load_and_validate_real_population,
)
from research_labs.candidate_c_reproduction.real_run.artifacts import output_artifact_paths
from research_labs.candidate_c_reproduction.real_run.harness import (
    RealCandidateCRunNotAuthorized,
    run_real_population,
    validate_prerun_inputs,
)
from research_labs.candidate_c_reproduction.real_run.release_a import evaluate_admitted_real_event_a
from research_labs.candidate_c_reproduction.real_run.release_b import evaluate_admitted_real_event_b
from research_labs.candidate_c_reproduction.real_run.validation import (
    RealRunValidationError,
    validate_adapter_equivalence,
    validate_row_keys,
)


def _position(body: str, sign: str, index: int, speed: float) -> dict[str, object]:
    return {
        "body": body,
        "siderealLongitudeDeg": float((index - 1) * 30 + 1),
        "siderealLongitudeSpeedDegPerDay": speed,
        "sign": sign,
        "signIndex": index,
    }


def fake_real_event() -> dict[str, object]:
    positions = [
        _position("SUN", "ARIES", 1, 1.0), _position("MOON", "TAURUS", 2, 13.0),
        _position("MARS", "GEMINI", 3, 0.5), _position("MERCURY", "CANCER", 4, 1.1),
        _position("JUPITER", "LEO", 5, 0.2), _position("VENUS", "VIRGO", 6, 1.0),
        _position("SATURN", "LIBRA", 7, 0.1), _position("RAHU", "SCORPIO", 8, -0.1),
        _position("KETU", "TAURUS", 2, -0.1),
    ]
    return {
        "eventId": "FAKE_REAL_RUN1_001",
        "eventHash": "FAKE_REAL_EVENT_HASH",
        "sideIdentity": "USD",
        "chartIdentity": {"chartId": "FAKE_FROZEN_CHART"},
        "exactUtc": "2099-01-01T00:00:00Z",
        "eventRoles": {"sourceBody": "MARS", "targetBody": "JUPITER", "sourceRole": "TRANSIT_BODY", "targetRole": "NATAL_TARGET"},
        "transitPositionAtExactUtc": positions[2],
        "natalTargetPositionAtFrozenChartUtc": positions[4],
        "sunPositionAtExactUtc": positions[0],
        "moonPositionAtExactUtc": positions[1],
        "planetaryPositionsAtExactUtc": positions,
    }


def test_real_population_validation_is_structure_only() -> None:
    summary = validate_prerun_inputs(Path(__file__).resolve().parents[3])
    assert summary.population_event_count == EXPECTED_EVENT_COUNT
    assert summary.expected_row_count == EXPECTED_ROW_COUNT
    assert summary.real_frozen_population_read is True
    assert summary.real_frozen_population_read_scope == "IDENTITY_STRUCTURE_AND_ADAPTER_VALIDATION_ONLY"
    assert summary.real_frozen_population_evaluated is False
    assert summary.real_candidate_c_output_produced is False
    assert summary.real_candidate_c_output_row_count == 0
    assert summary.protected_identities["v2ProjectionBlobHash"] == "4B4828FF09494EA3EAE8ACF57B0004177E6507B8ED8A198871F861E60C2AAF5E"


def test_truthful_admission_marker_and_adapter_equivalence() -> None:
    a_event = adapt_real_event_for_a(fake_real_event())
    assert a_event["_realRunAdmissionKind"] == REAL_ADMISSION_MARKER
    assert "_evaluatorInputKind" not in a_event
    context = validate_adapter_a(a_event)
    assert context["sourceBody"] == "MARS"
    b_event = adapt_real_event_for_b(a_event)
    validate_adapter_equivalence(a_event, b_event, "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915")


def test_real_adapter_rejects_synthetic_disguise() -> None:
    event = adapt_real_event_for_a(fake_real_event())
    event["_evaluatorInputKind"] = "SYNTHETIC_ONLY"
    with pytest.raises(RealPopulationAdmissionError, match="never be labelled SYNTHETIC_ONLY"):
        validate_adapter_a(event)


def test_frozen_public_a_api_still_rejects_real_marked_input() -> None:
    from research_labs.candidate_c_reproduction.evaluator_a.evaluator import (
        RealCandidateCExecutionBlocked,
        evaluate_synthetic_event,
    )

    with pytest.raises(RealCandidateCExecutionBlocked):
        evaluate_synthetic_event(adapt_real_event_for_a(fake_real_event()))


def test_thin_release_layers_reuse_frozen_cores_for_fake_only_input() -> None:
    from research_labs.candidate_c_reproduction.evaluator_a.contract_loader import load_frozen_contracts as load_a
    from research_labs.candidate_c_reproduction.evaluator_b.contract_loader import load_frozen_contracts as load_b

    a_event = adapt_real_event_for_a(fake_real_event())
    a_rows = evaluate_admitted_real_event_a(a_event, load_a())
    b_rows = evaluate_admitted_real_event_b(adapt_real_event_for_b(a_event), load_b())
    assert len(a_rows) == 8
    assert len(b_rows) == 8
    assert {row["eventId"] for row in a_rows} == {"FAKE_REAL_RUN1_001"}
    assert {row["eventId"] for row in b_rows} == {"FAKE_REAL_RUN1_001"}


def test_adapter_equivalence_rejects_changed_event_hash() -> None:
    a_event = adapt_real_event_for_a(fake_real_event())
    b_event = adapt_real_event_for_b(a_event)
    altered = deepcopy(a_event)
    altered["eventHash"] = "ALTERED"
    with pytest.raises(RealRunValidationError, match="immutable event identity"):
        validate_adapter_equivalence(altered, b_event, "F5CC39224D61D01D74B1C43EF838D3EDCA7999E11CE878B06EE115BAA2802915")


def test_population_admission_rejects_missing_snapshot_event(monkeypatch: pytest.MonkeyPatch) -> None:
    from research_labs.candidate_c_reproduction.real_run import admission

    root = Path(__file__).resolve().parents[3]
    documents = {
        admission.MANIFEST_PATH: json.loads((root / admission.MANIFEST_PATH).read_text(encoding="utf-8")),
        admission.SNAPSHOT_PATH: json.loads((root / admission.SNAPSHOT_PATH).read_text(encoding="utf-8")),
        admission.BINDINGS_PATH: json.loads((root / admission.BINDINGS_PATH).read_text(encoding="utf-8")),
    }
    documents[admission.SNAPSHOT_PATH]["events"] = documents[admission.SNAPSHOT_PATH]["events"][:-1]

    def fake_read(_root: Path, relative: Path) -> dict[str, object]:
        return deepcopy(documents[relative])

    monkeypatch.setattr(admission, "_read_json", fake_read)
    with pytest.raises(RealPopulationAdmissionError, match="snapshot self-hash"):
        load_and_validate_real_population(root)


def test_b_adapter_rejects_market_field() -> None:
    event = adapt_real_event_for_a(fake_real_event())
    event["price"] = 1.0
    with pytest.raises(RealPopulationAdmissionError, match="market or interpretation fields"):
        adapt_real_event_for_b(event)


def test_adapter_equivalence_rejects_altered_astronomy_identity() -> None:
    a_event = adapt_real_event_for_a(fake_real_event())
    b_event = adapt_real_event_for_b(a_event)
    with pytest.raises(RealRunValidationError, match="frozen astronomy snapshot"):
        validate_adapter_equivalence(a_event, b_event, "ALTERED")


def test_row_validator_rejects_duplicate_and_missing_rows() -> None:
    expected = [{"eventId": "E", "sourceProfile": "P", "componentId": "C", "sourceContractId": "O", "operatorId": "O"}]
    row = {"eventId": "E", "sourceProfile": "P", "componentId": "C", "sourceContractId": "O", "provenance": {"operatorId": "O"}}
    validate_row_keys([row], expected)
    with pytest.raises(RealRunValidationError, match="duplicate"):
        validate_row_keys([row, row], expected)
    with pytest.raises(RealRunValidationError, match="missing or extra"):
        validate_row_keys([], expected)


def test_future_output_paths_are_deterministic_and_unpopulated() -> None:
    paths = output_artifact_paths()
    assert set(paths) == {"evaluatorA", "evaluatorB", "comparison"}
    assert all(path.startswith("status/research/mo_r4a_candidate_c_run1_") for path in paths.values())


def test_real_execution_is_blocked_before_any_evaluator_call() -> None:
    with pytest.raises(RealCandidateCRunNotAuthorized, match="REAL_CANDIDATE_C_RUN_AUTHORIZED=false"):
        run_real_population()


def test_real_population_hash_is_frozen_constant() -> None:
    assert EXPECTED_POPULATION_HASH == "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6"


def test_v2_projection_has_only_the_frozen_drsti_aliases() -> None:
    from research_labs.candidate_c_reproduction.comparator_ab.projection import PROJECTION_CONTRACT

    aliases = PROJECTION_CONTRACT["canonicalSourceValueRules"]["SARAVALI_4_32_ORDINARY_DRSTI_V1"]
    assert aliases == {"DRSTI_1_4": "1/4", "DRSTI_1_2": "1/2", "DRSTI_3_4": "3/4", "DRSTI_FULL": "FULL"}


def test_harness_contains_no_provider_or_ephemeris_import() -> None:
    package = Path(__file__).resolve().parent
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in package.glob("*.py")
        if path.name != Path(__file__).name
    )
    assert "import requests" not in source
    assert "import swisseph" not in source
    assert "import boto3" not in source
