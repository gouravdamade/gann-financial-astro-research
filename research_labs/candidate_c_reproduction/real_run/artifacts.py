"""Deterministic, not-yet-populated output paths for the one-shot RUN1 record."""

from __future__ import annotations

from pathlib import Path


REAL_OUTPUT_ARTIFACTS = {
    "evaluatorA": Path("status/research/mo_r4a_candidate_c_run1_evaluator_a_real_output_v1.json"),
    "evaluatorB": Path("status/research/mo_r4a_candidate_c_run1_evaluator_b_real_output_v1.json"),
    "comparison": Path("status/research/mo_r4a_candidate_c_run1_ab_comparison_result_v1.json"),
}


def output_artifact_paths() -> dict[str, str]:
    """Return frozen future locations without creating result artifacts."""

    return {name: path.as_posix() for name, path in REAL_OUTPUT_ARTIFACTS.items()}
