"""Frozen Candidate C output-schema validation owned by Evaluator A."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from .canonical import canonical_hash


OUTPUT_SCHEMA_ID = "MO_R4A_CANDIDATE_C_P0_EVALUATOR_OUTPUT_SCHEMA_V1"
OUTPUT_FIELDS = (
    "eventId",
    "sourceProfile",
    "componentId",
    "sourceContractId",
    "inputIdentity",
    "inputIdentityHash",
    "outputStatus",
    "sourceValue",
    "unknownReasonCode",
    "provenance",
)
ROW_KEY_FIELDS = ("eventId", "sourceProfile", "componentId", "sourceContractId", "operatorId")
OUTPUT_STATUSES = frozenset({"VALUE", "UNKNOWN"})


class OutputSchemaError(ValueError):
    """Raised when an Evaluator A row does not satisfy the frozen schema."""


def row_key(row: Mapping[str, Any]) -> dict[str, Any]:
    provenance = row.get("provenance")
    if not isinstance(provenance, Mapping) or "operatorId" not in provenance:
        raise OutputSchemaError("row provenance must contain operatorId")
    return {
        "eventId": row.get("eventId"),
        "sourceProfile": row.get("sourceProfile"),
        "componentId": row.get("componentId"),
        "sourceContractId": row.get("sourceContractId"),
        "operatorId": provenance.get("operatorId"),
    }


def validate_row(row: Mapping[str, Any], allowed_unknown_codes: Iterable[str]) -> None:
    if not isinstance(row, Mapping):
        raise OutputSchemaError("output row must be an object")
    missing = {field for field in ("eventId", "sourceProfile", "componentId", "sourceContractId", "inputIdentity", "inputIdentityHash", "outputStatus", "provenance") if field not in row}
    if missing:
        raise OutputSchemaError(f"output row missing fields: {sorted(missing)}")
    if set(row) - set(OUTPUT_FIELDS):
        raise OutputSchemaError(f"output row has unexpected fields: {sorted(set(row) - set(OUTPUT_FIELDS))}")
    if not isinstance(row["eventId"], str) or not row["eventId"]:
        raise OutputSchemaError("eventId must be a non-empty string")
    if row["outputStatus"] not in OUTPUT_STATUSES:
        raise OutputSchemaError(f"unsupported outputStatus: {row['outputStatus']!r}")
    if not isinstance(row["inputIdentity"], Mapping):
        raise OutputSchemaError("inputIdentity must be an object")
    if row["inputIdentityHash"] != canonical_hash(dict(row["inputIdentity"])):
        raise OutputSchemaError("inputIdentityHash does not match inputIdentity")
    provenance = row["provenance"]
    if not isinstance(provenance, Mapping):
        raise OutputSchemaError("provenance must be an object")
    for field in ("sourceProfile", "sourceContractId", "operatorId", "operatorVersion", "sourceStatus", "sourceArtifact", "sourceLocators"):
        if field not in provenance:
            raise OutputSchemaError(f"provenance missing {field}")
    if provenance["sourceProfile"] != row["sourceProfile"] or provenance["sourceContractId"] != row["sourceContractId"]:
        raise OutputSchemaError("row and provenance source identities differ")
    if row["outputStatus"] == "VALUE":
        if "sourceValue" not in row or "unknownReasonCode" in row:
            raise OutputSchemaError("VALUE rows require sourceValue and exclude unknownReasonCode")
    else:
        if "unknownReasonCode" not in row or "sourceValue" in row:
            raise OutputSchemaError("UNKNOWN rows require unknownReasonCode and exclude sourceValue")
        if row["unknownReasonCode"] not in set(allowed_unknown_codes):
            raise OutputSchemaError(f"unknown reason is outside the frozen taxonomy: {row['unknownReasonCode']!r}")
    artifact = provenance["sourceArtifact"]
    if not isinstance(artifact, Mapping) or not isinstance(artifact.get("path"), str) or not isinstance(artifact.get("sha256"), str):
        raise OutputSchemaError("sourceArtifact must contain path and sha256")
    if not isinstance(provenance["sourceLocators"], Sequence) or isinstance(provenance["sourceLocators"], (str, bytes)) or not provenance["sourceLocators"]:
        raise OutputSchemaError("sourceLocators must be a non-empty sequence")


def validate_rows(rows: Sequence[Mapping[str, Any]], expected_row_keys: Sequence[Mapping[str, Any]], allowed_unknown_codes: Iterable[str]) -> None:
    if len(rows) != len(expected_row_keys):
        raise OutputSchemaError(f"row count mismatch: {len(rows)} != {len(expected_row_keys)}")
    for index, (row, expected) in enumerate(zip(rows, expected_row_keys)):
        validate_row(row, allowed_unknown_codes)
        actual_key = row_key(row)
        if actual_key != dict(expected):
            raise OutputSchemaError(f"row key/order mismatch at index {index}: {actual_key!r} != {expected!r}")
