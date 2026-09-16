"""Clean-room Candidate C Evaluator A implementation."""

from .contract_loader import FrozenContracts, load_frozen_contracts
from .evaluator import (
    REAL_CANDIDATE_C_EXECUTION_ALLOWED,
    RealCandidateCExecutionBlocked,
    evaluate_frozen_population,
    evaluate_synthetic_event,
)

__all__ = [
    "FrozenContracts",
    "REAL_CANDIDATE_C_EXECUTION_ALLOWED",
    "RealCandidateCExecutionBlocked",
    "evaluate_frozen_population",
    "evaluate_synthetic_event",
    "load_frozen_contracts",
]
