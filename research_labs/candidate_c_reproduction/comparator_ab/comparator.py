"""Symmetric, predeclared A/B semantic comparison with no adjudication path."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from research_labs.candidate_c_reproduction.evaluator_a import evaluate_synthetic_event as evaluate_a_synthetic
from research_labs.candidate_c_reproduction.evaluator_b import evaluate_synthetic_event as evaluate_b_synthetic

from .adapters import adapt_fixture_for_a, adapt_fixture_for_b
from .models import NeutralFixture, SemanticRow
from .projection import project_rows


MISMATCH_TAXONOMY = (
    "ROW_MISSING_A", "ROW_MISSING_B", "ROW_DUPLICATE_A", "ROW_DUPLICATE_B",
    "PROFILE_MISMATCH", "COMPONENT_MISMATCH", "CONTRACT_MISMATCH", "OPERATOR_MISMATCH",
    "OPERATOR_VERSION_MISMATCH", "OUTPUT_STATUS_MISMATCH", "SOURCE_VALUE_MISMATCH",
    "UNKNOWN_REASON_MISMATCH", "SOURCE_STATUS_MISMATCH", "ADAPTER_FAILURE_A", "ADAPTER_FAILURE_B",
    "EVALUATOR_FAILURE_A", "EVALUATOR_FAILURE_B",
)
EXPECTED_ROWS_PER_FIXTURE = 8


def _fixture_context(fixture: NeutralFixture) -> dict[str, Any]:
    return {
        "fixtureId": fixture.fixture_id,
        "semanticFixtureIdentityHash": fixture.semantic_fixture_identity_hash,
        "fixtureFamily": fixture.fixture_family,
        "coverageTags": list(fixture.coverage_tags),
        "canonicalSemanticInput": fixture.semantic_input(),
    }


def _index(rows: Sequence[SemanticRow]) -> tuple[dict[tuple[str, str, str, str, str], SemanticRow], list[SemanticRow]]:
    indexed: dict[tuple[str, str, str, str, str], SemanticRow] = {}
    duplicates: list[SemanticRow] = []
    for row in rows:
        if row.row_key() in indexed:
            duplicates.append(row)
        else:
            indexed[row.row_key()] = row
    return indexed, duplicates


def _mismatch(fixture: NeutralFixture, classifications: Iterable[str], a_row: SemanticRow | None, b_row: SemanticRow | None) -> dict[str, Any]:
    return _fixture_context(fixture) | {
        "mismatchClassifications": sorted(set(classifications)),
        "aSemanticProjection": a_row.comparison_view() if a_row else None,
        "bSemanticProjection": b_row.comparison_view() if b_row else None,
    }


def _compare_pair(fixture: NeutralFixture, a_row: SemanticRow, b_row: SemanticRow) -> dict[str, Any] | None:
    classes: list[str] = []
    if a_row.source_profile != b_row.source_profile:
        classes.append("PROFILE_MISMATCH")
    if a_row.component_id != b_row.component_id:
        classes.append("COMPONENT_MISMATCH")
    if a_row.source_contract_id != b_row.source_contract_id:
        classes.append("CONTRACT_MISMATCH")
    if a_row.operator_id != b_row.operator_id:
        classes.append("OPERATOR_MISMATCH")
    if a_row.operator_version is not None and b_row.operator_version is not None and a_row.operator_version != b_row.operator_version:
        classes.append("OPERATOR_VERSION_MISMATCH")
    if a_row.output_status != b_row.output_status:
        classes.append("OUTPUT_STATUS_MISMATCH")
    elif a_row.output_status == "VALUE" and a_row.source_value != b_row.source_value:
        classes.append("SOURCE_VALUE_MISMATCH")
    elif a_row.output_status == "UNKNOWN" and a_row.unknown_reason_code != b_row.unknown_reason_code:
        classes.append("UNKNOWN_REASON_MISMATCH")
    if a_row.source_status is not None and b_row.source_status is not None and a_row.source_status != b_row.source_status:
        classes.append("SOURCE_STATUS_MISMATCH")
    return _mismatch(fixture, classes, a_row, b_row) if classes else None


def compare_projected_batches(
    fixture: NeutralFixture,
    a_rows: Sequence[SemanticRow],
    b_rows: Sequence[SemanticRow],
) -> list[dict[str, Any]]:
    """Compare neutral semantic projections; neither evaluator is an oracle."""

    mismatches: list[dict[str, Any]] = []
    a_index, a_duplicates = _index(a_rows)
    b_index, b_duplicates = _index(b_rows)
    for row in a_duplicates:
        mismatches.append(_mismatch(fixture, ("ROW_DUPLICATE_A",), row, None))
    for row in b_duplicates:
        mismatches.append(_mismatch(fixture, ("ROW_DUPLICATE_B",), None, row))
    unmatched_a: list[SemanticRow] = []
    unmatched_b: list[SemanticRow] = []
    for key in sorted(set(a_index) | set(b_index)):
        a_row = a_index.get(key)
        b_row = b_index.get(key)
        if a_row is None:
            unmatched_b.append(b_row)
            continue
        if b_row is None:
            unmatched_a.append(a_row)
            continue
        mismatch = _compare_pair(fixture, a_row, b_row)
        if mismatch:
            mismatches.append(mismatch)
    unmatched_a.sort(key=lambda row: (row.component_id, row.source_contract_id, row.operator_id, row.source_profile))
    unmatched_b.sort(key=lambda row: (row.component_id, row.source_contract_id, row.operator_id, row.source_profile))
    while unmatched_a and unmatched_b:
        a_row = unmatched_a.pop(0)
        b_row = unmatched_b.pop(0)
        mismatch = _compare_pair(fixture, a_row, b_row)
        if mismatch:
            mismatches.append(mismatch)
        else:
            mismatches.append(_mismatch(fixture, ("ROW_MISSING_A", "ROW_MISSING_B"), a_row, b_row))
    for a_row in unmatched_a:
        mismatches.append(_mismatch(fixture, ("ROW_MISSING_B",), a_row, None))
    for b_row in unmatched_b:
        mismatches.append(_mismatch(fixture, ("ROW_MISSING_A",), None, b_row))
    return mismatches


def _evaluated_projection(
    fixture: NeutralFixture,
    adapter: Any,
    evaluator: Any,
    adapter_failure: str,
    evaluator_failure: str,
) -> tuple[list[SemanticRow], list[dict[str, Any]]]:
    try:
        event = adapter(fixture)
    except Exception as exc:
        return [], [_fixture_context(fixture) | {"mismatchClassifications": [adapter_failure], "error": str(exc), "aSemanticProjection": None, "bSemanticProjection": None}]
    try:
        rows = evaluator(event)
    except Exception as exc:
        return [], [_fixture_context(fixture) | {"mismatchClassifications": [evaluator_failure], "error": str(exc), "aSemanticProjection": None, "bSemanticProjection": None}]
    if len(rows) != EXPECTED_ROWS_PER_FIXTURE:
        return [], [_fixture_context(fixture) | {"mismatchClassifications": [evaluator_failure], "error": f"expected {EXPECTED_ROWS_PER_FIXTURE} rows, got {len(rows)}", "aSemanticProjection": None, "bSemanticProjection": None}]
    return project_rows(fixture, rows), []


def run_frozen_synthetic_comparison(fixtures: Sequence[NeutralFixture]) -> dict[str, Any]:
    """Run the first allowed synthetic-only comparison after a pre-reveal freeze."""

    a_row_count = 0
    b_row_count = 0
    compared = 0
    mismatches: list[dict[str, Any]] = []
    for fixture in fixtures:
        a_rows, a_failures = _evaluated_projection(fixture, adapt_fixture_for_a, evaluate_a_synthetic, "ADAPTER_FAILURE_A", "EVALUATOR_FAILURE_A")
        b_rows, b_failures = _evaluated_projection(fixture, adapt_fixture_for_b, evaluate_b_synthetic, "ADAPTER_FAILURE_B", "EVALUATOR_FAILURE_B")
        a_row_count += len(a_rows)
        b_row_count += len(b_rows)
        mismatches.extend(a_failures)
        mismatches.extend(b_failures)
        if not a_failures and not b_failures:
            compared += min(len(a_rows), len(b_rows))
            mismatches.extend(compare_projected_batches(fixture, a_rows, b_rows))
    mismatch_counts = Counter(
        mismatch_class
        for mismatch in mismatches
        for mismatch_class in mismatch["mismatchClassifications"]
    )
    return {
        "expectedRowsPerEvaluator": len(fixtures) * EXPECTED_ROWS_PER_FIXTURE,
        "actualASyntheticRowCount": a_row_count,
        "actualBSyntheticRowCount": b_row_count,
        "semanticRowsCompared": compared,
        "totalMismatches": len(mismatches),
        "mismatchCountsByClass": dict(sorted(mismatch_counts.items())),
        "mismatchRecords": mismatches,
        "exactAgreement": not mismatches,
        "result": "SYNTHETIC_SEMANTIC_AGREEMENT" if not mismatches else "SYNTHETIC_SEMANTIC_MISMATCH",
        "executionBoundaries": {
            "realFrozenPopulationArtifactReadForValidation": True,
            "realFrozenPopulationExposedToComparator": False,
            "realFrozenPopulationEvaluated": False,
            "realCandidateCOutputProduced": False,
            "realCandidateCOutputInspected": False,
            "realCandidateCOutputRowCount": 0,
            "marketOutcomeRead": False,
            "priceDataRead": False,
            "providerAccessed": False,
            "swissEphemerisAccessed": False,
            "executionAllowed": False,
        },
    }


def load_and_run_frozen_synthetic_comparison(corpus_path: Path) -> dict[str, Any]:
    from .fixtures import load_fixture_corpus

    return run_frozen_synthetic_comparison(load_fixture_corpus(corpus_path))
