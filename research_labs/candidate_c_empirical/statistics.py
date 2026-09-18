"""Deterministic, unsigned EMP0-R1 association statistics with no data access."""

from __future__ import annotations

import hashlib
from collections import Counter, defaultdict
from datetime import datetime
from math import isfinite
from statistics import fmean
from typing import Any, Mapping, Sequence


PERMUTATION_COUNT = 4999
PRIMARY_STATISTIC = "BETWEEN_STATE_EXPLAINED_VARIANCE"
PERMUTATION_CONTRACT_ID = "CANDIDATE_C_EMP0_R1_WITHIN_SIDE_WITHIN_UTC_MONTH_CIRCULAR_SHIFT_V2"


class StatisticalContractError(ValueError):
    """Raised for an invalid frozen statistical input or authorization."""


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
    attempt_index: int = 0,
) -> int:
    """Derive one monthly circular offset; zero is an admitted monthly shift."""

    if block_size <= 1:
        return 0
    payload = "|".join((
        PERMUTATION_CONTRACT_ID,
        side_identity,
        canonical_row_slot_id,
        str(horizon_seconds),
        month,
        str(replicate_index),
        str(attempt_index),
    ))
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest(), 16) % block_size


def _month(value: str) -> str:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m")


def _ordered_blocks(observations: Sequence[Mapping[str, Any]]) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    blocks: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for item in observations:
        blocks[(str(item["sideIdentity"]), _month(str(item["exactUtc"])))].append(item)
    return {
        key: sorted(block, key=lambda item: (str(item["exactUtc"]), str(item["eventId"])))
        for key, block in blocks.items()
    }


def deterministic_monthly_offsets(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    replicate_index: int,
) -> dict[tuple[str, str], int]:
    """Return a non-identity joint monthly shift vector for one replicate.

    Every month may legitimately receive offset zero. Only the all-zero vector
    is excluded, because the observed arrangement is separately counted by the
    plus-one p-value correction. The attempt index is part of the SHA-256 input,
    making a retry deterministic rather than data-dependent.
    """

    blocks = _ordered_blocks(observations)
    if not blocks or not any(len(block) > 1 for block in blocks.values()):
        raise StatisticalContractError("a non-identity monthly circular shift requires a block with at least two observations")
    attempt_index = 0
    while True:
        offsets = {
            (side, month): deterministic_offset(
                side,
                str(block[0]["canonicalRowSlotId"]),
                horizon_seconds,
                month,
                replicate_index,
                len(block),
                attempt_index,
            )
            for (side, month), block in sorted(blocks.items())
        }
        if any(offset != 0 for offset in offsets.values()):
            return offsets
        attempt_index += 1


def circular_shifted_observations(observations: Sequence[Mapping[str, Any]], horizon_seconds: int, replicate_index: int) -> list[dict[str, Any]]:
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


def deterministic_permutation_test(observations: Sequence[Mapping[str, Any]], horizon_seconds: int) -> dict[str, Any]:
    """Pure frozen core; callers must separately hold a data-execution authorization."""

    if not observations:
        raise StatisticalContractError("observations are required")
    observed = between_state_explained_variance(observations)
    if observed is None:
        return {"status": "ZERO_OUTCOME_VARIANCE_NOT_TESTABLE"}
    null_statistics = [
        between_state_explained_variance(circular_shifted_observations(observations, horizon_seconds, index))
        for index in range(1, PERMUTATION_COUNT + 1)
    ]
    if any(value is None for value in null_statistics):
        raise StatisticalContractError("shift must preserve nonzero outcome variance")
    exceedances = sum(value >= observed for value in null_statistics)
    return {
        "status": "PREREGISTERED_STATISTICAL_RESULT",
        "statistic": observed,
        "permutationCount": PERMUTATION_COUNT,
        "nullStatistics": null_statistics,
        "pRaw": (1 + exceedances) / (1 + PERMUTATION_COUNT),
    }


def run_authorized_market_analysis(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    execution_authorization: Mapping[str, Any],
) -> dict[str, Any]:
    """Invoke the frozen core only after a future immutable authorization binds data."""

    if execution_authorization.get("outcomeAnalysisAuthorized") is not True:
        raise StatisticalContractError("market analysis requires a future outcomeAnalysisAuthorized record")
    if execution_authorization.get("marketSnapshotAdmitted") is not True:
        raise StatisticalContractError("market analysis requires an admitted immutable market snapshot")
    if not isinstance(execution_authorization.get("marketSnapshotHash"), str) or not execution_authorization["marketSnapshotHash"]:
        raise StatisticalContractError("market analysis authorization must bind a marketSnapshotHash")
    if not isinstance(execution_authorization.get("analysisImplementationManifestHash"), str) or not execution_authorization["analysisImplementationManifestHash"]:
        raise StatisticalContractError("market analysis authorization must bind an analysisImplementationManifestHash")
    return deterministic_permutation_test(observations, horizon_seconds)


def market_eligible_testable(observations: Sequence[Mapping[str, Any]], eligible_tokens: set[str], min_state_count: int = 20, min_total_count: int = 60) -> bool:
    counts = Counter(str(item["stateTokenCanonicalJson"]) for item in observations if str(item["stateTokenCanonicalJson"]) in eligible_tokens)
    retained = [count for count in counts.values() if count >= min_state_count]
    return len(retained) >= 2 and sum(retained) >= min_total_count
