"""Canonical, immutable authorization validation for a future EMP2 run."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import self_hash


class EmpiricalAuthorizationError(ValueError):
    """Raised when a future empirical authorization is not exactly bound."""


_AUTHORIZATION_REQUIRED_FIELDS = frozenset({
    "schemaVersion", "authorizationId", "authorized", "authorizationRecordHash",
    "EMP0R3R1ImplementationCommit", "EMP0R3R1AcceptanceRecordHash", "EMP0R3R1AnalysisImplementationManifestHash",
    "EMP0R3R1PreregistrationHash", "EMP0R3R1TemporalNullContractHash", "EMP0R3R1EmpiricalExecutionContractHash",
    "EMP0R3R1ResultSchemaHash", "EMP0R3R1TestLedgerContractHash", "canonicalSourceStateSnapshotHash",
    "sourceStateEligibilityHash", "marketSnapshotHash", "marketAdmissionRecordHash", "marketSnapshotSchemaHash",
    "marketDataAdmissionContractHash", "marketAdmissionRecordContractHash", "instrumentId", "allowedHorizonSeconds",
    "permutationCount", "primaryStatistic", "primaryMultiplicity", "primaryAlpha", "secondaryMultiplicity",
    "secondaryQ", "oneShotExecutionIntent", "marketOutcomeAccess", "providerRequeryAllowed", "postHocTuningAllowed",
    "sourceEligibilityChangesAllowed", "newHorizonsAllowed", "newSourceStatesAllowed",
})


@dataclass(frozen=True)
class _EmpiricalAuthorizationExpectedBindings:
    emp0_r3_r1_implementation_commit: str
    emp0_r3_r1_acceptance_record_hash: str
    analysis_implementation_manifest_hash: str
    preregistration_hash: str
    temporal_null_contract_hash: str
    empirical_execution_contract_hash: str
    result_schema_hash: str
    test_ledger_contract_hash: str
    canonical_source_state_snapshot_hash: str
    source_state_eligibility_hash: str
    market_snapshot_hash: str
    market_admission_record_hash: str
    market_snapshot_schema_hash: str
    market_data_admission_contract_hash: str
    market_admission_record_contract_hash: str


@dataclass(frozen=True)
class _ValidatedEmpiricalAuthorization:
    authorization_id: str
    authorization_record_hash: str
    bindings: _EmpiricalAuthorizationExpectedBindings


def _validate_empirical_execution_authorization(
    record: Mapping[str, Any],
    expected: _EmpiricalAuthorizationExpectedBindings,
) -> _ValidatedEmpiricalAuthorization:
    """Convert only a verified canonical authorization into an immutable type."""

    missing = sorted(_AUTHORIZATION_REQUIRED_FIELDS - set(record))
    if missing:
        raise EmpiricalAuthorizationError(f"EMPIRICAL_AUTHORIZATION_INVALID: missing fields {missing}")
    extras = sorted(set(record) - _AUTHORIZATION_REQUIRED_FIELDS)
    if extras:
        raise EmpiricalAuthorizationError(f"EMPIRICAL_AUTHORIZATION_INVALID: unregistered fields {extras}")
    expected_hash = record["authorizationRecordHash"]
    if not isinstance(expected_hash, str) or self_hash(dict(record), "authorizationRecordHash") != expected_hash:
        raise EmpiricalAuthorizationError("EMPIRICAL_AUTHORIZATION_INVALID: authorizationRecordHash mismatch")
    if record["authorized"] is not True or record["oneShotExecutionIntent"] is not True or record["marketOutcomeAccess"] is not True:
        raise EmpiricalAuthorizationError("EMPIRICAL_AUTHORIZATION_INVALID: required authorization switches are not true")
    for field in ("providerRequeryAllowed", "postHocTuningAllowed", "sourceEligibilityChangesAllowed", "newHorizonsAllowed", "newSourceStatesAllowed"):
        if record[field] is not False:
            raise EmpiricalAuthorizationError(f"EMPIRICAL_AUTHORIZATION_INVALID: {field} must be false")
    required_values = {
        "EMP0R3R1ImplementationCommit": expected.emp0_r3_r1_implementation_commit,
        "EMP0R3R1AcceptanceRecordHash": expected.emp0_r3_r1_acceptance_record_hash,
        "EMP0R3R1AnalysisImplementationManifestHash": expected.analysis_implementation_manifest_hash,
        "EMP0R3R1PreregistrationHash": expected.preregistration_hash,
        "EMP0R3R1TemporalNullContractHash": expected.temporal_null_contract_hash,
        "EMP0R3R1EmpiricalExecutionContractHash": expected.empirical_execution_contract_hash,
        "EMP0R3R1ResultSchemaHash": expected.result_schema_hash,
        "EMP0R3R1TestLedgerContractHash": expected.test_ledger_contract_hash,
        "canonicalSourceStateSnapshotHash": expected.canonical_source_state_snapshot_hash,
        "sourceStateEligibilityHash": expected.source_state_eligibility_hash,
        "marketSnapshotHash": expected.market_snapshot_hash,
        "marketAdmissionRecordHash": expected.market_admission_record_hash,
        "marketSnapshotSchemaHash": expected.market_snapshot_schema_hash,
        "marketDataAdmissionContractHash": expected.market_data_admission_contract_hash,
        "marketAdmissionRecordContractHash": expected.market_admission_record_contract_hash,
        "instrumentId": "FX_SPOT_USDJPY",
        "allowedHorizonSeconds": [3600, 21600, 86400],
        "permutationCount": 4999,
        "primaryStatistic": "BETWEEN_STATE_EXPLAINED_VARIANCE",
        "primaryMultiplicity": "HOLM_BONFERRONI",
        "primaryAlpha": 0.05,
        "secondaryMultiplicity": "BENJAMINI_HOCHBERG",
        "secondaryQ": 0.10,
    }
    for field, value in required_values.items():
        if record[field] != value:
            raise EmpiricalAuthorizationError(f"EMPIRICAL_AUTHORIZATION_INVALID: {field} binding mismatch")
    if not isinstance(record["authorizationId"], str) or not record["authorizationId"].strip():
        raise EmpiricalAuthorizationError("EMPIRICAL_AUTHORIZATION_INVALID: authorizationId must be non-empty")
    return _ValidatedEmpiricalAuthorization(record["authorizationId"], expected_hash, expected)
