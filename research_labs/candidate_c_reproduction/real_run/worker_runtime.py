"""Same-process verified-root import and fake-only invocation mechanics.

This module intentionally uses only the standard library until a designated
historical runtime root has passed its byte and import-path checks.
"""

from __future__ import annotations

import hashlib
import hmac
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping


IPC_SCHEMA_VERSION = "MO_R4A_CANDIDATE_C_RUN1_R2_WORKER_IPC_V1"
TEST_EVENT_PREFIX = "FAKE_REAL_RUN1_"


class RuntimeFailure(RuntimeError):
    """Fail-closed worker runtime failure."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest().upper()


def _request_hash(request: Mapping[str, Any]) -> str:
    value = dict(request)
    value.pop("authorizationTicket", None)
    return _sha(value)


def _response(value: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result["responseHash"] = _sha(result)
    return result


def _fail(request: Mapping[str, Any], error: Exception) -> dict[str, Any]:
    return _response({
        "schemaVersion": IPC_SCHEMA_VERSION,
        "runSessionId": str(request.get("runSessionId", "UNKNOWN")),
        "workerRole": str(request.get("workerRole", "UNKNOWN")),
        "requestId": str(request.get("requestId", "UNKNOWN")),
        "requestHash": _request_hash(request),
        "runtimeVerificationStatus": "FAILED",
        "runtimeRootIdentity": {"pid": os.getpid()},
        "importPathVerificationStatus": "NOT_REACHED",
        "outputRowCount": 0,
        "outputPayload": {"errorCode": type(error).__name__, "message": str(error)},
    })


def _load_canonical_request(raw: bytes, expected_role: str) -> dict[str, Any]:
    try:
        request = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeFailure("worker stdin must be UTF-8 JSON") from exc
    required = {
        "schemaVersion", "runSessionId", "workerRole", "requestId", "executionIntent",
        "runtimeManifestHash", "populationHash", "rowUniverseHash", "inputPayloadHash",
        "authorizationTicket", "payload",
    }
    if not isinstance(request, dict) or _canonical(request) != raw or set(request) != required:
        raise RuntimeFailure("worker request is not canonical frozen IPC")
    if request["schemaVersion"] != IPC_SCHEMA_VERSION or request["workerRole"] != expected_role:
        raise RuntimeFailure("worker request does not target this worker role")
    if not isinstance(request["payload"], dict) or request["inputPayloadHash"] != _sha(request["payload"]):
        raise RuntimeFailure("worker payload hash mismatch")
    return request


def _manifest(path: Path, expected_hash: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeFailure("runtime manifest cannot be read") from exc
    declared = value.pop("runtimeManifestHash", None)
    actual = _sha(value)
    value["runtimeManifestHash"] = declared
    if declared != actual or declared != expected_hash:
        raise RuntimeFailure("runtime manifest self-hash mismatch")
    return value


def _assert_clean_git_root(runtime_root: Path, expected_commit: str) -> None:
    try:
        head = subprocess.run(["git", "-C", str(runtime_root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(runtime_root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeFailure("designated runtime root has no verifiable Git identity") from exc
    if head != expected_commit or dirty:
        raise RuntimeFailure("designated runtime root is not the clean protected commit")


def _reject_bytecode(runtime_root: Path) -> None:
    package_root = runtime_root / "research_labs" / "candidate_c_reproduction"
    stale = [path for path in package_root.rglob("*") if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}]
    if stale:
        raise RuntimeFailure("protected runtime tree contains pre-existing bytecode")


def _verify_bytes(runtime_root: Path, entries: list[Mapping[str, Any]]) -> None:
    for entry in entries:
        path = runtime_root / str(entry["path"])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest().upper() != entry["protectedBlobSha256"]:
            raise RuntimeFailure(f"protected runtime bytes differ: {entry['path']}")


def _reject_preload() -> None:
    protected = "research_labs.candidate_c_reproduction"
    contaminated = [name for name in sys.modules if name == protected or name.startswith(f"{protected}.")]
    if contaminated:
        raise RuntimeFailure("protected scientific package was loaded before root isolation")


def _isolate_path(runtime_root: Path) -> None:
    prior = list(sys.path)
    standard = [path for path in prior if path and "site-packages" not in path and "candidate-c-run1-r2" not in path.lower()]
    sys.path[:] = [str(runtime_root), *standard]


def _verify_modules(runtime_root: Path, entries: list[Mapping[str, Any]], module_names: list[str]) -> dict[str, Any]:
    imported: dict[str, Any] = {}
    for name in module_names:
        imported[name] = importlib.import_module(name)
    expected_by_module = {str(entry["moduleName"]): runtime_root / str(entry["path"]) for entry in entries if entry.get("moduleName")}
    for name, expected in expected_by_module.items():
        module = sys.modules.get(name)
        actual = Path(getattr(module, "__file__", "")).resolve() if module is not None else None
        if actual != expected.resolve():
            raise RuntimeFailure(f"protected module resolved outside designated root: {name}")
    return imported


def _ticket_mac(secret: str, claims: Mapping[str, Any]) -> str:
    return hmac.new(secret.encode("ascii"), _sha(claims).encode("ascii"), hashlib.sha256).hexdigest().upper()


def _event_ids(role: str, payload: Mapping[str, Any]) -> list[str]:
    if role in {"EVALUATOR_A", "EVALUATOR_B"}:
        event_id = payload.get("event", {}).get("eventId") if isinstance(payload.get("event"), Mapping) else None
        return [event_id] if isinstance(event_id, str) else []
    return list(payload.get("eventIds", [])) if isinstance(payload.get("eventIds"), list) else []


def _validate_ticket(request: Mapping[str, Any], role_entry: Mapping[str, Any]) -> None:
    secret = os.environ.get("RUN1_R2_TEST_TICKET_SECRET")
    ticket = request["authorizationTicket"]
    claims = ticket.get("claims") if isinstance(ticket, Mapping) else None
    mac = ticket.get("mac") if isinstance(ticket, Mapping) else None
    ids = _event_ids(str(request["workerRole"]), request["payload"])
    expected = {
        "testOnly": True,
        "executionIntent": "FAKE_ISOLATED_RUNTIME_PROBE",
        "workerRole": request["workerRole"],
        "runSessionId": request["runSessionId"],
        "requestId": request["requestId"],
        "eventIds": ids,
        "inputPayloadHash": request["inputPayloadHash"],
        "populationHash": request["populationHash"],
        "targetImplementationCommit": role_entry["protectedCommit"],
    }
    if not secret or not isinstance(claims, dict) or not isinstance(mac, str) or not hmac.compare_digest(mac, _ticket_mac(secret, claims)):
        raise RuntimeFailure("worker authorization ticket is untrusted")
    if any(claims.get(key) != value for key, value in expected.items()) or any(not event_id.startswith(TEST_EVENT_PREFIX) for event_id in ids):
        raise RuntimeFailure("worker authorization ticket does not bind a fake-only request")


def _run_a(modules: Mapping[str, Any], contract_input_root: Path, event: Mapping[str, Any]) -> list[dict[str, Any]]:
    evaluator = modules["research_labs.candidate_c_reproduction.evaluator_a.evaluator"]
    loader = modules["research_labs.candidate_c_reproduction.evaluator_a.contract_loader"]
    schema = modules["research_labs.candidate_c_reproduction.evaluator_a.schema"]
    # The historical evaluator code and its independently frozen source-input
    # snapshot have distinct immutable identities.  The loader validates every
    # source-input byte itself before returning an array-free contract object.
    contracts = loader.load_frozen_contracts(contract_input_root)
    context = evaluator._validate_event(event)
    rows = [evaluator._evaluate_template(context, contracts, profile, component_id, operator_id) for profile, component_id, operator_id in evaluator._templates(contracts)]
    schema.validate_rows(rows, evaluator.row_keys_for_event(event["eventId"], contracts), contracts.allowed_unknown_codes)
    return rows


def _run_b(modules: Mapping[str, Any], contract_input_root: Path, event: Mapping[str, Any]) -> list[dict[str, Any]]:
    evaluator = modules["research_labs.candidate_c_reproduction.evaluator_b.evaluator"]
    loader = modules["research_labs.candidate_c_reproduction.evaluator_b.contract_loader"]
    model = modules["research_labs.candidate_c_reproduction.evaluator_b.models"]
    frozen = loader.load_frozen_contracts(contract_input_root)
    b_event = dict(event)
    roles = event.get("eventRoles")
    if not isinstance(roles, Mapping):
        raise RuntimeFailure("B worker event has no role mapping")
    # Adapter representation is intentionally owned by the controller layer;
    # B's frozen input model admits only the two body identities.
    b_event["eventRoles"] = {"sourceBody": roles.get("sourceBody"), "targetBody": roles.get("targetBody")}
    chart_identity = event.get("chartIdentity")
    if isinstance(chart_identity, Mapping):
        b_event["chartIdentity"] = str(chart_identity.get("chartId", ""))
    item = model.SyntheticEvent.from_mapping(b_event)
    motion, motion_value = evaluator._motion_row(item, frozen)
    rows = [evaluator._natural_class(item, frozen, motion_value), evaluator._relationship_row(item, frozen), evaluator._temporary_row(item, frozen), evaluator._compound_row(item, frozen), evaluator._ordinary_drsti_row(item, frozen), evaluator._special_drsti_row(item, frozen), motion, evaluator._individual_record_row(item, frozen)]
    evaluator.validate_output_rows(rows, frozen)
    return rows


def _run_v2(modules: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    model = modules["research_labs.candidate_c_reproduction.comparator_ab.models"]
    projection = modules["research_labs.candidate_c_reproduction.comparator_ab.projection"]
    comparator = modules["research_labs.candidate_c_reproduction.comparator_ab.comparator"]
    fixture_value = payload.get("fixture")
    if not isinstance(fixture_value, Mapping):
        raise RuntimeFailure("V2 fake payload requires a neutral fixture")
    fixture = model.NeutralFixture(
        fixture_id=str(fixture_value["fixtureId"]), fixture_family=str(fixture_value["fixtureFamily"]),
        source_body=str(fixture_value["sourceBody"]), target_body=str(fixture_value["targetBody"]),
        source_sign_index=int(fixture_value["sourceSignIndex"]), target_sign_index=int(fixture_value["targetSignIndex"]),
        sun_sign_index=int(fixture_value["sunSignIndex"]), coverage_tags=tuple(fixture_value["coverageTags"]),
        optional_aspect_type=fixture_value.get("optionalAspectType"),
        semantic_fixture_identity_hash=str(fixture_value["semanticFixtureIdentityHash"]),
    )
    a_rows = projection.project_rows(fixture, payload.get("aRows", []))
    b_rows = projection.project_rows(fixture, payload.get("bRows", []))
    mismatches = comparator.compare_projected_batches(fixture, a_rows, b_rows)
    return {"mismatches": mismatches, "projectedARowCount": len(a_rows), "projectedBRowCount": len(b_rows)}


def execute_worker(raw: bytes, *, role: str, runtime_root: Path, contract_input_root: Path, manifest_path: Path) -> dict[str, Any]:
    request: dict[str, Any] = {}
    try:
        request = _load_canonical_request(raw, role)
        manifest = _manifest(manifest_path, request["runtimeManifestHash"])
        role_entry = manifest["runtimeRoots"][role]
        entries = role_entry["protectedFiles"]
        if runtime_root.resolve() == Path(manifest_path).resolve().parents[2]:
            raise RuntimeFailure("controller checkout cannot serve as a protected worker root")
        _validate_ticket(request, role_entry)
        _assert_clean_git_root(runtime_root, role_entry["protectedCommit"])
        _reject_bytecode(runtime_root)
        _verify_bytes(runtime_root, entries)
        _reject_preload()
        _isolate_path(runtime_root)
        modules = _verify_modules(runtime_root, entries, role_entry["moduleImports"])
        _verify_bytes(runtime_root, entries)
        if role == "EVALUATOR_A":
            output: Any = _run_a(modules, contract_input_root, request["payload"]["event"])
        elif role == "EVALUATOR_B":
            output = _run_b(modules, contract_input_root, request["payload"]["event"])
        else:
            output = _run_v2(modules, request["payload"])
        count = len(output) if isinstance(output, list) else int(output["projectedARowCount"]) + int(output["projectedBRowCount"])
        return _response({
            "schemaVersion": IPC_SCHEMA_VERSION,
            "runSessionId": request["runSessionId"], "workerRole": role, "requestId": request["requestId"],
            "requestHash": _request_hash(request), "runtimeVerificationStatus": "VERIFIED_SAME_PROCESS",
            "runtimeRootIdentity": {"runtimeRootName": role_entry["runtimeRootName"], "protectedCommit": role_entry["protectedCommit"], "pid": os.getpid(), "verificationPid": os.getpid(), "executionPid": os.getpid()},
            "importPathVerificationStatus": "VERIFIED_DESIGNATED_ROOT", "outputRowCount": count,
            "outputPayload": {"result": output, "diagnostic": {"fakeOnly": True, "scientificInvocationPid": os.getpid()}},
        })
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return _fail(request, exc)
