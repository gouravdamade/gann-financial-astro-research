"""Neutral synthetic comparator for frozen Candidate C evaluators."""

from .comparator import compare_projected_batches, run_frozen_synthetic_comparison
from .fixtures import build_fixture_corpus

__all__ = ["build_fixture_corpus", "compare_projected_batches", "run_frozen_synthetic_comparison"]
