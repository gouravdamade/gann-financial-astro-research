"""Render EMP0 source-only records and future market contracts without price data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .canonical import HASH_CONVENTION, canonical_json_bytes, self_hash
from .source_state import build_source_state_eligibility, build_source_state_snapshot


EMP0_MILESTONE = "MO-R4A-CANDIDATE-C-EMP0-OUTCOME-BLIND-MARKET-TEST-PREREGISTRATION-AND-ANALYSIS-FREEZE"
STARTING_COMMIT = "a2fec654d7c6ea0d72b79d9ee11c39fdaf20c6ea"
EMP0_R1_MILESTONE = "MO-R4A-CANDIDATE-C-EMP0-R1-PRE-DATA-REAL-ANALYSIS-PATH-AND-TEMPORAL-NULL-CLOSURE"
EMP0_HISTORICAL_FREEZE_COMMIT = "91a501c78613ad5c83dd95013cbba83387cdd041"
EMP0_HISTORICAL_FREEZE_HASH = "215BDD5803F48D8755307599853F14FE3EFC710D6EE7D5C87870CCB4A62C344F"


def _hashed(document: dict[str, Any], field: str) -> dict[str, Any]:
    document[field] = self_hash(document, field)
    return document


def _write(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(document))


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def market_data_admission_contract() -> dict[str, Any]:
    return _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_MARKET_DATA_ADMISSION_CONTRACT_V1",
        "instrumentId": "FX_SPOT_USDJPY",
        "providerSelected": False,
        "marketDataAcquisitionAllowed": False,
        "requiredProviderEvidence": ["providerIdentity", "datasetProductIdentity", "instrumentIdentity", "bidAskAvailability", "resolutionAtMost60Seconds", "utcTimestampSemantics", "coverage", "rawDataImmutability", "licensingUsageMetadata", "acquisitionTimestamp", "rawFileHashes"],
        "requiredCoverageStartUtc": "2025-05-01T01:58:38Z",
        "requiredCoverageEndUtc": "2025-08-01T23:20:56Z",
        "requiredResolutionSecondsMaximum": 60,
        "requiredQuoteFields": ["timestampUtc", "bid", "ask"],
        "midOnlySufficient": False,
        "marketDataAdmissionContractHash": None,
    }, "marketDataAdmissionContractHash")


def market_snapshot_schema() -> dict[str, Any]:
    return _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_MARKET_SNAPSHOT_SCHEMA_V1",
        "instrumentId": "FX_SPOT_USDJPY",
        "requiredFields": ["providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds", "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount", "quotes"],
        "quoteRequiredFields": ["timestampUtc", "bid", "ask"],
        "timestampPolicy": "UNAMBIGUOUS_UTC_ONLY",
        "duplicatePolicy": "IDENTICAL_TIMESTAMP_BID_ASK_DEDUPLICATE;_CONFLICTING_TIMESTAMP_REJECT",
        "containsActualQuotes": False,
        "marketSnapshotSchemaHash": None,
    }, "marketSnapshotSchemaHash")


def market_association_preregistration() -> dict[str, Any]:
    return _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_MARKET_ASSOCIATION_PREREGISTRATION_V1",
        "milestone": EMP0_MILESTONE,
        "researchQuestion": "For each eligible sideIdentity x rowSlot, do mean forward USDJPY log returns differ across frozen categorical Candidate C VALUE states?",
        "sourceInputs": "IMMUTABLE_AUTH1_A_B_OUTPUTS_PROJECTED_BY_FROZEN_V2",
        "stateTokenRule": {"VALUE": {"outputStatus": "VALUE", "sourceValue": "V2_CANONICAL_SOURCE_VALUE"}, "UNKNOWN": "SOURCE_UNKNOWN_ABSTAIN"},
        "unknownSourceDisposition": "ABSTAIN_NOT_MARKET_FEATURE",
        "minStateCount": 20,
        "minTotalTestCount": 60,
        "instrumentId": "FX_SPOT_USDJPY",
        "priceDefinition": "MID_BID_ASK",
        "p0Rule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_WITHIN_60_SECONDS",
        "phRule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_PLUS_HORIZON_WITHIN_60_SECONDS",
        "quoteToleranceSeconds": 60,
        "returnDefinition": "LN_PH_OVER_P0",
        "primaryHorizonSeconds": 86400,
        "secondaryHorizonSeconds": [3600, 21600],
        "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE",
        "zeroVarianceDisposition": "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE",
        "permutationMethod": "WITHIN_SIDE_WITHIN_UTC_MONTH_DETERMINISTIC_CIRCULAR_STATE_SHIFT",
        "permutationCount": 4999,
        "deterministicOffset": "SHA256(contractId|sideIdentity|canonicalRowSlotId|horizonSeconds|YYYY-MM|replicateIndex); 1 + digest mod (m - 1), or 0 when m <= 1",
        "primaryMultiplicity": {"method": "HOLM_BONFERRONI", "alpha": 0.05},
        "secondaryMultiplicity": {"method": "BENJAMINI_HOCHBERG", "q": 0.10},
        "usdJpySideSignMappingAssigned": False,
        "marketDirectionAssigned": False,
        "sourceWeightsAssigned": False,
        "pairFieldConstructed": False,
        "realMarketStatisticalExecutionAllowed": False,
        "marketOutcomeRead": False,
        "interpretationBoundary": "EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION",
        "marketAssociationPreregistrationHash": None,
    }, "marketAssociationPreregistrationHash")


def render_emp0_artifacts(root: Path | str, implementation_commit: str) -> dict[str, Any]:
    """Create source-only EMP0 freeze artifacts. No market snapshot is accepted here."""

    base = Path(root).resolve()
    snapshot = build_source_state_snapshot(base)
    eligibility = build_source_state_eligibility(snapshot)
    closure = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_SOURCE_REPRODUCTION_PHASE_CLOSURE_V1",
        "milestone": "MO-R4A-CANDIDATE-C-SOURCE-REPRODUCTION-PHASE-CLOSURE",
        "auth1R1Commit": STARTING_COMMIT,
        "auth1ResultCommit": "874636c8c4cc26cd6875ef6bd8f9f2cc46251b02",
        "auth1FreezeCommit": "985271d33f294f674e1dbc4d24fb5ca7231d7166",
        "authorizationRecordHash": "FC28DD7FE00FF010CFBECD672CDDB27F269AE45BBCD1C6531A42099807621705",
        "aArtifactSelfHash": snapshot["auth1AArtifactHash"],
        "bArtifactSelfHash": snapshot["auth1BArtifactHash"],
        "comparisonArtifactSelfHash": snapshot["auth1ComparisonHash"],
        "comparisonResult": "REAL_SOURCE_REPRODUCTION_SEMANTIC_AGREEMENT",
        "populationEventCount": 645, "rowsPerEvaluator": 5160, "semanticRowsCompared": 5160,
        "totalMismatches": 0, "candidateCSourceReproductionPhaseStatus": "CLOSED",
        "sourceReproductionRerunRequired": False, "sourceReproductionRerunAuthorized": False,
        "marketValidationEstablished": False, "forecastValidationEstablished": False,
        "sourceReproductionPhaseClosureHash": None,
    }, "sourceReproductionPhaseClosureHash")
    admission, schema, preregistration = market_data_admission_contract(), market_snapshot_schema(), market_association_preregistration()
    package = base / "research_labs/candidate_c_empirical"
    source_files = ["source_state.py", "market_contract.py", "returns.py", "statistics.py", "multiplicity.py", "preregistration.py"]
    tests = base / "research_labs/candidate_c_empirical/test_emp0.py"
    manifest = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_ANALYSIS_IMPLEMENTATION_MANIFEST_V1",
        "implementationCommit": implementation_commit,
        "hashConvention": HASH_CONVENTION,
        "implementationHashes": {name: _file_hash(package / name) for name in source_files},
        "testSourceHash": _file_hash(tests),
        "v2ProtectedImplementationCommit": "52c3b287a70018370e153a77b84c36e6b0dbfb42",
        "v2SemanticProjectionHash": "1DDFC3B79EC30913254A2FEA117A97EA1761E42D8681EB5D2CB6B2D698187BED",
        "v2ProjectionBlobHash": "4B4828FF09494EA3EAE8ACF57B0004177E6507B8ED8A198871F861E60C2AAF5E",
        "marketProviderImports": [],
        "realMarketStatisticalExecutionAllowed": False,
        "analysisImplementationManifestHash": None,
    }, "analysisImplementationManifestHash")
    acceptance = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_OUTCOME_BLIND_MARKET_PREREGISTRATION_FREEZE_V1",
        "milestone": EMP0_MILESTONE, "startingCommit": STARTING_COMMIT, "implementationCommit": implementation_commit,
        "sourceReproductionPhaseClosureHash": closure["sourceReproductionPhaseClosureHash"],
        "auth1AArtifactHash": snapshot["auth1AArtifactHash"], "auth1BArtifactHash": snapshot["auth1BArtifactHash"], "auth1ComparisonHash": snapshot["auth1ComparisonHash"],
        "v2ProtectedImplementationCommit": manifest["v2ProtectedImplementationCommit"], "v2SemanticProjectionHash": manifest["v2SemanticProjectionHash"], "v2ProjectionBlobHash": manifest["v2ProjectionBlobHash"],
        "populationEventCount": 645, "populationHash": snapshot["populationHash"], "populationOrderHash": snapshot["populationOrderHash"],
        "firstEventUtc": "2025-05-01T01:58:38Z", "lastEventUtc": "2025-07-31T23:19:56Z",
        "canonicalSourceStateRowCount": 5160, "canonicalSourceStateSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"], "sourceStateEligibilityHash": eligibility["sourceStateEligibilityHash"],
        "minStateCount": 20, "minTotalTestCount": 60, "primaryInstrument": "FX_SPOT_USDJPY", "primaryHorizonSeconds": 86400, "secondaryHorizonSeconds": [3600, 21600], "quoteToleranceSeconds": 60, "priceDefinition": "MID_BID_ASK", "returnDefinition": "LN_PH_OVER_P0", "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "permutationMethod": "WITHIN_SIDE_WITHIN_UTC_MONTH_DETERMINISTIC_CIRCULAR_STATE_SHIFT", "permutationCount": 4999, "primaryMultiplicity": "HOLM_BONFERRONI", "primaryAlpha": 0.05, "secondaryMultiplicity": "BENJAMINI_HOCHBERG", "secondaryQ": 0.10, "unknownSourceDisposition": "ABSTAIN_NOT_MARKET_FEATURE",
        "usdJpySideSignMappingAssigned": False, "marketDirectionAssigned": False, "sourceWeightsAssigned": False, "providerSelected": False, "marketDataAcquisitionAllowed": False, "marketDataSnapshotPresent": False, "marketOutcomeRead": False, "realMarketStatisticalExecutionAllowed": False, "sourceOutputRead": True, "analysisCodeFrozenBeforeMarketData": True,
        "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP0_OUTCOME_BLIND_MARKET_TEST_PREREGISTRATION", "acceptanceRecordHash": None,
    }, "acceptanceRecordHash")
    documents = {
        base / "status/acceptance/mo_r4a_candidate_c_source_reproduction_phase_closure_v1.json": closure,
        base / "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json": snapshot,
        base / "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json": eligibility,
        base / "status/research/mo_r4a_candidate_c_emp0_market_data_admission_contract_v1.json": admission,
        base / "status/research/mo_r4a_candidate_c_emp0_market_snapshot_schema_v1.json": schema,
        base / "status/research/mo_r4a_candidate_c_emp0_market_association_preregistration_v1.json": preregistration,
        base / "status/research/mo_r4a_candidate_c_emp0_analysis_implementation_manifest_v1.json": manifest,
        base / "status/acceptance/mo_r4a_candidate_c_emp0_outcome_blind_market_preregistration_freeze.json": acceptance,
    }
    for path, document in documents.items():
        _write(path, document)
    return {"snapshot": snapshot, "eligibility": eligibility, "closure": closure, "admission": admission, "schema": schema, "preregistration": preregistration, "manifest": manifest, "acceptance": acceptance}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_emp0_r1_artifacts(root: Path | str, implementation_commit: str) -> dict[str, Any]:
    """Render successor records without rewriting the historical EMP0 freeze."""

    base = Path(root).resolve()
    historical = _read_json(base / "status/acceptance/mo_r4a_candidate_c_emp0_outcome_blind_market_preregistration_freeze.json")
    snapshot = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json")
    eligibility = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json")
    admission = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R1_MARKET_DATA_ADMISSION_CONTRACT_V1",
        "milestone": EMP0_R1_MILESTONE,
        "historicalEmp0FreezeCommit": EMP0_HISTORICAL_FREEZE_COMMIT,
        "historicalEmp0FreezeHash": EMP0_HISTORICAL_FREEZE_HASH,
        "instrumentId": "FX_SPOT_USDJPY",
        "providerSelected": False,
        "marketDataAcquisitionAllowed": False,
        "providerIndependentValidationCoreFrozen": True,
        "futureImmutableSnapshotAuthorizationRequired": True,
        "requiredProviderEvidence": ["providerIdentity", "datasetProductIdentity", "instrumentIdentity", "bidAskAvailability", "resolutionAtMost60Seconds", "utcTimestampSemantics", "coverage", "rawDataImmutability", "licensingUsageMetadata", "acquisitionTimestamp", "rawFileHashes"],
        "requiredCoverageStartUtc": "2025-05-01T01:58:38Z",
        "requiredCoverageEndUtc": "2025-08-01T23:20:56Z",
        "requiredResolutionSecondsMaximum": 60,
        "requiredQuoteFields": ["timestampUtc", "bid", "ask"],
        "midOnlySufficient": False,
        "marketDataAdmissionContractHash": None,
    }, "marketDataAdmissionContractHash")
    schema = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R1_MARKET_SNAPSHOT_SCHEMA_V1",
        "milestone": EMP0_R1_MILESTONE,
        "instrumentId": "FX_SPOT_USDJPY",
        "providerIdentityRule": "NON_EMPTY_FUTURE_ADMITTED_PROVIDER_IDENTITY",
        "datasetIdentityRule": "NON_EMPTY_FUTURE_IMMUTABLE_DATASET_IDENTITY",
        "requiredFields": ["providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds", "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount", "quotes"],
        "quoteRequiredFields": ["timestampUtc", "bid", "ask"],
        "timestampPolicy": "UNAMBIGUOUS_UTC_ONLY",
        "duplicatePolicy": "IDENTICAL_TIMESTAMP_BID_ASK_DEDUPLICATE;_CONFLICTING_TIMESTAMP_REJECT",
        "containsActualQuotes": False,
        "marketSnapshotSchemaHash": None,
    }, "marketSnapshotSchemaHash")
    preregistration = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R1_MARKET_ASSOCIATION_PREREGISTRATION_V1",
        "milestone": EMP0_R1_MILESTONE,
        "historicalEmp0FreezeHash": EMP0_HISTORICAL_FREEZE_HASH,
        "researchQuestion": "For each eligible sideIdentity x rowSlot, do mean forward USDJPY log returns differ across frozen categorical Candidate C VALUE states?",
        "sourceInputs": "IMMUTABLE_AUTH1_A_B_OUTPUTS_PROJECTED_BY_FROZEN_V2",
        "unknownSourceDisposition": "ABSTAIN_NOT_MARKET_FEATURE",
        "minStateCount": 20,
        "minTotalTestCount": 60,
        "instrumentId": "FX_SPOT_USDJPY",
        "priceDefinition": "MID_BID_ASK",
        "p0Rule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_WITHIN_60_SECONDS",
        "phRule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_PLUS_HORIZON_WITHIN_60_SECONDS",
        "quoteToleranceSeconds": 60,
        "returnDefinition": "LN_PH_OVER_P0",
        "primaryHorizonSeconds": 86400,
        "secondaryHorizonSeconds": [3600, 21600],
        "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE",
        "zeroVarianceDisposition": "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE",
        "permutationMethod": "WITHIN_SIDE_WITHIN_UTC_MONTH_DETERMINISTIC_CIRCULAR_STATE_SHIFT_V2",
        "permutationCount": 4999,
        "temporalNull": {
            "monthlyOffsetRule": "SHA256(contractId|sideIdentity|canonicalRowSlotId|horizonSeconds|YYYY-MM|replicateIndex|attemptIndex) mod m",
            "monthlyZeroOffsetAllowed": True,
            "globalAllZeroJointOffsetExcluded": True,
            "allZeroResolution": "INCREMENT_ATTEMPT_INDEX_DETERMINISTICALLY_UNTIL_AT_LEAST_ONE_MONTH_SHIFTS",
            "observedArrangementAccounting": "OBSERVED_ARRANGEMENT_SEPARATELY_COUNTED_BY_PLUS_ONE_P_VALUE_CORRECTION",
        },
        "primaryMultiplicity": {"method": "HOLM_BONFERRONI", "alpha": 0.05},
        "secondaryMultiplicity": {"method": "BENJAMINI_HOCHBERG", "q": 0.10},
        "usdJpySideSignMappingAssigned": False,
        "marketDirectionAssigned": False,
        "sourceWeightsAssigned": False,
        "pairFieldConstructed": False,
        "realMarketStatisticalExecutionAllowed": False,
        "marketOutcomeRead": False,
        "interpretationBoundary": "EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION",
        "marketAssociationPreregistrationHash": None,
    }, "marketAssociationPreregistrationHash")
    package = base / "research_labs/candidate_c_empirical"
    source_files = ["source_state.py", "market_contract.py", "returns.py", "statistics.py", "multiplicity.py", "preregistration.py"]
    manifest = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R1_ANALYSIS_IMPLEMENTATION_MANIFEST_V1",
        "milestone": EMP0_R1_MILESTONE,
        "implementationCommit": implementation_commit,
        "hashConvention": HASH_CONVENTION,
        "implementationHashes": {name: _file_hash(package / name) for name in source_files},
        "testSourceHash": _file_hash(package / "test_emp0.py"),
        "marketProviderImports": [],
        "providerIndependentValidationCoreFrozen": True,
        "genericStatisticalCoreFrozen": True,
        "futureExecutionAuthorizationRequired": True,
        "realMarketStatisticalExecutionAllowed": False,
        "analysisImplementationManifestHash": None,
    }, "analysisImplementationManifestHash")
    acceptance = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R1_PRE_DATA_ANALYSIS_PATH_AND_TEMPORAL_NULL_CLOSURE_V1",
        "milestone": EMP0_R1_MILESTONE,
        "startingCommit": EMP0_HISTORICAL_FREEZE_COMMIT,
        "implementationCommit": implementation_commit,
        "historicalEmp0FreezePreserved": True,
        "historicalEmp0FreezeHash": historical["acceptanceRecordHash"],
        "canonicalSourceStateSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"],
        "sourceStateEligibilityHash": eligibility["sourceStateEligibilityHash"],
        "marketDataAdmissionContractHash": admission["marketDataAdmissionContractHash"],
        "marketSnapshotSchemaHash": schema["marketSnapshotSchemaHash"],
        "marketAssociationPreregistrationHash": preregistration["marketAssociationPreregistrationHash"],
        "analysisImplementationManifestHash": manifest["analysisImplementationManifestHash"],
        "providerIndependentAnalysisPathFrozen": True,
        "temporalNullCorrected": True,
        "marketDataAcquisitionAllowed": False,
        "providerSelected": False,
        "marketDataSnapshotPresent": False,
        "marketOutcomeRead": False,
        "realMarketStatisticalExecutionAllowed": False,
        "executionAllowed": False,
        "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP0_R1_PRE_DATA_REAL_ANALYSIS_PATH_AND_TEMPORAL_NULL_CLOSURE",
        "acceptanceRecordHash": None,
    }, "acceptanceRecordHash")
    documents = {
        base / "status/research/mo_r4a_candidate_c_emp0_r1_market_data_admission_contract_v1.json": admission,
        base / "status/research/mo_r4a_candidate_c_emp0_r1_market_snapshot_schema_v1.json": schema,
        base / "status/research/mo_r4a_candidate_c_emp0_r1_market_association_preregistration_v1.json": preregistration,
        base / "status/research/mo_r4a_candidate_c_emp0_r1_analysis_implementation_manifest_v1.json": manifest,
        base / "status/acceptance/mo_r4a_candidate_c_emp0_r1_pre_data_analysis_path_and_temporal_null_closure_v1.json": acceptance,
    }
    for path, document in documents.items():
        _write(path, document)
    return {"admission": admission, "schema": schema, "preregistration": preregistration, "manifest": manifest, "acceptance": acceptance}
