"""Successor-owned execution audit checks; no evaluator or V2 science lives here."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .canonical import canonical_hash


ROW_KEY_FIELDS = ("eventId", "sourceProfile", "componentId", "sourceContractId", "operatorId")
# Read from the accepted frozen V2 comparator taxonomy.  The protected V2
# comparator emits sorted, unique lists, and one mismatch record may carry
# several independently observed classifications.
FROZEN_MISMATCH_TAXONOMY = frozenset({
    "ROW_MISSING_A", "ROW_MISSING_B", "ROW_DUPLICATE_A", "ROW_DUPLICATE_B",
    "PROFILE_MISMATCH", "COMPONENT_MISMATCH", "CONTRACT_MISMATCH", "OPERATOR_MISMATCH",
    "OPERATOR_VERSION_MISMATCH", "OUTPUT_STATUS_MISMATCH", "SOURCE_VALUE_MISMATCH",
    "UNKNOWN_REASON_MISMATCH", "SOURCE_STATUS_MISMATCH", "ADAPTER_FAILURE_A",
    "ADAPTER_FAILURE_B", "EVALUATOR_FAILURE_A", "EVALUATOR_FAILURE_B",
})


class RowUniverseValidationError(ValueError):
    pass


class MismatchAccountingError(ValueError):
    pass


def row_identity(row: Mapping[str, Any]) -> dict[str, Any]:
    provenance = row.get("provenance")
    operator = provenance.get("operatorId") if isinstance(provenance, Mapping) else row.get("operatorId")
    identity = {"eventId": row.get("eventId"), "sourceProfile": row.get("sourceProfile"), "componentId": row.get("componentId"), "sourceContractId": row.get("sourceContractId"), "operatorId": operator}
    if any(not isinstance(value, str) or not value for value in identity.values()):
        raise RowUniverseValidationError("row lacks a frozen Candidate C row identity field")
    return identity


def validate_complete_row_universe(rows: Sequence[Mapping[str, Any]], expected: Sequence[Mapping[str, Any]], *, expected_hash: str | None = None) -> dict[str, Any]:
    actual = [row_identity(row) for row in rows]
    frozen = [row_identity(row) for row in expected]
    if len(actual) != len(frozen):
        raise RowUniverseValidationError(f"row count mismatch: {len(actual)} != {len(frozen)}")
    if len(actual) != len({canonical_hash(item) for item in actual}):
        raise RowUniverseValidationError("batch has duplicate frozen row identities")
    if len(frozen) != len({canonical_hash(item) for item in frozen}):
        raise RowUniverseValidationError("expected row universe has duplicate identities")
    if set(map(canonical_hash, actual)) != set(map(canonical_hash, frozen)):
        raise RowUniverseValidationError("batch row universe has missing or extra frozen identities")
    actual_hash, frozen_hash = canonical_hash(actual), canonical_hash(frozen)
    if actual_hash != frozen_hash:
        raise RowUniverseValidationError("batch row universe order/hash differs from frozen universe")
    if expected_hash is not None and frozen_hash != expected_hash:
        raise RowUniverseValidationError("expected row universe does not match its frozen hash")
    return {"rowCount": len(actual), "expectedRowUniverseHash": frozen_hash, "actualRowUniverseHash": actual_hash, "rowUniverseValidated": True}


def fake_expected_universe(*, frozen_universe: Sequence[Mapping[str, Any]], fake_event_ids: Sequence[str]) -> list[dict[str, Any]]:
    if not fake_event_ids or any(not value.startswith("FAKE_REAL_RUN1_") for value in fake_event_ids):
        raise RowUniverseValidationError("fake expected universe requires FAKE_REAL_RUN1 identifiers")
    first_event = str(frozen_universe[0].get("eventId")) if frozen_universe else ""
    template = [row_identity(item) for item in frozen_universe if item.get("eventId") == first_event]
    if len(template) != 8:
        raise RowUniverseValidationError("frozen source does not expose the expected eight-row event template")
    return [{**item, "eventId": event_id} for event_id in fake_event_ids for item in template]


def summarize_mismatches(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for record in records:
        classes = record.get("mismatchClassifications")
        if not isinstance(classes, list) or not classes:
            raise MismatchAccountingError("frozen V2 mismatch record lacks classifications")
        if any(not isinstance(item, str) or item not in FROZEN_MISMATCH_TAXONOMY for item in classes):
            raise MismatchAccountingError("frozen V2 mismatch record has an unrecognized classification")
        if classes != sorted(set(classes)):
            raise MismatchAccountingError("frozen V2 mismatch classifications are not sorted and unique")
        for item in classes:
            counts[item] = counts.get(item, 0) + 1
    sorted_counts = dict(sorted(counts.items()))
    classification_total = sum(sorted_counts.values())
    record_total = len(records)
    if classification_total != sum(len(record["mismatchClassifications"]) for record in records):
        raise MismatchAccountingError("mismatch classification occurrence accounting failed")
    return {
        "totalMismatches": record_total,
        "totalMismatchClassifications": classification_total,
        "mismatchCountsByClass": sorted_counts,
    }


def mismatch_counts_by_class(records: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    """Compatibility accessor for the frozen-V2-compatible audit summary."""

    return summarize_mismatches(records)["mismatchCountsByClass"]


def terminal_result(summary: Mapping[str, Any]) -> str:
    if summary.get("totalMismatches") == 0:
        return "REAL_SOURCE_REPRODUCTION_SEMANTIC_AGREEMENT"
    return "REAL_SOURCE_REPRODUCTION_SEMANTIC_MISMATCH"
