"""Build EMP0 source-only states from immutable AUTH1 outputs."""

from __future__ import annotations

import json
import hashlib
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_labs.candidate_c_reproduction.comparator_ab.models import NeutralFixture
from research_labs.candidate_c_reproduction.comparator_ab import projection as frozen_projection
from research_labs.candidate_c_reproduction.comparator_ab.projection import PROJECTION_CONTRACT, project_rows
from research_labs.candidate_c_reproduction.real_run.admission import load_and_validate_real_population
from research_labs.candidate_c_reproduction.real_run.artifacts_r3r3 import verify_artifact
from research_labs.candidate_c_reproduction.real_run.real_v2_bridge_r3r2 import bridge_event

from .canonical import canonical_json_text, self_hash


AUTH1_A_PATH = Path("status/research/mo_r4a_candidate_c_run1_evaluator_a_real_output_v1.json")
AUTH1_B_PATH = Path("status/research/mo_r4a_candidate_c_run1_evaluator_b_real_output_v1.json")
AUTH1_COMPARISON_PATH = Path("status/research/mo_r4a_candidate_c_run1_ab_comparison_result_v1.json")
AUTH1_A_HASH = "D72622AFDA30DC1092D0E96E40714FB1C1B37737E3B8BB8FCCB94DA55FCB0F25"
AUTH1_B_HASH = "A9B9F19A2868FE85478357A47BB8BB3B1EBBBA84A85CE27D2268DDFD5ACE17C9"
AUTH1_COMPARISON_HASH = "A368D85E9AF89D8C8B3ED07A22357F324497A78C88C5F10FE80894CAF7DDD335"
MIN_STATE_COUNT = 20
MIN_TOTAL_TEST_COUNT = 60
V2_PROTECTED_COMMIT = "52c3b287a70018370e153a77b84c36e6b0dbfb42"
V2_PROJECTION_PATH = "research_labs/candidate_c_reproduction/comparator_ab/projection.py"
V2_PROJECTION_BLOB_SHA256 = "4B4828FF09494EA3EAE8ACF57B0004177E6507B8ED8A198871F861E60C2AAF5E"


class SourceStateError(ValueError):
    """Raised when immutable AUTH1 source evidence is inconsistent."""


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceStateError(f"expected object at {path}")
    return value


def _verify_frozen_v2_projection(base: Path) -> None:
    """Fail closed unless the imported V2 projector matches its protected blob."""

    current_bytes = Path(frozen_projection.__file__).read_bytes()
    if hashlib.sha256(current_bytes).hexdigest().upper() != V2_PROJECTION_BLOB_SHA256:
        raise SourceStateError("imported V2 projection bytes differ from the protected projection blob")
    committed_bytes = subprocess.check_output(["git", "show", f"{V2_PROTECTED_COMMIT}:{V2_PROJECTION_PATH}"], cwd=base)
    if hashlib.sha256(committed_bytes).hexdigest().upper() != V2_PROJECTION_BLOB_SHA256:
        raise SourceStateError("protected V2 projection Git blob identity mismatch")


def _fixture_from_event(event: Mapping[str, Any]) -> NeutralFixture:
    bridge = bridge_event(event)
    return NeutralFixture(
        fixture_id=bridge["fixtureId"],
        semantic_fixture_identity_hash=bridge["semanticFixtureIdentityHash"],
        fixture_family=bridge["fixtureFamily"],
        source_body=bridge["sourceBody"],
        target_body=bridge["targetBody"],
        source_sign_index=bridge["sourceSignIndex"],
        target_sign_index=bridge["targetSignIndex"],
        sun_sign_index=bridge["sunSignIndex"],
        coverage_tags=tuple(bridge["coverageTags"]),
        optional_aspect_type=bridge["optionalAspectType"],
    )


def _row_slot(view: Mapping[str, Any]) -> dict[str, str]:
    return {
        "sourceProfile": str(view["sourceProfile"]),
        "componentId": str(view["componentId"]),
        "sourceContractId": str(view["sourceContractId"]),
        "operatorId": str(view["operatorId"]),
    }


def _semantic_view(row: Any) -> dict[str, Any]:
    view = row.comparison_view()
    return {key: view[key] for key in sorted(view) if key not in {"fixtureId", "semanticFixtureIdentityHash"}}


def _index_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        event_id = row.get("eventId")
        if not isinstance(event_id, str):
            raise SourceStateError("AUTH1 row has no eventId")
        grouped[event_id].append(row)
    return grouped


def build_source_state_snapshot(root: Path | str = ".") -> dict[str, Any]:
    """Reproject immutable A/B rows with the frozen V2 semantic projector."""

    base = Path(root).resolve()
    _verify_frozen_v2_projection(base)
    a_artifact = _read_json(base / AUTH1_A_PATH)
    b_artifact = _read_json(base / AUTH1_B_PATH)
    comparison = _read_json(base / AUTH1_COMPARISON_PATH)
    if not all(verify_artifact(item) for item in (a_artifact, b_artifact, comparison)):
        raise SourceStateError("AUTH1 artifact self-hash verification failed")
    if a_artifact.get("artifactSelfHash") != AUTH1_A_HASH or b_artifact.get("artifactSelfHash") != AUTH1_B_HASH:
        raise SourceStateError("AUTH1 evaluator artifact identity mismatch")
    if comparison.get("artifactSelfHash") != AUTH1_COMPARISON_HASH or comparison.get("totalMismatches") != 0:
        raise SourceStateError("AUTH1 comparison is not the accepted zero-mismatch result")

    population = load_and_validate_real_population(base)
    a_by_event = _index_rows(a_artifact.get("rows", []))
    b_by_event = _index_rows(b_artifact.get("rows", []))
    records: list[dict[str, Any]] = []
    for event in population.events:
        event_id = str(event["eventId"])
        a_rows, b_rows = a_by_event.get(event_id), b_by_event.get(event_id)
        if a_rows is None or b_rows is None or len(a_rows) != 8 or len(b_rows) != 8:
            raise SourceStateError(f"AUTH1 event {event_id} does not retain eight A/B rows")
        fixture = _fixture_from_event(event)
        a_projected = project_rows(fixture, a_rows)
        b_projected = project_rows(fixture, b_rows)
        a_index = {row.row_key(): row for row in a_projected}
        b_index = {row.row_key(): row for row in b_projected}
        if len(a_index) != 8 or len(b_index) != 8 or set(a_index) != set(b_index):
            raise SourceStateError(f"AUTH1 event {event_id} row slots do not agree")
        for key in sorted(a_index):
            a_view, b_view = _semantic_view(a_index[key]), _semantic_view(b_index[key])
            if a_view != b_view:
                raise SourceStateError(f"AUTH1 semantic projection disagreement for {event_id}/{key}")
            slot = _row_slot(a_view)
            record: dict[str, Any] = {
                "eventId": event_id,
                "eventHash": str(event["eventHash"]),
                "sideIdentity": str(event["sideIdentity"]),
                "exactUtc": str(event["exactUtc"]),
                "rowSlot": slot,
                "canonicalRowSlotId": canonical_json_text(slot),
                "sourceProfile": slot["sourceProfile"],
                "componentId": slot["componentId"],
                "sourceContractId": slot["sourceContractId"],
                "operatorId": slot["operatorId"],
                "operatorVersion": a_view.get("operatorVersion"),
                "outputStatus": a_view["outputStatus"],
                "sourceStatus": a_view.get("sourceStatus"),
            }
            if a_view["outputStatus"] == "VALUE":
                token = {"outputStatus": "VALUE", "sourceValue": a_view["sourceValue"]}
                record["sourceValue"] = a_view["sourceValue"]
                record["stateToken"] = token
                record["stateTokenCanonicalJson"] = canonical_json_text(token)
                record["inferentialDisposition"] = "VALUE_STATE_CANDIDATE"
            else:
                record["unknownReasonCode"] = a_view["unknownReasonCode"]
                record["inferentialDisposition"] = "SOURCE_UNKNOWN_ABSTAIN"
            records.append(record)
    if len(records) != 5160:
        raise SourceStateError(f"expected 5160 source states, got {len(records)}")
    if len({(item["eventId"], item["canonicalRowSlotId"]) for item in records}) != 5160:
        raise SourceStateError("source-state records are not unique by event and row slot")
    snapshot = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_CANONICAL_SOURCE_STATE_SNAPSHOT_V1",
        "milestone": "MO-R4A-CANDIDATE-C-EMP0-OUTCOME-BLIND-MARKET-TEST-PREREGISTRATION-AND-ANALYSIS-FREEZE",
        "projectionContractId": PROJECTION_CONTRACT["contractId"],
        "auth1AArtifactHash": AUTH1_A_HASH,
        "auth1BArtifactHash": AUTH1_B_HASH,
        "auth1ComparisonHash": AUTH1_COMPARISON_HASH,
        "populationEventCount": 645,
        "populationHash": a_artifact["populationHash"],
        "populationOrderHash": a_artifact["populationOrderHash"],
        "rowSlotsPerEvent": 8,
        "canonicalSourceStateRowCount": len(records),
        "aBSemanticProjectionAgreement": True,
        "sourceOutputRead": True,
        "marketOutcomeRead": False,
        "sourceStateRecords": records,
        "canonicalSourceStateSnapshotHash": None,
    }
    snapshot["canonicalSourceStateSnapshotHash"] = self_hash(snapshot, "canonicalSourceStateSnapshotHash")
    return snapshot


def build_source_state_eligibility(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Freeze source-only VALUE-state eligibility without any market observation."""

    records = snapshot.get("sourceStateRecords")
    if not isinstance(records, list) or len(records) != 5160:
        raise SourceStateError("source snapshot must retain exactly 5160 records")
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(str(record["sideIdentity"]), str(record["canonicalRowSlotId"]))].append(record)
    cells: list[dict[str, Any]] = []
    for (side, slot_id), rows in sorted(grouped.items()):
        values = Counter(str(row["stateTokenCanonicalJson"]) for row in rows if row["outputStatus"] == "VALUE")
        unknowns = [row for row in rows if row["outputStatus"] == "UNKNOWN"]
        unknown_reasons = Counter(str(row["unknownReasonCode"]) for row in unknowns)
        eligible = sorted(token for token, count in values.items() if count >= MIN_STATE_COUNT)
        rare = sorted(token for token, count in values.items() if count < MIN_STATE_COUNT)
        eligible_total = sum(values[token] for token in eligible)
        if not values:
            testable, reason = False, "NOT_EMPIRICALLY_TESTABLE_SOURCE_ABSTENTION"
        elif len(eligible) < 2:
            testable, reason = False, "INSUFFICIENT_SOURCE_ELIGIBLE_STATES"
        elif eligible_total < MIN_TOTAL_TEST_COUNT:
            testable, reason = False, "INSUFFICIENT_SOURCE_ELIGIBLE_TOTAL"
        else:
            testable, reason = True, None
        cells.append({
            "sideIdentity": side,
            "canonicalRowSlotId": slot_id,
            "rowSlot": json.loads(slot_id),
            "valueStateCounts": [{"stateTokenCanonicalJson": token, "count": values[token]} for token in sorted(values)],
            "unknownCount": len(unknowns),
            "unknownReasonCounts": dict(sorted(unknown_reasons.items())),
            "rareValueStates": [{"stateTokenCanonicalJson": token, "count": values[token], "disposition": "RARE_VALUE_STATE_DESCRIPTIVE_ONLY"} for token in rare],
            "eligibleValueStates": [{"stateTokenCanonicalJson": token, "count": values[token]} for token in eligible],
            "eligibleValueStateCount": len(eligible),
            "eligibleValueTotalCount": eligible_total,
            "sourceTestable": testable,
            "nonTestableReason": reason,
        })
    eligibility = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_SOURCE_STATE_ELIGIBILITY_V1",
        "sourceSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"],
        "minStateCount": MIN_STATE_COUNT,
        "minTotalTestCount": MIN_TOTAL_TEST_COUNT,
        "unknownDisposition": "SOURCE_UNKNOWN_ABSTAIN",
        "cells": cells,
        "sourceStateEligibilityHash": None,
    }
    eligibility["sourceStateEligibilityHash"] = self_hash(eligibility, "sourceStateEligibilityHash")
    return eligibility
