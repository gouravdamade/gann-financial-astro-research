"""Frozen, unsigned EMP0-R2 test-cell statistics with no market data access."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from math import isfinite
from statistics import fmean
from typing import Any, Callable, Mapping, Sequence


ALLOWED_HORIZON_SECONDS = frozenset({3600, 21600, 86400})
HORIZON_ROLES = {3600: "SECONDARY_EXPLORATORY", 21600: "SECONDARY_EXPLORATORY", 86400: "PRIMARY_CONFIRMATORY"}
PERMUTATION_COUNT = 4999
PRIMARY_STATISTIC = "BETWEEN_STATE_EXPLAINED_VARIANCE"
TEMPORAL_NULL_CONTRACT_ID = "CANDIDATE_C_EMP0_R1_WITHIN_SIDE_WITHIN_UTC_MONTH_CIRCULAR_SHIFT_V2"
MAX_IDENTITY_REJECTION_ATTEMPTS = 100000


class StatisticalContractError(ValueError):
    """Raised when a frozen empirical test-cell contract is violated."""


OffsetResolver = Callable[[str, str, int, str, int, int, int], int]


def validate_test_cell_observations(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    eligible_state_tokens: set[str],
) -> tuple[str, str]:
    """Require exactly one frozen side, row slot, horizon, and eligible state set."""

    if horizon_seconds not in ALLOWED_HORIZON_SECONDS:
        raise StatisticalContractError("UNREGISTERED_HORIZON")
    if not observations:
        raise StatisticalContractError("test cell observations are required")
    if not eligible_state_tokens:
        raise StatisticalContractError("eligible source state tokens are required")
    sides = {str(item.get("sideIdentity")) for item in observations}
    if len(sides) != 1 or not sides <= {"USD", "JPY"}:
        raise StatisticalContractError("TEST_CELL_MIXED_OR_INVALID_SIDE")
    row_slots = {str(item.get("canonicalRowSlotId")) for item in observations}
    if len(row_slots) != 1:
        raise StatisticalContractError("TEST_CELL_MIXED_ROW_SLOT")
    for item in observations:
        item_horizon = item.get("horizonSeconds")
        if item_horizon is not None and item_horizon != horizon_seconds:
            raise StatisticalContractError("TEST_CELL_HORIZON_BINDING_MISMATCH")
        token = str(item.get("stateTokenCanonicalJson"))
        if token not in eligible_state_tokens:
            raise StatisticalContractError("TEST_CELL_NON_ELIGIBLE_SOURCE_STATE")
        value = item.get("logReturn")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
            raise StatisticalContractError("TEST_CELL_LOG_RETURN_NOT_FINITE")
    return next(iter(sides)), next(iter(row_slots))


def between_state_explained_variance(observations: Sequence[Mapping[str, Any]]) -> float | None:
    returns = [float(item["logReturn"]) for item in observations]
    if not returns or not all(isfinite(value) for value in returns):
        raise StatisticalContractError("returns must be finite")
    overall = fmean(returns)
    total = sum((value - overall) ** 2 for value in returns)
    if total == 0:
        return None
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in observations:
        grouped[str(item["stateTokenCanonicalJson"])].append(float(item["logReturn"]))
    between = sum(len(values) * (fmean(values) - overall) ** 2 for values in grouped.values())
    return between / total


def deterministic_offset(
    side_identity: str,
    canonical_row_slot_id: str,
    horizon_seconds: int,
    month: str,
    replicate_index: int,
    block_size: int,
    attempt_index: int,
) -> int:
    if block_size <= 1:
        return 0
    payload = "|".join((TEMPORAL_NULL_CONTRACT_ID, side_identity, canonical_row_slot_id, str(horizon_seconds), month, str(replicate_index), str(attempt_index)))
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest(), 16) % block_size


def _month(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m")


def _ordered_blocks(observations: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    blocks: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for item in observations:
        blocks[(str(item["sideIdentity"]), _month(str(item["exactUtc"])))].append(item)
    return {key: sorted(block, key=lambda item: (str(item["exactUtc"]), str(item["eventId"]))) for key, block in blocks.items()}


def deterministic_monthly_offsets(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    replicate_index: int,
    *,
    offset_resolver: OffsetResolver = deterministic_offset,
    max_attempts: int = MAX_IDENTITY_REJECTION_ATTEMPTS,
) -> dict[tuple[str, str], int]:
    """Generate a finite, non-identity joint monthly vector without biasing a block."""

    blocks = _ordered_blocks(observations)
    if not blocks or not any(len(block) > 1 for block in blocks.values()):
        raise StatisticalContractError("NO_NONTRIVIAL_TEMPORAL_SHIFT_AVAILABLE")
    for attempt_index in range(max_attempts):
        offsets = {
            (side, month): offset_resolver(side, str(block[0]["canonicalRowSlotId"]), horizon_seconds, month, replicate_index, len(block), attempt_index)
            for (side, month), block in sorted(blocks.items())
        }
        if any(offset != 0 for offset in offsets.values()):
            return offsets
    raise StatisticalContractError("TEMPORAL_NULL_GENERATION_FAILURE")


def circular_shifted_observations(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    eligible_state_tokens: set[str],
    replicate_index: int,
) -> list[dict[str, Any]]:
    validate_test_cell_observations(observations, horizon_seconds, eligible_state_tokens)
    blocks = _ordered_blocks(observations)
    offsets = deterministic_monthly_offsets(observations, horizon_seconds, replicate_index)
    shifted: list[dict[str, Any]] = []
    for key, block in sorted(blocks.items()):
        offset = offsets[key]
        labels = [str(item["stateTokenCanonicalJson"]) for item in block]
        shifted_labels = labels[offset:] + labels[:offset]
        for item, label in zip(block, shifted_labels, strict=True):
            shifted.append(dict(item) | {"stateTokenCanonicalJson": label})
    return shifted


def deterministic_permutation_test(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    eligible_state_tokens: set[str],
) -> dict[str, Any]:
    """Run one validated side x row-slot x horizon omnibus test."""

    validate_test_cell_observations(observations, horizon_seconds, eligible_state_tokens)
    observed = between_state_explained_variance(observations)
    if observed is None:
        return {"status": "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE"}
    null_statistics = [
        between_state_explained_variance(circular_shifted_observations(observations, horizon_seconds, eligible_state_tokens, index))
        for index in range(1, PERMUTATION_COUNT + 1)
    ]
    if any(value is None for value in null_statistics):
        raise StatisticalContractError("shift must preserve nonzero outcome variance")
    exceedances = sum(value >= observed for value in null_statistics)
    return {"status": "PREREGISTERED_STATISTICAL_RESULT", "statistic": observed, "permutationCount": PERMUTATION_COUNT, "nullStatistics": null_statistics, "pRaw": (1 + exceedances) / 5000}


def market_eligible_testable(observations: Sequence[Mapping[str, Any]], eligible_tokens: set[str], min_state_count: int = 20, min_total_count: int = 60) -> bool:
    counts = Counter(str(item["stateTokenCanonicalJson"]) for item in observations if str(item["stateTokenCanonicalJson"]) in eligible_tokens)
    retained = [count for count in counts.values() if count >= min_state_count]
    return len(retained) >= 2 and sum(retained) >= min_total_count
