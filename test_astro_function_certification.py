from __future__ import annotations

from pathlib import Path

from astro_function_certification import (
    CLASSICAL_PLANETS,
    SAMPLES,
    STRENGTH_FEATURE_PREFIXES,
    ExternalTemplateRow,
    build_position_baseline,
    compare_external_value,
    external_gate_summary,
    validate_external_import,
)
from doctrine_config import load_doctrine_config


def row(
    sample_id: str,
    feature_key: str,
    *,
    local: str = "10.0",
    expected: str = "10.0",
    status: str = "pass",
) -> ExternalTemplateRow:
    return ExternalTemplateRow(
        gate="Gate 3",
        sample_id=sample_id,
        feature_key=feature_key,
        local_value=local,
        external_expected_value=expected,
        external_source="saved JHora export",
        pass_fail=status,
        notes="test",
    )


def full_strength_matrix(status: str = "pass") -> list[ExternalTemplateRow]:
    return [
        row(sample.sample_id, f"{prefix}{planet}", status=status)
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
        for prefix in STRENGTH_FEATURE_PREFIXES
    ]


def test_strength_comparison_is_numeric_and_strict() -> None:
    assert compare_external_value("shadbala_implemented_total_virupa.SUN", "300", "300.49")[0] == "pass"
    assert compare_external_value("shadbala_implemented_total_virupa.SUN", "300", "300.51")[0] == "fail"
    assert compare_external_value("drik_bala_virupa.MOON", "-12.0", "-12.4")[0] == "pass"


def test_external_import_rejects_duplicate_unknown_and_unsourced_values() -> None:
    templates = [row("sample", "drik_bala_virupa.SUN")]
    external_rows = [
        {
            "gate": "Gate 3",
            "sample_id": "sample",
            "feature_key": "drik_bala_virupa.SUN",
            "external_expected_value": "10",
            "external_source": "",
        },
        {
            "gate": "Gate 3",
            "sample_id": "sample",
            "feature_key": "drik_bala_virupa.SUN",
            "external_expected_value": "10",
            "external_source": "duplicate",
        },
        {
            "gate": "Gate 3",
            "sample_id": "sample",
            "feature_key": "made_up_feature",
            "external_expected_value": "10",
            "external_source": "unknown",
        },
    ]
    issues = validate_external_import(templates, external_rows)
    assert any("has no external source" in issue for issue in issues)
    assert any("duplicate external key" in issue for issue in issues)
    assert any("unknown external key" in issue for issue in issues)


def test_gate_passes_only_for_complete_strength_matrix() -> None:
    gate = external_gate_summary(full_strength_matrix(), [], Path("missing.csv"))
    assert gate["status"] == "passed_external_validation"
    assert gate["certified"] is True
    assert gate["executionAllowed"] is False

    pending = full_strength_matrix()
    pending[0] = row(
        SAMPLES[0].sample_id,
        f"{STRENGTH_FEATURE_PREFIXES[0]}{CLASSICAL_PLANETS[0]}",
        expected="",
        status="pending",
    )
    gate = external_gate_summary(pending, [], Path("missing.csv"))
    assert gate["status"] == "blocked_pending_external_values"
    assert gate["certified"] is False


def test_local_certification_matrix_contains_finite_planet_values() -> None:
    config = load_doctrine_config(Path(__file__).with_name("doctrine_config.yaml"))
    positions, panchanga, templates = build_position_baseline(config)
    strength_rows = [
        item
        for item in templates
        if item.feature_key.startswith(STRENGTH_FEATURE_PREFIXES)
    ]
    assert len(positions) == len(SAMPLES) * 9
    assert len(panchanga) == len(SAMPLES)
    assert len(strength_rows) == len(SAMPLES) * len(CLASSICAL_PLANETS) * 2
    assert all(not item.local_value.startswith("needs ") for item in strength_rows)
    assert all(float(item.local_value) == float(item.local_value) for item in strength_rows)
