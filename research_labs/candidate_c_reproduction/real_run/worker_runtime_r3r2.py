"""One-process-per-role batch runtime for fake R3R2A production-shape probes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .worker_runtime import (
    TEST_EVENT_PREFIX, _assert_clean_git_root, _isolate_path, _reject_bytecode,
    _reject_preload, _run_a, _run_b, _run_v2, _verify_bytes, _verify_modules,
)


class BatchWorkerError(RuntimeError):
    """Raised before an invalid batch reaches a frozen science function."""


def _fake_events(events: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    if not events or any(not isinstance(event.get("eventId"), str) or not str(event["eventId"]).startswith(TEST_EVENT_PREFIX) for event in events):
        raise BatchWorkerError("R3R2A batch workers accept FAKE_REAL_RUN1 events only")
    if len({event["eventId"] for event in events}) != len(events):
        raise BatchWorkerError("fake batch event IDs must be unique")
    return list(events)


def run_fake_evaluator_batch(
    role: str, runtime_root: Path, contract_input_root: Path, role_entry: Mapping[str, Any], events: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Run all fake events in one protected-runtime process and return raw rows."""

    batch = _fake_events(events)
    _assert_clean_git_root(runtime_root, str(role_entry["protectedCommit"]))
    _reject_bytecode(runtime_root)
    _verify_bytes(runtime_root, role_entry["protectedFiles"])
    _reject_preload()
    _isolate_path(runtime_root)
    modules = _verify_modules(runtime_root, role_entry["protectedFiles"], role_entry["moduleImports"])
    rows: list[dict[str, Any]] = []
    for event in batch:
        if role == "EVALUATOR_A":
            synthetic = dict(event)
            synthetic["_evaluatorInputKind"] = "SYNTHETIC_ONLY"
            rows.extend(_run_a(modules, contract_input_root, synthetic))
        elif role == "EVALUATOR_B":
            rows.extend(_run_b(modules, contract_input_root, event))
        else:
            raise BatchWorkerError("batch evaluator role is invalid")
    return {"workerRole": role, "pid": os.getpid(), "eventCount": len(batch), "outputRowCount": len(rows), "rows": rows}


def run_fake_v2_batch(
    runtime_root: Path, role_entry: Mapping[str, Any], fixtures: Sequence[Mapping[str, Any]], a_rows_by_event: Mapping[str, Sequence[Mapping[str, Any]]], b_rows_by_event: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Run all fake fixture comparisons in one protected V2 process."""

    _assert_clean_git_root(runtime_root, str(role_entry["protectedCommit"]))
    _reject_bytecode(runtime_root)
    _verify_bytes(runtime_root, role_entry["protectedFiles"])
    _reject_preload()
    _isolate_path(runtime_root)
    modules = _verify_modules(runtime_root, role_entry["protectedFiles"], role_entry["moduleImports"])
    compared = 0
    mismatches: list[dict[str, Any]] = []
    for fixture in fixtures:
        event_id = str(fixture["fixtureId"])
        a_rows, b_rows = list(a_rows_by_event.get(event_id, [])), list(b_rows_by_event.get(event_id, []))
        if len(a_rows) != 8 or len(b_rows) != 8 or any(row.get("eventId") != event_id for row in [*a_rows, *b_rows]):
            raise BatchWorkerError("cross-event row mixing or incomplete event batch before V2")
        result = _run_v2(modules, {"fixture": fixture, "aRows": a_rows, "bRows": b_rows})
        compared += int(result["projectedARowCount"])
        mismatches.extend(result["mismatches"])
    return {"workerRole": "V2_COMPARATOR", "pid": os.getpid(), "eventCount": len(fixtures), "semanticRowsCompared": compared, "mismatches": mismatches}


def run_real_batch(*_: Any, **__: Any) -> None:
    raise BatchWorkerError("external authorization is absent; real Candidate C batch execution is unavailable")
