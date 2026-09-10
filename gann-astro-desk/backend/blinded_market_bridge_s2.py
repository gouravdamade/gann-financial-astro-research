"""Outcome-blind MO-R4A-S2 currency-side bridge freeze.

This module deliberately consumes only the checked-in S1R1-R1 source coverage
and immutable blank-packet identity records.  It neither regenerates astronomy
nor reads Founder Review decisions, market outcomes, price data, SBC, a
catalogue, or the unsigned activity runtime.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


S2_HYPOTHESIS_REGISTRY_CONTRACT = "MACHINE_ASSISTED_EXPERIMENTAL_MARKET_HYPOTHESIS_REGISTRY_S2_V1"
S2_HYPOTHESIS_REGISTRY_SCHEMA_VERSION = 1
S2_PREDICTION_FREEZE_CONTRACT = "MO_R4A_S2_BLINDED_MARKET_BRIDGE_PREDICTION_FREEZE_V1"
S2_INVARIANCE_AUDIT_CONTRACT = "MO_R4A_S2_BLINDED_MARKET_BRIDGE_INVARIANCE_AUDIT_V1"
S2_ACCEPTANCE_CONTRACT = "MO_R4A_S2_BLINDED_MARKET_BRIDGE_HYPOTHESIS_FREEZE_V1"
S2_EXPECTED_STARTING_MASTER = "c4abc811d40ce2fbc6e3972e0f7d4ff59e61ce09"
S2_EXPECTED_LEDGER_CONTRACT = "MO_R4A_S1R1_R1_CLASSICAL_SOURCE_OPERATOR_LEDGER_V1"
S2_EXPECTED_LEDGER_HASH = "00A63DFA1ED2154D9935D9502191D5574C5D1BF38E924ABD8BDA95FD9E6C1379"
S2_EXPECTED_COVERAGE_CONTRACT = "MO_R4A_S1R1_R1_REAL_24_SOURCE_OPERATOR_COVERAGE_V1"
S2_EXPECTED_COVERAGE_HASH = "359C905C6CF7792F6782E53552CEBCC9D43A63E93EC375E8314ABE795445A2AD"
S2_PRIMARY_OPERATOR_ID = "BJ_SARAVALI_COMPOUND_RELATIONSHIP_V1"
S2_PRIMARY_OPERATOR_VERSION = "1"
S2_HYPOTHESIS_FAMILY_ID = "MO_R4A_S2_COMPOUND_RELATIONSHIP_DIRECT_VALENCE_V1"
S2_HYPOTHESIS_IDS = {
    "USD": "H-MO-S2-COMPOUND-REL-DIRECT-USD-V1",
    "JPY": "H-MO-S2-COMPOUND-REL-DIRECT-JPY-V1",
}
S2_STATE_MAP = {
    "GREAT_FRIEND": "SUPPORTIVE",
    "FRIEND": "SUPPORTIVE",
    "NEUTRAL": "NEUTRAL",
    "ENEMY": "ADVERSE",
    "GREAT_ENEMY": "ADVERSE",
}
S2_SIDES = ("USD", "JPY")
S2_GUARDRAIL_KEYS = (
    "priceDataRead",
    "outcomeDataRead",
    "founderDecisionRead",
    "reviewStoreRead",
    "sbcRead",
    "catalogueAdmission",
    "evidenceAdmission",
    "signedWaveRendered",
    "pairResultantCreated",
    "magnitudeConfigured",
    "autoSuggestEnabled",
    "mlEnabled",
    "mt5Enabled",
    "executionAllowed",
)
S2_IDENTITY_FIELDS = (
    "eventId",
    "eventHash",
    "sideIdentity",
    "instrumentIdentity",
    "chartId",
    "chartHypothesisId",
    "transitBody",
    "natalTarget",
    "aspectType",
    "applyingStartUtc",
    "exactUtc",
    "separatingEndUtc",
    "astronomyContract",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
SOURCE_OPERATOR_ROOT = MACHINE_INTERPRETATION_ROOT / "source_operators"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"
FOUNDER_REVIEW_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects" / "founder_review"

DEFAULT_S2_REGISTRY_PATH = MACHINE_INTERPRETATION_ROOT / "experimental_market_hypothesis_registry_s2_v1.json"
DEFAULT_S1R1_R1_LEDGER_PATH = SOURCE_OPERATOR_ROOT / "classical_source_operator_ledger_s1r1_r1_v1.json"
DEFAULT_S1R1_R1_COVERAGE_PATH = AUDIT_ROOT / "mo_r4a_s1r1_r1_real_24_source_operator_coverage.json"
DEFAULT_S2_FREEZE_PATH = AUDIT_ROOT / "mo_r4a_s2_blinded_market_bridge_prediction_freeze.json"
DEFAULT_S2_INVARIANCE_AUDIT_PATH = AUDIT_ROOT / "mo_r4a_s2_blinded_market_bridge_invariance_audit.json"
DEFAULT_S2_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s2_blinded_market_bridge_hypothesis_freeze.json"
DEFAULT_S2_REVIEW_TABLE_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S2_REAL_24_EVENT_PREDICTION_FREEZE.md"


class BlindedMarketBridgeS2Error(ValueError):
    """Raised when S2 would cross its frozen, outcome-blind contract."""


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _normalized_file_sha256(path: Path) -> str:
    try:
        content = path.read_bytes().replace(b"\r\n", b"\n")
    except FileNotFoundError as exc:
        raise BlindedMarketBridgeS2Error(f"Required immutable input is missing: {path}") from exc
    return hashlib.sha256(content).hexdigest().upper()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise BlindedMarketBridgeS2Error(f"Required {label} is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BlindedMarketBridgeS2Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(raw, dict):
        raise BlindedMarketBridgeS2Error(f"{label} must be a JSON object: {path}")
    return raw


def _required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise BlindedMarketBridgeS2Error(f"{label} is required")
    return text


def _require_false_flags(mapping: Any, keys: Sequence[str], label: str) -> None:
    if not isinstance(mapping, dict):
        raise BlindedMarketBridgeS2Error(f"{label} must be an object")
    invalid = [key for key in keys if mapping.get(key) is not False]
    if invalid:
        raise BlindedMarketBridgeS2Error(f"{label} must remain false: {', '.join(invalid)}")


def _exact_keys(mapping: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(mapping, dict):
        raise BlindedMarketBridgeS2Error(f"{label} must be an object")
    actual = set(mapping)
    if actual != keys:
        missing = sorted(keys - actual)
        unexpected = sorted(actual - keys)
        raise BlindedMarketBridgeS2Error(f"{label} keys differ; missing={missing}, unexpected={unexpected}")
    return mapping


def _assert_sha256(value: Any, label: str) -> str:
    text = _required_text(value, label)
    if len(text) != 64 or any(character not in "0123456789ABCDEF" for character in text):
        raise BlindedMarketBridgeS2Error(f"{label} must be an uppercase SHA-256 hex value")
    return text


@dataclass(frozen=True)
class S2MarketHypothesis:
    """The one authorized direct-valence bridge for exactly one currency side."""

    raw: Mapping[str, Any]
    hypothesis_hash: str

    @property
    def hypothesis_id(self) -> str:
        return str(self.raw["hypothesisId"])

    @property
    def target_side(self) -> str:
        return str(self.raw["targetSide"])

    @property
    def state_map(self) -> Mapping[str, str]:
        return self.raw["stateMap"]


def _hypothesis_decision_content(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in raw.items() if key != "hypothesisHash"}


def _load_hypothesis(raw: Any) -> S2MarketHypothesis:
    expected_keys = {
        "hypothesisFamilyId",
        "hypothesisId",
        "version",
        "author",
        "createdAtUtc",
        "hypothesisScope",
        "bridgeBasis",
        "inputOperatorIds",
        "primaryInputOperatorId",
        "primaryInputOperatorVersion",
        "stateMap",
        "targetSide",
        "applicabilityPolicy",
        "abstentionPolicy",
        "sourceClaim",
        "experimentalClaim",
        "reasoning",
        "sourceDependencies",
        "experimentalAssumptions",
        "prohibitedGeneralizations",
        "validationStatus",
        "outcomeDataSeenAtCreation",
        "approvalStatus",
        "signedUnitIfConfigured",
        "magnitudeConfigured",
        "mode",
        "productionAdmission",
        "hypothesisHash",
    }
    mapping = _exact_keys(raw, expected_keys, "S2 market hypothesis")
    if mapping["hypothesisFamilyId"] != S2_HYPOTHESIS_FAMILY_ID:
        raise BlindedMarketBridgeS2Error("S2 hypothesis belongs to an unauthorized family")
    hypothesis_id = _required_text(mapping["hypothesisId"], "S2 hypothesisId")
    version = _required_text(mapping["version"], "S2 hypothesis version")
    if version != "1":
        raise BlindedMarketBridgeS2Error("S2 hypothesis version must remain 1")
    _required_text(mapping["author"], "S2 hypothesis author")
    created = _required_text(mapping["createdAtUtc"], "S2 hypothesis createdAtUtc")
    if not created.endswith("Z"):
        raise BlindedMarketBridgeS2Error("S2 hypothesis createdAtUtc must be explicit UTC")
    _required_text(mapping["hypothesisScope"], "S2 hypothesis scope")
    if mapping["bridgeBasis"] != "SOURCE_OPERATOR_STATE_PREDICATE":
        raise BlindedMarketBridgeS2Error("S2 bridge basis must be SOURCE_OPERATOR_STATE_PREDICATE")
    if mapping["inputOperatorIds"] != [S2_PRIMARY_OPERATOR_ID]:
        raise BlindedMarketBridgeS2Error("S2 may use only the compound-relationship operator as a bridge input")
    if mapping["primaryInputOperatorId"] != S2_PRIMARY_OPERATOR_ID:
        raise BlindedMarketBridgeS2Error("S2 primary input operator is not the compound relationship")
    if mapping["primaryInputOperatorVersion"] != S2_PRIMARY_OPERATOR_VERSION:
        raise BlindedMarketBridgeS2Error("S2 primary input operator version is not frozen")
    if mapping["stateMap"] != S2_STATE_MAP:
        raise BlindedMarketBridgeS2Error("S2 compound relationship state map differs from central authorization")
    side = _required_text(mapping["targetSide"], "S2 target side").upper()
    if side not in S2_SIDES or mapping["targetSide"] != side:
        raise BlindedMarketBridgeS2Error("S2 target side must be USD or JPY")
    if mapping["applicabilityPolicy"] != "SOURCE_CLOSED_MACHINE_EVALUATED_COMPOUND_RELATIONSHIP_ONLY":
        raise BlindedMarketBridgeS2Error("S2 applicability policy is not fail-closed")
    abstention = _exact_keys(
        mapping["abstentionPolicy"],
        {"currencyPressureState", "bridgeApplied", "fallbackOperatorAllowed"},
        "S2 abstention policy",
    )
    if abstention != {
        "currencyPressureState": "UNKNOWN_MORE_EVIDENCE_REQUIRED",
        "bridgeApplied": False,
        "fallbackOperatorAllowed": False,
    }:
        raise BlindedMarketBridgeS2Error("S2 abstention policy may not use an alternate source operator")
    for field in (
        "sourceClaim",
        "experimentalClaim",
        "reasoning",
    ):
        _required_text(mapping[field], f"S2 hypothesis {field}")
    for field in ("sourceDependencies", "experimentalAssumptions", "prohibitedGeneralizations"):
        values = mapping[field]
        if not isinstance(values, list) or not values or not all(isinstance(value, str) and value.strip() for value in values):
            raise BlindedMarketBridgeS2Error(f"S2 hypothesis {field} must be a non-empty text list")
    expected_dependencies = {
        "TRAILOKYA_1972_NATURAL_RELATIONSHIP_V1",
        "BJ_SARAVALI_TEMPORARY_RELATIONSHIP_V1",
        S2_PRIMARY_OPERATOR_ID,
    }
    if not expected_dependencies.issubset(set(mapping["sourceDependencies"])):
        raise BlindedMarketBridgeS2Error("S2 hypothesis does not preserve the compound-relationship source dependency chain")
    if mapping["validationStatus"] != "NOT_FINANCIALLY_VALIDATED":
        raise BlindedMarketBridgeS2Error("S2 hypothesis must remain NOT_FINANCIALLY_VALIDATED")
    if mapping["outcomeDataSeenAtCreation"] is not False:
        raise BlindedMarketBridgeS2Error("S2 hypothesis cannot be created after seeing outcomes")
    if mapping["approvalStatus"] != "AUTHORIZED_FOR_BLINDED_TEST":
        raise BlindedMarketBridgeS2Error("S2 hypothesis is not authorized for the blinded test")
    if mapping["signedUnitIfConfigured"] is not None or mapping["magnitudeConfigured"] is not False:
        raise BlindedMarketBridgeS2Error("S2 cannot configure signed units or magnitude")
    if mapping["mode"] != "EXPERIMENTAL_PROFILED" or mapping["productionAdmission"] is not False:
        raise BlindedMarketBridgeS2Error("S2 must remain experimental and non-production")
    supplied_hash = _assert_sha256(mapping["hypothesisHash"], "S2 hypothesisHash")
    computed_hash = _canonical_hash(_hypothesis_decision_content(mapping))
    if supplied_hash != computed_hash:
        raise BlindedMarketBridgeS2Error(f"S2 hypothesis hash does not bind its decision content: {hypothesis_id}")
    return S2MarketHypothesis(raw=copy.deepcopy(mapping), hypothesis_hash=supplied_hash)


@dataclass(frozen=True)
class S2HypothesisRegistry:
    """Frozen S2 bridge family, intentionally separate from historical P0."""

    raw: Mapping[str, Any]
    entries_by_side: Mapping[str, S2MarketHypothesis]
    registry_hash: str


def load_s2_hypothesis_registry(path: Path = DEFAULT_S2_REGISTRY_PATH) -> S2HypothesisRegistry:
    expected_keys = {
        "contract",
        "schemaVersion",
        "registryId",
        "registryStatus",
        "purpose",
        "entryPolicy",
        "startingMaster",
        "upstreamSourceLedgerContract",
        "upstreamSourceLedgerHash",
        "upstreamCoverageContract",
        "upstreamCoverageHash",
        "hypothesisFamilyId",
        "entries",
        "guardrails",
        "registryHash",
    }
    raw = _exact_keys(_read_json(Path(path), "S2 market hypothesis registry"), expected_keys, "S2 market hypothesis registry")
    if raw["contract"] != S2_HYPOTHESIS_REGISTRY_CONTRACT or raw["schemaVersion"] != S2_HYPOTHESIS_REGISTRY_SCHEMA_VERSION:
        raise BlindedMarketBridgeS2Error("Unsupported S2 market hypothesis registry contract")
    if raw["registryStatus"] != "AUTHORIZED_FOR_BLINDED_TEST_FROZEN":
        raise BlindedMarketBridgeS2Error("S2 market hypothesis registry is not frozen for blinded testing")
    if raw["startingMaster"] != S2_EXPECTED_STARTING_MASTER:
        raise BlindedMarketBridgeS2Error("S2 registry is not bound to the authorized starting master")
    if raw["upstreamSourceLedgerContract"] != S2_EXPECTED_LEDGER_CONTRACT:
        raise BlindedMarketBridgeS2Error("S2 registry has an unexpected source ledger contract")
    if raw["upstreamSourceLedgerHash"] != S2_EXPECTED_LEDGER_HASH:
        raise BlindedMarketBridgeS2Error("S2 registry has an unexpected source ledger hash")
    if raw["upstreamCoverageContract"] != S2_EXPECTED_COVERAGE_CONTRACT:
        raise BlindedMarketBridgeS2Error("S2 registry has an unexpected source coverage contract")
    if raw["upstreamCoverageHash"] != S2_EXPECTED_COVERAGE_HASH:
        raise BlindedMarketBridgeS2Error("S2 registry has an unexpected source coverage hash")
    if raw["hypothesisFamilyId"] != S2_HYPOTHESIS_FAMILY_ID:
        raise BlindedMarketBridgeS2Error("S2 registry contains an unauthorized hypothesis family")
    _required_text(raw["registryId"], "S2 registryId")
    _required_text(raw["purpose"], "S2 registry purpose")
    _required_text(raw["entryPolicy"], "S2 registry entry policy")
    _require_false_flags(raw["guardrails"], S2_GUARDRAIL_KEYS, "S2 registry guardrails")
    entries_raw = raw["entries"]
    if not isinstance(entries_raw, list) or len(entries_raw) != 2:
        raise BlindedMarketBridgeS2Error("S2 registry must contain exactly two authorized side hypotheses")
    entries = tuple(_load_hypothesis(item) for item in entries_raw)
    entries_by_side = {entry.target_side: entry for entry in entries}
    if set(entries_by_side) != set(S2_SIDES) or len(entries_by_side) != len(entries):
        raise BlindedMarketBridgeS2Error("S2 registry requires exactly one USD and one JPY hypothesis")
    if {entry.hypothesis_id for entry in entries} != set(S2_HYPOTHESIS_IDS.values()):
        raise BlindedMarketBridgeS2Error("S2 registry contains an unapproved hypothesis ID")
    for side, hypothesis_id in S2_HYPOTHESIS_IDS.items():
        if entries_by_side[side].hypothesis_id != hypothesis_id:
            raise BlindedMarketBridgeS2Error("S2 hypothesis is bound to the wrong currency side")
    supplied_hash = _assert_sha256(raw["registryHash"], "S2 registryHash")
    computed_hash = _canonical_hash({key: copy.deepcopy(value) for key, value in raw.items() if key != "registryHash"})
    if supplied_hash != computed_hash:
        raise BlindedMarketBridgeS2Error("S2 registry hash does not match frozen registry content")
    return S2HypothesisRegistry(raw=copy.deepcopy(raw), entries_by_side=entries_by_side, registry_hash=supplied_hash)


def _load_verified_upstream_inputs(resource_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(resource_root).resolve()
    ledger = _read_json(
        root / "configs" / "research" / "machine_interpretation" / "source_operators" / DEFAULT_S1R1_R1_LEDGER_PATH.name,
        "S1R1-R1 source ledger",
    )
    if ledger.get("contract") != S2_EXPECTED_LEDGER_CONTRACT:
        raise BlindedMarketBridgeS2Error("S2 requires the frozen S1R1-R1 source ledger contract")
    if _canonical_hash(ledger) != S2_EXPECTED_LEDGER_HASH:
        raise BlindedMarketBridgeS2Error("S2 requires the exact frozen S1R1-R1 source ledger hash")

    coverage = _read_json(
        root / "status" / "audits" / DEFAULT_S1R1_R1_COVERAGE_PATH.name,
        "S1R1-R1 source coverage",
    )
    if coverage.get("contract") != S2_EXPECTED_COVERAGE_CONTRACT:
        raise BlindedMarketBridgeS2Error("S2 requires the frozen S1R1-R1 coverage contract")
    coverage_body = {key: copy.deepcopy(value) for key, value in coverage.items() if key != "sourceOperatorCoverageHash"}
    if coverage.get("sourceOperatorCoverageHash") != _canonical_hash(coverage_body):
        raise BlindedMarketBridgeS2Error("S1R1-R1 source coverage hash does not match its content")
    if coverage["sourceOperatorCoverageHash"] != S2_EXPECTED_COVERAGE_HASH:
        raise BlindedMarketBridgeS2Error("S2 requires the exact frozen S1R1-R1 coverage hash")
    if coverage.get("sourceOperatorLedgerContract") != S2_EXPECTED_LEDGER_CONTRACT:
        raise BlindedMarketBridgeS2Error("S1R1-R1 coverage is not bound to the expected source ledger contract")
    if coverage.get("sourceOperatorLedgerCanonicalHash") != S2_EXPECTED_LEDGER_HASH:
        raise BlindedMarketBridgeS2Error("S1R1-R1 coverage is not bound to the expected source ledger hash")
    for key in ("reviewStoreRead", "founderDecisionRead", "priceOrOutcomeRead", "eventUniverseRegenerated"):
        if coverage.get(key) is not False:
            raise BlindedMarketBridgeS2Error(f"S1R1-R1 coverage guardrail is no longer false: {key}")
    _require_false_flags(
        coverage.get("guardrails"),
        (
            "catalogueAdmission",
            "evidenceAdmission",
            "priceDataRead",
            "outcomeDataRead",
            "reviewStoreRead",
            "founderDecisionRead",
            "sbcRead",
            "signedUsdWaveCreated",
            "signedJpyWaveCreated",
            "signedPairResultantCreated",
            "magnitudeConfigured",
            "autoSuggestEnabled",
            "mlEnabled",
            "mt5Enabled",
            "executionAllowed",
        ),
        "S1R1-R1 coverage guardrails",
    )
    summary = coverage.get("summary")
    if not isinstance(summary, dict) or (
        summary.get("eventCount"),
        summary.get("usdEventCount"),
        summary.get("jpyEventCount"),
        summary.get("singlePassVerifiedCount"),
        summary.get("astrologyUnknownCount"),
        summary.get("astrologySourceStateCount"),
    ) != (24, 12, 12, 24, 24, 0):
        raise BlindedMarketBridgeS2Error("S1R1-R1 coverage no longer represents the accepted 24-event unknown-composition pilot")
    return ledger, coverage


def _load_immutable_blank_packet_identities(resource_root: Path, coverage: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    root = Path(resource_root).resolve()
    coverage_sides = coverage.get("sides")
    if not isinstance(coverage_sides, list) or [side.get("sideIdentity") for side in coverage_sides] != list(S2_SIDES):
        raise BlindedMarketBridgeS2Error("S1R1-R1 coverage side order is not the frozen USD, JPY order")
    records: dict[str, list[dict[str, Any]]] = {}
    for coverage_side in coverage_sides:
        side = str(coverage_side["sideIdentity"])
        packet_root = root / "research_labs" / "chart_conditioned_aspects" / "founder_review"
        packet_path = packet_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
        manifest_path = packet_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json"
        if coverage_side.get("blankPacketSha256") != _normalized_file_sha256(packet_path):
            raise BlindedMarketBridgeS2Error(f"{side} immutable blank packet hash no longer matches S1R1-R1 coverage")
        if coverage_side.get("identityIntegrityManifestSha256") != _normalized_file_sha256(manifest_path):
            raise BlindedMarketBridgeS2Error(f"{side} identity manifest hash no longer matches S1R1-R1 coverage")
        packet = _read_json(packet_path, f"{side} immutable blank packet")
        if packet.get("sideIdentity") != side:
            raise BlindedMarketBridgeS2Error(f"{side} immutable blank packet has the wrong side identity")
        rows = packet.get("rows")
        if not isinstance(rows, list) or len(rows) != 12:
            raise BlindedMarketBridgeS2Error(f"{side} immutable blank packet must contain exactly 12 rows")
        identities: list[dict[str, Any]] = []
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("eventIdentity"), dict):
                raise BlindedMarketBridgeS2Error(f"{side} immutable blank packet lacks event identity data")
            identity = copy.deepcopy(row["eventIdentity"])
            missing = [field for field in S2_IDENTITY_FIELDS if field not in identity]
            if missing:
                raise BlindedMarketBridgeS2Error(f"{side} immutable identity lacks fields: {missing}")
            identities.append(identity)
        records[side] = identities
    return records


def _verify_coverage_identity(coverage_event: Mapping[str, Any], identity: Mapping[str, Any]) -> None:
    coverage_fields = ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")
    if any(coverage_event.get(field) != identity.get(field) for field in coverage_fields):
        raise BlindedMarketBridgeS2Error(f"S1R1-R1 event identity mismatch: {identity.get('eventId')}")
    snapshot = coverage_event.get("astronomySnapshot")
    if not isinstance(snapshot, dict):
        raise BlindedMarketBridgeS2Error(f"S1R1-R1 event lacks astronomy snapshot: {identity.get('eventId')}")
    snapshot_fields = ("chartId", "chartHypothesisId", "astronomyContract", "exactUtc", "transitBody", "natalTarget")
    if any(snapshot.get(field) != identity.get(field) for field in snapshot_fields):
        raise BlindedMarketBridgeS2Error(f"S1R1-R1 astronomy snapshot mismatch: {identity.get('eventId')}")


def _compound_output(coverage_event: Mapping[str, Any]) -> dict[str, Any]:
    outputs = coverage_event.get("operatorOutputs")
    if not isinstance(outputs, list):
        raise BlindedMarketBridgeS2Error("S1R1-R1 event lacks source operator outputs")
    matches = [
        output
        for output in outputs
        if isinstance(output, dict)
        and output.get("operatorId") == S2_PRIMARY_OPERATOR_ID
        and output.get("operatorVersion") == S2_PRIMARY_OPERATOR_VERSION
    ]
    if len(matches) != 1:
        raise BlindedMarketBridgeS2Error("S1R1-R1 event must expose exactly one compound-relationship output")
    return copy.deepcopy(matches[0])


def _source_operator_input_snapshot(compound: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "contract",
        "operatorId",
        "operatorVersion",
        "status",
        "outputState",
        "sourceLocators",
        "unresolvedDependencies",
        "machineEvaluated",
        "marketDirectionAuthorized",
        "marketMagnitudeAuthorized",
    }
    if not required.issubset(compound):
        raise BlindedMarketBridgeS2Error("Compound-relationship output lacks required source fields")
    if compound["marketDirectionAuthorized"] is not False or compound["marketMagnitudeAuthorized"] is not False:
        raise BlindedMarketBridgeS2Error("Source compound relationship cannot authorize market direction or magnitude")
    return {
        "contract": compound["contract"],
        "operatorId": compound["operatorId"],
        "operatorVersion": compound["operatorVersion"],
        "sourceStatus": compound["status"],
        "outputState": compound["outputState"],
        "machineEvaluated": compound["machineEvaluated"],
        "sourceLocators": copy.deepcopy(compound["sourceLocators"]),
        "unresolvedDependencies": copy.deepcopy(compound["unresolvedDependencies"]),
    }


def _build_prediction(
    coverage_event: Mapping[str, Any],
    identity: Mapping[str, Any],
    hypothesis: S2MarketHypothesis,
    registry: S2HypothesisRegistry,
) -> dict[str, Any]:
    _verify_coverage_identity(coverage_event, identity)
    compound = _compound_output(coverage_event)
    source_input = _source_operator_input_snapshot(compound)
    source_state = str(source_input["outputState"])
    source_closed = str(source_input["sourceStatus"]).startswith("SOURCE_CLOSED")
    bridge_eligible = source_closed and source_input["machineEvaluated"] is True
    if bridge_eligible:
        if source_state not in S2_STATE_MAP:
            raise BlindedMarketBridgeS2Error(f"Unauthorized compound relationship state for S2: {source_state}")
        currency_state = hypothesis.state_map[source_state]
        bridge_applied = True
        abstention_reason: str | None = None
    else:
        if source_state != "UNKNOWN":
            raise BlindedMarketBridgeS2Error("Non-evaluated compound relationship must fail closed as UNKNOWN")
        dependencies = source_input["unresolvedDependencies"]
        if not dependencies:
            raise BlindedMarketBridgeS2Error("Abstained compound relationship must expose an unresolved dependency")
        currency_state = "UNKNOWN_MORE_EVIDENCE_REQUIRED"
        bridge_applied = False
        abstention_reason = str(dependencies[0])
    if coverage_event.get("astrologicalCompositionStatus") != "NO_APPROVED_ASTROLOGICAL_COMPOSITION_CONTRACT":
        raise BlindedMarketBridgeS2Error("S2 may not replace the frozen source composition status")
    if coverage_event.get("astrologicalInterpretationState") != "UNKNOWN_ASTRO_STATE":
        raise BlindedMarketBridgeS2Error("S2 may not replace the frozen unknown source interpretation")

    body = {
        **{field: copy.deepcopy(identity[field]) for field in S2_IDENTITY_FIELDS},
        "identityStatus": coverage_event["identityStatus"],
        "astronomySnapshot": copy.deepcopy(coverage_event["astronomySnapshot"]),
        "upstreamSourceLedgerContract": registry.raw["upstreamSourceLedgerContract"],
        "upstreamSourceLedgerHash": registry.raw["upstreamSourceLedgerHash"],
        "upstreamCoverageContract": registry.raw["upstreamCoverageContract"],
        "upstreamCoverageHash": registry.raw["upstreamCoverageHash"],
        "hypothesisFamilyId": hypothesis.raw["hypothesisFamilyId"],
        "hypothesisId": hypothesis.hypothesis_id,
        "hypothesisHash": hypothesis.hypothesis_hash,
        "hypothesisRegistryHash": registry.registry_hash,
        "primaryInputOperatorId": S2_PRIMARY_OPERATOR_ID,
        "primaryInputOperatorVersion": S2_PRIMARY_OPERATOR_VERSION,
        "sourceOperatorInput": source_input,
        "bridgeApplied": bridge_applied,
        "currencyPressureState": currency_state,
        "abstentionReason": abstention_reason,
        "signedUnit": None,
        "magnitudeConfigured": False,
        "overallAstrologicalCompositionStatus": coverage_event["astrologicalCompositionStatus"],
        "overallAstrologicalInterpretation": coverage_event["astrologicalInterpretationState"],
        "experimentalAssumptionLabel": "DIRECT_COMPOUND_RELATIONSHIP_VALENCE_CURRENCY_SIDE_PRESSURE",
        "sourceClaim": hypothesis.raw["sourceClaim"],
        "experimentalClaim": hypothesis.raw["experimentalClaim"],
        "financialValidation": hypothesis.raw["validationStatus"],
        "outcomeDataSeen": False,
        "priceDataRead": False,
        "executionAllowed": False,
    }
    return {**body, "eventPredictionHash": _canonical_hash(body)}


def _side_counts(predictions: Sequence[Mapping[str, Any]], side: str) -> dict[str, Any]:
    records = [prediction for prediction in predictions if prediction["sideIdentity"] == side]
    return {
        "sideIdentity": side,
        "eventCount": len(records),
        "bridgeEligibleCount": sum(prediction["bridgeApplied"] for prediction in records),
        "abstentionCount": sum(not prediction["bridgeApplied"] for prediction in records),
        "supportiveCount": sum(prediction["currencyPressureState"] == "SUPPORTIVE" for prediction in records),
        "adverseCount": sum(prediction["currencyPressureState"] == "ADVERSE" for prediction in records),
        "neutralCount": sum(prediction["currencyPressureState"] == "NEUTRAL" for prediction in records),
        "unknownCount": sum(
            prediction["currencyPressureState"] == "UNKNOWN_MORE_EVIDENCE_REQUIRED" for prediction in records
        ),
    }


def build_s2_blinded_prediction_freeze(
    resource_root: Path = PROJECT_ROOT,
    *,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """Freeze side-local categorical S2 predictions from the checked-in S1R1-R1 coverage."""

    root = Path(resource_root).resolve()
    registry = load_s2_hypothesis_registry(registry_path or root / "configs" / "research" / "machine_interpretation" / DEFAULT_S2_REGISTRY_PATH.name)
    _, coverage = _load_verified_upstream_inputs(root)
    if (
        registry.raw["upstreamSourceLedgerContract"],
        registry.raw["upstreamSourceLedgerHash"],
        registry.raw["upstreamCoverageContract"],
        registry.raw["upstreamCoverageHash"],
    ) != (
        coverage["sourceOperatorLedgerContract"],
        coverage["sourceOperatorLedgerCanonicalHash"],
        coverage["contract"],
        coverage["sourceOperatorCoverageHash"],
    ):
        raise BlindedMarketBridgeS2Error("S2 registry is not bound to the exact frozen S1R1-R1 input artifacts")
    identities_by_side = _load_immutable_blank_packet_identities(root, coverage)
    predictions: list[dict[str, Any]] = []
    for coverage_side in coverage["sides"]:
        side = coverage_side["sideIdentity"]
        events = coverage_side.get("events")
        identities = identities_by_side.get(side)
        if (
            not isinstance(events, list)
            or identities is None
            or len(events) != 12
            or len(identities) != 12
            or len(events) != len(identities)
        ):
            raise BlindedMarketBridgeS2Error(f"S2 source coverage/identity order mismatch for {side}")
        hypothesis = registry.entries_by_side[side]
        for coverage_event, identity in zip(events, identities, strict=True):
            prediction = _build_prediction(coverage_event, identity, hypothesis, registry)
            if prediction["sideIdentity"] != hypothesis.target_side:
                raise BlindedMarketBridgeS2Error("S2 hypothesis cannot be applied to the other currency side")
            predictions.append(prediction)
    if len(predictions) != 24 or len({prediction["eventId"] for prediction in predictions}) != 24:
        raise BlindedMarketBridgeS2Error("S2 prediction freeze requires exactly 24 unique frozen events")
    if any(prediction["identityStatus"] != "SINGLE_PASS_VERIFIED" for prediction in predictions):
        raise BlindedMarketBridgeS2Error("S2 may only freeze SINGLE_PASS_VERIFIED events")

    sides = [_side_counts(predictions, side) for side in S2_SIDES]
    summary = {
        "eventCount": len(predictions),
        "usdEventCount": sides[0]["eventCount"],
        "jpyEventCount": sides[1]["eventCount"],
        "singlePassVerifiedCount": sum(prediction["identityStatus"] == "SINGLE_PASS_VERIFIED" for prediction in predictions),
        "bridgeEligibleCount": sum(prediction["bridgeApplied"] for prediction in predictions),
        "abstentionCount": sum(not prediction["bridgeApplied"] for prediction in predictions),
        "supportiveCount": sum(prediction["currencyPressureState"] == "SUPPORTIVE" for prediction in predictions),
        "adverseCount": sum(prediction["currencyPressureState"] == "ADVERSE" for prediction in predictions),
        "neutralCount": sum(prediction["currencyPressureState"] == "NEUTRAL" for prediction in predictions),
        "unknownCount": sum(
            prediction["currencyPressureState"] == "UNKNOWN_MORE_EVIDENCE_REQUIRED" for prediction in predictions
        ),
        "overallAstrologyUnknownCount": sum(
            prediction["overallAstrologicalInterpretation"] == "UNKNOWN_ASTRO_STATE" for prediction in predictions
        ),
    }
    if (
        summary["eventCount"],
        summary["usdEventCount"],
        summary["jpyEventCount"],
        summary["singlePassVerifiedCount"],
        summary["bridgeEligibleCount"],
        summary["abstentionCount"],
        summary["overallAstrologyUnknownCount"],
    ) != (24, 12, 12, 24, 17, 7, 24):
        raise BlindedMarketBridgeS2Error("S2 source artifact no longer has the authorized frozen pilot shape")
    body = {
        "contract": S2_PREDICTION_FREEZE_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2",
        "startingMaster": S2_EXPECTED_STARTING_MASTER,
        "inputPolicy": "FROZEN_S1R1_R1_COVERAGE_PLUS_IMMUTABLE_BLANK_PACKET_IDENTITY_ONLY",
        "eventUniverseRegenerated": False,
        "sourceCoverageArtifactRead": True,
        "immutableBlankPacketIdentityRead": True,
        "reviewStoreRead": False,
        "founderDecisionRead": False,
        "priceDataRead": False,
        "outcomeDataRead": False,
        "upstreamSourceLedgerContract": registry.raw["upstreamSourceLedgerContract"],
        "upstreamSourceLedgerHash": registry.raw["upstreamSourceLedgerHash"],
        "upstreamCoverageContract": registry.raw["upstreamCoverageContract"],
        "upstreamCoverageHash": registry.raw["upstreamCoverageHash"],
        "hypothesisRegistryContract": registry.raw["contract"],
        "hypothesisRegistryHash": registry.registry_hash,
        "hypothesisIds": [registry.entries_by_side[side].hypothesis_id for side in S2_SIDES],
        "frozenEventOrder": [prediction["eventId"] for prediction in predictions],
        "predictions": predictions,
        "summary": summary,
        "perSide": sides,
        "guardrails": {
            **{key: False for key in S2_GUARDRAIL_KEYS},
            "productionAdmission": False,
            "eventUniverseRegenerated": False,
            "signedUnitConfigured": False,
        },
    }
    return {**body, "predictionFreezeHash": _canonical_hash(body)}


def build_s2_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    prediction_freeze: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Prove S2 retained frozen source identities, snapshots, and source composition."""

    root = Path(resource_root).resolve()
    _, coverage = _load_verified_upstream_inputs(root)
    freeze = copy.deepcopy(prediction_freeze) if prediction_freeze is not None else build_s2_blinded_prediction_freeze(root)
    if freeze.get("predictionFreezeHash") != _canonical_hash(
        {key: copy.deepcopy(value) for key, value in freeze.items() if key != "predictionFreezeHash"}
    ):
        raise BlindedMarketBridgeS2Error("S2 prediction freeze hash does not match frozen content")
    coverage_events = [event for side in coverage["sides"] for event in side["events"]]
    predictions = freeze.get("predictions")
    if not isinstance(predictions, list) or len(coverage_events) != len(predictions) != 24:
        raise BlindedMarketBridgeS2Error("S2 invariance audit requires 24 source events and 24 predictions")
    rows: list[dict[str, Any]] = []
    for coverage_event, prediction in zip(coverage_events, predictions, strict=True):
        identity_unchanged = all(
            prediction.get(field) == coverage_event.get(field)
            for field in ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")
        )
        snapshot_unchanged = prediction.get("astronomySnapshot") == coverage_event.get("astronomySnapshot")
        composition_unchanged = (
            prediction.get("overallAstrologicalCompositionStatus") == coverage_event.get("astrologicalCompositionStatus")
            and prediction.get("overallAstrologicalInterpretation") == coverage_event.get("astrologicalInterpretationState")
        )
        rows.append(
            {
                "eventId": coverage_event["eventId"],
                "eventHash": coverage_event["eventHash"],
                "identityUnchanged": identity_unchanged,
                "astronomySnapshotUnchanged": snapshot_unchanged,
                "overallSourceCompositionUnchanged": composition_unchanged,
                "predictionHash": prediction.get("eventPredictionHash"),
            }
        )
    if not all(
        row["identityUnchanged"] and row["astronomySnapshotUnchanged"] and row["overallSourceCompositionUnchanged"]
        for row in rows
    ):
        raise BlindedMarketBridgeS2Error("S2 prediction freeze changed source identities, astronomy, or source composition")
    body = {
        "contract": S2_INVARIANCE_AUDIT_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2",
        "upstreamSourceLedgerHash": freeze["upstreamSourceLedgerHash"],
        "upstreamCoverageHash": freeze["upstreamCoverageHash"],
        "hypothesisRegistryHash": freeze["hypothesisRegistryHash"],
        "predictionFreezeHash": freeze["predictionFreezeHash"],
        "eventCount": len(rows),
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
            "executionAllowed": False,
        },
    }
    return {**body, "invarianceAuditHash": _canonical_hash(body)}


def build_s2_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    prediction_freeze: Mapping[str, Any] | None = None,
    invariance_audit: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind the exact registry and prediction packet for central S3 review."""

    root = Path(resource_root).resolve()
    registry = load_s2_hypothesis_registry(root / "configs" / "research" / "machine_interpretation" / DEFAULT_S2_REGISTRY_PATH.name)
    freeze = copy.deepcopy(prediction_freeze) if prediction_freeze is not None else build_s2_blinded_prediction_freeze(root)
    audit = copy.deepcopy(invariance_audit) if invariance_audit is not None else build_s2_invariance_audit(root, prediction_freeze=freeze)
    if freeze.get("hypothesisRegistryHash") != registry.registry_hash:
        raise BlindedMarketBridgeS2Error("S2 prediction freeze is not bound to the checked-in S2 registry")
    if audit.get("predictionFreezeHash") != freeze.get("predictionFreezeHash"):
        raise BlindedMarketBridgeS2Error("S2 invariance audit is not bound to the prediction freeze")
    body = {
        "contract": S2_ACCEPTANCE_CONTRACT,
        "schemaVersion": 1,
        "milestone": "MO-R4A-S2",
        "status": "BLINDED_HYPOTHESIS_FREEZE_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "startingMaster": S2_EXPECTED_STARTING_MASTER,
        "upstreamSourceLedgerContract": freeze["upstreamSourceLedgerContract"],
        "upstreamSourceLedgerHash": freeze["upstreamSourceLedgerHash"],
        "upstreamCoverageContract": freeze["upstreamCoverageContract"],
        "upstreamCoverageHash": freeze["upstreamCoverageHash"],
        "hypothesisRegistryContract": registry.raw["contract"],
        "hypothesisRegistryHash": registry.registry_hash,
        "hypotheses": [
            {
                "hypothesisId": registry.entries_by_side[side].hypothesis_id,
                "hypothesisHash": registry.entries_by_side[side].hypothesis_hash,
                "targetSide": side,
            }
            for side in S2_SIDES
        ],
        "predictionFreezeHash": freeze["predictionFreezeHash"],
        "invarianceAuditHash": audit["invarianceAuditHash"],
        "summary": copy.deepcopy(freeze["summary"]),
        "guardrails": copy.deepcopy(freeze["guardrails"]),
        "s3Prerequisite": "CENTRAL_REVIEW_REQUIRED_BEFORE_S3_PREREGISTRATION",
        "executionAllowed": False,
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def render_s2_prediction_freeze_markdown(freeze: Mapping[str, Any]) -> str:
    """Render a compact source-and-hypothesis review table without market outcomes."""

    if freeze.get("contract") != S2_PREDICTION_FREEZE_CONTRACT:
        raise BlindedMarketBridgeS2Error("Cannot render an unsupported S2 prediction freeze")
    summary = freeze["summary"]
    lines = [
        "# MO-R4A-S2 Real 24 Event Blinded Prediction Freeze",
        "",
        "This packet is an outcome-blind, side-local experimental hypothesis freeze. It is not classical doctrine, "
        "a price forecast, a signed oscillator, or a USDJPY pair prediction.",
        "",
        f"Prediction freeze hash: `{freeze['predictionFreezeHash']}`",
        f"S2 registry hash: `{freeze['hypothesisRegistryHash']}`",
        f"Frozen S1R1-R1 ledger hash: `{freeze['upstreamSourceLedgerHash']}`",
        f"Frozen S1R1-R1 coverage hash: `{freeze['upstreamCoverageHash']}`",
        "",
        f"Events: {summary['eventCount']} ({summary['usdEventCount']} USD, {summary['jpyEventCount']} JPY)",
        f"Bridge eligible: {summary['bridgeEligibleCount']}; abstained: {summary['abstentionCount']}",
        f"Categorical states: {summary['supportiveCount']} SUPPORTIVE, {summary['adverseCount']} ADVERSE, "
        f"{summary['neutralCount']} NEUTRAL, {summary['unknownCount']} UNKNOWN_MORE_EVIDENCE_REQUIRED",
        "",
        "| Side | Event ID | Compound source state | S2 side pressure | Bridge | Overall source astrology |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for prediction in freeze["predictions"]:
        lines.append(
            "| "
            + " | ".join(
                (
                    prediction["sideIdentity"],
                    prediction["eventId"],
                    prediction["sourceOperatorInput"]["outputState"],
                    prediction["currencyPressureState"],
                    "APPLIED" if prediction["bridgeApplied"] else "ABSTAIN",
                    prediction["overallAstrologicalInterpretation"],
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Every prediction has `signedUnit=null` and `magnitudeConfigured=false`. A JPY-side SUPPORTIVE state is "
            "support for JPY only; no USDJPY pair result is created. Price, outcomes, Founder Review, SBC, catalogue, "
            "Auto Suggest, ML, MT5, and execution remain outside this packet.",
            "",
        ]
    )
    return "\n".join(lines)


def write_s2_artifacts(resource_root: Path = PROJECT_ROOT) -> dict[str, Path]:
    """Materialize deterministic S2 review artifacts from frozen source inputs only."""

    root = Path(resource_root).resolve()
    freeze = build_s2_blinded_prediction_freeze(root)
    audit = build_s2_invariance_audit(root, prediction_freeze=freeze)
    acceptance = build_s2_acceptance_manifest(root, prediction_freeze=freeze, invariance_audit=audit)
    artifacts = {
        "predictionFreeze": root / "status" / "audits" / DEFAULT_S2_FREEZE_PATH.name,
        "invarianceAudit": root / "status" / "audits" / DEFAULT_S2_INVARIANCE_AUDIT_PATH.name,
        "acceptance": root / "status" / "acceptance" / DEFAULT_S2_ACCEPTANCE_PATH.name,
        "reviewTable": root / "docs" / "research" / DEFAULT_S2_REVIEW_TABLE_PATH.name,
    }
    for path in artifacts.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    artifacts["predictionFreeze"].write_text(json.dumps(freeze, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    artifacts["invarianceAudit"].write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    artifacts["acceptance"].write_text(json.dumps(acceptance, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    artifacts["reviewTable"].write_text(render_s2_prediction_freeze_markdown(freeze), encoding="utf-8")
    return artifacts
