"""Standalone R3R3 batch worker runtime.

Only the standard library is imported before the protected runtime root has
been verified.  The same code supports the future real path and fake-only
subprocess proof; caller-issued HMAC tickets distinguish them.
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
from typing import Any, Mapping, Sequence


IPC_SCHEMA_VERSION = "MO_R4A_CANDIDATE_C_RUN1_R3R3_WORKER_IPC_V1"
FAKE_PREFIX = "FAKE_REAL_RUN1_"


class RuntimeFailure(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest().upper()


def _request_hash(request: Mapping[str, Any]) -> str:
    value = dict(request); value.pop("authorizationTicket", None)
    return _sha(value)


def _response(value: Mapping[str, Any]) -> dict[str, Any]:
    answer = dict(value); answer["responseHash"] = _sha(answer); return answer


def _load(raw: bytes, role: str) -> dict[str, Any]:
    try:
        request = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeFailure("worker stdin must be canonical UTF-8 JSON") from exc
    required = {"schemaVersion", "runSessionId", "workerRole", "requestId", "executionIntent", "runtimeManifestHash", "payloadHash", "authorizationTicket", "payload"}
    if not isinstance(request, dict) or set(request) != required or _canonical(request) != raw:
        raise RuntimeFailure("worker request is not canonical R3R3 IPC")
    if request["schemaVersion"] != IPC_SCHEMA_VERSION or request["workerRole"] != role:
        raise RuntimeFailure("worker request role mismatch")
    if not isinstance(request["payload"], dict) or request["payloadHash"] != _sha(request["payload"]):
        raise RuntimeFailure("worker payload hash mismatch")
    return request


def _manifest(path: Path, expected_hash: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    declared = value.pop("runtimeManifestHash", None)
    if declared != _sha(value) or declared != expected_hash:
        raise RuntimeFailure("runtime manifest self-hash mismatch")
    value["runtimeManifestHash"] = declared
    return value


def _assert_root(root: Path, commit: str) -> None:
    try:
        head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeFailure("runtime root Git identity cannot be verified") from exc
    if head != commit or dirty:
        raise RuntimeFailure("runtime root is not the clean protected commit")


def _reject_bytecode(root: Path) -> None:
    protected = root / "research_labs" / "candidate_c_reproduction"
    if any(item.name == "__pycache__" or item.suffix in {".pyc", ".pyo"} for item in protected.rglob("*")):
        raise RuntimeFailure("protected runtime contains stale bytecode")


def _verify_bytes(root: Path, entries: Sequence[Mapping[str, Any]]) -> None:
    for entry in entries:
        file = root / str(entry["path"])
        actual = hashlib.sha256(file.read_bytes()).hexdigest().upper() if file.is_file() else None
        if actual != entry["protectedBlobSha256"]:
            raise RuntimeFailure(f"protected runtime bytes differ: {entry['path']}")


def _reject_preload() -> None:
    name = "research_labs.candidate_c_reproduction"
    if any(module == name or module.startswith(f"{name}.") for module in sys.modules):
        raise RuntimeFailure("protected scientific package was preloaded")


def _import_verified(root: Path, entries: Sequence[Mapping[str, Any]], imports: Sequence[str]) -> dict[str, Any]:
    sys.path[:] = [str(root), *[p for p in sys.path if p and "site-packages" not in p]]
    imported = {name: importlib.import_module(name) for name in imports}
    expected = {str(entry["moduleName"]): (root / str(entry["path"])).resolve() for entry in entries if entry.get("moduleName")}
    for name, expected_file in expected.items():
        module = sys.modules.get(name)
        if module is None or Path(getattr(module, "__file__", "")).resolve() != expected_file:
            raise RuntimeFailure(f"protected module resolved outside designated root: {name}")
    _verify_bytes(root, entries)
    return imported


def _mac(secret: str, claims: Mapping[str, Any]) -> str:
    return hmac.new(secret.encode("ascii"), _sha(claims).encode("ascii"), hashlib.sha256).hexdigest().upper()


def _claims(request: Mapping[str, Any], entry: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    ticket = request["authorizationTicket"]
    if not isinstance(ticket, Mapping) or not isinstance(ticket.get("claims"), Mapping):
        raise RuntimeFailure("worker ticket missing claims")
    claims = dict(ticket["claims"])
    expected = {
        "testOnly": claims.get("testOnly"), "authorizationRecordHash": claims.get("authorizationRecordHash"),
        "runSessionId": request["runSessionId"], "workerRole": request["workerRole"], "requestId": request["requestId"],
        "requestHash": _request_hash(request), "payloadHash": request["payloadHash"],
        "populationHash": claims.get("populationHash"), "populationOrderHash": claims.get("populationOrderHash"),
        "rowUniverseHash": claims.get("rowUniverseHash"), "bundleManifestHash": claims.get("bundleManifestHash"),
        "canonicalGitBundleAggregateHash": claims.get("canonicalGitBundleAggregateHash"),
        "loaderViewBundleAggregateHash": claims.get("loaderViewBundleAggregateHash"),
        "targetProtectedCommit": entry["protectedCommit"], "targetProtectedIdentity": claims.get("targetProtectedIdentity"),
        "oneShotExecutionIntent": True,
    }
    if request["workerRole"] == "V2_COMPARATOR":
        for key in ("aRawArtifactHash", "bRawArtifactHash", "realV2BridgeHash", "realV2BridgePopulationHash"):
            expected[key] = claims.get(key)
    if claims != expected:
        raise RuntimeFailure("worker ticket claims do not bind this request")
    secret = os.environ.get("RUN1_R3R3_SESSION_SECRET")
    if not secret or not isinstance(ticket.get("mac"), str) or not hmac.compare_digest(str(ticket["mac"]), _mac(secret, claims)):
        raise RuntimeFailure("worker ticket HMAC mismatch")
    events = payload.get("events", [])
    if claims["testOnly"] is True:
        if claims["populationHash"] == "A486D0045DC233207C0A2A50D50CFEFAC0B6493A6775630A068791B919F1F2A6":
            raise RuntimeFailure("test-only authorization cannot bind real population")
        if request["workerRole"] != "V2_COMPARATOR" and (not isinstance(events, list) or any(not str(item.get("eventId", "")).startswith(FAKE_PREFIX) for item in events if isinstance(item, Mapping))):
            raise RuntimeFailure("test-only worker accepts FAKE_REAL_RUN1 events only")
    return claims


def _real_a_context(event: Mapping[str, Any], evaluator: Any) -> dict[str, Any]:
    if event.get("_evaluatorInputKind") == "SYNTHETIC_ONLY":
        raise RuntimeFailure("real A path refuses synthetic admission")
    bodies, signs = evaluator.EVENT_BODIES, evaluator.SIGN_NAMES
    roles = event.get("eventRoles", {})
    source, target = roles.get("sourceBody"), roles.get("targetBody")
    if roles.get("sourceRole") != "TRANSIT_BODY" or roles.get("targetRole") != "NATAL_TARGET" or source not in bodies or target not in bodies:
        raise RuntimeFailure("real A role identity is invalid")
    def position(key: str, body: str | None = None) -> Mapping[str, Any]:
        value = event.get(key)
        if not isinstance(value, Mapping) or value.get("body") not in bodies or (body and value.get("body") != body) or signs.get(value.get("signIndex")) != value.get("sign") or not isinstance(value.get("siderealLongitudeSpeedDegPerDay"), (int, float)):
            raise RuntimeFailure(f"real A position invalid: {key}")
        return value
    transit, natal = position("transitPositionAtExactUtc", source), position("natalTargetPositionAtFrozenChartUtc", target)
    sun, moon = position("sunPositionAtExactUtc", "SUN"), position("moonPositionAtExactUtc", "MOON")
    planetary = event.get("planetaryPositionsAtExactUtc")
    if not isinstance(planetary, list) or len(planetary) != len(bodies) or {item.get("body") for item in planetary if isinstance(item, Mapping)} != set(bodies):
        raise RuntimeFailure("real A nine-body snapshot invalid")
    return {"event": event, "sourceBody": source, "targetBody": target, "transit": transit, "natal": natal, "sun": sun, "moon": moon}


def _run_a(modules: Mapping[str, Any], contract_root: Path, events: Sequence[Mapping[str, Any]], test_only: bool) -> list[dict[str, Any]]:
    evaluator = modules["research_labs.candidate_c_reproduction.evaluator_a.evaluator"]
    loader = modules["research_labs.candidate_c_reproduction.evaluator_a.contract_loader"]
    schema = modules["research_labs.candidate_c_reproduction.evaluator_a.schema"]
    contracts, rows = loader.load_frozen_contracts(contract_root), []
    for original in events:
        event = dict(original)
        context = evaluator._validate_event({**event, "_evaluatorInputKind": "SYNTHETIC_ONLY"}) if test_only else _real_a_context(event, evaluator)
        generated = [evaluator._evaluate_template(context, contracts, profile, component, operator) for profile, component, operator in evaluator._templates(contracts)]
        schema.validate_rows(generated, evaluator.row_keys_for_event(event["eventId"], contracts), contracts.allowed_unknown_codes)
        rows.extend(generated)
    return rows


def _run_b(modules: Mapping[str, Any], contract_root: Path, events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    evaluator = modules["research_labs.candidate_c_reproduction.evaluator_b.evaluator"]
    loader = modules["research_labs.candidate_c_reproduction.evaluator_b.contract_loader"]
    model = modules["research_labs.candidate_c_reproduction.evaluator_b.models"]
    frozen, rows = loader.load_frozen_contracts(contract_root), []
    for event in events:
        roles, chart = event.get("eventRoles"), event.get("chartIdentity")
        if not isinstance(roles, Mapping): raise RuntimeFailure("B event lacks roles")
        value = dict(event); value["eventRoles"] = {"sourceBody": roles.get("sourceBody"), "targetBody": roles.get("targetBody")}; value["chartIdentity"] = str(chart.get("chartId", "")) if isinstance(chart, Mapping) else str(chart or "")
        item = model.SyntheticEvent.from_mapping(value)
        motion, motion_value = evaluator._motion_row(item, frozen)
        generated = [evaluator._natural_class(item, frozen, motion_value), evaluator._relationship_row(item, frozen), evaluator._temporary_row(item, frozen), evaluator._compound_row(item, frozen), evaluator._ordinary_drsti_row(item, frozen), evaluator._special_drsti_row(item, frozen), motion, evaluator._individual_record_row(item, frozen)]
        evaluator.validate_output_rows(generated, frozen); rows.extend(generated)
    return rows


def _run_v2(modules: Mapping[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    model = modules["research_labs.candidate_c_reproduction.comparator_ab.models"]
    projection = modules["research_labs.candidate_c_reproduction.comparator_ab.projection"]
    comparator = modules["research_labs.candidate_c_reproduction.comparator_ab.comparator"]
    a_by, b_by = payload.get("aRowsByEvent", {}), payload.get("bRowsByEvent", {})
    mismatches: list[dict[str, Any]] = []; a_projected = b_projected = 0
    for raw in payload.get("fixtures", []):
        event_id = str(raw["fixtureId"]); a_rows, b_rows = a_by.get(event_id, []), b_by.get(event_id, [])
        if len(a_rows) != 8 or len(b_rows) != 8 or any(row.get("eventId") != event_id for row in [*a_rows, *b_rows]): raise RuntimeFailure("V2 requires eight aligned rows per event")
        fixture = model.NeutralFixture(fixture_id=event_id, fixture_family=str(raw["fixtureFamily"]), source_body=str(raw["sourceBody"]), target_body=str(raw["targetBody"]), source_sign_index=int(raw["sourceSignIndex"]), target_sign_index=int(raw["targetSignIndex"]), sun_sign_index=int(raw["sunSignIndex"]), coverage_tags=tuple(raw["coverageTags"]), optional_aspect_type=raw.get("optionalAspectType"), semantic_fixture_identity_hash=str(raw["semanticFixtureIdentityHash"]))
        pa, pb = projection.project_rows(fixture, a_rows), projection.project_rows(fixture, b_rows)
        a_projected += len(pa); b_projected += len(pb); mismatches.extend(comparator.compare_projected_batches(fixture, pa, pb))
    return {"projectedARowCount": a_projected, "projectedBRowCount": b_projected, "semanticRowsCompared": a_projected, "mismatches": mismatches}


def execute_worker(raw: bytes, *, role: str, runtime_root: Path, contract_input_root: Path, manifest_path: Path) -> dict[str, Any]:
    request: dict[str, Any] = {}
    try:
        request = _load(raw, role); manifest = _manifest(manifest_path, request["runtimeManifestHash"]); entry = manifest["runtimeRoots"][role]
        if runtime_root.resolve() == manifest_path.resolve().parents[2]: raise RuntimeFailure("controller checkout cannot be a worker root")
        claims = _claims(request, entry, request["payload"]); _assert_root(runtime_root, str(entry["protectedCommit"])); _reject_bytecode(runtime_root); _verify_bytes(runtime_root, entry["protectedFiles"]); _reject_preload()
        modules = _import_verified(runtime_root, entry["protectedFiles"], entry["moduleImports"])
        if role == "EVALUATOR_A": result: Any = _run_a(modules, contract_input_root, request["payload"]["events"], bool(claims["testOnly"]))
        elif role == "EVALUATOR_B": result = _run_b(modules, contract_input_root, request["payload"]["events"])
        else: result = _run_v2(modules, request["payload"])
        count = len(result) if isinstance(result, list) else int(result["semanticRowsCompared"])
        return _response({"schemaVersion": IPC_SCHEMA_VERSION, "runSessionId": request["runSessionId"], "workerRole": role, "requestId": request["requestId"], "requestHash": _request_hash(request), "runtimeVerificationStatus": "VERIFIED_ROOT_BYTES_IMPORT_PATH_REVERIFIED_EXECUTED_SAME_PROCESS", "runtimeRootIdentity": {"runtimeRootName": entry["runtimeRootName"], "protectedCommit": entry["protectedCommit"], "pid": os.getpid(), "verificationPid": os.getpid(), "executionPid": os.getpid()}, "importPathVerificationStatus": "VERIFIED_DESIGNATED_ROOT", "outputRowCount": count, "outputPayload": {"result": result, "diagnostic": {"testOnly": claims["testOnly"], "scientificInvocationPid": os.getpid()}}})
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return _response({"schemaVersion": IPC_SCHEMA_VERSION, "runSessionId": str(request.get("runSessionId", "UNKNOWN")), "workerRole": role, "requestId": str(request.get("requestId", "UNKNOWN")), "requestHash": _request_hash(request), "runtimeVerificationStatus": "FAILED", "runtimeRootIdentity": {"pid": os.getpid()}, "importPathVerificationStatus": "NOT_REACHED", "outputRowCount": 0, "outputPayload": {"errorCode": type(exc).__name__, "message": str(exc)}})
