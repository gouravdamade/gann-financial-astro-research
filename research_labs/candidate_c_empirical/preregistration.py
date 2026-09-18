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
EMP0_R2_MILESTONE = "MO-R4A-CANDIDATE-C-EMP0-R2-PRE-DATA-SNAPSHOT-INTEGRITY-AUTHORIZATION-AND-TEST-CELL-CLOSURE"
EMP0_R1_FREEZE_COMMIT = "eabe9cb983aa42f3f7b8375edb92a68de571c678"


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


def render_emp0_r2_artifacts(root: Path | str, implementation_commit: str) -> dict[str, Any]:
    """Freeze R2 integrity contracts without opening a market snapshot or provider."""

    base = Path(root).resolve()
    snapshot = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json")
    eligibility = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json")
    predecessor = _read_json(base / "status/acceptance/mo_r4a_candidate_c_emp0_r1_pre_data_analysis_path_and_temporal_null_closure_v1.json")
    if snapshot["canonicalSourceStateSnapshotHash"] != "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284" or snapshot["populationEventCount"] != 645 or snapshot["canonicalSourceStateRowCount"] != 5160:
        raise ValueError("historical Candidate C source snapshot changed")
    if eligibility["sourceStateEligibilityHash"] != "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1" or len(eligibility["cells"]) != 16 or sum(cell["sourceTestable"] for cell in eligibility["cells"]) != 8:
        raise ValueError("historical Candidate C source eligibility changed")
    market_schema = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_MARKET_SNAPSHOT_SCHEMA_V1", "milestone": EMP0_R2_MILESTONE,
        "requiredFields": ["providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds", "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount", "quotes", "marketSnapshotHash"],
        "instrumentId": "FX_SPOT_USDJPY", "timezone": "UTC", "resolutionSecondsRange": [1, 60],
        "coverageStartMaximumUtc": "2025-05-01T01:58:38Z", "coverageEndMinimumUtc": "2025-08-01T23:20:56Z",
        "quoteCountMeaning": "RAW_QUOTES_ARRAY_LENGTH_BEFORE_EXACT_DUPLICATE_NORMALIZATION",
        "admittedQuoteCountMeaning": "DERIVED_COUNT_AFTER_IDENTICAL_TIMESTAMP_BID_ASK_NORMALIZATION",
        "rawArtifactHashesRequired": True, "marketSnapshotCanonicalSelfHashRequired": True,
        "canonicalHashField": "marketSnapshotHash", "duplicatePolicy": "IDENTICAL_DEDUPLICATE_CONFLICT_REJECT", "marketSnapshotSchemaHash": None,
    }, "marketSnapshotSchemaHash")
    market_contract = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_MARKET_DATA_ADMISSION_CONTRACT_V1", "milestone": EMP0_R2_MILESTONE,
        "instrumentId": "FX_SPOT_USDJPY", "providerSelected": False, "marketDataAcquisitionAllowed": False,
        "requiredCoverageStartUtc": "2025-05-01T01:58:38Z", "requiredCoverageEndUtc": "2025-08-01T23:20:56Z", "requiredResolutionSecondsMaximum": 60,
        "requiredQuoteFields": ["timestampUtc", "bid", "ask"], "requiredProviderEvidence": ["providerIdentity", "datasetProductIdentity", "rawArtifactHashes", "licensingUsageMetadata", "acquisitionTimestamp"],
        "marketDataAdmissionContractHash": None,
    }, "marketDataAdmissionContractHash")
    admission_record_contract = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_MARKET_ADMISSION_RECORD_CONTRACT_V1", "milestone": EMP0_R2_MILESTONE,
        "requiredFields": ["schemaVersion", "admissionId", "admitted", "marketSnapshotHash", "providerId", "datasetId", "instrumentId", "coverageStartUtc", "coverageEndUtc", "resolutionSeconds", "rawArtifactHashes", "emp0R2MarketSnapshotSchemaHash", "emp0R2MarketDataAdmissionContractHash", "admissionRecordHash"],
        "admissionRecordCanonicalSelfHashRequired": True, "realMarketAdmissionRecordPresent": False, "marketAdmissionRecordContractHash": None,
    }, "marketAdmissionRecordContractHash")
    temporal = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_TEMPORAL_NULL_CONTRACT_V1", "contractId": "CANDIDATE_C_EMP0_R1_WITHIN_SIDE_WITHIN_UTC_MONTH_CIRCULAR_SHIFT_V2",
        "blockDefinition": "SINGLE_SIDE_X_SINGLE_ROW_SLOT_X_UTC_MONTH", "monthOrdering": "LEXICAL_YYYY_MM", "eventOrdering": "EXACT_UTC_THEN_EVENT_ID",
        "individualOffsetDomain": "0_TO_M_MINUS_1", "individualMonthZeroOffsetAllowed": True, "globalIdentityTransformAllowed": False,
        "globalIdentityRejection": "DETERMINISTIC_FULL_VECTOR_REGENERATION_WITH_ATTEMPT_INDEX", "maxIdentityRejectionAttempts": 100000,
        "permutationCount": 4999, "pValueRule": "ONE_PLUS_EXCEEDANCES_DIVIDED_BY_5000", "returnsShifted": False, "stateLabelsShifted": True,
        "withinMonthStateCountsPreserved": True, "semanticNullDistributionChanged": False, "safetyBoundAdded": True, "temporalNullContractHash": None,
    }, "temporalNullContractHash")
    testable_cells = sorted((cell for cell in eligibility["cells"] if cell["sourceTestable"]), key=lambda cell: (cell["sideIdentity"], cell["canonicalRowSlotId"]))
    ledger_entries = [{"sideIdentity": cell["sideIdentity"], "canonicalRowSlotId": cell["canonicalRowSlotId"], "horizonSeconds": horizon, "horizonRole": "PRIMARY_CONFIRMATORY" if horizon == 86400 else "SECONDARY_EXPLORATORY", "status": "PENDING_MARKET_ADMISSION"} for cell in testable_cells for horizon in (3600, 21600, 86400)]
    ledger = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_FUTURE_TEST_LEDGER_CONTRACT_V1", "sourceTestableCellCount": 8,
        "allowedHorizonSeconds": [3600, 21600, 86400], "futureTestLedgerEntryCount": 24, "entries": ledger_entries,
        "statusEnum": ["PENDING_MARKET_ADMISSION", "EXECUTED", "INSUFFICIENT_MARKET_ELIGIBLE_SAMPLE", "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE", "NO_NONTRIVIAL_TEMPORAL_SHIFT_AVAILABLE", "TEMPORAL_NULL_GENERATION_FAILURE", "MARKET_QUOTE_UNAVAILABLE_FOR_ALL_ELIGIBLE_STATES", "MARKET_DATA_SNAPSHOT_INVALID"],
        "testLedgerContractHash": None,
    }, "testLedgerContractHash")
    execution = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_EMPIRICAL_EXECUTION_CONTRACT_V1", "milestone": EMP0_R2_MILESTONE,
        "sequence": ["VERIFY_FREEZE_BINDING", "VERIFY_SOURCE_SNAPSHOT", "VERIFY_SOURCE_ELIGIBILITY", "VERIFY_MARKET_SNAPSHOT", "VERIFY_ADMISSION_RECORD", "VERIFY_VALIDATED_AUTHORIZATION", "BUILD_FROZEN_TEST_LEDGER", "EXECUTE_24H_PRIMARY", "EXECUTE_1H_6H_SECONDARY", "APPLY_FROZEN_MULTIPLICITY", "FREEZE_FIRST_RESULT", "STOP"],
        "providerRequeryAllowed": False, "EMP1AnalysisCodeChangesAllowed": False, "EMP2AnalysisCodeChangesAllowed": False,
        "EMP1SourceStateChangesAllowed": False, "EMP2SourceStateChangesAllowed": False, "EMP2PreregistrationChangesAllowed": False,
        "EMP2TemporalNullChangesAllowed": False, "EMP2MultiplicityChangesAllowed": False, "empiricalExecutionContractHash": None,
    }, "empiricalExecutionContractHash")
    preregistration = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_MARKET_ASSOCIATION_PREREGISTRATION_V1", "milestone": EMP0_R2_MILESTONE,
        "supersedesPreregistrationHash": "A5AD430B92C67303170FD36A08C2212121C44F2F7A3240D4045A2F651D02B0DC",
        "supersessionReason": "PRE_DATA_SNAPSHOT_INTEGRITY_AUTHORIZATION_AND_TEST_CELL_CLOSURE", "outcomeDataSeenBeforeSupersession": False,
        "providerSelectedBeforeSupersession": False, "marketSnapshotPresentBeforeSupersession": False,
        "researchQuestion": "For each eligible sideIdentity x rowSlot, do mean forward USDJPY log returns differ across frozen categorical Candidate C VALUE states?",
        "unknownSourceDisposition": "ABSTAIN_NOT_MARKET_FEATURE", "minStateCount": 20, "minTotalTestCount": 60, "instrumentId": "FX_SPOT_USDJPY",
        "priceDefinition": "MID_BID_ASK", "p0Rule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_WITHIN_60_SECONDS", "phRule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_PLUS_HORIZON_WITHIN_60_SECONDS", "quoteToleranceSeconds": 60, "returnDefinition": "LN_PH_OVER_P0",
        "primaryHorizonSeconds": 86400, "secondaryHorizonSeconds": [3600, 21600], "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "permutationCount": 4999,
        "temporalNullContractHash": temporal["temporalNullContractHash"], "primaryMultiplicity": {"method": "HOLM_BONFERRONI", "alpha": 0.05}, "secondaryMultiplicity": {"method": "BENJAMINI_HOCHBERG", "q": 0.10},
        "marketDirectionAssigned": False, "sourceWeightsAssigned": False, "usdJpySideSignMappingAssigned": False, "pairFieldConstructed": False, "marketOutcomeRead": False, "realMarketStatisticalExecutionAllowed": False,
        "marketAssociationPreregistrationHash": None,
    }, "marketAssociationPreregistrationHash")
    package = base / "research_labs/candidate_c_empirical"
    source_files = ["market_contract.py", "returns.py", "statistics.py", "multiplicity.py", "authorization.py", "execution.py", "preregistration.py"]
    manifest = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_ANALYSIS_IMPLEMENTATION_MANIFEST_V1", "milestone": EMP0_R2_MILESTONE, "implementationCommit": implementation_commit,
        "hashConvention": HASH_CONVENTION, "implementationHashes": {name: _file_hash(package / name) for name in source_files}, "testSourceHash": _file_hash(package / "test_emp0.py"),
        "marketProviderImports": [], "marketFileDiscoveryImplemented": False, "validatedAuthorizationTypeRequired": True, "analysisImplementationManifestHash": None,
    }, "analysisImplementationManifestHash")
    authorization = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_EMPIRICAL_AUTHORIZATION_CONTRACT_V1", "milestone": EMP0_R2_MILESTONE,
        "requiredFields": ["schemaVersion", "authorizationId", "authorized", "authorizationRecordHash", "EMP0R2ImplementationCommit", "EMP0R2FreezeCommit", "EMP0R2AnalysisImplementationManifestHash", "EMP0R2PreregistrationHash", "EMP0R2TemporalNullContractHash", "EMP0R2EmpiricalExecutionContractHash", "canonicalSourceStateSnapshotHash", "sourceStateEligibilityHash", "marketSnapshotHash", "marketAdmissionRecordHash", "marketSnapshotSchemaHash", "marketDataAdmissionContractHash", "instrumentId", "allowedHorizonSeconds", "permutationCount", "primaryStatistic", "primaryMultiplicity", "primaryAlpha", "secondaryMultiplicity", "secondaryQ", "oneShotExecutionIntent", "marketOutcomeAccess", "providerRequeryAllowed", "postHocTuningAllowed", "sourceEligibilityChangesAllowed", "newHorizonsAllowed"],
        "plainMappingAuthorizationAllowed": False, "validatedAuthorizationTypeRequired": True, "authorizationCanonicalSelfHashRequired": True, "oneShotExecutionRequired": True,
        "marketSnapshotBindingRequired": True, "marketAdmissionBindingRequired": True, "sourceSnapshotBindingRequired": True, "sourceEligibilityBindingRequired": True, "preregistrationBindingRequired": True, "temporalNullBindingRequired": True,
        "empiricalExecutionAuthorizationPresent": False, "empiricalExecutionAuthorized": False, "empiricalAuthorizationContractHash": None,
    }, "empiricalAuthorizationContractHash")
    acceptance = _hashed({
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R2_PRE_DATA_SNAPSHOT_INTEGRITY_AUTHORIZATION_TEST_CELL_FREEZE_V1", "milestone": EMP0_R2_MILESTONE,
        "predecessorEmp0R1FreezeCommit": EMP0_R1_FREEZE_COMMIT, "implementationCommit": implementation_commit, "historicalSourceSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"], "historicalSourceEligibilityHash": eligibility["sourceStateEligibilityHash"],
        "predecessorEmp0R1PreregistrationHash": "A5AD430B92C67303170FD36A08C2212121C44F2F7A3240D4045A2F651D02B0DC", "successorPreregistrationHash": preregistration["marketAssociationPreregistrationHash"],
        "marketSnapshotSchemaHash": market_schema["marketSnapshotSchemaHash"], "marketDataAdmissionContractHash": market_contract["marketDataAdmissionContractHash"], "marketAdmissionRecordContractHash": admission_record_contract["marketAdmissionRecordContractHash"], "temporalNullContractHash": temporal["temporalNullContractHash"], "empiricalAuthorizationContractHash": authorization["empiricalAuthorizationContractHash"], "empiricalExecutionContractHash": execution["empiricalExecutionContractHash"], "analysisImplementationManifestHash": manifest["analysisImplementationManifestHash"], "testLedgerContractHash": ledger["testLedgerContractHash"],
        "populationEventCount": 645, "canonicalSourceStateRowCount": 5160, "sourceTestableCellCount": 8, "futureTestLedgerEntryCount": 24, "allowedHorizonSeconds": [3600, 21600, 86400], "singleSidePerTestRequired": True, "singleRowSlotPerTestRequired": True, "unregisteredHorizonAllowed": False,
        "marketSnapshotCanonicalSelfHashRequired": True, "rawArtifactHashesRequired": True, "quoteCountMeansRawQuoteArrayLength": True, "coverageIntegrityRequired": True, "marketAdmissionRecordRequired": True, "plainMappingAuthorizationAllowed": False, "validatedAuthorizationTypeRequired": True, "authorizationCanonicalSelfHashRequired": True, "marketSnapshotBindingRequired": True, "marketAdmissionBindingRequired": True, "sourceSnapshotBindingRequired": True, "sourceEligibilityBindingRequired": True, "preregistrationBindingRequired": True, "temporalNullBindingRequired": True, "oneShotExecutionRequired": True,
        "temporalNullSemanticDistributionChanged": False, "individualMonthZeroOffsetAllowed": True, "globalIdentityTransformAllowed": False, "maxIdentityRejectionAttempts": 100000, "permutationCount": 4999, "primaryHorizonSeconds": 86400, "secondaryHorizonSeconds": [3600, 21600], "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "primaryMultiplicity": "HOLM_BONFERRONI", "primaryAlpha": 0.05, "secondaryMultiplicity": "BENJAMINI_HOCHBERG", "secondaryQ": 0.10,
        "EMP1AnalysisCodeChangesAllowed": False, "EMP2AnalysisCodeChangesAllowed": False, "providerSelected": False, "marketDataAcquisitionAllowed": False, "marketSnapshotPresent": False, "marketAdmissionRecordPresent": False, "marketOutcomeRead": False, "realMarketReturnComputed": False, "realMarketStatisticComputed": False, "realMarketPValueComputed": False, "realMarketStatisticalExecutionAllowed": False, "empiricalExecutionAuthorizationPresent": False, "empiricalExecutionAuthorized": False, "sourceWeightsAssigned": False, "marketDirectionAssigned": False, "usdJpySideSignMappingAssigned": False, "executionAllowed": False,
        "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP0_R2_PRE_DATA_SNAPSHOT_INTEGRITY_AUTHORIZATION_AND_TEST_CELL_CLOSURE", "acceptanceRecordHash": None,
    }, "acceptanceRecordHash")
    documents = {
        base / "status/research/mo_r4a_candidate_c_emp0_r2_market_snapshot_schema_v1.json": market_schema,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_market_data_admission_contract_v1.json": market_contract,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_market_admission_record_contract_v1.json": admission_record_contract,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_temporal_null_contract_v1.json": temporal,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_future_test_ledger_contract_v1.json": ledger,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_empirical_execution_contract_v1.json": execution,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_market_association_preregistration_v1.json": preregistration,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_analysis_implementation_manifest_v1.json": manifest,
        base / "status/research/mo_r4a_candidate_c_emp0_r2_empirical_authorization_contract_v1.json": authorization,
        base / "status/acceptance/mo_r4a_candidate_c_emp0_r2_pre_data_snapshot_integrity_authorization_test_cell_freeze.json": acceptance,
    }
    for path, document in documents.items():
        _write(path, document)
    return {"schema": market_schema, "marketContract": market_contract, "admissionContract": admission_record_contract, "temporal": temporal, "ledger": ledger, "execution": execution, "preregistration": preregistration, "manifest": manifest, "authorization": authorization, "acceptance": acceptance, "predecessor": predecessor}


def render_emp0_r3_artifacts(root: Path | str, implementation_commit: str) -> dict[str, Any]:
    """Freeze EMP0-R3 runtime contracts without reading provider or outcome data."""

    base = Path(root).resolve()
    snapshot = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_canonical_source_state_snapshot_v1.json")
    eligibility = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_source_state_eligibility_v1.json")
    r2_preregistration = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_r2_market_association_preregistration_v1.json")
    r2_ledger = _read_json(base / "status/research/mo_r4a_candidate_c_emp0_r2_future_test_ledger_contract_v1.json")
    if snapshot["canonicalSourceStateSnapshotHash"] != "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284":
        raise ValueError("historical Candidate C source snapshot changed")
    if eligibility["sourceStateEligibilityHash"] != "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1":
        raise ValueError("historical Candidate C source eligibility changed")
    if r2_ledger["testLedgerContractHash"] != "91322F3A5759A6BDDA3C87CDDFDDC3A70F9E27A58CC15327AEA45F1C04B0DDAA":
        raise ValueError("historical Candidate C future ledger changed")
    milestone = "MO-R4A-CANDIDATE-C-EMP0-R3-PRE-DATA-END-TO-END-EXECUTION-BINDING-AND-IMMUTABILITY-CLOSURE"
    market_schema = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_MARKET_SNAPSHOT_SCHEMA_V1", "milestone": milestone, "instrumentId": "FX_SPOT_USDJPY", "timezone": "UTC", "resolutionSecondsRange": [1, 60], "requiredFields": ["providerId", "datasetId", "instrumentId", "timezone", "resolutionSeconds", "coverageStartUtc", "coverageEndUtc", "rawArtifactHashes", "quoteCount", "quotes", "marketSnapshotHash"], "deepValidatedQuoteType": "FrozenMarketQuote", "rawArtifactHashesImmutable": True, "marketSnapshotSchemaHash": None}, "marketSnapshotSchemaHash")
    market_contract = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_MARKET_DATA_ADMISSION_CONTRACT_V1", "milestone": milestone, "instrumentId": "FX_SPOT_USDJPY", "providerSelected": False, "marketDataAcquisitionAllowed": False, "requiredCoverageStartUtc": "2025-05-01T01:58:38Z", "requiredCoverageEndUtc": "2025-08-01T23:20:56Z", "requiredResolutionSecondsMaximum": 60, "requiredQuoteFields": ["timestampUtc", "bid", "ask"], "marketDataAdmissionContractHash": None}, "marketDataAdmissionContractHash")
    admission_contract = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_MARKET_ADMISSION_RECORD_CONTRACT_V1", "milestone": milestone, "requiredFields": ["admissionId", "admitted", "marketSnapshotHash", "providerId", "datasetId", "instrumentId", "coverageStartUtc", "coverageEndUtc", "resolutionSeconds", "rawArtifactHashes", "emp0R3MarketSnapshotSchemaHash", "emp0R3MarketDataAdmissionContractHash", "admissionRecordHash"], "admissionRecordCanonicalSelfHashRequired": True, "marketAdmissionRecordContractHash": None}, "marketAdmissionRecordContractHash")
    temporal = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_TEMPORAL_NULL_CONTRACT_V1", "contractId": "CANDIDATE_C_EMP0_R1_WITHIN_SIDE_WITHIN_UTC_MONTH_CIRCULAR_SHIFT_V2", "blockDefinition": "SINGLE_SIDE_X_SINGLE_ROW_SLOT_X_UTC_MONTH", "individualMonthZeroOffsetAllowed": True, "globalIdentityTransformAllowed": False, "maxIdentityRejectionAttempts": 100000, "permutationCount": 4999, "pValueRule": "ONE_PLUS_EXCEEDANCES_DIVIDED_BY_5000", "returnsShifted": False, "stateLabelsShifted": True, "temporalNullContractHash": None}, "temporalNullContractHash")
    result_schema = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_EMP2_RESULT_SCHEMA_V1", "milestone": milestone, "relativeResultPath": "status/research/mo_r4a_candidate_c_emp2_market_association_result_v1.json", "resultSelfHashRequired": True, "firstResultOverwriteAllowed": False, "testLedgerEntryCount": 24, "primaryFamily": "HOLM_BONFERRONI_ALL_EXECUTED_86400", "secondaryFamily": "BENJAMINI_HOCHBERG_ALL_EXECUTED_3600_21600", "interpretationBoundary": "EMPIRICAL_ASSOCIATION_DISCOVERY_NOT_FORECAST_OR_TRADING_VALIDATION", "resultSchemaHash": None}, "resultSchemaHash")
    execution = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_EMPIRICAL_EXECUTION_CONTRACT_V1", "milestone": milestone, "sequence": ["VERIFY_RUNTIME_IDENTITY", "VERIFY_SOURCE_SNAPSHOT", "VERIFY_SOURCE_ELIGIBILITY", "VERIFY_MARKET_SNAPSHOT", "VERIFY_MARKET_ADMISSION", "DERIVE_AUTHORIZATION_EXPECTED_BINDINGS", "VERIFY_EXTERNAL_AUTHORIZATION", "VERIFY_FIRST_RESULT_ABSENT", "LOAD_FROZEN_TEST_LEDGER", "DERIVE_RETURNS", "APPLY_MARKET_SAMPLE_GATES", "EXECUTE_PRIMARY_TESTS", "EXECUTE_SECONDARY_TESTS", "APPLY_HOLM", "APPLY_BH", "BUILD_RESULT", "VERIFY_RESULT_SELF_HASH", "ATOMIC_FIRST_RESULT_WRITE", "STOP"], "providerRequeryAllowed": False, "sourceEligibilityChangesAllowed": False, "newSourceStatesAllowed": False, "newHorizonsAllowed": False, "postHocTuningAllowed": False, "scientificRetriesAllowed": False, "empiricalExecutionContractHash": None}, "empiricalExecutionContractHash")
    preregistration = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_MARKET_ASSOCIATION_PREREGISTRATION_V1", "milestone": milestone, "supersedesPreregistrationHash": r2_preregistration["marketAssociationPreregistrationHash"], "supersessionReason": "PRE_DATA_END_TO_END_EXECUTION_BINDING_AND_IMMUTABILITY_CLOSURE", "outcomeDataSeenBeforeSupersession": False, "providerSelectedBeforeSupersession": False, "marketSnapshotPresentBeforeSupersession": False, "researchQuestion": r2_preregistration["researchQuestion"], "unknownSourceDisposition": "ABSTAIN_NOT_MARKET_FEATURE", "minStateCount": 20, "minTotalTestCount": 60, "instrumentId": "FX_SPOT_USDJPY", "priceDefinition": "MID_BID_ASK", "p0Rule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_WITHIN_60_SECONDS", "phRule": "FIRST_QUOTE_AT_OR_AFTER_EVENT_PLUS_HORIZON_WITHIN_60_SECONDS", "quoteToleranceSeconds": 60, "returnDefinition": "LN_PH_OVER_P0", "primaryHorizonSeconds": 86400, "secondaryHorizonSeconds": [3600, 21600], "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "permutationCount": 4999, "temporalNullContractHash": temporal["temporalNullContractHash"], "primaryMultiplicity": {"method": "HOLM_BONFERRONI", "alpha": 0.05}, "secondaryMultiplicity": {"method": "BENJAMINI_HOCHBERG", "q": 0.10}, "marketDirectionAssigned": False, "sourceWeightsAssigned": False, "usdJpySideSignMappingAssigned": False, "pairFieldConstructed": False, "marketOutcomeRead": False, "realMarketStatisticalExecutionAllowed": False, "marketAssociationPreregistrationHash": None}, "marketAssociationPreregistrationHash")
    package = base / "research_labs/candidate_c_empirical"
    files = ["canonical.py", "market_contract.py", "returns.py", "statistics.py", "multiplicity.py", "authorization.py", "execution.py", "runtime.py", "artifact.py", "preregistration.py"]
    manifest = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_ANALYSIS_IMPLEMENTATION_MANIFEST_V1", "milestone": milestone, "implementationCommit": implementation_commit, "hashConvention": HASH_CONVENTION, "implementationHashes": {name: _file_hash(package / name) for name in files}, "testSourceHashes": {name: _file_hash(package / name) for name in ["test_emp0.py", "test_emp0_r3.py"]}, "marketProviderImports": [], "marketFileDiscoveryImplemented": False, "marketNetworkAccessImplemented": False, "analysisImplementationManifestHash": None}, "analysisImplementationManifestHash")
    authorization = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_EMPIRICAL_AUTHORIZATION_CONTRACT_V1", "milestone": milestone, "supersessionReason": "AUTHORIZATION_BINDING_ARCHITECTURE_CORRECTION_PRE_DATA", "expectedBindingsDerivedFromVerifiedRuntime": True, "callerSuppliedExpectedBindingsAllowed": False, "publicExecutionAcceptsValidatedTokenDirectly": False, "publicExecutionRevalidatesRawAuthorization": True, "requiredFields": ["EMP0R3ImplementationCommit", "EMP0R3AcceptanceRecordHash", "EMP0R3AnalysisImplementationManifestHash", "EMP0R3PreregistrationHash", "EMP0R3TemporalNullContractHash", "EMP0R3EmpiricalExecutionContractHash", "EMP0R3ResultSchemaHash", "EMP0R3TestLedgerContractHash", "canonicalSourceStateSnapshotHash", "sourceStateEligibilityHash", "marketSnapshotHash", "marketAdmissionRecordHash"], "empiricalExecutionAuthorizationPresent": False, "empiricalExecutionAuthorized": False, "empiricalAuthorizationContractHash": None}, "empiricalAuthorizationContractHash")
    runtime = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_RUNTIME_IDENTITY_CONTRACT_V1", "implementationCommit": implementation_commit, "analysisManifestHash": manifest["analysisImplementationManifestHash"], "preregistrationHash": preregistration["marketAssociationPreregistrationHash"], "temporalNullContractHash": temporal["temporalNullContractHash"], "executionContractHash": execution["empiricalExecutionContractHash"], "authorizationContractHash": authorization["empiricalAuthorizationContractHash"], "resultSchemaHash": result_schema["resultSchemaHash"], "testLedgerContractHash": r2_ledger["testLedgerContractHash"], "marketSnapshotSchemaHash": market_schema["marketSnapshotSchemaHash"], "marketDataAdmissionContractHash": market_contract["marketDataAdmissionContractHash"], "marketAdmissionRecordContractHash": admission_contract["marketAdmissionRecordContractHash"], "canonicalSourceStateSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"], "sourceStateEligibilityHash": eligibility["sourceStateEligibilityHash"], "implementationFileHashes": manifest["implementationHashes"], "runtimeIdentityContractHash": None}, "runtimeIdentityContractHash")
    acceptance = _hashed({"schemaVersion": "MO_R4A_CANDIDATE_C_EMP0_R3_PRE_DATA_END_TO_END_EXECUTION_BINDING_IMMUTABILITY_FREEZE_V1", "milestone": milestone, "predecessorEmp0R2FreezeCommit": "7f8c5a1572f1ac637d03d34fa8cc1ecbe0f969b7", "implementationCommit": implementation_commit, "historicalSourceSnapshotHash": snapshot["canonicalSourceStateSnapshotHash"], "historicalSourceEligibilityHash": eligibility["sourceStateEligibilityHash"], "predecessorEmp0R2PreregistrationHash": r2_preregistration["marketAssociationPreregistrationHash"], "successorPreregistrationHash": preregistration["marketAssociationPreregistrationHash"], "analysisImplementationManifestHash": manifest["analysisImplementationManifestHash"], "runtimeIdentityContractHash": runtime["runtimeIdentityContractHash"], "marketSnapshotSchemaHash": market_schema["marketSnapshotSchemaHash"], "marketDataAdmissionContractHash": market_contract["marketDataAdmissionContractHash"], "marketAdmissionRecordContractHash": admission_contract["marketAdmissionRecordContractHash"], "temporalNullContractHash": temporal["temporalNullContractHash"], "empiricalAuthorizationContractHash": authorization["empiricalAuthorizationContractHash"], "empiricalExecutionContractHash": execution["empiricalExecutionContractHash"], "testLedgerContractHash": r2_ledger["testLedgerContractHash"], "emp2ResultSchemaHash": result_schema["resultSchemaHash"], "deepValidatedMarketSnapshotImmutable": True, "validatedQuotesImmutable": True, "runtimeExpectedBindingsRepositoryDerived": True, "callerSuppliedExpectedBindingsAllowed": False, "publicExecutionAcceptsValidatedAuthorizationObjectDirectly": False, "publicExecutionRevalidatesRawAuthorization": True, "sourceEligibilityDerivedFromFrozenArtifact": True, "callerSuppliedEligibleStatesAllowed": False, "marketSampleGateEnforcedInsideExecution": True, "full24EntryOrchestratorFrozen": True, "holmAppliedInsideOrchestrator": True, "bhAppliedInsideOrchestrator": True, "firstResultAtomicWriteFrozen": True, "firstResultOverwriteAllowed": False, "populationEventCount": 645, "canonicalSourceStateRowCount": 5160, "sourceTestableCellCount": 8, "futureTestLedgerEntryCount": 24, "minStateCount": 20, "minTotalTestCount": 60, "allowedHorizonSeconds": [3600, 21600, 86400], "primaryHorizonSeconds": 86400, "secondaryHorizonSeconds": [3600, 21600], "permutationCount": 4999, "maxIdentityRejectionAttempts": 100000, "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE", "primaryMultiplicity": "HOLM_BONFERRONI", "primaryAlpha": 0.05, "secondaryMultiplicity": "BENJAMINI_HOCHBERG", "secondaryQ": 0.10, "providerSelected": False, "marketDataAcquisitionAllowed": False, "marketSnapshotPresent": False, "marketAdmissionRecordPresent": False, "marketOutcomeRead": False, "realMarketReturnComputed": False, "realMarketStatisticComputed": False, "realMarketPValueComputed": False, "realMarketStatisticalExecutionAllowed": False, "empiricalExecutionAuthorizationPresent": False, "empiricalExecutionAuthorized": False, "executionAllowed": False, "marketDirectionAssigned": False, "usdJpySideSignMappingAssigned": False, "sourceWeightsAssigned": False, "pairFieldConstructed": False, "EMP1AnalysisCodeChangesAllowed": False, "EMP1AuthorizationCodeChangesAllowed": False, "EMP1SourceStateChangesAllowed": False, "EMP2AnalysisCodeChangesAllowed": False, "EMP2AuthorizationCodeChangesAllowed": False, "EMP2SourceStateChangesAllowed": False, "EMP2PreregistrationChangesAllowed": False, "EMP2TemporalNullChangesAllowed": False, "EMP2MultiplicityChangesAllowed": False, "EMP2ReturnContractChangesAllowed": False, "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP0_R3_PRE_DATA_END_TO_END_EXECUTION_BINDING_AND_IMMUTABILITY_CLOSURE", "acceptanceRecordHash": None}, "acceptanceRecordHash")
    documents = {"status/research/mo_r4a_candidate_c_emp0_r3_market_snapshot_schema_v1.json": market_schema, "status/research/mo_r4a_candidate_c_emp0_r3_market_data_admission_contract_v1.json": market_contract, "status/research/mo_r4a_candidate_c_emp0_r3_market_admission_record_contract_v1.json": admission_contract, "status/research/mo_r4a_candidate_c_emp0_r3_temporal_null_contract_v1.json": temporal, "status/research/mo_r4a_candidate_c_emp0_r3_emp2_result_schema_v1.json": result_schema, "status/research/mo_r4a_candidate_c_emp0_r3_empirical_execution_contract_v1.json": execution, "status/research/mo_r4a_candidate_c_emp0_r3_market_association_preregistration_v1.json": preregistration, "status/research/mo_r4a_candidate_c_emp0_r3_analysis_implementation_manifest_v1.json": manifest, "status/research/mo_r4a_candidate_c_emp0_r3_empirical_authorization_contract_v1.json": authorization, "status/research/mo_r4a_candidate_c_emp0_r3_runtime_identity_contract_v1.json": runtime, "status/acceptance/mo_r4a_candidate_c_emp0_r3_pre_data_end_to_end_execution_binding_immutability_freeze.json": acceptance}
    for relative, document in documents.items():
        _write(base / relative, document)
    return {"marketSchema": market_schema, "marketContract": market_contract, "admissionContract": admission_contract, "temporal": temporal, "resultSchema": result_schema, "execution": execution, "preregistration": preregistration, "manifest": manifest, "authorization": authorization, "runtime": runtime, "acceptance": acceptance}
