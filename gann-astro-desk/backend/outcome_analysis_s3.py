"""MO-R4A-S3 outcome-analysis preregistration and synthetic-only evaluator.

S3 freezes *how* the approved, outcome-blind 24-event pilot may later be
evaluated.  It deliberately has no provider client, market-file reader,
Founder Review dependency, or production output.  The only runtime inputs to
the evaluator are caller-supplied in-memory synthetic tick mappings.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import combinations, product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import blinded_market_bridge_s2 as s2
import blinded_market_bridge_s2r1_r1 as s2r1r1


S3_PREREGISTRATION_CONTRACT = "MO_R4A_S3_OUTCOME_ANALYSIS_PREREGISTRATION_V1"
S3_PRIMARY_POPULATION_CONTRACT = "MO_R4A_S3_PRIMARY_ANALYSIS_POPULATION_V1"
S3_OVERLAP_CLUSTERS_CONTRACT = "MO_R4A_S3_OVERLAP_CLUSTERS_V1"
S3_INVARIANCE_AUDIT_CONTRACT = "MO_R4A_S3_ANALYSIS_PLAN_INVARIANCE_AUDIT_V1"
S3_ACCEPTANCE_CONTRACT = "MO_R4A_S3_OUTCOME_ANALYSIS_PREREGISTRATION_ACCEPTANCE_V1"
S3_SCHEMA_VERSION = 1
S3_MILESTONE = "MO-R4A-S3"
S3_EXPECTED_STARTING_MASTER = "41d335be460f5f0b3f6ba522028ee14b44a94f25"

EXPECTED_UPSTREAM_HASHES = {
    "sourceOperatorLedgerHash": "2D4AD6E151602FBF2FC3E0ADDFDCDE7C7211CC52ED44D801AD3925AD9D5F3366",
    "sourceCoverageHash": "A4437C2A116EBD5D465339BCB0C9D81F8149CE65FAF37CF81C0F29D75B44F8B0",
    "hypothesisRegistryHash": "D76E208F52511BD8B5380BB32049B0C47275261443E587E3E09184E439FF3110",
    "usdHypothesisHash": "1C816B735FCCA52B84ED26C03D1755D251EADA7C2606B1D56533A06D71B713F9",
    "jpyHypothesisHash": "EF2D18CEA75BCC1A137D8687F332B5586FB62D8803D44819204AFDD6472ED24F",
    "predictionFreezeHash": "83F1456271B510468A0DF28C66AD705318CD06F5D5B5E0566F6DE05FA06CF71D",
}
S2R1_R1_EXPECTED_INVARIANCE_AUDIT_HASH = "9275312E183B631ED28F568509883328ACBEC4D6775B8AF3066E0DF515FA3BE3"
S2R1_R1_EXPECTED_ACCEPTANCE_HASH = "DFE2837578DB17AE6E286EA7585A2E17E3B39DBF78D63984A48EFBFD72EDA4C6"

OUTCOME_ACCESS_FLAGS = (
    "PRICE_DATA_READ",
    "OUTCOME_DATA_READ",
    "FOUNDER_DECISION_READ",
    "REVIEW_STORE_READ",
    "SBC_READ",
    "CATALOGUE_ADMISSION",
    "EVIDENCE_ADMISSION",
    "SIGNED_WAVE_RENDERED",
    "PAIR_RESULTANT_CREATED",
    "MAGNITUDE_CONFIGURED",
    "AUTO_SUGGEST",
    "ML",
    "MT5",
    "EXECUTION_ALLOWED",
    "PRODUCTION_ADMISSION",
    "OUTCOME_UNLOCKED",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MACHINE_INTERPRETATION_ROOT = PROJECT_ROOT / "configs" / "research" / "machine_interpretation"
AUDIT_ROOT = PROJECT_ROOT / "status" / "audits"
ACCEPTANCE_ROOT = PROJECT_ROOT / "status" / "acceptance"
DOCS_ROOT = PROJECT_ROOT / "docs" / "research"

DEFAULT_PREREGISTRATION_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3_v1.json"
DEFAULT_PREREGISTRATION_SCHEMA_PATH = MACHINE_INTERPRETATION_ROOT / "outcome_analysis_preregistration_s3_v1.schema.json"
DEFAULT_PRIMARY_POPULATION_PATH = AUDIT_ROOT / "mo_r4a_s3_primary_analysis_population.json"
DEFAULT_OVERLAP_CLUSTERS_PATH = AUDIT_ROOT / "mo_r4a_s3_overlap_clusters.json"
DEFAULT_INVARIANCE_AUDIT_PATH = AUDIT_ROOT / "mo_r4a_s3_analysis_plan_invariance_audit.json"
DEFAULT_ACCEPTANCE_PATH = ACCEPTANCE_ROOT / "mo_r4a_s3_outcome_analysis_preregistration.json"
DEFAULT_REPORT_PATH = DOCS_ROOT / "MULTI_OSCILLATOR_MO_R4A_S3_OUTCOME_ANALYSIS_PREREGISTRATION.md"


class OutcomeAnalysisS3Error(ValueError):
    """Raised when S3 loses its frozen lineage or its outcome-blind boundary."""


class OutcomeAccessBlockedError(OutcomeAnalysisS3Error):
    """Raised when an attempted materialization tries to attach outcome access."""


class SyntheticTickInputError(OutcomeAnalysisS3Error):
    """Raised when a synthetic tick cannot be identified as a UTC observation."""


class SyntheticTickQuoteError(OutcomeAnalysisS3Error):
    """Raised when an in-scope synthetic quote is not a valid bid/ask pair."""


class SyntheticTickConflictError(OutcomeAnalysisS3Error):
    """Raised when in-scope quotes disagree at one UTC timestamp."""

    def __init__(self, timestamp_utc: str) -> None:
        self.timestamp_utc = timestamp_utc
        super().__init__(f"Conflicting synthetic quotes at {timestamp_utc}")


@dataclass(frozen=True)
class CanonicalTick:
    """One validated in-memory bid/ask observation used only by synthetic tests."""

    timestamp_utc: datetime
    bid: float
    ask: float
    source_index: int

    @property
    def midpoint(self) -> float:
        # Avoid overflowing before division when a synthetic edge case uses
        # very large finite quote values.
        return self.bid + (self.ask - self.bid) / 2.0


def _canonical_hash(value: Any) -> str:
    return s2._canonical_hash(value)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise OutcomeAnalysisS3Error(f"Missing {label}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise OutcomeAnalysisS3Error(f"Invalid JSON in {label}: {path}") from exc
    if not isinstance(raw, dict):
        raise OutcomeAnalysisS3Error(f"{label} must be a JSON object")
    return raw


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _without_hash(payload: Mapping[str, Any], hash_key: str) -> dict[str, Any]:
    return {key: copy.deepcopy(value) for key, value in payload.items() if key != hash_key}


def _require_upper_sha256(value: Any, label: str) -> str:
    text = str(value or "")
    if len(text) != 64 or any(character not in "0123456789ABCDEF" for character in text):
        raise OutcomeAnalysisS3Error(f"{label} must be an uppercase SHA-256")
    return text


def _parse_utc(value: Any, label: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise OutcomeAnalysisS3Error(f"{label} must be an ISO-8601 UTC timestamp") from exc
    else:
        raise OutcomeAnalysisS3Error(f"{label} must be an ISO-8601 UTC timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise OutcomeAnalysisS3Error(f"{label} must be explicit UTC")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _assert_all_false(flags: Mapping[str, Any], label: str) -> None:
    if set(flags) != set(OUTCOME_ACCESS_FLAGS) or any(value is not False for value in flags.values()):
        raise OutcomeAnalysisS3Error(f"{label} must retain every S3 access flag as false")


def _outcome_blind_flags() -> dict[str, bool]:
    return {key: False for key in OUTCOME_ACCESS_FLAGS}


def _validation_expected_pair_direction(side: str, state: str) -> str:
    mapping = {
        ("USD", "SUPPORTIVE"): "UP",
        ("USD", "ADVERSE"): "DOWN",
        ("JPY", "SUPPORTIVE"): "DOWN",
        ("JPY", "ADVERSE"): "UP",
        ("USD", "NEUTRAL"): "NO_DIRECTIONAL_PREDICTION",
        ("JPY", "NEUTRAL"): "NO_DIRECTIONAL_PREDICTION",
        ("USD", "UNKNOWN_MORE_EVIDENCE_REQUIRED"): "ABSTAIN",
        ("JPY", "UNKNOWN_MORE_EVIDENCE_REQUIRED"): "ABSTAIN",
    }
    try:
        return mapping[(side, state)]
    except KeyError as exc:
        raise OutcomeAnalysisS3Error(f"No approved S3 validation mapping for {side}/{state}") from exc


def _expected_direction_unit(direction: str) -> int:
    if direction == "UP":
        return 1
    if direction == "DOWN":
        return -1
    raise OutcomeAnalysisS3Error(f"Directional primary requires UP or DOWN, not {direction}")


def _s2r1_paths(root: Path) -> dict[str, Path]:
    return {
        "ledger": root / s2r1r1.DEFAULT_S2R1_R1_LEDGER_PATH.relative_to(PROJECT_ROOT),
        "coverage": root / s2r1r1.DEFAULT_S2R1_R1_COVERAGE_PATH.relative_to(PROJECT_ROOT),
        "registry": root / s2r1r1.DEFAULT_S2R1_R1_REGISTRY_PATH.relative_to(PROJECT_ROOT),
        "freeze": root / s2r1r1.DEFAULT_S2R1_R1_FREEZE_PATH.relative_to(PROJECT_ROOT),
        "invariance": root / s2r1r1.DEFAULT_S2R1_R1_INVARIANCE_AUDIT_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / s2r1r1.DEFAULT_S2R1_R1_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
    }


def load_verified_s2r1_r1_inputs(resource_root: Path = PROJECT_ROOT) -> dict[str, dict[str, Any]]:
    """Load only the fixed S2R1-R1 source/freeze records, never outcome state."""

    root = Path(resource_root).resolve()
    paths = _s2r1_paths(root)
    raw = {name: _read_json(path, f"S2R1-R1 {name}") for name, path in paths.items()}
    ledger = raw["ledger"]
    coverage = raw["coverage"]
    registry = raw["registry"]
    freeze = raw["freeze"]
    invariance = raw["invariance"]
    acceptance = raw["acceptance"]

    checks = {
        "sourceOperatorLedgerHash": _canonical_hash(ledger),
        "sourceCoverageHash": _canonical_hash(_without_hash(coverage, "sourceOperatorCoverageHash")),
        "hypothesisRegistryHash": _canonical_hash(_without_hash(registry, "registryHash")),
        "predictionFreezeHash": _canonical_hash(_without_hash(freeze, "predictionFreezeHash")),
    }
    if checks["sourceCoverageHash"] != coverage.get("sourceOperatorCoverageHash"):
        raise OutcomeAnalysisS3Error("S2R1-R1 coverage hash does not bind its source coverage")
    if checks["hypothesisRegistryHash"] != registry.get("registryHash"):
        raise OutcomeAnalysisS3Error("S2R1-R1 registry hash does not bind its source registry")
    if checks["predictionFreezeHash"] != freeze.get("predictionFreezeHash"):
        raise OutcomeAnalysisS3Error("S2R1-R1 prediction freeze hash does not bind frozen predictions")
    for key in ("sourceOperatorLedgerHash", "sourceCoverageHash", "hypothesisRegistryHash", "predictionFreezeHash"):
        if checks[key] != EXPECTED_UPSTREAM_HASHES[key]:
            raise OutcomeAnalysisS3Error(f"S3 is bound to an unexpected {key}")
    entries = {str(entry.get("targetSide")): entry for entry in registry.get("entries", [])}
    if set(entries) != {"USD", "JPY"}:
        raise OutcomeAnalysisS3Error("S2R1-R1 registry must retain one USD and one JPY hypothesis")
    if entries["USD"].get("hypothesisHash") != EXPECTED_UPSTREAM_HASHES["usdHypothesisHash"]:
        raise OutcomeAnalysisS3Error("S3 USD hypothesis binding differs from the accepted S2R1-R1 freeze")
    if entries["JPY"].get("hypothesisHash") != EXPECTED_UPSTREAM_HASHES["jpyHypothesisHash"]:
        raise OutcomeAnalysisS3Error("S3 JPY hypothesis binding differs from the accepted S2R1-R1 freeze")
    invariance_body = _without_hash(invariance, "invarianceAuditHash")
    acceptance_body = _without_hash(acceptance, "acceptanceManifestHash")
    if (
        invariance.get("invarianceAuditHash"), _canonical_hash(invariance_body),
        acceptance.get("acceptanceManifestHash"), _canonical_hash(acceptance_body),
    ) != (
        S2R1_R1_EXPECTED_INVARIANCE_AUDIT_HASH, S2R1_R1_EXPECTED_INVARIANCE_AUDIT_HASH,
        S2R1_R1_EXPECTED_ACCEPTANCE_HASH, S2R1_R1_EXPECTED_ACCEPTANCE_HASH,
    ):
        raise OutcomeAnalysisS3Error("S2R1-R1 invariance or acceptance binding differs from the accepted freeze")
    freeze_event_ids = [row.get("eventId") for row in freeze.get("predictions", [])]
    if freeze_event_ids != freeze.get("frozenEventOrder") or len(freeze_event_ids) != 24:
        raise OutcomeAnalysisS3Error("S2R1-R1 frozen order must retain all 24 immutable event identities")
    upstream_rows = invariance.get("rows")
    if not isinstance(upstream_rows, list) or len(upstream_rows) != 24:
        raise OutcomeAnalysisS3Error("S2R1-R1 invariance audit must bind every frozen event")
    upstream_by_event = {row.get("eventId"): row for row in upstream_rows}
    if set(upstream_by_event) != set(freeze_event_ids):
        raise OutcomeAnalysisS3Error("S2R1-R1 invariance rows must match every frozen event")
    if any(
        not all(row.get(key) is True for key in ("identityUnchanged", "astronomySnapshotUnchanged", "overallSourceCompositionUnchanged"))
        for row in upstream_rows
    ):
        raise OutcomeAnalysisS3Error("S2R1-R1 invariance audit cannot be weakened before S3")
    for prediction in freeze["predictions"]:
        if upstream_by_event[prediction["eventId"]].get("predictionHash") != prediction.get("eventPredictionHash"):
            raise OutcomeAnalysisS3Error("S2R1-R1 event prediction binding changed before S3")
    for item in (coverage, freeze, invariance, acceptance):
        for key in ("priceDataRead", "outcomeDataRead", "founderDecisionRead", "reviewStoreRead"):
            if item.get(key) is True:
                raise OutcomeAnalysisS3Error(f"S2R1-R1 input unexpectedly read protected state: {key}")
    if acceptance.get("predictionFreezeHash") != EXPECTED_UPSTREAM_HASHES["predictionFreezeHash"]:
        raise OutcomeAnalysisS3Error("S2R1-R1 acceptance does not bind the accepted prediction freeze")
    return raw


def build_outcome_analysis_preregistration(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Build S3's static plan without obtaining or evaluating a market outcome."""

    load_verified_s2r1_r1_inputs(resource_root)
    body = {
        "contract": S3_PREREGISTRATION_CONTRACT,
        "schemaVersion": S3_SCHEMA_VERSION,
        "milestone": S3_MILESTONE,
        "startingMaster": S3_EXPECTED_STARTING_MASTER,
        "createdAtUtc": "2026-09-11T00:00:00Z",
        "status": "OUTCOME_ANALYSIS_PREREGISTRATION_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT",
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "frozenPilot": {
            "eventCount": 24,
            "usdEventCount": 12,
            "jpyEventCount": 12,
            "singlePassVerifiedCount": 24,
            "bridgeApplicableCount": 17,
            "directionalCount": 14,
            "supportiveCount": 9,
            "adverseCount": 5,
            "neutralCount": 3,
            "unknownAbstainCount": 7,
            "primaryMarketScorableCount": 13,
            "structuralWeekendExclusionCount": 1,
        },
        "marketDataSource": {
            "provider": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
            "instrument": "USDJPY",
            "quoteConvention": "JPY_PER_USD",
            "timestampConvention": "UTC_ONLY",
            "requiredFields": ["timestampUtc", "bid", "ask"],
            "midpointFormula": "m(t)=(bid(t)+ask(t))/2",
            "validQuoteRules": ["bid finite positive", "ask finite positive", "ask >= bid"],
            "fallbackProviderAllowed": False,
            "s3ProviderAccessAllowed": False,
            "s4ProviderAccessRequiresIndependentCentralReview": True,
        },
        "primaryInterval": {
            "definition": "[applyingStartUtc_i, separatingEndUtc_i)",
            "exactUtcRole": "PROVENANCE_ONLY_NEVER_RETURN_BOUNDARY",
            "halfOpen": True,
            "startTick": "earliest valid tick timestamp >= applyingStartUtc and < separatingEndUtc",
            "endTick": "latest valid tick timestamp < separatingEndUtc and >= startTick timestamp",
            "outsideIntervalRescueAllowed": False,
            "minimumDistinctTickTimestamps": 2,
            "sameTimestampStatus": "DATA_UNSCORABLE",
            "insufficientTicksStatus": "DATA_UNSCORABLE",
            "alignmentGapsRecordedOnly": True,
            "returnFormula": "r_i=ln(P_end/P_start)",
        },
        "validationMapping": {
            "scope": "VALIDATION_ONLY_NOT_PRODUCTION_SIGNED_WAVE_OR_PAIR_RESULTANT",
            "USD_SUPPORTIVE": "UP",
            "USD_ADVERSE": "DOWN",
            "JPY_SUPPORTIVE": "DOWN",
            "JPY_ADVERSE": "UP",
            "NEUTRAL": "NO_DIRECTIONAL_PREDICTION",
            "UNKNOWN": "ABSTAIN",
            "signedUnitCreated": False,
            "pairRawCreated": False,
            "pairDisplayCreated": False,
        },
        "zeroAndAbstentionPolicy": {
            "returnPositive": "UP",
            "returnNegative": "DOWN",
            "returnZero": "ZERO_MOVE_DIRECTIONAL_MISS",
            "neutral": "EXCLUDED_FROM_DIRECTIONAL_PRIMARY_SCORING_NOT_NUMERIC_ZERO",
            "unknown": "ABSTAIN_EXCLUDED_FROM_DIRECTIONAL_PRIMARY_SCORING",
        },
        "weekendExclusion": {
            "eventId": "TN_BD340A6100B173B5F254EDC1",
            "sideIdentity": "USD",
            "pressureState": "SUPPORTIVE",
            "status": "PRIMARY_NONTRADING_WEEKEND_EXCLUSION",
            "intervalUtc": ["2025-04-05T01:45:04Z", "2025-04-05T12:34:35Z"],
            "reason": "COMPLETE_PRIMARY_INTERVAL_IS_SATURDAY_UTC",
            "retainedInFrozenPilot": True,
            "resampleOrExtendAllowed": False,
        },
        "overlapClusters": {
            "overlapRule": "a.start < b.end and b.start < a.end",
            "touchingBoundaryIsOverlap": False,
            "connectedComponents": "TRANSITIVE_HALF_OPEN_INTERVAL_GRAPH",
            "primaryClusters": ["C1", "C2", "C3", "C4"],
        },
        "primaryStatistic": {
            "expectedDirectionUnit": {"UP": 1, "DOWN": -1},
            "realizedDirectionUnit": {"UP": 1, "DOWN": -1},
            "hitDefinition": "hit_i=1 if q_i*r_i>0 else 0",
            "primaryHitCount": "H=sum(hit_i) over all 13 primary market-scorable events",
            "primaryHitRate": "H/13",
            "oneSidedAlternative": "GREATER_THAN_CHANCE",
        },
        "exactPermutation": {
            "usdLabelPositions": "choose 1 SUPPORTIVE position among 5 USD primary events",
            "jpyLabelPositions": "choose 7 SUPPORTIVE positions among 8 JPY primary events",
            "assignmentCountFormula": "C(5,1)*C(8,7)",
            "assignmentCount": 40,
            "sideLocalOnly": True,
            "eventWindowsAndReturnsFixedAtS4": True,
            "observedAssignmentIncluded": True,
            "retainAll40PermutationHitCountsAndHistogramAtS4": True,
            "pExact": "count(H_perm >= H_observed)/40",
            "noMonteCarlo": True,
            "noTimestampPermutation": True,
            "noCrossSidePermutation": True,
            "noNeutralOrUnknownInPrimary": True,
        },
        "clusterSecondary": {
            "clusterActivity": "A_c=mean(hit_i for i in cluster c)",
            "clusterBalancedHitRate": "mean(A_c for C1,C2,C3,C4)",
            "equalClusterWeighting": True,
            "secondaryPValueAllowed": False,
        },
        "secondaryDescriptive": [
            "USD hit rate over 5 primary events",
            "JPY hit rate over 8 primary events",
            "mean and median q_i*r_i",
            "cluster-balanced hit rate",
            "coverage accounting 14/24 directional, 13/24 primary market-scorable, 17/24 applicable, 3 neutral, 7 abstain, 1 weekend exclusion",
            "start/end alignment gaps as descriptive audit fields",
        ],
        "timeShiftDiagnostics": {
            "shiftsCalendarDays": [-7, 7],
            "preserve": ["duration", "side", "label", "UTC clock"],
            "sameBoundaryAndReturnRule": True,
            "diagnosticOnly": True,
            "secondaryPValueAllowed": False,
            "timingSpecificityFlag": "TIMING_SPECIFICITY_NOT_DEMONSTRATED",
        },
        "multiplicity": {
            "primaryInferentialTestCount": 1,
            "secondaryPValues": False,
            "multiplicityCorrectionRequired": False,
            "newAnalysisRequiresAmendment": True,
        },
        "survivalRule": {
            "all13PrimaryValidlyScorable": True,
            "primaryHitRateStrictlyGreaterThan": 0.5,
            "pExactAtMost": 0.1,
            "clusterBalancedHitRateStrictlyGreaterThan": 0.5,
            "survivedStatus": "PILOT_ASSOCIATION_SURVIVED",
            "notSurvivedStatus": "PILOT_ASSOCIATION_NOT_SURVIVED",
            "invalidDataStatus": "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE",
            "denominatorShrinkAllowed": False,
            "providerSubstitutionAllowed": False,
        },
        "amendmentAndStopping": {
            "outcomeAccessBeforeCentralReview": False,
            "s4AstraBeforeCentralReview": False,
            "alternativeHorizonAllowed": False,
            "marketOutcomeInS3Artifacts": False,
            "productionClaimAllowed": False,
            "executionAllowed": False,
        },
        "outcomeAccessFlags": _outcome_blind_flags(),
    }
    return {**body, "preregistrationHash": _canonical_hash(body)}


def build_preregistration_schema() -> dict[str, Any]:
    """Return the strict envelope schema for the checked-in preregistration."""

    sample = build_outcome_analysis_preregistration(PROJECT_ROOT)
    required = list(sample)
    properties: dict[str, Any] = {key: {} for key in required}
    for key in ("schemaVersion",):
        properties[key] = {"type": "integer"}
    for key in ("upstreamHashes", "frozenPilot", "marketDataSource", "primaryInterval", "validationMapping", "zeroAndAbstentionPolicy", "weekendExclusion", "overlapClusters", "primaryStatistic", "exactPermutation", "clusterSecondary", "timeShiftDiagnostics", "multiplicity", "survivalRule", "amendmentAndStopping", "outcomeAccessFlags"):
        properties[key] = {"type": "object"}
    properties["secondaryDescriptive"] = {"type": "array"}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": S3_PREREGISTRATION_CONTRACT,
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": properties,
    }


def validate_preregistration(preregistration: Mapping[str, Any]) -> None:
    """Use a deliberately strict standard-library validation path for S3 JSON."""

    expected = set(build_outcome_analysis_preregistration(PROJECT_ROOT))
    if set(preregistration) != expected:
        raise OutcomeAnalysisS3Error("S3 preregistration keys do not match its immutable schema envelope")
    if (
        preregistration.get("contract"), preregistration.get("schemaVersion"), preregistration.get("milestone"),
        preregistration.get("startingMaster"), preregistration.get("status"), preregistration.get("nextGate"),
    ) != (
        S3_PREREGISTRATION_CONTRACT, S3_SCHEMA_VERSION, S3_MILESTONE,
        S3_EXPECTED_STARTING_MASTER, "OUTCOME_ANALYSIS_PREREGISTRATION_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT",
    ):
        raise OutcomeAnalysisS3Error("S3 preregistration identity or central-review gate is invalid")
    if preregistration.get("upstreamHashes") != EXPECTED_UPSTREAM_HASHES:
        raise OutcomeAnalysisS3Error("S3 preregistration does not bind all six accepted upstream hashes")
    if preregistration.get("preregistrationHash") != _canonical_hash(_without_hash(preregistration, "preregistrationHash")):
        raise OutcomeAnalysisS3Error("S3 preregistration hash does not bind its plan")
    _assert_all_false(preregistration["outcomeAccessFlags"], "S3 preregistration outcome-access flags")
    if preregistration["marketDataSource"].get("s3ProviderAccessAllowed") is not False:
        raise OutcomeAnalysisS3Error("S3 cannot access a market provider")
    if preregistration["validationMapping"].get("signedUnitCreated") is not False:
        raise OutcomeAnalysisS3Error("S3 validation mapping cannot create a signed unit")


def _frozen_predictions(resource_root: Path) -> list[dict[str, Any]]:
    upstream = load_verified_s2r1_r1_inputs(resource_root)
    freeze = upstream["freeze"]
    predictions = freeze.get("predictions")
    if not isinstance(predictions, list) or len(predictions) != 24:
        raise OutcomeAnalysisS3Error("S3 requires the frozen 24-event prediction population")
    if len({row.get("eventId") for row in predictions}) != 24:
        raise OutcomeAnalysisS3Error("S3 frozen prediction IDs must be unique")
    if any(row.get("identityStatus") != "SINGLE_PASS_VERIFIED" for row in predictions):
        raise OutcomeAnalysisS3Error("S3 requires every frozen prediction to remain SINGLE_PASS_VERIFIED")
    if sum(row.get("sideIdentity") == "USD" for row in predictions) != 12 or sum(row.get("sideIdentity") == "JPY" for row in predictions) != 12:
        raise OutcomeAnalysisS3Error("S3 frozen pilot must retain 12 USD and 12 JPY rows")
    return copy.deepcopy(predictions)


def _population_row(prediction: Mapping[str, Any]) -> dict[str, Any]:
    side = str(prediction["sideIdentity"])
    state = str(prediction["currencyPressureState"])
    interval_start = str(prediction["applyingStartUtc"])
    interval_end = str(prediction["separatingEndUtc"])
    _parse_utc(interval_start, "applyingStartUtc")
    _parse_utc(interval_end, "separatingEndUtc")
    if _parse_utc(interval_start, "applyingStartUtc") >= _parse_utc(interval_end, "separatingEndUtc"):
        raise OutcomeAnalysisS3Error("Frozen primary interval must have positive half-open duration")
    disposition = ""
    if state in {"SUPPORTIVE", "ADVERSE"}:
        disposition = "PRIMARY_DIRECTIONAL"
    elif state == "NEUTRAL":
        disposition = "CATEGORICAL_NEUTRAL_NOT_DIRECTIONAL"
    elif state == "UNKNOWN_MORE_EVIDENCE_REQUIRED":
        disposition = "ABSTAIN_UNKNOWN_NOT_DIRECTIONAL"
    else:
        raise OutcomeAnalysisS3Error(f"S3 cannot classify unexpected frozen pressure state: {state}")
    if prediction["eventId"] == "TN_BD340A6100B173B5F254EDC1":
        if (side, state, interval_start, interval_end) != (
            "USD", "SUPPORTIVE", "2025-04-05T01:45:04Z", "2025-04-05T12:34:35Z",
        ):
            raise OutcomeAnalysisS3Error("Weekend exclusion identity or interval changed")
        start = _parse_utc(interval_start, "weekend start")
        end = _parse_utc(interval_end, "weekend end")
        if start.weekday() != 5 or end.weekday() != 5:
            raise OutcomeAnalysisS3Error("Weekend exclusion must remain entirely Saturday UTC")
        disposition = "PRIMARY_NONTRADING_WEEKEND_EXCLUSION"
    return {
        "eventId": prediction["eventId"],
        "eventHash": prediction["eventHash"],
        "eventPredictionHash": prediction["eventPredictionHash"],
        "sideIdentity": side,
        "pressureState": state,
        "identityStatus": prediction["identityStatus"],
        "applyingStartUtc": interval_start,
        "exactUtc": prediction["exactUtc"],
        "separatingEndUtc": interval_end,
        "analysisDisposition": disposition,
        "validationExpectedPairDirection": _validation_expected_pair_direction(side, state),
    }


EXPECTED_PRIMARY_EVENT_ORDER = (
    "TN_4A15CCC7D126313A14BCB562",
    "TN_6E2DD561FB40D45D406F808E",
    "TN_7CCC78DA82BDAC13D3CF60B0",
    "TN_397A2B053BC76D9D788E5E5E",
    "TN_B24B1690FD8612329198D379",
    "TN_8C3582F7101F4F14BC4ECC4F",
    "TN_B8750233DA923D431E121862",
    "TN_529E2CBC72B405EAD0990350",
    "TN_29BCE2386E5DB19625921587",
    "TN_6F48D71F91F1382FAA720581",
    "TN_97C9294ED13CD6C36FB0840B",
    "TN_574C7A7407B855CD78DF8E0D",
    "TN_A32A6104A917D4918B269910",
)


def build_primary_analysis_population(resource_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Derive the primary set and its one structural weekend exclusion from S2R1-R1."""

    root = Path(resource_root).resolve()
    preregistration = build_outcome_analysis_preregistration(root)
    rows = [_population_row(prediction) for prediction in _frozen_predictions(root)]
    directional = [row for row in rows if row["analysisDisposition"] in {"PRIMARY_DIRECTIONAL", "PRIMARY_NONTRADING_WEEKEND_EXCLUSION"}]
    primary = sorted((row for row in rows if row["analysisDisposition"] == "PRIMARY_DIRECTIONAL"), key=lambda row: row["applyingStartUtc"])
    counts = {
        "frozenEventCount": len(rows),
        "directionalCount": len(directional),
        "primaryMarketScorableCount": len(primary),
        "structuralWeekendExclusionCount": sum(row["analysisDisposition"] == "PRIMARY_NONTRADING_WEEKEND_EXCLUSION" for row in rows),
        "neutralCount": sum(row["analysisDisposition"] == "CATEGORICAL_NEUTRAL_NOT_DIRECTIONAL" for row in rows),
        "unknownAbstainCount": sum(row["analysisDisposition"] == "ABSTAIN_UNKNOWN_NOT_DIRECTIONAL" for row in rows),
        "usdPrimaryCount": sum(row["sideIdentity"] == "USD" for row in primary),
        "jpyPrimaryCount": sum(row["sideIdentity"] == "JPY" for row in primary),
        "usdSupportivePrimaryCount": sum(row["sideIdentity"] == "USD" and row["pressureState"] == "SUPPORTIVE" for row in primary),
        "usdAdversePrimaryCount": sum(row["sideIdentity"] == "USD" and row["pressureState"] == "ADVERSE" for row in primary),
        "jpySupportivePrimaryCount": sum(row["sideIdentity"] == "JPY" and row["pressureState"] == "SUPPORTIVE" for row in primary),
        "jpyAdversePrimaryCount": sum(row["sideIdentity"] == "JPY" and row["pressureState"] == "ADVERSE" for row in primary),
    }
    expected_counts = {
        "frozenEventCount": 24, "directionalCount": 14, "primaryMarketScorableCount": 13,
        "structuralWeekendExclusionCount": 1, "neutralCount": 3, "unknownAbstainCount": 7,
        "usdPrimaryCount": 5, "jpyPrimaryCount": 8, "usdSupportivePrimaryCount": 1,
        "usdAdversePrimaryCount": 4, "jpySupportivePrimaryCount": 7, "jpyAdversePrimaryCount": 1,
    }
    if counts != expected_counts or tuple(row["eventId"] for row in primary) != EXPECTED_PRIMARY_EVENT_ORDER:
        raise OutcomeAnalysisS3Error("S3 primary population differs from the frozen approved 13-event plan")
    body = {
        "contract": S3_PRIMARY_POPULATION_CONTRACT,
        "schemaVersion": S3_SCHEMA_VERSION,
        "milestone": S3_MILESTONE,
        "preregistrationHash": preregistration["preregistrationHash"],
        "predictionFreezeHash": EXPECTED_UPSTREAM_HASHES["predictionFreezeHash"],
        "populationCounts": counts,
        "allFrozenRows": rows,
        "primaryMarketScorableRows": primary,
        "structuralExclusion": next(row for row in rows if row["analysisDisposition"] == "PRIMARY_NONTRADING_WEEKEND_EXCLUSION"),
        "outcomeAccessFlags": _outcome_blind_flags(),
    }
    return {**body, "primaryPopulationHash": _canonical_hash(body)}


def intervals_overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    """Return true only for a strict overlap of two half-open S3 intervals."""

    left_start = _parse_utc(left["applyingStartUtc"], "left applyingStartUtc")
    left_end = _parse_utc(left["separatingEndUtc"], "left separatingEndUtc")
    right_start = _parse_utc(right["applyingStartUtc"], "right applyingStartUtc")
    right_end = _parse_utc(right["separatingEndUtc"], "right separatingEndUtc")
    return left_start < right_end and right_start < left_end


def derive_overlap_clusters(primary_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Derive connected components from half-open event intervals without inference."""

    ordered = sorted((copy.deepcopy(dict(row)) for row in primary_rows), key=lambda row: row["applyingStartUtc"])
    if not ordered:
        raise OutcomeAnalysisS3Error("S3 requires primary rows before deriving overlap clusters")
    components: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    latest_end: datetime | None = None
    for row in ordered:
        start = _parse_utc(row["applyingStartUtc"], "cluster applyingStartUtc")
        end = _parse_utc(row["separatingEndUtc"], "cluster separatingEndUtc")
        if latest_end is None or start >= latest_end:
            if current:
                components.append(current)
            current = [row]
            latest_end = end
        else:
            current.append(row)
            latest_end = max(latest_end, end)
    if current:
        components.append(current)
    clusters = []
    for index, members in enumerate(components, start=1):
        clusters.append(
            {
                "clusterId": f"C{index}",
                "memberEventIds": [member["eventId"] for member in members],
                "memberCount": len(members),
                "earliestStartUtc": min(member["applyingStartUtc"] for member in members),
                "latestEndUtc": max(member["separatingEndUtc"] for member in members),
            }
        )
    return clusters


EXPECTED_CLUSTERS = (
    ("C1", ("TN_4A15CCC7D126313A14BCB562", "TN_6E2DD561FB40D45D406F808E", "TN_7CCC78DA82BDAC13D3CF60B0", "TN_397A2B053BC76D9D788E5E5E", "TN_B24B1690FD8612329198D379"), "2025-03-31T20:48:24Z", "2025-04-02T06:09:08Z"),
    ("C2", ("TN_8C3582F7101F4F14BC4ECC4F",), "2025-04-02T08:39:52Z", "2025-04-02T18:38:57Z"),
    ("C3", ("TN_B8750233DA923D431E121862", "TN_529E2CBC72B405EAD0990350"), "2025-04-02T21:43:26Z", "2025-04-03T08:04:32Z"),
    ("C4", ("TN_29BCE2386E5DB19625921587", "TN_6F48D71F91F1382FAA720581", "TN_97C9294ED13CD6C36FB0840B", "TN_574C7A7407B855CD78DF8E0D", "TN_A32A6104A917D4918B269910"), "2025-04-03T08:35:23Z", "2025-04-04T20:32:38Z"),
)


def build_overlap_clusters(resource_root: Path = PROJECT_ROOT, *, population: Mapping[str, Any] | None = None) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    primary_population = copy.deepcopy(population) if population is not None else build_primary_analysis_population(root)
    if primary_population.get("primaryPopulationHash") != _canonical_hash(_without_hash(primary_population, "primaryPopulationHash")):
        raise OutcomeAnalysisS3Error("S3 primary population hash does not bind its rows")
    clusters = derive_overlap_clusters(primary_population["primaryMarketScorableRows"])
    observed = tuple((row["clusterId"], tuple(row["memberEventIds"]), row["earliestStartUtc"], row["latestEndUtc"]) for row in clusters)
    if observed != EXPECTED_CLUSTERS:
        raise OutcomeAnalysisS3Error("S3 half-open overlap graph does not yield the four frozen clusters")
    body = {
        "contract": S3_OVERLAP_CLUSTERS_CONTRACT,
        "schemaVersion": S3_SCHEMA_VERSION,
        "milestone": S3_MILESTONE,
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapRule": "a.start < b.end and b.start < a.end",
        "touchingBoundaryIsOverlap": False,
        "clusterConstruction": "TRANSITIVE_CONNECTED_COMPONENTS",
        "clusters": clusters,
        "outcomeAccessFlags": _outcome_blind_flags(),
    }
    return {**body, "overlapClustersHash": _canonical_hash(body)}


def build_analysis_plan_invariance_audit(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Prove the S3 plan changed no event identity, astronomy, or bridge state."""

    root = Path(resource_root).resolve()
    upstream = load_verified_s2r1_r1_inputs(root)
    prereg = copy.deepcopy(preregistration) if preregistration is not None else build_outcome_analysis_preregistration(root)
    primary_population = copy.deepcopy(population) if population is not None else build_primary_analysis_population(root)
    overlap_clusters = copy.deepcopy(clusters) if clusters is not None else build_overlap_clusters(root, population=primary_population)
    validate_preregistration(prereg)
    freeze_rows = upstream["freeze"]["predictions"]
    coverage_rows = [event for side in upstream["coverage"]["sides"] for event in side["events"]]
    if len(freeze_rows) != len(coverage_rows) != 24:
        raise OutcomeAnalysisS3Error("S3 invariance audit requires all 24 accepted S2R1-R1 records")
    rows = []
    upstream_invariance_by_event = {row["eventId"]: row for row in upstream["invariance"]["rows"]}
    for coverage, prediction in zip(coverage_rows, freeze_rows, strict=True):
        identity_fields = ("eventId", "eventHash", "sideIdentity", "transitBody", "natalTarget", "aspectType", "exactUtc")
        rows.append(
            {
                "eventId": prediction["eventId"],
                "eventHash": prediction["eventHash"],
                "identityUnchanged": all(prediction.get(key) == coverage.get(key) for key in identity_fields),
                "astronomySnapshotUnchanged": prediction.get("astronomySnapshot") == coverage.get("astronomySnapshot"),
                "intervalUnchanged": upstream_invariance_by_event[prediction["eventId"]].get("predictionHash") == prediction.get("eventPredictionHash"),
                "pressureStateUnchanged": upstream_invariance_by_event[prediction["eventId"]].get("predictionHash") == prediction.get("eventPredictionHash"),
                "signedUnit": prediction.get("signedUnit"),
                "magnitudeConfigured": prediction.get("magnitudeConfigured"),
            }
        )
    if not all(row["identityUnchanged"] and row["astronomySnapshotUnchanged"] and row["intervalUnchanged"] and row["pressureStateUnchanged"] for row in rows):
        raise OutcomeAnalysisS3Error("S3 cannot proceed after a frozen identity, interval, or astronomy change")
    if any(row["signedUnit"] is not None or row["magnitudeConfigured"] is not False for row in rows):
        raise OutcomeAnalysisS3Error("S3 cannot proceed if a signed unit or magnitude has been introduced")
    body = {
        "contract": S3_INVARIANCE_AUDIT_CONTRACT,
        "schemaVersion": S3_SCHEMA_VERSION,
        "milestone": S3_MILESTONE,
        "preregistrationHash": prereg["preregistrationHash"],
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapClustersHash": overlap_clusters["overlapClustersHash"],
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "eventRows": rows,
        "summary": {
            "eventCount": 24,
            "usdEventCount": 12,
            "jpyEventCount": 12,
            "singlePassVerifiedCount": 24,
            "allEventIdentitiesUnchanged": True,
            "allAstronomySnapshotsUnchanged": True,
            "allIntervalsUnchanged": True,
            "allPressureStatesRetained": True,
            "directionalCount": 14,
            "supportiveCount": 9,
            "adverseCount": 5,
            "neutralCount": 3,
            "unknownAbstainCount": 7,
            "sourceOperatorDoctrineChanged": False,
            "signedUnitCreated": False,
            "magnitudeCreated": False,
            "marketOutcomeInS3Artifacts": False,
        },
        "outcomeAccessFlags": _outcome_blind_flags(),
    }
    return {**body, "analysisPlanInvarianceAuditHash": _canonical_hash(body)}


def build_acceptance_manifest(
    resource_root: Path = PROJECT_ROOT,
    *,
    preregistration: Mapping[str, Any] | None = None,
    population: Mapping[str, Any] | None = None,
    clusters: Mapping[str, Any] | None = None,
    invariance: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(resource_root).resolve()
    prereg = copy.deepcopy(preregistration) if preregistration is not None else build_outcome_analysis_preregistration(root)
    primary_population = copy.deepcopy(population) if population is not None else build_primary_analysis_population(root)
    overlap_clusters = copy.deepcopy(clusters) if clusters is not None else build_overlap_clusters(root, population=primary_population)
    audit = copy.deepcopy(invariance) if invariance is not None else build_analysis_plan_invariance_audit(root, preregistration=prereg, population=primary_population, clusters=overlap_clusters)
    for payload, key in ((prereg, "preregistrationHash"), (primary_population, "primaryPopulationHash"), (overlap_clusters, "overlapClustersHash"), (audit, "analysisPlanInvarianceAuditHash")):
        if payload.get(key) != _canonical_hash(_without_hash(payload, key)):
            raise OutcomeAnalysisS3Error(f"S3 acceptance cannot bind an invalid {key}")
    body = {
        "contract": S3_ACCEPTANCE_CONTRACT,
        "schemaVersion": S3_SCHEMA_VERSION,
        "milestone": S3_MILESTONE,
        "status": "OUTCOME_ANALYSIS_PREREGISTRATION_COMPLETE_CENTRAL_REVIEW_REQUIRED",
        "nextGate": "INDEPENDENT_CENTRAL_REVIEW_BEFORE_ASTRA_PRE_OUTCOME_AUDIT",
        "startingMaster": S3_EXPECTED_STARTING_MASTER,
        "upstreamHashes": copy.deepcopy(EXPECTED_UPSTREAM_HASHES),
        "preregistrationHash": prereg["preregistrationHash"],
        "primaryPopulationHash": primary_population["primaryPopulationHash"],
        "overlapClustersHash": overlap_clusters["overlapClustersHash"],
        "analysisPlanInvarianceAuditHash": audit["analysisPlanInvarianceAuditHash"],
        "populationAccounting": primary_population["populationCounts"],
        "marketDataSourceFrozenForLaterS4": "DUKASCOPY_HISTORICAL_USDJPY_TICK_SERVICE",
        "marketDataRead": False,
        "outcomeDataRead": False,
        "executionAllowed": False,
        "outcomeAccessFlags": _outcome_blind_flags(),
    }
    return {**body, "acceptanceManifestHash": _canonical_hash(body)}


def _tick_from_mapping(raw: Mapping[str, Any], source_index: int) -> CanonicalTick:
    if not isinstance(raw, Mapping):
        raise SyntheticTickInputError("Synthetic tick must be a mapping")
    timestamp = _parse_utc(raw.get("timestampUtc"), "tick timestampUtc")
    try:
        bid = float(raw.get("bid"))
        ask = float(raw.get("ask"))
    except (TypeError, ValueError) as exc:
        raise SyntheticTickQuoteError("Synthetic tick bid/ask must be numeric") from exc
    if not math.isfinite(bid) or not math.isfinite(ask) or bid <= 0.0 or ask <= 0.0 or ask < bid:
        raise SyntheticTickQuoteError("Synthetic tick bid/ask must be finite positive and ask >= bid")
    return CanonicalTick(timestamp, bid, ask, source_index)


def canonicalize_synthetic_ticks(ticks: Iterable[Mapping[str, Any]]) -> list[CanonicalTick]:
    """Canonical sort/dedup for test-supplied quotes; different same-time quotes retain source order."""

    parsed = [_tick_from_mapping(raw, index) for index, raw in enumerate(ticks)]
    parsed.sort(key=lambda tick: (tick.timestamp_utc, tick.source_index))
    canonical: list[CanonicalTick] = []
    seen_identical: set[tuple[datetime, float, float]] = set()
    for tick in parsed:
        identity = (tick.timestamp_utc, tick.bid, tick.ask)
        if identity in seen_identical:
            continue
        seen_identical.add(identity)
        canonical.append(tick)
    if any(right.timestamp_utc < left.timestamp_utc for left, right in zip(canonical, canonical[1:], strict=False)):
        raise OutcomeAnalysisS3Error("Canonical synthetic tick timestamps must be nondecreasing")
    return canonical


def canonicalize_synthetic_ticks_in_interval(
    ticks: Iterable[Mapping[str, Any]],
    *,
    applying_start_utc: datetime,
    separating_end_utc: datetime,
    reject_conflicts: bool = True,
) -> list[CanonicalTick]:
    """Validate only quotes in a half-open interval while parsing every timestamp.

    A malformed timestamp is an input error even when it would fall outside the
    interval.  Invalid prices and same-time quote conflicts outside the interval
    are irrelevant to this interval and therefore do not poison it.
    """

    materialized = list(ticks)
    parsed: list[CanonicalTick] = []
    for index, raw in enumerate(materialized):
        if not isinstance(raw, Mapping):
            raise SyntheticTickInputError("Synthetic tick must be a mapping")
        try:
            timestamp = _parse_utc(raw.get("timestampUtc"), "tick timestampUtc")
        except OutcomeAnalysisS3Error as exc:
            raise SyntheticTickInputError("tick timestampUtc must be an ISO-8601 UTC timestamp") from exc
        if not applying_start_utc <= timestamp < separating_end_utc:
            continue
        parsed.append(_tick_from_mapping(raw, index))

    parsed.sort(key=lambda tick: (tick.timestamp_utc, tick.source_index))
    canonical: list[CanonicalTick] = []
    seen_identical: set[tuple[datetime, float, float]] = set()
    for tick in parsed:
        identity = (tick.timestamp_utc, tick.bid, tick.ask)
        if identity in seen_identical:
            continue
        seen_identical.add(identity)
        canonical.append(tick)
    if reject_conflicts:
        quotes_by_timestamp: dict[datetime, set[tuple[float, float]]] = {}
        for tick in canonical:
            quotes_by_timestamp.setdefault(tick.timestamp_utc, set()).add((tick.bid, tick.ask))
        conflicts = [timestamp for timestamp, quotes in quotes_by_timestamp.items() if len(quotes) > 1]
        if conflicts:
            raise SyntheticTickConflictError(_utc_text(min(conflicts)))
    return canonical


def _numeric_return_or_invalid(start_tick: CanonicalTick, end_tick: CanonicalTick) -> tuple[float, str | None]:
    """Return a stable log return or a fail-closed numeric reason."""

    start_midpoint = start_tick.midpoint
    end_midpoint = end_tick.midpoint
    if not math.isfinite(start_midpoint) or not math.isfinite(end_midpoint):
        return 0.0, "NONFINITE_DERIVED_MIDPOINT"
    if start_midpoint <= 0.0 or end_midpoint <= 0.0:
        return 0.0, "NONPOSITIVE_DERIVED_MIDPOINT"
    try:
        start_log = math.log(start_midpoint)
        end_log = math.log(end_midpoint)
    except (ValueError, OverflowError) as exc:
        return 0.0, f"LOG_RETURN_DOMAIN_ERROR:{type(exc).__name__}"
    if not math.isfinite(start_log) or not math.isfinite(end_log):
        return 0.0, "NONFINITE_LOG_MIDPOINT"
    log_return = end_log - start_log
    if not math.isfinite(log_return):
        return 0.0, "NONFINITE_LOG_RETURN"
    return log_return, None


def score_synthetic_interval(
    ticks: Iterable[Mapping[str, Any]],
    *,
    applying_start_utc: str,
    separating_end_utc: str,
    validation_expected_pair_direction: str,
) -> dict[str, Any]:
    """Apply S3's frozen interval/tick rules to in-memory synthetic data only."""

    start = _parse_utc(applying_start_utc, "applying_start_utc")
    end = _parse_utc(separating_end_utc, "separating_end_utc")
    if start >= end:
        raise OutcomeAnalysisS3Error("Synthetic interval must be a nonempty half-open UTC range")
    q = _expected_direction_unit(validation_expected_pair_direction)
    try:
        selected = canonicalize_synthetic_ticks_in_interval(
            ticks,
            applying_start_utc=start,
            separating_end_utc=end,
            reject_conflicts=False,
        )
    except SyntheticTickConflictError as exc:
        return {
            "dataStatus": "DATA_CONFLICT_UNSCORABLE",
            "reason": "CONFLICTING_QUOTES_AT_SAME_TIMESTAMP",
            "conflictingTimestampUtc": exc.timestamp_utc,
            "outsideIntervalRescueUsed": False,
        }
    except SyntheticTickQuoteError:
        return {
            "dataStatus": "DATA_NUMERIC_INVALID_UNSCORABLE",
            "reason": "INVALID_IN_INTERVAL_QUOTE",
            "selectedTickCount": 0,
            "outsideIntervalRescueUsed": False,
        }
    if len(selected) < 2:
        return {
            "dataStatus": "DATA_UNSCORABLE",
            "reason": "FEWER_THAN_TWO_VALID_IN_INTERVAL_TICKS",
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    start_tick, end_tick = selected[0], selected[-1]
    if start_tick.timestamp_utc == end_tick.timestamp_utc:
        return {
            "dataStatus": "DATA_UNSCORABLE",
            "reason": "START_AND_END_TICK_SHARE_TIMESTAMP",
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    log_return, numeric_reason = _numeric_return_or_invalid(start_tick, end_tick)
    if numeric_reason is not None:
        return {
            "dataStatus": "DATA_NUMERIC_INVALID_UNSCORABLE",
            "reason": numeric_reason,
            "selectedTickCount": len(selected),
            "outsideIntervalRescueUsed": False,
        }
    realized = "UP" if log_return > 0 else "DOWN" if log_return < 0 else "ZERO_MOVE"
    return {
        "dataStatus": "SCORABLE_SYNTHETIC_ONLY",
        "selectedTickCount": len(selected),
        "startTickUtc": _utc_text(start_tick.timestamp_utc),
        "endTickUtc": _utc_text(end_tick.timestamp_utc),
        "startMidpoint": start_tick.midpoint,
        "endMidpoint": end_tick.midpoint,
        "logReturn": log_return,
        "realizedDirection": realized,
        "hit": int((q * log_return) > 0),
        "startAlignmentGapSeconds": (start_tick.timestamp_utc - start).total_seconds(),
        "endAlignmentGapSeconds": (end - end_tick.timestamp_utc).total_seconds(),
        "outsideIntervalRescueUsed": False,
    }


def enumerate_within_side_label_assignments(primary_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Enumerate the frozen 5*8 side-local SUPPORTIVE/ADVERSE assignments exactly."""

    by_side = {side: [row for row in primary_rows if row["sideIdentity"] == side] for side in ("USD", "JPY")}
    if (len(by_side["USD"]), len(by_side["JPY"])) != (5, 8):
        raise OutcomeAnalysisS3Error("Exact S3 permutation requires 5 USD and 8 JPY primary rows")
    supportive_counts = {side: sum(row["pressureState"] == "SUPPORTIVE" for row in rows) for side, rows in by_side.items()}
    if supportive_counts != {"USD": 1, "JPY": 7}:
        raise OutcomeAnalysisS3Error("Exact S3 permutation requires its frozen side-local label counts")
    side_assignments: list[list[dict[str, str]]] = []
    for side in ("USD", "JPY"):
        rows = by_side[side]
        assignments = []
        for positions in combinations(range(len(rows)), supportive_counts[side]):
            supportive_positions = set(positions)
            assignments.append({row["eventId"]: "SUPPORTIVE" if index in supportive_positions else "ADVERSE" for index, row in enumerate(rows)})
        side_assignments.append(assignments)
    combined = [{**usd, **jpy} for usd, jpy in product(*side_assignments)]
    if len(combined) != 40:
        raise OutcomeAnalysisS3Error("S3 exact assignment universe must contain exactly 40 assignments")
    observed = {row["eventId"]: row["pressureState"] for row in primary_rows}
    if observed not in combined:
        raise OutcomeAnalysisS3Error("Observed frozen assignment must remain in the exact null universe")
    return combined


def exact_one_sided_permutation(
    primary_rows: Sequence[Mapping[str, Any]],
    realized_direction_by_event: Mapping[str, str],
) -> dict[str, Any]:
    """Synthetic-only exact 40-assignment calculation used to test S4 mechanics."""

    expected_ids = {row["eventId"] for row in primary_rows}
    if set(realized_direction_by_event) != expected_ids:
        raise OutcomeAnalysisS3Error("Synthetic realized directions must cover exactly the frozen primary population")
    if any(value not in {"UP", "DOWN", "ZERO_MOVE"} for value in realized_direction_by_event.values()):
        raise OutcomeAnalysisS3Error("Synthetic realized direction must be UP, DOWN, or ZERO_MOVE")
    assignments = enumerate_within_side_label_assignments(primary_rows)

    def count_hits(assignment: Mapping[str, str]) -> int:
        total = 0
        for row in primary_rows:
            direction = _validation_expected_pair_direction(row["sideIdentity"], assignment[row["eventId"]])
            realized = realized_direction_by_event[row["eventId"]]
            total += int(realized != "ZERO_MOVE" and direction == realized)
        return total

    observed_assignment = {row["eventId"]: row["pressureState"] for row in primary_rows}
    observed_hits = count_hits(observed_assignment)
    permutation_hits = [count_hits(assignment) for assignment in assignments]
    histogram = {str(hit_count): permutation_hits.count(hit_count) for hit_count in sorted(set(permutation_hits))}
    return {
        "observedHitCount": observed_hits,
        "permutationHitCounts": permutation_hits,
        "permutationHitHistogram": histogram,
        "assignmentCount": len(assignments),
        "oneSidedPExact": sum(value >= observed_hits for value in permutation_hits) / len(permutation_hits),
        "observedAssignmentIncluded": observed_assignment in assignments,
    }


def cluster_balanced_hit_rate(primary_rows: Sequence[Mapping[str, Any]], hit_by_event: Mapping[str, int]) -> float:
    clusters = derive_overlap_clusters(primary_rows)
    if set(hit_by_event) != {row["eventId"] for row in primary_rows}:
        raise OutcomeAnalysisS3Error("Cluster hit input must cover exactly the frozen primary rows")
    cluster_rates = []
    for cluster in clusters:
        values = [hit_by_event[event_id] for event_id in cluster["memberEventIds"]]
        if any(value not in {0, 1} for value in values):
            raise OutcomeAnalysisS3Error("Cluster hit values must remain binary")
        cluster_rates.append(sum(values) / len(values))
    return sum(cluster_rates) / len(cluster_rates)


def shift_primary_interval(interval: Mapping[str, str], calendar_days: int) -> dict[str, str]:
    if calendar_days not in {-7, 7}:
        raise OutcomeAnalysisS3Error("S3 time-shift diagnostics permit only -7 and +7 calendar days")
    start = _parse_utc(interval["applyingStartUtc"], "shift applyingStartUtc")
    end = _parse_utc(interval["separatingEndUtc"], "shift separatingEndUtc")
    return {
        "applyingStartUtc": _utc_text(start + timedelta(days=calendar_days)),
        "separatingEndUtc": _utc_text(end + timedelta(days=calendar_days)),
    }


def primary_survival_status(
    *,
    all_primary_validly_scorable: bool,
    primary_hit_rate: float | None,
    exact_p_value: float | None,
    cluster_balanced_rate: float | None,
) -> str:
    if not all_primary_validly_scorable:
        return "PRIMARY_EVALUATION_INVALID_DATA_INCOMPLETE"
    if primary_hit_rate is None or exact_p_value is None or cluster_balanced_rate is None:
        raise OutcomeAnalysisS3Error("Scorable S3 primary evaluation requires all preregistered metrics")
    if primary_hit_rate > 0.5 and exact_p_value <= 0.1 and cluster_balanced_rate > 0.5:
        return "PILOT_ASSOCIATION_SURVIVED"
    return "PILOT_ASSOCIATION_NOT_SURVIVED"


def render_outcome_analysis_preregistration_markdown(
    preregistration: Mapping[str, Any],
    population: Mapping[str, Any],
    clusters: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> str:
    """Render a readable S3 plan; never render a market result."""

    counts = population["populationCounts"]
    lines = [
        "# MO-R4A-S3 Outcome Analysis Preregistration",
        "",
        "This is a frozen, outcome-blind analysis plan. It contains no price, tick, candle, return, PnL, market reaction, Founder Review decision, or scored result.",
        "",
        f"Preregistration hash: `{preregistration['preregistrationHash']}`",
        f"Acceptance hash: `{acceptance['acceptanceManifestHash']}`",
        f"Frozen S2R1-R1 prediction hash: `{preregistration['upstreamHashes']['predictionFreezeHash']}`",
        "",
        "## Frozen Population",
        "",
        f"24 frozen identities: 12 USD and 12 JPY. The plan retains {counts['directionalCount']} directional rows, {counts['primaryMarketScorableCount']} primary market-scorable rows, one structural weekend exclusion, {counts['neutralCount']} categorical NEUTRAL rows, and {counts['unknownAbstainCount']} abstentions.",
        "",
        "| Event ID | Side | Frozen state | Validation direction | Primary disposition |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in population["primaryMarketScorableRows"]:
        lines.append(f"| {row['eventId']} | {row['sideIdentity']} | {row['pressureState']} | {row['validationExpectedPairDirection']} | {row['analysisDisposition']} |")
    lines.extend([
        "",
        "The excluded directional row is `TN_BD340A6100B173B5F254EDC1`: its complete primary interval is Saturday UTC. It remains in the 24-event frozen pilot and is never replaced, extended, or scored as zero.",
        "",
        "## Tick Rule",
        "",
        "At the separately authorized outcome phase, the only source is Dukascopy historical USDJPY tick data in UTC. The interval is `[applyingStartUtc, separatingEndUtc)`, with the first valid in-range tick as start and last valid in-range tick as end. Midpoints use `(bid + ask) / 2`; the return is `ln(P_end / P_start)`. S3 does not access that provider or any market file.",
        "",
        "## Exact Test",
        "",
        "The primary test is a one-sided exact label permutation with `C(5,1) * C(8,7) = 40` within-side assignments. It retains event windows and later observed returns, includes the observed assignment, and calculates `p_exact = count(H_perm >= H_observed) / 40`. There is no Monte Carlo, timestamp permutation, cross-side reassignment, or secondary p-value.",
        "",
        "## Overlap Clusters",
        "",
        "| Cluster | Members | Start | End |",
        "| --- | ---: | --- | --- |",
    ])
    for cluster in clusters["clusters"]:
        lines.append(f"| {cluster['clusterId']} | {cluster['memberCount']} | {cluster['earliestStartUtc']} | {cluster['latestEndUtc']} |")
    lines.extend([
        "",
        "The secondary cluster-balanced rate equally weights C1-C4. The time-shift diagnostics use exactly -7 and +7 calendar days, preserve interval duration and UTC clock, and never redefine the primary test.",
        "",
        "## Boundary",
        "",
        "All S3 access flags remain false. No source doctrine is changed; no signed unit, pair resultant, magnitude, score, Auto Suggest, ML, MT5, execution, or production admission is created. Independent central review is required before any Astra pre-outcome audit or provider access.",
        "",
    ])
    return "\n".join(lines)


def materialize_s3_artifacts(
    resource_root: Path = PROJECT_ROOT,
    *,
    outcome_source: object | None = None,
) -> dict[str, Path]:
    """Write only plan artifacts; any outcome attachment is a hard S3 boundary error."""

    if outcome_source is not None:
        raise OutcomeAccessBlockedError("S3 materialization cannot accept a market provider, outcome file, or tick source")
    root = Path(resource_root).resolve()
    preregistration = build_outcome_analysis_preregistration(root)
    validate_preregistration(preregistration)
    population = build_primary_analysis_population(root)
    clusters = build_overlap_clusters(root, population=population)
    invariance = build_analysis_plan_invariance_audit(root, preregistration=preregistration, population=population, clusters=clusters)
    acceptance = build_acceptance_manifest(root, preregistration=preregistration, population=population, clusters=clusters, invariance=invariance)
    artifacts = {
        "preregistration": root / DEFAULT_PREREGISTRATION_PATH.relative_to(PROJECT_ROOT),
        "schema": root / DEFAULT_PREREGISTRATION_SCHEMA_PATH.relative_to(PROJECT_ROOT),
        "population": root / DEFAULT_PRIMARY_POPULATION_PATH.relative_to(PROJECT_ROOT),
        "clusters": root / DEFAULT_OVERLAP_CLUSTERS_PATH.relative_to(PROJECT_ROOT),
        "invariance": root / DEFAULT_INVARIANCE_AUDIT_PATH.relative_to(PROJECT_ROOT),
        "acceptance": root / DEFAULT_ACCEPTANCE_PATH.relative_to(PROJECT_ROOT),
        "report": root / DEFAULT_REPORT_PATH.relative_to(PROJECT_ROOT),
    }
    _write_json(artifacts["preregistration"], preregistration)
    _write_json(artifacts["schema"], build_preregistration_schema())
    _write_json(artifacts["population"], population)
    _write_json(artifacts["clusters"], clusters)
    _write_json(artifacts["invariance"], invariance)
    _write_json(artifacts["acceptance"], acceptance)
    artifacts["report"].parent.mkdir(parents=True, exist_ok=True)
    artifacts["report"].write_text(
        render_outcome_analysis_preregistration_markdown(preregistration, population, clusters, acceptance),
        encoding="utf-8",
    )
    return artifacts
