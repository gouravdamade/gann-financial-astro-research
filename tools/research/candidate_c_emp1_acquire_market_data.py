#!/usr/bin/env python3
"""Acquire the EMP1 USDJPY daily BI5 partitions without source-state access.

This utility is intentionally outside the frozen Candidate C empirical runtime.
It uses the single centrally approved Dukascopy requester-pays route, preserves
successful response bytes unchanged, and emits only market/provenance metadata.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


PROVIDER_ID = "DUKASCOPY_HISTORICAL_PRICE_DATA_S3_REQUESTER_PAYS_DAILY_BI5_OBJECT_STORE"
DATASET_ID = "DUKASCOPY_USDJPY_DAILY_TICKS_BI5"
BUCKET = "cfg-public-proper-wallaby"
PROFILE = "gann-acquisition"
INSTRUMENT_ID = "FX_SPOT_USDJPY"
START_DATE = date(2025, 5, 1)
END_DATE = date(2025, 8, 1)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def date_key(day: date) -> str:
    return f"USDJPY/{day.year:04d}/{day.month - 1:02d}/{day.day:02d}_ticks.bi5"


def artifact_id(day: date) -> str:
    return f"DUKASCOPY_USDJPY_{day:%Y%m%d}_TICKS_BI5"


def artifact_name(day: date) -> str:
    return f"USDJPY_{day:%Y-%m-%d}_ticks.bi5"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".new")
    temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def response_metadata(response: dict[str, Any]) -> dict[str, Any]:
    last_modified = response.get("LastModified")
    return {
        "contentLength": response.get("ContentLength"),
        "contentType": response.get("ContentType"),
        "etag": response.get("ETag"),
        "checksumCRC32": response.get("ChecksumCRC32"),
        "checksumType": response.get("ChecksumType"),
        "versionId": response.get("VersionId"),
        "serverSideEncryption": response.get("ServerSideEncryption"),
        "requestCharged": response.get("RequestCharged"),
        "replicationStatus": response.get("ReplicationStatus"),
        "lastModifiedUtc": last_modified.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        if last_modified else None,
        "httpStatusCode": response.get("ResponseMetadata", {}).get("HTTPStatusCode"),
    }


def acquire_one(client: Any, day: date, raw_dir: Path, existing_receipts: dict[str, Any]) -> dict[str, Any]:
    key = date_key(day)
    target = raw_dir / artifact_name(day)
    partial = target.with_suffix(target.suffix + ".acquiring")
    receipt = existing_receipts.get(key)
    base = {
        "artifactId": artifact_id(day),
        "providerId": PROVIDER_ID,
        "datasetId": DATASET_ID,
        "instrumentId": INSTRUMENT_ID,
        "bucket": BUCKET,
        "key": key,
        "requestPayer": "requester",
        "partitionDateUtc": day.isoformat(),
        "originalFilename": target.name,
        "durablePrivateStoragePath": str(target),
    }
    if day.weekday() == 5:
        base.update({
            "status": "DOCUMENTED_WEEKEND_MARKET_CLOSED_NO_PROVIDER_OBJECT_REQUESTED",
            "closureReason": "DOCUMENTED_FX_SATURDAY_MARKET_CLOSURE",
            "emp1CheckedAtUtc": utc_now(),
        })
        return base
    if target.exists():
        base.update({
            "status": "PRESENT_EXISTING_RAW_BYTES",
            "byteCount": target.stat().st_size,
            "sha256": sha256_file(target),
            "emp1CustodyRecordedAtUtc": utc_now(),
            "responseMetadata": receipt.get("responseMetadata") if isinstance(receipt, dict) else None,
            "providerAcquisitionTimestampUtc": receipt.get("providerAcquisitionTimestampUtc") if isinstance(receipt, dict) else None,
        })
        return base
    if partial.exists():
        raise RuntimeError(f"EMP1_ACQUISITION_INCOMPLETE_PARTIAL_ARTIFACT_PRESENT: {partial}")
    try:
        response = client.get_object(Bucket=BUCKET, Key=key, RequestPayer="requester")
    except ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in {"NoSuchKey", "404", "NotFound"}:
            base.update({
                "status": "OBJECT_ABSENT_NO_RAW_BYTES",
                "providerErrorCode": code,
                "emp1CheckedAtUtc": utc_now(),
            })
            return base
        raise RuntimeError(f"EMP1_PROVIDER_GETOBJECT_FAILED: {key}: {code}") from exc
    with partial.open("xb") as handle:
        body = response["Body"]
        while True:
            chunk = body.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    byte_count = partial.stat().st_size
    header_length = response.get("ContentLength")
    if header_length != byte_count:
        raise RuntimeError(
            f"EMP1_PROVIDER_CONTENT_LENGTH_MISMATCH: {key}: header={header_length} local={byte_count}"
        )
    os.replace(partial, target)
    base.update({
        "status": "ACQUIRED_RAW_BYTES",
        "byteCount": byte_count,
        "sha256": sha256_file(target),
        "providerAcquisitionTimestampUtc": utc_now(),
        "responseMetadata": response_metadata(response),
    })
    return base


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--existing-receipts", type=Path)
    args = parser.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    receipts = read_json(args.existing_receipts) if args.existing_receipts else {}
    session = boto3.Session(profile_name=PROFILE)
    client = session.client("s3", region_name="eu-west-1", config=Config(retries={"max_attempts": 0, "mode": "standard"}))
    artifacts: list[dict[str, Any]] = []
    current = START_DATE
    while current <= END_DATE:
        record = acquire_one(client, current, args.raw_dir, receipts)
        artifacts.append(record)
        manifest = {
            "schemaVersion": "MO_R4A_CANDIDATE_C_EMP1_PRIVATE_ACQUISITION_MANIFEST_V1",
            "providerId": PROVIDER_ID,
            "datasetId": DATASET_ID,
            "instrumentId": INSTRUMENT_ID,
            "route": {"bucket": BUCKET, "requestPayer": "requester", "profile": PROFILE},
            "requestedCoverageStartUtc": "2025-05-01T01:58:38Z",
            "requestedCoverageEndUtc": "2025-08-01T23:20:56Z",
            "artifacts": artifacts,
        }
        write_json(args.manifest, manifest)
        current += timedelta(days=1)
    print(json.dumps({
        "artifactRecordCount": len(artifacts),
        "acquiredRawObjectCount": sum(item["status"] == "ACQUIRED_RAW_BYTES" for item in artifacts),
        "existingRawObjectCount": sum(item["status"] == "PRESENT_EXISTING_RAW_BYTES" for item in artifacts),
        "absentObjectCount": sum(item["status"] == "OBJECT_ABSENT_NO_RAW_BYTES" for item in artifacts),
        "manifest": str(args.manifest),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
