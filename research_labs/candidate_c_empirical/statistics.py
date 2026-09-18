"""Deterministic, unsigned EMP0 association statistics for synthetic fixtures."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from math import isfinite
from statistics import fmean
from typing import Any, Mapping, Sequence


PERMUTATION_COUNT = 4999
PRIMARY_STATISTIC = "BETWEEN_STATE_EXPLAINED_VARIANCE"
PERMUTATION_CONTRACT_ID = "CANDIDATE_C_EMP0_WITHIN_SIDE_WITHIN_UTC_MONTH_CIRCULAR_SHIFT_V1"


class StatisticalContractError(ValueError):
    """Raised for an invalid frozen statistical input."""


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


def deterministic_offset(side_identity: str, canonical_row_slot_id: str, horizon_seconds: int, month: str, replicate_index: int, block_size: int) -> int:
    if block_size <= 1:
        return 0
    payload = "|".join((PERMUTATION_CONTRACT_ID, side_identity, canonical_row_slot_id, str(horizon_seconds), month, str(replicate_index)))
    return 1 + (int(hashlib.sha256(payload.encode("utf-8")).hexdigest(), 16) % (block_size - 1))


def _month(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m")


def circular_shifted_observations(observations: Sequence[Mapping[str, Any]], horizon_seconds: int, replicate_index: int) -> list[dict[str, Any]]:
    blocks: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for item in observations:
        blocks[(str(item["sideIdentity"]), _month(str(item["exactUtc"])))].append(item)
    shifted: list[dict[str, Any]] = []
    for (side, month), block in sorted(blocks.items()):
        ordered = sorted(block, key=lambda item: (str(item["exactUtc"]), str(item["eventId"])))
        offset = deterministic_offset(side, str(ordered[0]["canonicalRowSlotId"]), horizon_seconds, month, replicate_index, len(ordered))
        labels = [str(item["stateTokenCanonicalJson"]) for item in ordered]
        shifted_labels = labels[offset:] + labels[:offset]
        for item, label in zip(ordered, shifted_labels, strict=True):
            shifted.append(dict(item) | {"stateTokenCanonicalJson": label})
    return shifted


def deterministic_permutation_test(observations: Sequence[Mapping[str, Any]], horizon_seconds: int) -> dict[str, Any]:
    """Run the frozen 4,999-replicate null for FAKE_MARKET_ test records only."""

    if not observations or any(not str(item["eventId"]).startswith("FAKE_SOURCE_") for item in observations):
        raise StatisticalContractError("EMP0 statistical execution accepts FAKE_SOURCE_ observations only")
    observed = between_state_explained_variance(observations)
    if observed is None:
        return {"status": "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE"}
    null_statistics = [between_state_explained_variance(circular_shifted_observations(observations, horizon_seconds, index)) for index in range(1, PERMUTATION_COUNT + 1)]
    if any(value is None for value in null_statistics):
        raise StatisticalContractError("shift must preserve nonzero outcome variance")
    exceedances = sum(value >= observed for value in null_statistics)
    return {
        "status": "FAKE_MARKET_STATISTICAL_RESULT",
        "statistic": observed,
        "permutationCount": PERMUTATION_COUNT,
        "nullStatistics": null_statistics,
        "pRaw": (1 + exceedances) / (1 + PERMUTATION_COUNT),
    }


def market_eligible_testable(observations: Sequence[Mapping[str, Any]], eligible_tokens: set[str], min_state_count: int = 20, min_total_count: int = 60) -> bool:
    counts = Counter(str(item["stateTokenCanonicalJson"]) for item in observations if str(item["stateTokenCanonicalJson"]) in eligible_tokens)
    retained = [count for count in counts.values() if count >= min_state_count]
    return len(retained) >= 2 and sum(retained) >= min_total_count
