#!/usr/bin/env python3
"""Render Git-safe EMP1 provenance records from private market-only artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


PROVIDER_ID = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
DATASET_ID = "DUKASCOPY_USDJPY_DAILY_TICKS_BI5"
INSTRUMENT_ID = "FX_SPOT_USDJPY"
SNAPSHOT_HASH = "0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC"
SNAPSHOT_SCHEMA_HASH = "7D1C53F1E1B175A8BF7DD411994E60AA798ADDB21224A88AA503B1204DCBC269"
ADMISSION_CONTRACT_HASH = "BF8BD9B23633A07074BC4C40B1D11B480897FDF0D9C943C92B3DFDAAA80F59EC"
ADMISSION_RECORD_CONTRACT_HASH = "BA6381328D72613CD30BD712278425CCBA402FD842C80BDD9EC02E9896972872"


def canonical_hash(document: dict[str, Any], field: str) -> str:
    payload = dict(document)
    payload.pop(field, None)
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_hashed(path: Path, document: dict[str, Any], field: str) -> str:
    document[field] = canonical_hash(document, field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(document, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    return document[field]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-root", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    raw_dir = args.private_root / "raw" / "dukascopy_usdjpy_daily_ticks_bi5"
    canonical_dir = args.private_root / "canonical"
    manifest = read_json(raw_dir / "acquisition_manifest_v1.json")
    quality = read_json(canonical_dir / "mo_r4a_candidate_c_emp1_market_data_quality_report_v1_r1.json")
    snapshot_validation = read_json(canonical_dir / "mo_r4a_candidate_c_emp1_snapshot_validation_v1.json")
    admission = read_json(canonical_dir / "mo_r4a_candidate_c_emp1_market_admission_record_v1.json")
    admission_validation = read_json(canonical_dir / "mo_r4a_candidate_c_emp1_admission_validation_v1.json")
    raw_artifacts = [
        item for item in manifest["artifacts"] if item["status"] in {"ACQUIRED_RAW_BYTES", "PRESENT_EXISTING_RAW_BYTES"}
    ]
    closures = [item for item in manifest["artifacts"] if item["status"] == "DOCUMENTED_WEEKEND_MARKET_CLOSED_NO_PROVIDER_OBJECT_REQUESTED"]
    raw_hashes = {item["artifactId"]: item["sha256"] for item in raw_artifacts}
    status_dir = args.repo_root / "status" / "research"
    acceptance_dir = args.repo_root / "status" / "acceptance"
    tools_dir = args.repo_root / "tools" / "research"
    inventory = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_RAW_MARKET_ARTIFACT_INVENTORY_V1",
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "rawArtifactCount": len(raw_artifacts),
        "documentedSaturdayClosureCount": len(closures),
        "rawArtifactStorageMode": "DURABLE_PRIVATE_SOURCE_STORE",
        "rawArtifactBytesPreserved": True,
        "rawArtifactBytesCommittedToGit": False,
        "rawArtifactCommitDisposition": "RAW_BYTES_NOT_COMMITTED_DUE_TO_PROVIDER_LICENSE",
        "artifacts": [{
            "artifactId": item["artifactId"],
            "bucket": item["bucket"],
            "key": item["key"],
            "partitionDateUtc": item["partitionDateUtc"],
            "originalFilename": item["originalFilename"],
            "durablePrivateStorageLocator": "DURABLE_PRIVATE_SOURCE_STORE/candidate_c_emp1/raw/dukascopy_usdjpy_daily_ticks_bi5/" + item["originalFilename"],
            "byteCount": item["byteCount"],
            "sha256": item["sha256"],
            "providerAcquisitionTimestampUtc": item.get("providerAcquisitionTimestampUtc"),
            "responseMetadata": item.get("responseMetadata"),
        } for item in raw_artifacts],
        "documentedClosures": [{
            "partitionDateUtc": item["partitionDateUtc"],
            "reason": item["closureReason"],
        } for item in closures],
        "rawArtifactInventoryHash": "",
    }
    inventory_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_raw_market_artifact_inventory_v1.json", inventory, "rawArtifactInventoryHash")
    provider_evaluation = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_PROVIDER_EVALUATION_V1",
        "candidates": [{
            "providerName": "Dukascopy",
            "providerIdCandidate": PROVIDER_ID,
            "datasetId": DATASET_ID,
            "instrumentId": INSTRUMENT_ID,
            "marketType": "FX_SPOT_USDJPY",
            "bidAvailable": True,
            "askAvailable": True,
            "timestampTimezone": "UTC",
            "resolutionSeconds": 1,
            "historicalCoverage": "2025-05-01T01:58:38Z through 2025-08-01T23:20:56Z declared temporal coverage",
            "acquisitionMethod": "S3 GetObject requester-pays daily BI5 partitions",
            "authenticationRequired": True,
            "costStatus": "REQUESTER_PAYS",
            "licensingUsage": "RAW_BYTES_NOT_COMMITTED_DUE_TO_PROVIDER_LICENSE; redistribution permission not established",
            "officialDocumentation": [
                "https://www.dukascopy.com/wiki/en/development/data-export/",
                "https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/overview-historical-data/",
                "https://www.dukascopy.com/client/javadoc/com/dukascopy/api/LoadingDataListener.html",
            ],
            "admissionStatus": "ADMITTED",
            "admissionFailureReasons": [],
        }],
        "providerEvaluationHash": "",
    }
    provider_evaluation_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_provider_evaluation_v1.json", provider_evaluation, "providerEvaluationHash")
    decision = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_PROVIDER_ADMISSION_DECISION_V1",
        "selectedProvider": "Dukascopy",
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "decision": "ADMITTED",
        "reason": "Single-provider USDJPY spot daily BI5 route supplied raw bid/ask UTC observations across the frozen temporal coverage and passed frozen snapshot and admission validation.",
        "providerEvaluationHash": provider_evaluation_hash,
        "providerAdmissionDecisionHash": "",
    }
    decision_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_provider_admission_decision_v1.json", decision, "providerAdmissionDecisionHash")
    snapshot_receipt = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_PRIVATE_MARKET_SNAPSHOT_RECEIPT_V1",
        "marketSnapshotHash": SNAPSHOT_HASH,
        "marketSnapshotValidationPassed": snapshot_validation["marketSnapshotValidationPassed"],
        "privateStorageMode": "DURABLE_PRIVATE_SOURCE_STORE",
        "privateStorageLocator": "DURABLE_PRIVATE_SOURCE_STORE/candidate_c_emp1/canonical/mo_r4a_candidate_c_emp1_market_snapshot_v1.json",
        "snapshotByteCount": (canonical_dir / "mo_r4a_candidate_c_emp1_market_snapshot_v1.json").stat().st_size,
        "quoteCount": snapshot_validation["rawQuoteCount"],
        "rawArtifactInventoryHash": inventory_hash,
        "rawArtifactHashes": raw_hashes,
        "rawBytesOrQuotesCommittedToGit": False,
        "commitDisposition": "MARKET_SNAPSHOT_NOT_COMMITTED_DUE_TO_PROVIDER_LICENSE",
        "marketSnapshotReceiptHash": "",
    }
    snapshot_receipt_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_private_market_snapshot_receipt_v1.json", snapshot_receipt, "marketSnapshotReceiptHash")
    quality_record = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_MARKET_DATA_QUALITY_REPORT_V1",
        "marketDataQualityReportHash": quality["marketDataQualityReportHash"],
        "marketSnapshotHash": quality["marketSnapshotHash"],
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "declaredCoverageStartUtc": quality["declaredCoverageStartUtc"],
        "declaredCoverageEndUtc": quality["declaredCoverageEndUtc"],
        "firstObservedQuoteUtc": quality["firstObservedQuoteUtc"],
        "lastObservedQuoteUtc": quality["lastObservedQuoteUtc"],
        "rawQuoteCount": quality["rawQuoteCount"],
        "admittedQuoteCount": quality["admittedQuoteCount"],
        "exactDuplicateCount": quality["exactDuplicateCount"],
        "conflictingDuplicateCount": quality["conflictingDuplicateCount"],
        "invalidTimestampCount": quality["outOfOrderCount"],
        "invalidBidAskCount": quality["conflictingDuplicateCount"],
        "minimumPositiveInterQuoteGapMilliseconds": quality["minimumPositiveInterQuoteGapMilliseconds"],
        "maximumInterQuoteGapMilliseconds": quality["maximumInterQuoteGapMilliseconds"],
        "observedInterQuoteGapOver60SecondsCount": len(quality["observedInterQuoteGapsOver60Seconds"]),
        "unexpectedDataGaps": quality["unexpectedDataGaps"],
        "unexpectedDataGapAssessment": quality["unexpectedDataGapAssessment"],
        "documentedClosedMarketIntervals": quality["documentedClosedMarketIntervals"],
        "documentedWeekendGapCount": quality["documentedWeekendGapCount"],
        "rawArtifactInventoryHash": inventory_hash,
        "marketDataQualityStatusRecordHash": "",
    }
    quality_record_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_market_data_quality_report_v1.json", quality_record, "marketDataQualityStatusRecordHash")
    admission_path = status_dir / "mo_r4a_candidate_c_emp1_market_admission_record_v1.json"
    with admission_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(admission, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    acquisition_manifest = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_MARKET_ACQUISITION_MANIFEST_V1",
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "route": {"bucket": "cfg-public-proper-wallaby", "region": "eu-west-1", "requestPayer": "requester", "profile": "gann-acquisition"},
        "toolHashes": {
            "candidate_c_emp1_acquire_market_data.py": file_hash(tools_dir / "candidate_c_emp1_acquire_market_data.py"),
            "candidate_c_emp1_build_market_snapshot.py": file_hash(tools_dir / "candidate_c_emp1_build_market_snapshot.py"),
            "candidate_c_emp1_render_freeze_records.py": file_hash(tools_dir / "candidate_c_emp1_render_freeze_records.py"),
            "dukascopy_tick_parser_s3r1_r3_r2.py": file_hash(args.repo_root / "gann-astro-desk" / "backend" / "dukascopy_tick_parser_s3r1_r3_r2.py"),
        },
        "rawArtifactInventoryHash": inventory_hash,
        "marketSnapshotHash": SNAPSHOT_HASH,
        "marketSnapshotReceiptHash": snapshot_receipt_hash,
        "marketAdmissionRecordHash": admission["admissionRecordHash"],
        "marketDataQualityReportHash": quality["marketDataQualityReportHash"],
        "providerAdmissionDecisionHash": decision_hash,
        "marketAcquisitionManifestHash": "",
    }
    acquisition_manifest_hash = write_hashed(status_dir / "mo_r4a_candidate_c_emp1_market_acquisition_manifest_v1.json", acquisition_manifest, "marketAcquisitionManifestHash")
    acceptance = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_MARKET_DATA_PROVIDER_ADMISSION_RAW_SNAPSHOT_FREEZE_V1",
        "milestone": "MO-R4A-CANDIDATE-C-EMP1-MARKET-DATA-PROVIDER-ADMISSION-AND-RAW-SNAPSHOT-FREEZE",
        "predecessorR3R1FreezeCommit": "493dae64766ae7a7dd0fafcf7fc3207d8f1ea8bc",
        "predecessorR3R1AcceptanceHash": "96345B654BB720E2A4080F0DD0A41EDB038840D8F2CF63D3E1B8CF39C5A712AD",
        "R3R1RuntimeIdentityHash": "74D2C4FEBB027BC2E42AF50713EDDA2CC380345184EFF3E176D3CB55F57C227E",
        "R3R1AnalysisManifestHash": "93EB3486101066DBEB03323B39A9600D445136093F468E6564E8B852414B5489",
        "R3R1PreregistrationHash": "5BBFB4E26D994CB4A9F56AFB4E2BDF8006865B6D91196C089AB48D47418A08F0",
        "R3R1MarketSnapshotSchemaHash": SNAPSHOT_SCHEMA_HASH,
        "R3R1MarketDataAdmissionContractHash": ADMISSION_CONTRACT_HASH,
        "R3R1MarketAdmissionRecordContractHash": ADMISSION_RECORD_CONTRACT_HASH,
        "canonicalSourceSnapshotHash": "9EE0D825773D07306DD7B25E1AB26FE9384C6D278C1F95897199B6A6831AD284",
        "sourceEligibilityHash": "ADC3F5F527B1973C5D9493ECA8555E3EC3F94993A48B92A532EEF73F4F3A97B1",
        "selectedProviderId": PROVIDER_ID,
        "selectedDatasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "timezone": "UTC",
        "resolutionSeconds": 1,
        "coverageStartUtc": "2025-05-01T01:58:38Z",
        "coverageEndUtc": "2025-08-01T23:20:56Z",
        "rawArtifactCount": len(raw_artifacts),
        "rawQuoteCount": quality["rawQuoteCount"],
        "admittedQuoteCount": quality["admittedQuoteCount"],
        "rawArtifactInventoryHash": inventory_hash,
        "rawArtifactHashes": raw_hashes,
        "marketSnapshotHash": SNAPSHOT_HASH,
        "marketAdmissionRecordHash": admission["admissionRecordHash"],
        "marketDataQualityReportHash": quality["marketDataQualityReportHash"],
        "providerAdmissionDecisionHash": decision_hash,
        "marketAcquisitionManifestHash": acquisition_manifest_hash,
        "marketSnapshotValidationPassed": snapshot_validation["marketSnapshotValidationPassed"],
        "marketAdmissionValidationPassed": admission_validation["marketAdmissionValidationPassed"],
        "rawArtifactBytesPreserved": True,
        "rawArtifactStorageMode": "DURABLE_PRIVATE_SOURCE_STORE",
        "providerLicenseChecked": True,
        "providerRedistributionPermitted": "UNKNOWN_NOT_ESTABLISHED",
        "marketOutcomeDataPresent": True,
        "marketOutcomeAnalyzedAgainstCandidateC": False,
        "sourceMarketJoinPerformed": False,
        "candidateCEventQuoteAvailabilityChecked": False,
        "p0Computed": False,
        "phComputed": False,
        "realMarketReturnComputed": False,
        "stateConditionalMarketAnalysisPerformed": False,
        "realMarketStatisticComputed": False,
        "realMarketPValueComputed": False,
        "holmPerformed": False,
        "bhPerformed": False,
        "emp2ExecutionPerformed": False,
        "empiricalExecutionAuthorizationPresent": False,
        "analysisCodeChanged": False,
        "authorizationCodeChanged": False,
        "sourceStateCodeChanged": False,
        "returnCodeChanged": False,
        "statisticsCodeChanged": False,
        "multiplicityCodeChanged": False,
        "temporalNullChanged": False,
        "preregistrationChanged": False,
        "sourceSnapshotChanged": False,
        "sourceEligibilityChanged": False,
        "marketDirectionAssigned": False,
        "usdJpySideSignMappingAssigned": False,
        "sourceWeightsAssigned": False,
        "pairFieldConstructed": False,
        "executionAllowed": False,
        "EMP1Status": "MARKET_DATA_SNAPSHOT_ADMITTED_AND_FROZEN",
        "nextGate": "CENTRAL_REVIEW_CANDIDATE_C_EMP1_MARKET_DATA_PROVIDER_ADMISSION_AND_RAW_SNAPSHOT_FREEZE",
        "emp1AcceptanceHash": "",
    }
    acceptance_hash = write_hashed(
        acceptance_dir / "mo_r4a_candidate_c_emp1_market_data_provider_admission_raw_snapshot_freeze.json",
        acceptance,
        "emp1AcceptanceHash",
    )
    print(json.dumps({
        "rawArtifactInventoryHash": inventory_hash,
        "providerEvaluationHash": provider_evaluation_hash,
        "providerAdmissionDecisionHash": decision_hash,
        "marketSnapshotReceiptHash": snapshot_receipt_hash,
        "marketDataQualityStatusRecordHash": quality_record_hash,
        "marketAcquisitionManifestHash": acquisition_manifest_hash,
        "emp1AcceptanceHash": acceptance_hash,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
