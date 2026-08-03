"""Consistency gates for the R4 read-only classical coverage ledger."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
MATRIX_PATH = ROOT / "configs" / "research" / "classical_oscillator_coverage_matrix_v1.yaml"
STATUS_PATH = ROOT / "status" / "classical_oscillator_coverage_v1.json"

REQUIRED_PARAMETER_FIELDS = {
    "parameterId",
    "displayName",
    "traditionalMeaning",
    "domain",
    "currentMode",
    "proposedMode",
    "oscillatorRole",
    "sourceTitle",
    "sourceEdition",
    "sourceLocator",
    "sourceProfileId",
    "sourceStatus",
    "sourceBackedValueOrRule",
    "implementationFormula",
    "dependencies",
}


def _matrix() -> dict:
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def test_coverage_matrix_has_a_complete_unique_parameter_register() -> None:
    matrix = _matrix()
    parameters = matrix["parameters"]
    assert parameters
    assert len({item["parameterId"] for item in parameters}) == len(parameters)
    for item in parameters:
        assert REQUIRED_PARAMETER_FIELDS <= item.keys()
        assert item["currentMode"] in matrix["allowedModes"]
        assert item["proposedMode"] in matrix["allowedModes"]
        assert item["oscillatorRole"] in matrix["allowedRoles"]
        assert item["sourceStatus"] in matrix["allowedStatuses"]
        assert item["dependencies"]


def test_blocked_and_fitted_parameters_cannot_be_ready_mode1() -> None:
    matrix = _matrix()
    prohibited = {
        "SOURCE_MISSING",
        "CONFLICTED",
        "MODE2_EMPIRICALLY_FITTED",
        "MODE2_ENGINEERING_HYPOTHESIS",
    }
    for item in matrix["parameters"]:
        if item["sourceStatus"] in prohibited:
            assert item["sourceStatus"] != "READY_MODE1_WITH_LIMITS"
            assert item["currentMode"] != "SOURCE_ONLY_BASELINE"


def test_mode1_excludes_strength_totals_and_wave_kernels() -> None:
    matrix = _matrix()
    excluded = {
        "SHADBALA_TOTAL",
        "DRIK_BALA",
        "ASHTAKAVARGA_TO_WAVE",
        "ARGHYA_PRICE_CONVERSION",
        "ASPECT_PHASE_KERNEL",
        "VEDHA_DURATION_KERNEL",
    }
    by_id = {item["parameterId"]: item for item in matrix["parameters"]}
    for parameter_id in excluded:
        assert by_id[parameter_id]["currentMode"] != "SOURCE_ONLY_BASELINE"


def test_status_summary_matches_machine_ledger_and_locks_remain_false() -> None:
    matrix = _matrix()
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    counts = Counter(item["sourceStatus"] for item in matrix["parameters"])
    assert status["parameterCount"] == len(matrix["parameters"])
    assert status["countsByStatus"] == {
        key: counts.get(key, 0) for key in status["countsByStatus"]
    }
    assert status["mode1ParameterCount"] == 0
    assert status["executionAllowed"] is False
    assert status["automaticOrderPlacement"] is False
    assert status["autoSuggestInfluenceAllowed"] is False
    assert status["financialValidationClaimed"] is False
    assert status["packagingAllowed"] is False
