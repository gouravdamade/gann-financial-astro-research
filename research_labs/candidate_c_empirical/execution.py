"""Future EMP2 orchestration entrypoint; no authorization instance exists in EMP0-R2."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .authorization import ValidatedEmpiricalExecutionAuthorization
from .statistics import deterministic_permutation_test


class EmpiricalExecutionError(ValueError):
    """Raised when the future entrypoint is not given a validated authorization."""


def execute_validated_empirical_test(
    observations: Sequence[Mapping[str, Any]],
    horizon_seconds: int,
    eligible_state_tokens: set[str],
    authorization: ValidatedEmpiricalExecutionAuthorization,
) -> dict[str, Any]:
    """Run only a prevalidated one-cell test; plain mappings never authorize it."""

    if not isinstance(authorization, ValidatedEmpiricalExecutionAuthorization):
        raise EmpiricalExecutionError("EMPIRICAL_EXECUTION_REQUIRES_VALIDATED_AUTHORIZATION_TYPE")
    return deterministic_permutation_test(observations, horizon_seconds, eligible_state_tokens)
