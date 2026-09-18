"""R3R3 fake-only integration and authorization-boundary tests."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from .artifacts_r3r3 import ArtifactWriteError, verify_artifact, write_first_artifact
from .authorization_record_r3r3 import ExternalAuthorizationError, validate_external_authorization
from .canonical import canonical_hash, self_hash
from .audit_r3r3_r1 import MismatchAccountingError, RowUniverseValidationError, mismatch_counts_by_class, summarize_mismatches, terminal_result, validate_complete_row_universe
from .controller_r3r3 import FUTURE_RESULT_PATHS, REAL_RESULT_PATHS, _order, future_result_paths_are_unpopulated, resolved_result_paths, run_fake_dry_run


ROOT = Path(__file__).resolve().parents[3]
RUNTIMES = {"EVALUATOR_A": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r3r3-a-runtime"), "EVALUATOR_B": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r3r3-b-runtime"), "V2_COMPARATOR": Path(r"D:\PycharmProjects-cgvo-candidate-c-run1-r3r3-v2-runtime")}


def _position(body: str, sign: str, index: int, speed: float) -> dict[str, object]:
    return {"body": body, "sign": sign, "signIndex": index, "siderealLongitudeDeg": float(index), "siderealLongitudeSpeedDegPerDay": speed}


def _event(number: int) -> dict[str, object]:
    positions = [_position("SUN", "ARIES", 1, 1.0), _position("MOON", "TAURUS", 2, 13.0), _position("MARS", "GEMINI", 3, 0.5), _position("MERCURY", "CANCER", 4, 1.1), _position("JUPITER", "LEO", 5, 0.2), _position("VENUS", "VIRGO", 6, 1.0), _position("SATURN", "LIBRA", 7, 0.1), _position("RAHU", "SCORPIO", 8, -0.1), _position("KETU", "PISCES", 12, -0.1)]
    return {"eventId": f"FAKE_REAL_RUN1_{number:03d}", "eventHash": f"FAKE_HASH_{number:03d}", "sideIdentity": "USD", "chartIdentity": {"chartId": f"FAKE_{number}"}, "exactUtc": "2099-01-01T00:00:00Z", "eventRoles": {"sourceBody": "MARS", "targetBody": "JUPITER", "sourceRole": "TRANSIT_BODY", "targetRole": "NATAL_TARGET"}, "transitPositionAtExactUtc": positions[2], "natalTargetPositionAtFrozenChartUtc": positions[4], "sunPositionAtExactUtc": positions[0], "moonPositionAtExactUtc": positions[1], "planetaryPositionsAtExactUtc": positions}


def test_fake_subprocess_chain_is_one_worker_per_role_and_preserves_first_artifacts(tmp_path: Path) -> None:
    result = run_fake_dry_run(ROOT, [_event(1), _event(2), _event(3)], runtime_roots=RUNTIMES, temp_root=tmp_path)
    assert result["a"]["outputRowCount"] == result["b"]["outputRowCount"] == result["v2"]["outputRowCount"] == 24
    pids = {result[role]["runtimeRootIdentity"]["pid"] for role in ("a", "b", "v2")}
    assert len(pids) == 3
    assert result["a"]["runtimeVerificationStatus"].endswith("SAME_PROCESS")
    assert verify_artifact(result["aArtifact"]) and verify_artifact(result["bArtifact"]) and verify_artifact(result["comparison"])
    assert result["aArtifact"]["runSessionId"] == result["bArtifact"]["runSessionId"] == result["comparison"]["runSessionId"]
    assert result["comparison"]["totalMismatches"] == 0
    assert result["comparison"]["totalMismatchClassifications"] == 0
    assert result["comparison"]["mismatchCountsByClass"] == {}
    paths = resolved_result_paths(tmp_path)
    assert set(paths) == {"EVALUATOR_A", "EVALUATOR_B", "V2_COMPARISON"}
    assert all(path.exists() for path in paths.values())
    assert not any((tmp_path / name).exists() for name in ("a.json", "b.json", "comparison.json"))
    with pytest.raises(ArtifactWriteError):
        run_fake_dry_run(ROOT, [_event(1), _event(2), _event(3)], runtime_roots=RUNTIMES, temp_root=tmp_path)


def test_authorization_self_hash_and_all_real_paths_remain_locked() -> None:
    expected = {"populationHash": "NOT_REAL"}
    with pytest.raises(ExternalAuthorizationError):
        validate_external_authorization(None, expected)
    assert future_result_paths_are_unpopulated(ROOT)
    assert all(not (ROOT / path).exists() for path in FUTURE_RESULT_PATHS)
    assert _order([_event(1), _event(2)]) != "91B8BF4FE842876F7EC70640A75342E7E58B5D17EA16D5CFE6A4DCFB3308C7C3"


def _rows() -> list[dict[str, object]]:
    return [{"eventId": "FAKE_REAL_RUN1_001", "sourceProfile": "PROFILE", "componentId": f"C{value}", "sourceContractId": "CONTRACT", "provenance": {"operatorId": f"OP{value}"}} for value in range(8)]


def test_full_batch_universe_rejects_missing_duplicate_extra_and_wrong_identity() -> None:
    expected = _rows()
    assert validate_complete_row_universe(expected, expected)["rowUniverseValidated"] is True
    for malformed in (expected[:-1], [*expected, expected[0]], [*expected, {**expected[0], "componentId": "EXTRA", "provenance": {"operatorId": "EXTRA"}}], [{**expected[0], "eventId": "FAKE_REAL_RUN1_CHANGED"}, *expected[1:]], [{**expected[0], "sourceProfile": "OTHER"}, *expected[1:]], [{**expected[0], "componentId": "OTHER"}, *expected[1:]], [{**expected[0], "sourceContractId": "OTHER"}, *expected[1:]], [{**expected[0], "provenance": {"operatorId": "OTHER"}}, *expected[1:]]):
        with pytest.raises(RowUniverseValidationError):
            validate_complete_row_universe(malformed, expected)


def test_mismatch_accounting_is_deterministic_and_fail_closed() -> None:
    assert summarize_mismatches([]) == {"totalMismatches": 0, "totalMismatchClassifications": 0, "mismatchCountsByClass": {}}
    single = [{"mismatchClassifications": ["SOURCE_VALUE_MISMATCH"]}]
    assert summarize_mismatches(single) == {"totalMismatches": 1, "totalMismatchClassifications": 1, "mismatchCountsByClass": {"SOURCE_VALUE_MISMATCH": 1}}
    two_classes = [{"mismatchClassifications": ["ROW_MISSING_A", "ROW_MISSING_B"]}]
    assert summarize_mismatches(two_classes) == {"totalMismatches": 1, "totalMismatchClassifications": 2, "mismatchCountsByClass": {"ROW_MISSING_A": 1, "ROW_MISSING_B": 1}}
    assert terminal_result(summarize_mismatches(two_classes)) == "REAL_SOURCE_REPRODUCTION_SEMANTIC_MISMATCH"
    records = [{"mismatchClassifications": ["COMPONENT_MISMATCH", "PROFILE_MISMATCH"]}, {"mismatchClassifications": ["SOURCE_VALUE_MISMATCH"]}, {"mismatchClassifications": ["PROFILE_MISMATCH", "SOURCE_STATUS_MISMATCH"]}]
    assert summarize_mismatches(records) == {"totalMismatches": 3, "totalMismatchClassifications": 5, "mismatchCountsByClass": {"COMPONENT_MISMATCH": 1, "PROFILE_MISMATCH": 2, "SOURCE_STATUS_MISMATCH": 1, "SOURCE_VALUE_MISMATCH": 1}}
    assert mismatch_counts_by_class(list(reversed(records))) == {"COMPONENT_MISMATCH": 1, "PROFILE_MISMATCH": 2, "SOURCE_STATUS_MISMATCH": 1, "SOURCE_VALUE_MISMATCH": 1}
    with pytest.raises(MismatchAccountingError):
        mismatch_counts_by_class([{"mismatchClassifications": ["UNKNOWN_CLASS"]}])
    with pytest.raises(MismatchAccountingError):
        mismatch_counts_by_class([{"mismatchClassifications": []}])
    with pytest.raises(MismatchAccountingError):
        mismatch_counts_by_class([{"mismatchClassifications": ["SOURCE_VALUE_MISMATCH", "SOURCE_VALUE_MISMATCH"]}])
    with pytest.raises(MismatchAccountingError):
        mismatch_counts_by_class([{"mismatchClassifications": "SOURCE_VALUE_MISMATCH"}])
    with pytest.raises(MismatchAccountingError):
        mismatch_counts_by_class([{"mismatchClassifications": ["SOURCE_VALUE_MISMATCH", "PROFILE_MISMATCH"]}])


def test_actual_protected_v2_multiclass_record_is_accepted_without_mutation() -> None:
    script = '''
import json, sys
from pathlib import Path
runtime = Path(sys.argv[1]); sys.path.insert(0, str(runtime))
from research_labs.candidate_c_reproduction.comparator_ab.comparator import compare_projected_batches
from research_labs.candidate_c_reproduction.comparator_ab.models import NeutralFixture, SemanticRow
fixture = NeutralFixture("FAKE_REAL_RUN1_MULTICLASS", "FAKE", "MARS", "JUPITER", 3, 5, 1, ("FAKE",), semantic_fixture_identity_hash="FAKE_SEMANTIC")
def row(profile, component, contract, operator, value):
    return SemanticRow(fixture.fixture_id, fixture.semantic_fixture_identity_hash, fixture.fixture_family, fixture.coverage_tags, profile, component, contract, operator, "V1", "VALUE", value, None, "SOURCE_CLOSED", {})
records = compare_projected_batches(fixture, [row("PROFILE_A", "COMPONENT_A", "CONTRACT_A", "OPERATOR_A", "A")], [row("PROFILE_B", "COMPONENT_B", "CONTRACT_B", "OPERATOR_B", "B")])
assert len(records) == 1 and len(records[0]["mismatchClassifications"]) > 1
print(json.dumps(records[0], sort_keys=True, separators=(",", ":")))
'''
    completed = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(RUNTIMES["V2_COMPARATOR"])], text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    record = json.loads(completed.stdout)
    before = canonical_hash(record)
    summary = summarize_mismatches([record])
    assert canonical_hash(record) == before
    assert summary["totalMismatches"] == 1
    assert summary["totalMismatchClassifications"] == len(record["mismatchClassifications"])
    assert summary["totalMismatchClassifications"] > summary["totalMismatches"]


def test_preflight_and_writer_use_one_exact_result_path_mapping(tmp_path: Path) -> None:
    assert set(REAL_RESULT_PATHS.values()) == set(FUTURE_RESULT_PATHS)
    assert set(resolved_result_paths(tmp_path).values()) == {tmp_path / value for value in FUTURE_RESULT_PATHS}


def test_r3r3_status_documents_are_canonical_self_hashed() -> None:
    for path, field in (("status/research/mo_r4a_candidate_c_run1_r3r3_runtime_manifest_v1.json", "runtimeManifestHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_r2_runtime_manifest_v1.json", "runtimeManifestHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_worker_ipc_contract_v1.json", "workerIpcContractHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_external_authorization_contract_v1.json", "externalAuthorizationContractHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_worker_ticket_contract_v1.json", "workerTicketContractHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_output_artifact_contract_v1.json", "outputArtifactContractHash"), ("status/research/mo_r4a_candidate_c_run1_r3r3_final_execution_contract_v1.json", "finalExecutionContractHash")):
        document = json.loads((ROOT / path).read_text(encoding="utf-8"))
        assert document[field] == self_hash(document, field)


def test_truthful_a_adapter_context_equals_frozen_synthetic_context() -> None:
    """Compare the exact context fields consumed by frozen A in a clean process."""
    event = _event(19)
    script = '''
import importlib.util, json, sys
from pathlib import Path
root=Path(sys.argv[1]); runtime=Path(sys.argv[2]); event=json.loads(sys.stdin.read())
spec=importlib.util.spec_from_file_location("truthful_adapter",root/"research_labs/candidate_c_reproduction/real_run/real_context_a_r3r2.py")
adapter=importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
sys.path.insert(0,str(runtime))
from research_labs.candidate_c_reproduction.evaluator_a.evaluator import EVENT_BODIES, SIGN_NAMES, _validate_event
class Frozen: EVENT_BODIES=EVENT_BODIES; SIGN_NAMES=SIGN_NAMES
real=adapter.build_real_a_context(event,Frozen)
synthetic=_validate_event({**event,"_evaluatorInputKind":"SYNTHETIC_ONLY"})
keys=("sourceBody","targetBody","transit","natal","sun","moon")
assert all(real[key]==synthetic[key] for key in keys)
assert "_evaluatorInputKind" not in real["event"]
print(json.dumps({"equivalent":True},sort_keys=True,separators=(",",":")))
'''
    completed = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(ROOT), str(RUNTIMES["EVALUATOR_A"])], input=json.dumps(event), text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {"equivalent": True}
