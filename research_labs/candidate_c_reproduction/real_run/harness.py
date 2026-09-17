"""RUN1 pre-run validation and a hard authorization stop before real evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .adapter_a import adapt_real_event_for_a
from .adapter_b import adapt_real_event_for_b
from .admission import EXPECTED_EVENT_COUNT, EXPECTED_ROW_COUNT, load_and_validate_real_population
from .artifacts import output_artifact_paths
from .authorization import REAL_CANDIDATE_C_RUN_AUTHORIZED, RealCandidateCRunNotAuthorized
from .validation import (
    validate_adapter_equivalence,
    verify_protected_identities,
    verify_runtime_checkout_against_protected_blobs,
    verify_runtime_module_paths,
)


@dataclass(frozen=True)
class PreRunValidationSummary:
    population_event_count: int
    expected_row_count: int
    protected_identities: dict[str, str]
    runtime_identity_file_count: int
    artifact_paths: dict[str, str]
    real_frozen_population_read: bool
    real_frozen_population_read_scope: str
    real_frozen_population_evaluated: bool
    real_candidate_c_output_produced: bool
    real_candidate_c_output_row_count: int


def validate_prerun_inputs(
    root: Path | str | None = None,
    runtime_roots: Mapping[str, Path | str] | None = None,
) -> PreRunValidationSummary:
    """Validate the real frozen population and adapters without evaluating C01-C07."""

    repository_root = Path(root) if root is not None else Path(__file__).resolve().parents[3]
    repository_root = repository_root.resolve()
    runtime_records = verify_runtime_checkout_against_protected_blobs(repository_root, runtime_roots)
    verify_runtime_module_paths(repository_root, runtime_roots)
    protected_identities = verify_protected_identities(repository_root)
    population = load_and_validate_real_population(repository_root)
    for event in population.events:
        a_event = adapt_real_event_for_a(event)
        b_event = adapt_real_event_for_b(a_event)
        validate_adapter_equivalence(a_event, b_event, str(population.snapshot["sharedAstronomyInputSnapshotHash"]))
    return PreRunValidationSummary(
        population_event_count=EXPECTED_EVENT_COUNT,
        expected_row_count=EXPECTED_ROW_COUNT,
        protected_identities=protected_identities,
        runtime_identity_file_count=len(runtime_records),
        artifact_paths=output_artifact_paths(),
        real_frozen_population_read=True,
        real_frozen_population_read_scope="IDENTITY_STRUCTURE_ADAPTER_AND_EXECUTION_BOUNDARY_VALIDATION_ONLY",
        real_frozen_population_evaluated=False,
        real_candidate_c_output_produced=False,
        real_candidate_c_output_row_count=0,
    )


def run_real_population(*_args: Any, **_kwargs: Any) -> None:
    """The future one-shot RUN1 path is intentionally unavailable in this milestone."""

    if not REAL_CANDIDATE_C_RUN_AUTHORIZED:
        raise RealCandidateCRunNotAuthorized(
            "REAL_CANDIDATE_C_RUN_AUTHORIZED=false; central authorization is required before any 645-event evaluation"
        )
    raise AssertionError("a future authorized runner must be preregistered in a successor milestone")
