"""Clean-room Candidate C Evaluator B implementation."""

from .contract_loader import FrozenContractError, load_frozen_contracts
from .evaluator import (
    EvaluatorB,
    RealCandidateCExecutionBlocked,
    evaluate_real_population,
    evaluate_synthetic_event,
    validate_output_rows,
)
from .models import SyntheticEvent, SyntheticInputError

__all__ = [
    "EvaluatorB",
    "FrozenContractError",
    "RealCandidateCExecutionBlocked",
    "SyntheticEvent",
    "SyntheticInputError",
    "evaluate_real_population",
    "evaluate_synthetic_event",
    "load_frozen_contracts",
    "validate_output_rows",
]
