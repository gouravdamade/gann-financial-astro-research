"""Outcome-blind S2R1_R1 successor freeze after Saravali relationship lineage closure.

This module reads only immutable historical S2/S1R1-R1 artifacts, the checked-in
Saravali successor records, and blank-packet identities. It never regenerates
astronomy and never reads review, price, outcome, SBC, catalogue, or execution
state.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Mapping

import blinded_market_bridge_s2 as s2
import blinded_market_bridge_s2r1 as historical_s2r1
import classical_source_operators as operators


S2R1_R1_HYPOTHESIS_REGISTRY_CONTRACT = "MACHINE_ASSISTED_EXPERIMENTAL_MARKET_HYPOTHESIS_REGISTRY_S2R1_R1_V1"
S2R1_R1_PREDICTION_FREEZE_CONTRACT = "MO_R4A_S2R1_R1_BLINDED_MARKET_BRIDGE_PREDICTION_FREEZE_V1"
S2R1_R1_INVARIANCE_AUDIT_CONTRACT = "MO_R4A_S2R1_R1_BLINDED_MARKET_BRIDGE_INVARIANCE_AUDIT_V1"
S2R1_R1_ACCEPTANCE_CONTRACT = "MO_R4A_S2R1_R1_BLINDED_MARKET_BRIDGE_HYPOTHESIS_FREEZE_V1"
S2R1_R1_LINEAGE_RECONCILIATION_CONTRACT = "MO_R4A_S2R1_R1_SARAVALI_RELATIONSHIP_LINEAGE_RECONCILIATION_V1"
S2R1_R1_EXPECTED_STARTING_MASTER = "a620ae4a33b7455087aee7a4ded296d60b7ae450"
HISTORICAL_S1R1_R1_LEDGER_HASH = "00A63DFA1ED2154D9935D9502191D5574C5D1BF38E924ABD8BDA95FD9E6C1379"
HISTORICAL_S1R1_R1_COVERAGE_HASH = "359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD"
HISTORICAL_S2R1_LEDGER_HASH = "E9DB0C92B449045FB2ED35D482E3F7063C547CD2562305EEF778064C2F5558E6"
HISTORICAL_S2R1_COVERAGE_HASH = "B22F42E78D20858045AE98F0010355E1E8895C60F1DD49570230ECC5B2C7F62A"
HISTORICAL_S2R1_REGISTRY_HASH = "4655316D94188E9B4187E24D67DC9466124C977002F129508F62B518F4786CDE"
HISTORICAL_S2R1_FREEZE_HASH = "68E7FEDB23EBD3CF52367DF7DEAB241977C7EA8B1720BCF4F01C07F89CB34F7C"
HISTORICAL_S2R1_INVARIANCE_AUDIT_HASH = "A282DC181591B1F7BA11457E3F86A3FBBDCF54290BF7A3C0E98CDB3140AD07BC"
HISTORICAL_S2R1_RECONCILIATION_HASH = "8C973561EC72B5FF00AA057C1353946B9792F85E13CFBA8EFF6972C356E39B01"
HISTORICAL_S2R1_ACCEPTANCE_HASH = "72404E54ECC169107AD5C5CDB3932D5827D3319D19D29EF252F2C60C64416C75"
S2R1_R1_EXPECTED_LEDGER_HASH = "2D4AD6E151602FBF2FC3E0ADDFDCDE7C7211CC52ED44D801AD3925AD9D5F3366"
S2R1_R1_EXPECTED_COVERAGE_HASH = "A4437C2A116EBD5D465339BCB0C9D81F8149CE65FAF37CF81C0F29D75B44F8B0"
S2R1_R1_HYPOTHESIS_FAMILY_ID = "MO_R4A_S2R1_R1_COMPOUND_RELATIONSHIP_DIRECT_VALENCE_V1"
S2R1_R1_HYPOTHESIS_IDS = {
    "USD": "H-MO-S2R1-R1-COMPOUND-REL-DIRECT-USD-V1",
    "JPY": "H-MO-S2R1-R1-COMPOUND-REL-DIRECT-JPY-V1",
}
S2R1_R1_GUARDRAIL_KEYS = s2.S2_GUARDRAIL_KEYS
S2R1_R1_SIDES = s2.S2_SIDES

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
SOURCE_OPERATOR_ROOT = MACHINE_INTERPRETATION_ROOT / "source_operators"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_S2R1_R1_REGISTRY_PATH = MACHINE_INTERPRETATION_ROOT / "experimental_market_hypothesis_registry_s2r1_r1_v1.json"
DEFAULT_S2R1_R1_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_s2r1_r1_saravali_adjudicated_v1.json"
DEFAULT_S2R1_R1_COVERAGE_PATH = AUDIT_ROOT / "mo_r4a_s2r1_r1_real_24_source_operator_coverage.json"
DEFAULT_S2R1_R1_FREEZE_PATH = AUDIT_ROOT / "mo_r4a_s2r1_r1_blinded_market_bridge_prediction_freeze.json"
DEFAULT_S2R1_R1_INVARIANCE_AUDIT_PATH = AUDIT_ROOT / "mo_r4a_s2r1_r1_blinded_market_bridge_invariance_audit.json"
DEFAULT_S2R1_R1_RECONCILIATION_PATH = AUDIT_ROOT / "mo_r4a_s2r1_r1_saravali_relationship_lineage_reconciliation.json"
DEFAULT_S2R1_R1_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s2r1_r1_blinded_market_bridge_hypothesis_freeze.json"
DEFAULT_S2R1_R1_REVIEW_TABLE_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S2R1_R1_REAL_24_EVENT_PREDICTION_FREEZE.md"


class BlindedMarketBridgeS2R1_R1Error(ValueError):
    """Raised if the successor loses its exact source or outcome-blind bindings."""


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BlindedMarketBridgeS2R1_R1Error(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BlindedMarketBridgeS2R1_R1Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(raw, dict):
        raise BlindedMarketBridgeS2R1_R1Error(f"{label} must be a JSON object")
    return raw


def _exact_keys(mapping: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(mapping, dict) or set(mapping) != expected:
        raise BlindedMarketBridgeS2R1_R1Error(f"{label} keys do not match its bounded contract")
    return mapping


def _assert_hash(value: Any, label: str) -> str:
    value = str(value or "")
    if len(value) != 64 or any(character not in "0123456789ABCDEF" for character in value):
        raise BlindedMarketBridgeS2R1_R1Error(f"{label} must be an uppercase SHA-256")
    return value


def _entry_content(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in entry.items() if key != "hypothesisHash"}


def _load_registry(path: Path) -> s2.S2HypothesisRegistry:
    expected = {
        "contract", "schemaVersion", "registryId", "registryStatus", "purpose", "entryPolicy", "startingMaster",
        "historicalS2R1RegistryHash", "historicalS2R1PredictionFreezeHash", "sourceAdjudicationReason",
        "upstreamSourceLedgerContract", "upstreamSourceLedgerHash", "upstreamCoverageContract", "upstreamCoverageHash",
        "hypothesisFamilyId", "entries", "guardrails", "registryHash",
    }
    raw = _exact_keys(_read_json(path, "S2R1_R1 market hypothesis registry"), expected, "S2R1_R1 market hypothesis registry")
    if (
        raw["contract"], raw["schemaVersion"], raw["registryStatus"], raw["startingMaster"], raw["hypothesisFamilyId"]
    ) != (
        S2R1_R1_HYPOTHESIS_REGISTRY_CONTRACT, 1, "AUTHORIZED_FOR_BLINDED_SUCCESSOR_REFREEZE", S2R1_R1_EXPECTED_STARTING_MASTER,
        S2R1_R1_HYPOTHESIS_FAMILY_ID,
    ):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry has an unauthorized identity")
    if (raw["historicalS2R1RegistryHash"], raw["historicalS2R1PredictionFreezeHash"]) != (
        HISTORICAL_S2R1_REGISTRY_HASH, HISTORICAL_S2R1_FREEZE_HASH
    ):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1-R1 registry does not preserve the historical S2R1 bindings")
    if (raw["upstreamSourceLedgerContract"], raw["upstreamSourceLedgerHash"], raw["upstreamCoverageContract"], raw["upstreamCoverageHash"]) != (
        operators.CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT, S2R1_R1_EXPECTED_LEDGER_HASH,
        operators.CLASSICAL_SOURCE_OPERATOR_S2R1_R1_COVERAGE_CONTRACT, S2R1_R1_EXPECTED_COVERAGE_HASH,
    ):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry is not bound to the exact Saravali successor source artifacts")
    s2._require_false_flags(raw["guardrails"], S2R1_R1_GUARDRAIL_KEYS, "S2R1_R1 registry guardrails")
    entries_raw = raw["entries"]
    if not isinstance(entries_raw, list) or len(entries_raw) != 2:
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry requires exactly two side-local hypotheses")
    entries: list[s2.S2MarketHypothesis] = []
    expected_entry_keys = {
        "hypothesisFamilyId", "hypothesisId", "version", "author", "createdAtUtc", "hypothesisScope", "bridgeBasis",
        "inputOperatorIds", "primaryInputOperatorId", "primaryInputOperatorVersion", "stateMap", "targetSide",
        "applicabilityPolicy", "abstentionPolicy", "sourceClaim", "experimentalClaim", "reasoning", "sourceDependencies",
        "experimentalAssumptions", "prohibitedGeneralizations", "validationStatus", "outcomeDataSeenAtCreation",
        "approvalStatus", "signedUnitIfConfigured", "magnitudeConfigured", "mode", "productionAdmission",
        "supersedesHypothesisId", "supersedesHypothesisHash", "sourceAdjudicationReason",
        "newUpstreamSourceLedgerHash", "newUpstreamCoverageHash", "hypothesisHash",
    }
    historical_ids = historical_s2r1.S2R1_HYPOTHESIS_IDS
    for entry in entries_raw:
        entry = _exact_keys(entry, expected_entry_keys, "S2R1_R1 hypothesis")
        side = str(entry["targetSide"])
        if (
            entry["hypothesisFamilyId"], entry["version"], entry["bridgeBasis"], entry["inputOperatorIds"],
            entry["primaryInputOperatorId"], entry["primaryInputOperatorVersion"], entry["stateMap"],
            entry["applicabilityPolicy"], entry["abstentionPolicy"], entry["validationStatus"], entry["approvalStatus"],
            entry["outcomeDataSeenAtCreation"], entry["signedUnitIfConfigured"], entry["magnitudeConfigured"], entry["mode"],
            entry["productionAdmission"], entry["supersedesHypothesisId"], entry["newUpstreamSourceLedgerHash"], entry["newUpstreamCoverageHash"],
        ) != (
            S2R1_R1_HYPOTHESIS_FAMILY_ID, "1", "SOURCE_OPERATOR_STATE_PREDICATE", [s2.S2_PRIMARY_OPERATOR_ID],
            s2.S2_PRIMARY_OPERATOR_ID, "1", s2.S2_STATE_MAP,
            "SOURCE_CLOSED_MACHINE_EVALUATED_COMPOUND_RELATIONSHIP_ONLY",
            {"currencyPressureState": "UNKNOWN_MORE_EVIDENCE_REQUIRED", "bridgeApplied": False, "fallbackOperatorAllowed": False},
            "NOT_FINANCIALLY_VALIDATED", "AUTHORIZED_FOR_BLINDED_TEST", False, None, False, "EXPERIMENTAL_PROFILED",
            False, historical_ids.get(side), S2R1_R1_EXPECTED_LEDGER_HASH, S2R1_R1_EXPECTED_COVERAGE_HASH,
        ):
            raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 hypothesis exceeds its bounded direct compound-state bridge")
        _assert_hash(entry["supersedesHypothesisHash"], "S2R1_R1 supersedesHypothesisHash")
        if entry["hypothesisHash"] != s2._canonical_hash(_entry_content(entry)):
            raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 hypothesis hash does not bind the successor decision content")
        entries.append(s2.S2MarketHypothesis(raw=copy.deepcopy(entry), hypothesis_hash=entry["hypothesisHash"]))
    by_side = {entry.target_side: entry for entry in entries}
    if set(by_side) != set(S2R1_R1_SIDES) or {entry.hypothesis_id for entry in entries} != set(S2R1_R1_HYPOTHESIS_IDS.values()):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry must contain one approved USD and one approved JPY successor")
    if raw["registryHash"] != s2._canonical_hash({key: copy.deepcopy(value) for key, value in raw.items() if key != "registryHash"}):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry hash does not bind its frozen contents")
    return s2.S2HypothesisRegistry(raw=copy.deepcopy(raw), entries_by_side=by_side, registry_hash=raw["registryHash"])


def _load_verified_upstream_inputs(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    ledger = _read_json(root / DEFAULT_S2R1_R1_LEDGER_PATH.relative_to(PROJECT_ROOT), "S2R1_R1 successor ledger")
    coverage = _read_json(root / DEFAULT_S2R1_R1_COVERAGE_PATH.relative_to(PROJECT_ROOT), "S2R1_R1 successor coverage")
    if (ledger.get("contract"), s2._canonical_hash(ledger)) != (operators.CLASSICAL_SOURCE_OPERATOR_S2R1_R1_LEDGER_CONTRACT, S2R1_R1_EXPECTED_LEDGER_HASH):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 ledger has an unexpected source lineage binding")
    coverage_body = {key: copy.deepcopy(value) for key, value in coverage.items() if key != "sourceOperatorCoverageHash"}
    if (
        coverage.get("contract"), coverage.get("sourceOperatorCoverageHash"), s2._canonical_hash(coverage_body),
        coverage.get("sourceOperatorLedgerCanonicalHash"),
    ) != (
        operators.CLASSICAL_SOURCE_OPERATOR_S2R1_R1_COVERAGE_CONTRACT, S2R1_R1_EXPECTED_COVERAGE_HASH, S2R1_R1_EXPECTED_COVERAGE_HASH,
        S2R1_R1_EXPECTED_LEDGER_HASH,
    ):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 coverage has an unexpected source lineage binding")
    if ledger != operators.build_s2r1_r1_saravali_adjudicated_ledger(root) or coverage != operators.build_s2r1_r1_real_24_source_operator_coverage(root):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 checked-in source artifacts do not match deterministic source rebinding")
    for key in ("reviewStoreRead", "founderDecisionRead", "priceOrOutcomeRead", "eventUniverseRegenerated"):
        if coverage.get(key) is not False:
            raise BlindedMarketBridgeS2R1_R1Error(f"S2R1_R1 coverage guardrail is no longer false: {key}")
    return ledger, coverage


def build_s2r1_r1_blinded_prediction_freeze(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Freeze the successor's two side-local predictions from corrected source lineage only."""

    root = Path(resource_root).resolve()
    registry = _load_registry(root / DEFAULT_S2R1_R1_REGISTRY_PATH.relative_to(PROJECT_ROOT))
    _, coverage = _load_verified_upstream_inputs(root)
    if (
        registry.raw["upstreamSourceLedgerHash"], registry.raw["upstreamCoverageHash"],
    ) != (coverage["sourceOperatorLedgerCanonicalHash"], coverage["sourceOperatorCoverageHash"]):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 registry is not bound to its checked-in successor source coverage")
    identities_by_side = s2._load_immutable_blank_packet_identities(root, coverage)
    predictions: list[dict[str, Any]] = []
    for coverage_side in coverage["sides"]:
        side = coverage_side["sideIdentity"]
        events = coverage_side["events"]
        identities = identities_by_side.get(side)
        if not isinstance(identities, list) or len(events) != len(identities) != 12:
            raise BlindedMarketBridgeS2R1_R1Error(f"S2R1_R1 coverage/identity order mismatch for {side}")
        for event, identity in zip(events, identities, strict=True):
            prediction = s2._build_prediction(event, identity, registry.entries_by_side[side], registry)
            prediction["sourceLineage"] = "SARAVALI_NATURAL_RELATIONSHIP_V1_PLUS_BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"
            body = {key: copy.deepcopy(value) for key, value in prediction.items() if key != "eventPredictionHash"}
            prediction["eventPredictionHash"] = s2._canonical_hash(body)
            predictions.append(prediction)
    if len(predictions) != 24 or len({item["eventId"] for item in predictions}) != 24:
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 requires exactly 24 unique frozen events")
    per_side = [s2._side_counts(predictions, side) for side in S2R1_R1_SIDES]
    summary = {
        "eventCount": 24,
        "usdEventCount": per_side[0]["eventCount"],
        "jpyEventCount": per_side[1]["eventCount"],
        "singlePassVerifiedCount": sum(item["identityStatus"] == "SINGLE_PASS_VERIFIED" for item in predictions),
        "bridgeEligibleCount": sum(item["bridgeApplied"] for item in predictions),
        "directionalCount": sum(item["currencyPressureState"] in {"SUPPORTIVE", "ADVERSE"} for item in predictions),
        "abstentionCount": sum(not item["bridgeApplied"] for item in predictions),
        "supportiveCount": sum(item["currencyPressureState"] == "SUPPORTIVE" for item in predictions),
        "adverseCount": sum(item["currencyPressureState"] == "ADVERSE" for item in predictions),
        "neutralCount": sum(item["currencyPressureState"] == "NEUTRAL" for item in predictions),
        "unknownCount": sum(item["currencyPressureState"] == "UNKNOWN_MORE_EVIDENCE_REQUIRED" for item in predictions),
        "overallAstrologyUnknownCount": sum(item["overallAstrologicalInterpretation"] == "UNKNOWN_ASTRO_STATE" for item in predictions),
    }
    if tuple(summary[key] for key in ("eventCount", "usdEventCount", "jpyEventCount", "singlePassVerifiedCount", "bridgeEligibleCount", "directionalCount", "neutralCount", "abstentionCount")) != (24, 12, 12, 24, 17, 14, 3, 7):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 successor has an unexpected frozen pilot shape")
    body = {
        "contract": S2R1_R1_PREDICTION_FREEZE_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2R1-R1",
        "startingMaster": S2R1_R1_EXPECTED_STARTING_MASTER,
        "inputPolicy": "FROZEN_S2R1_R1_SARAVALI_LINEAGE_COVERAGE_PLUS_IMMUTABLE_BLANK_PACKET_IDENTITY_ONLY",
        "eventUniverseRegenerated": False,
        "sourceCoverageArtifactRead": True,
        "immutableBlankPacketIdentityRead": True,
        "reviewStoreRead": False,
        "founderDecisionRead": False,
        "priceDataRead": False,
        "outcomeDataRead": False,
        "historicalS2R1RegistryHash": HISTORICAL_S2R1_REGISTRY_HASH,
        "historicalS2R1PredictionFreezeHash": HISTORICAL_S2R1_FREEZE_HASH,
        "upstreamSourceLedgerContract": registry.raw["upstreamSourceLedgerContract"],
        "upstreamSourceLedgerHash": registry.raw["upstreamSourceLedgerHash"],
        "upstreamCoverageContract": registry.raw["upstreamCoverageContract"],
        "upstreamCoverageHash": registry.raw["upstreamCoverageHash"],
        "hypothesisRegistryContract": registry.raw["contract"],
        "hypothesisRegistryHash": registry.registry_hash,
        "hypothesisIds": [registry.entries_by_side[side].hypothesis_id for side in S2R1_R1_SIDES],
        "frozenEventOrder": [item["eventId"] for item in predictions],
        "predictions": predictions,
        "summary": summary,
        "perSide": per_side,
        "guardrails": {
            **{key: False for key in S2R1_R1_GUARDRAIL_KEYS},
            "productionAdmission": False,
            "eventUniverseRegenerated": False,
            "signedUnitConfigured": False,
        },
    }
    return {**body, "predictionFreezeHash": s2._canonical_hash(body)}


def _historical_s2r1_freeze(root: Path) -> dict[str, Any]:
    historical = _read_json(
        root / "status" / "audits" / "mo_r4a_s2r1_blinded_market_bridge_prediction_freeze.json",
        "historical S2R1 freeze",
    )
    body = {key: copy.deepcopy(value) for key, value in historical.items() if key != "predictionFreezeHash"}
    if historical.get("predictionFreezeHash") != HISTORICAL_S2R1_FREEZE_HASH or s2._canonical_hash(body) != HISTORICAL_S2R1_FREEZE_HASH:
        raise BlindedMarketBridgeS2R1_R1Error("Historical S2R1 prediction freeze must remain immutable")
    return historical


def build_s2r1_r1_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    prediction_freeze: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind every S2R1_R1 result to the same frozen identity and astronomy snapshot."""

    root = Path(resource_root).resolve()
    _, coverage = _load_verified_upstream_inputs(root)
    freeze = copy.deepcopy(prediction_freeze) if prediction_freeze is not None else build_s2r1_r1_blinded_prediction_freeze(root)
    if freeze.get("predictionFreezeHash") != s2._canonical_hash({key: value for key, value in freeze.items() if key != "predictionFreezeHash"}):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 freeze hash does not bind frozen content")
    coverage_events = [event for side in coverage["sides"] for event in side["events"]]
    if len(coverage_events) != len(freeze["predictions"]) != 24:
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 invariance audit requires 24 source events and predictions")
    rows = []
    for event, prediction in zip(coverage_events, freeze["predictions"], strict=True):
        rows.append(
            {
                "eventId": event["eventId"],
                "eventHash": event["eventHash"],
                "identityUnchanged": all(prediction.get(key) == event.get(key) for key in ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")),
                "astronomySnapshotUnchanged": prediction.get("astronomySnapshot") == event.get("astronomySnapshot"),
                "overallSourceCompositionUnchanged": prediction.get("overallAstrologicalCompositionStatus") == event.get("astrologicalCompositionStatus") and prediction.get("overallAstrologicalInterpretation") == event.get("astrologicalInterpretationState"),
                "predictionHash": prediction["eventPredictionHash"],
            }
        )
    if not all(row["identityUnchanged"] and row["astronomySnapshotUnchanged"] and row["overallSourceCompositionUnchanged"] for row in rows):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 successor changed an event identity, astronomy snapshot, or overall unknown composition")
    body = {
        "contract": S2R1_R1_INVARIANCE_AUDIT_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2R1-R1",
        "upstreamSourceLedgerHash": freeze["upstreamSourceLedgerHash"],
        "upstreamCoverageHash": freeze["upstreamCoverageHash"],
        "hypothesisRegistryHash": freeze["hypothesisRegistryHash"],
        "predictionFreezeHash": freeze["predictionFreezeHash"],
        "eventCount": 24,
        "rows": rows,
        "summary": {
            "allEventIdentitiesUnchanged": True,
            "allAstronomySnapshotsUnchanged": True,
            "allOverallSourceCompositionUnchanged": True,
            "sourceAstronomyRegenerated": False,
            "reviewStoreRead": False,
            "founderDecisionRead": False,
            "priceDataRead": False,
            "outcomeDataRead": False,
            "sbcRead": False,
            "catalogueAdmission": False,
            "evidenceAdmission": False,
            "signedWaveRendered": False,
            "pairResultantCreated": False,
            "magnitudeConfigured": False,
            "autoSuggestEnabled": False,
            "mlEnabled": False,
            "mt5Enabled": False,
            "executionAllowed": False,
        },
    }
    return {**body, "invarianceAuditHash": s2._canonical_hash(body)}


def build_s2r1_r1_lineage_reconciliation(
    resource_root: Path = PROJECT_ROOT,
    *,
    successor_freeze: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Record all 24 historical-to-successor source and prediction comparisons."""

    root = Path(resource_root).resolve()
    historical = _historical_s2r1_freeze(root)
    _, corrected_coverage = _load_verified_upstream_inputs(root)
    successor = copy.deepcopy(successor_freeze) if successor_freeze is not None else build_s2r1_r1_blinded_prediction_freeze(root)
    comparison = operators.build_s2r1_r1_relationship_matrix_comparison(root)
    historical_coverage = _read_json(
        root / "status" / "audits" / "mo_r4a_s2r1_real_24_source_operator_coverage.json",
        "historical S2R1 coverage",
    )
    old_events = [event for side in historical_coverage["sides"] for event in side["events"]]
    new_events = [event for side in corrected_coverage["sides"] for event in side["events"]]
    rows = []
    for old_prediction, new_prediction, old_event, new_event in zip(historical["predictions"], successor["predictions"], old_events, new_events, strict=True):
        old_natural = next(item for item in old_event["operatorOutputs"] if item["operatorId"] == "SARAVALI_NATURAL_RELATIONSHIP_V1")
        new_natural = next(item for item in new_event["operatorOutputs"] if item["operatorId"] == "SARAVALI_NATURAL_RELATIONSHIP_V1")
        old_compound = old_prediction["sourceOperatorInput"]["outputState"]
        new_compound = new_prediction["sourceOperatorInput"]["outputState"]
        prediction_changed = (old_prediction["currencyPressureState"], old_prediction["bridgeApplied"]) != (new_prediction["currencyPressureState"], new_prediction["bridgeApplied"])
        compound_changed = old_compound != new_compound
        if compound_changed or prediction_changed:
            reason = "SARAVALI_ADJUDICATION_CHANGED_A_SOURCE_OPERATOR_OUTPUT"
        else:
            reason = "SOURCE_LINEAGE_ADJUDICATION_ONLY; relationship doctrine and frozen event output remain unchanged."
        rows.append(
            {
                "eventId": old_prediction["eventId"],
                "sideIdentity": old_prediction["sideIdentity"],
                "transitBody": old_prediction["transitBody"],
                "natalTarget": old_prediction["natalTarget"],
                "historicalS2R1NaturalSource": {"operatorId": old_natural["operatorId"], "outputState": old_natural["outputState"]},
                "adjudicatedNaturalSource": {"operatorId": new_natural["operatorId"], "outputState": new_natural["outputState"]},
                "oldNaturalRelationshipOperator": old_natural["operatorId"],
                "newNaturalRelationshipOperator": new_natural["operatorId"],
                "oldNaturalRelationshipState": old_natural["outputState"],
                "newNaturalRelationshipState": new_natural["outputState"],
                "historicalS2R1CompoundState": old_compound,
                "adjudicatedCompoundState": new_compound,
                "oldCompoundState": old_compound,
                "newCompoundState": new_compound,
                "compoundStateChanged": compound_changed,
                "sourceLineageChanged": True,
                "eventIdentityChanged": False,
                "astronomyChanged": False,
                "historicalS2R1PressureState": old_prediction["currencyPressureState"],
                "adjudicatedPressureState": new_prediction["currencyPressureState"],
                "historicalS2R1BridgeApplied": old_prediction["bridgeApplied"],
                "adjudicatedBridgeApplied": new_prediction["bridgeApplied"],
                "predictionChanged": prediction_changed,
                "reason": reason,
            }
        )
    if len(rows) != 24 or any(row["eventId"] != successor["frozenEventOrder"][index] for index, row in enumerate(rows)):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 lineage diff must preserve every frozen event exactly once in order")
    summary = {
        "unchangedPredictionCount": sum(not row["predictionChanged"] for row in rows),
        "changedPredictionCount": sum(row["predictionChanged"] for row in rows),
        "changedNaturalStateCount": sum(row["oldNaturalRelationshipState"] != row["newNaturalRelationshipState"] for row in rows),
        "changedCompoundEventCount": sum(row["historicalS2R1CompoundState"] != row["adjudicatedCompoundState"] for row in rows),
        "oldSupportiveCount": historical["summary"]["supportiveCount"],
        "newSupportiveCount": successor["summary"]["supportiveCount"],
        "oldAdverseCount": historical["summary"]["adverseCount"],
        "newAdverseCount": successor["summary"]["adverseCount"],
        "oldNeutralCount": historical["summary"]["neutralCount"],
        "newNeutralCount": successor["summary"]["neutralCount"],
        "oldUnknownCount": historical["summary"]["unknownCount"],
        "newUnknownCount": successor["summary"]["unknownCount"],
        "oldBridgeAppliedCount": historical["summary"]["bridgeEligibleCount"],
        "newBridgeAppliedCount": successor["summary"]["bridgeEligibleCount"],
        "oldDirectionalCount": historical["summary"]["supportiveCount"] + historical["summary"]["adverseCount"],
        "newDirectionalCount": successor["summary"]["directionalCount"],
    }
    pilot_relevant = [row for row in comparison["comparisonRows"] if row["relationshipStatus"] == "CONFLICT" and any(item["transitBody"] == row["sourceBody"] and item["natalTarget"] == row["targetBody"] for item in rows)]
    body = {
        "contract": S2R1_R1_LINEAGE_RECONCILIATION_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2R1-R1",
        "startingMaster": S2R1_R1_EXPECTED_STARTING_MASTER,
        "saravaliWitnessId": "SARAVALI_RANJAN_SANTHANAM_1983_HELD_PARTIAL",
        "saravaliWitnessSha256": "3BFD4F7F717798F87B7EFD6FA5A3DE2E28E7E09FC2520F0F05AE12B2E1BF9A58",
        "exactSourceLocator": "Saravali 4.28-29, printed p.56 / scan p.60",
        "sourceLayer": "SARAVALI_ROOT",
        "saravaliNaturalRelationshipOperatorId": "SARAVALI_NATURAL_RELATIONSHIP_V1",
        "trailokyaNaturalRelationshipOperatorId": "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
        "comparisonRows": comparison["comparisonRows"],
        "comparisonSummary": comparison["comparisonSummary"],
        "pilotRelevantConflicts": pilot_relevant,
        "branchTaken": "B",
        "historicalS1R1R1LedgerHash": HISTORICAL_S1R1_R1_LEDGER_HASH,
        "historicalS1R1R1CoverageHash": HISTORICAL_S1R1_R1_COVERAGE_HASH,
        "newSourceLedgerHash": successor["upstreamSourceLedgerHash"],
        "newCoverageHash": successor["upstreamCoverageHash"],
        "historicalS2R1LedgerHash": HISTORICAL_S2R1_LEDGER_HASH,
        "historicalS2R1CoverageHash": HISTORICAL_S2R1_COVERAGE_HASH,
        "historicalS2R1RegistryHash": HISTORICAL_S2R1_REGISTRY_HASH,
        "successorS2R1R1RegistryHash": successor["hypothesisRegistryHash"],
        "historicalS2R1PredictionFreezeHash": HISTORICAL_S2R1_FREEZE_HASH,
        "successorS2R1R1PredictionFreezeHash": successor["predictionFreezeHash"],
        "historicalS2R1InvarianceAuditHash": HISTORICAL_S2R1_INVARIANCE_AUDIT_HASH,
        "historicalS2R1ReconciliationHash": HISTORICAL_S2R1_RECONCILIATION_HASH,
        "historicalS2R1AcceptanceManifestHash": HISTORICAL_S2R1_ACCEPTANCE_HASH,
        "eventDiff": rows,
        "summary": summary,
        "priceDataRead": False,
        "outcomeDataRead": False,
        "founderDecisionRead": False,
        "reviewStoreRead": False,
        "executionAllowed": False,
    }
    return {**body, "lineageReconciliationHash": s2._canonical_hash(body)}


def build_s2r1_r1_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    prediction_freeze: Mapping[str, Any] | None = None,
    invariance_audit: Mapping[str, Any] | None = None,
    reconciliation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Record completion for independent central review, never central acceptance."""

    root = Path(resource_root).resolve()
    registry = _load_registry(root / DEFAULT_S2R1_R1_REGISTRY_PATH.relative_to(PROJECT_ROOT))
    freeze = copy.deepcopy(prediction_freeze) if prediction_freeze is not None else build_s2r1_r1_blinded_prediction_freeze(root)
    audit = copy.deepcopy(invariance_audit) if invariance_audit is not None else build_s2r1_r1_invariance_audit(root, prediction_freeze=freeze)
    lineage = copy.deepcopy(reconciliation) if reconciliation is not None else build_s2r1_r1_lineage_reconciliation(root, successor_freeze=freeze)
    if (freeze["hypothesisRegistryHash"], audit["predictionFreezeHash"], lineage["successorS2R1R1PredictionFreezeHash"]) != (
        registry.registry_hash, freeze["predictionFreezeHash"], freeze["predictionFreezeHash"]
    ):
        raise BlindedMarketBridgeS2R1_R1Error("S2R1_R1 acceptance inputs are not bound to one successor freeze")
    body = {
        "contract": S2R1_R1_ACCEPTANCE_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2R1-R1",
        "status": "S2R1_R1_SOURCE_ADJUDICATED_AND_BLINDED_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_MO_R4A_S3",
        "startingMaster": S2R1_R1_EXPECTED_STARTING_MASTER,
        "upstreamSourceLedgerContract": freeze["upstreamSourceLedgerContract"],
        "upstreamSourceLedgerHash": freeze["upstreamSourceLedgerHash"],
        "upstreamCoverageContract": freeze["upstreamCoverageContract"],
        "upstreamCoverageHash": freeze["upstreamCoverageHash"],
        "hypothesisRegistryContract": registry.raw["contract"],
        "hypothesisRegistryHash": registry.registry_hash,
        "predictionFreezeHash": freeze["predictionFreezeHash"],
        "invarianceAuditHash": audit["invarianceAuditHash"],
        "lineageReconciliationHash": lineage["lineageReconciliationHash"],
        "summary": copy.deepcopy(freeze["summary"]),
        "guardrails": copy.deepcopy(freeze["guardrails"]),
        "executionAllowed": False,
    }
    return {**body, "acceptanceManifestHash": s2._canonical_hash(body)}


def render_s2r1_r1_prediction_freeze_markdown(freeze: Mapping[str, Any], reconciliation: Mapping[str, Any]) -> str:
    """Render a source-only review table and the all-24 lineage diff without outcomes."""

    if freeze.get("contract") != S2R1_R1_PREDICTION_FREEZE_CONTRACT:
        raise BlindedMarketBridgeS2R1_R1Error("Cannot render an unsupported S2R1_R1 freeze")
    summary = freeze["summary"]
    lines = [
        "# MO-R4A-S2R1-R1 Real 24 Event Blinded Prediction Successor Freeze",
        "",
        "Saravali 4.28-29 adjudicates the natural-relationship lineage used before the unchanged temporary and compound rules. This is outcome-blind and side-local, not a market forecast or pair result.",
        "",
        f"Successor prediction freeze hash: `{freeze['predictionFreezeHash']}`",
        f"Historical S2R1 prediction freeze hash: `{HISTORICAL_S2R1_FREEZE_HASH}`",
        f"Saravali successor ledger hash: `{freeze['upstreamSourceLedgerHash']}`",
        f"Saravali successor coverage hash: `{freeze['upstreamCoverageHash']}`",
        "",
        f"Total events: {summary['eventCount']}; bridge-applicable: {summary['bridgeEligibleCount']}; directional: {summary['directionalCount']}; neutral: {summary['neutralCount']}; abstentions: {summary['abstentionCount']}",
        "",
        "| Side | Event ID | Old compound | New compound | Old pressure | New pressure | Prediction changed |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in reconciliation["eventDiff"]:
        lines.append(
            f"| {row['sideIdentity']} | {row['eventId']} | {row['historicalS2R1CompoundState']} | {row['adjudicatedCompoundState']} | {row['historicalS2R1PressureState']} | {row['adjudicatedPressureState']} | {str(row['predictionChanged']).lower()} |"
        )
    lines.extend(
        [
            "",
            "Every row retains `signedUnit=null` and `magnitudeConfigured=false`. No price, outcomes, Founder Review, SBC, catalogue, signed wave, pair resultant, Auto Suggest, ML, MT5, or execution state was read or created.",
            "",
        ]
    )
    return "\n".join(lines)


def write_s2r1_r1_artifacts(resource_root: Path = PROJECT_ROOT) -> dict[str, Path]:
    """Materialize deterministic successor artifacts after source-only rebinding."""

    root = Path(resource_root).resolve()
    operators.write_s2r1_r1_source_lineage_artifacts(root)
    freeze = build_s2r1_r1_blinded_prediction_freeze(root)
    audit = build_s2r1_r1_invariance_audit(root, prediction_freeze=freeze)
    reconciliation = build_s2r1_r1_lineage_reconciliation(root, successor_freeze=freeze)
    acceptance = build_s2r1_r1_acceptance_manifest(root, prediction_freeze=freeze, invariance_audit=audit, reconciliation=reconciliation)
    artifacts = {
        "predictionFreeze": root / DEFAULT_S2R1_R1_FREEZE_PATH.relative_to(PROJECT_ROOT),
        "invarianceAudit": root / DEFAULT_S2R1_R1_INVARIANCE_AUDIT_PATH.relative_to(PROJECT_ROOT),
        "reconciliation": root / DEFAULT_S2R1_R1_RECONCILIATION_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / DEFAULT_S2R1_R1_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
        "reviewTable": root / DEFAULT_S2R1_R1_REVIEW_TABLE_PATH.relative_to(PROJECT_ROOT),
    }
    payloads = {
        "predictionFreeze": freeze,
        "invarianceAudit": audit,
        "reconciliation": reconciliation,
        "acceptance": acceptance,
    }
    for name, payload in payloads.items():
        artifacts[name].parent.mkdir(parents=True, exist_ok=True)
        artifacts[name].write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    artifacts["reviewTable"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["reviewTable"].write_text(render_s2r1_r1_prediction_freeze_markdown(freeze, reconciliation), encoding="utf-8")
    return artifacts
