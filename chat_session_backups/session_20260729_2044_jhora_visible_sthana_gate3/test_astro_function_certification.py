from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from astro_function_certification import (
    CLASSICAL_PLANETS,
    SAMPLES,
    STRENGTH_FEATURE_PREFIXES,
    ExternalTemplateRow,
    build_position_baseline,
    compare_external_value,
    external_gate_summary,
    independent_drik_gate_summary,
    kaala_capture_assistant_summary,
    kaala_formula_profile_gate_summary,
    merge_external_values,
    shadbala_component_witness_gate_summary,
    validate_external_import,
    visible_kaala_gate_summary,
    visible_sthana_gate_summary,
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


def test_external_merge_replaces_stale_local_methodology_and_keeps_provenance() -> None:
    templates = [
        ExternalTemplateRow(
            gate="Gate 3",
            sample_id="sample",
            feature_key="drik_bala_virupa.SUN",
            local_value="10.0",
            external_expected_value="",
            external_source="",
            pass_fail="pending",
            notes="Local strict-v6 BPHS source-profile value. Fill an independent witness.",
        )
    ]
    external_rows = [
        {
            "gate": "Gate 3",
            "sample_id": "sample",
            "feature_key": "drik_bala_virupa.SUN",
            "external_expected_value": "10.0",
            "external_source": "saved comparator",
            "notes": (
                "Local strict-v4 value with obsolete methodology. | "
                "Independent PyJHora Raman-mode export. | "
                "numeric delta=99.000000000; tolerance=0.5"
            ),
        }
    ]
    merged = merge_external_values(templates, external_rows)
    assert len(merged) == 1
    assert merged[0].pass_fail == "pass"
    assert "strict-v6" in merged[0].notes
    assert "strict-v4" not in merged[0].notes
    assert "Independent PyJHora Raman-mode export." in merged[0].notes
    assert merged[0].notes.count("numeric delta=") == 1


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


def test_independent_drik_witness_is_a_separate_fail_closed_gate() -> None:
    pending = [
        row(
            sample.sample_id,
            f"drik_bala_virupa.{planet}",
            expected="",
            status="pending",
        )
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
    ]
    gate = independent_drik_gate_summary(pending, [], None)
    assert gate["status"] == "blocked_pending_independent_values"
    assert gate["certified"] is False

    passed = [
        row(sample.sample_id, f"drik_bala_virupa.{planet}")
        for sample in SAMPLES
        for planet in CLASSICAL_PLANETS
    ]
    gate = independent_drik_gate_summary(passed, [], Path("missing.csv"))
    assert gate["status"] == "passed_independent_validation"
    assert gate["certified"] is True


def test_visible_kaala_witness_promotes_only_complete_subcomponents(
    tmp_path: Path,
) -> None:
    components = {
        name: {
            "rows": 35,
            "localPass": 35,
            "localMaeVirupa": 0.0,
            "localMaxVirupa": 0.0,
        }
        for name in (
            "abda",
            "masa",
            "vara",
            "tribhaga",
            "yuddha",
            "paksha",
            "hora",
            "nathonnatha",
            "ayana",
            "total",
        )
    }
    for name, passed in {
        "hora": 33,
        "nathonnatha": 11,
        "ayana": 13,
        "total": 4,
    }.items():
        components[name]["localPass"] = passed
    path = tmp_path / "visible_kaala.json"
    path.write_text(
        json.dumps(
            {
                "witnessRows": 350,
                "comparisonRows": 350,
                "toleranceVirupa": 0.5,
                "components": components,
            }
        ),
        encoding="utf-8",
    )

    gate = visible_kaala_gate_summary(path)

    assert gate["status"] == "partial_component_validation"
    assert gate["certified"] is False
    assert gate["aggregateKaalaCertified"] is False
    assert gate["promotedComponents"] == ["paksha"]
    assert gate["retainedValidatedComponents"] == [
        "abda",
        "masa",
        "vara",
        "tribhaga",
        "yuddha",
    ]
    assert gate["provisionalComponents"] == [
        "hora",
        "nathonnatha",
        "ayana",
        "total",
    ]


def test_visible_sthana_witness_keeps_compatibility_separate_from_source(
    tmp_path: Path,
) -> None:
    components = (
        "uchcha",
        "saptavargaja",
        "ojayugma",
        "kendradi",
        "drekkana",
    )

    def profile(passes: dict[str, int]) -> dict[str, object]:
        values = {
            component: {
                "rows": 35,
                "pass": passes.get(component, 35),
                "fail": 35 - passes.get(component, 35),
                "maeVirupa": 0.0,
                "maxErrorVirupa": (
                    0.01 if passes.get(component, 35) == 35 else 12.62
                ),
            }
            for component in components
        }
        total_pass = min(passes.values(), default=35)
        return {
            "profileId": "test-profile",
            "components": values,
            "total": {
                "rows": 35,
                "pass": total_pass,
                "fail": 35 - total_pass,
                "maeVirupa": 0.0,
                "maxErrorVirupa": 0.01 if total_pass == 35 else 12.62,
            },
        }

    locked_inputs: dict[str, dict[str, str]] = {}
    for name in ("witness", "topLevelWitness", "doctrineConfig"):
        input_path = tmp_path / f"{name}.txt"
        input_path.write_text(name, encoding="utf-8")
        locked_inputs[name] = {
            "path": str(input_path),
            "sha256": hashlib.sha256(input_path.read_bytes())
            .hexdigest()
            .upper(),
        }

    path = tmp_path / "visible_sthana.json"
    path.write_text(
        json.dumps(
            {
                "contract": (
                    "GANN_JHORA_STHANA_SUBCOMPONENT_COMPARATOR_V1"
                ),
                "status": "visible_witness_reconciled_diagnostic_only",
                "witnessContract": (
                    "GANN_JHORA_STHANA_SUBCOMPONENT_WITNESS_V1"
                ),
                "witnessRows": 175,
                "comparisonRows": 175,
                "toleranceVirupa": 0.5,
                "tolerancePolicy": "frozen; no widening",
                "productionProfile": "bphs_ch27_source",
                "productionChangeAllowed": False,
                "sourceCertified": False,
                "financiallyValidated": False,
                "executionAllowed": False,
                "inputs": locked_inputs,
                "profiles": {
                    "source": {
                        **profile({"saptavargaja": 3}),
                        "profileId": "bphs_ch27_source",
                    },
                    "pyjhora": {
                        **profile({"saptavargaja": 34}),
                        "profileId": "pyjhora_4_8_7_compatibility",
                    },
                    "jhora_visible": {
                        **profile({}),
                        "profileId": "jhora_8_visible_compatibility",
                    },
                },
                "evidenceConclusions": ["diagnostic only"],
            }
        ),
        encoding="utf-8",
    )

    gate = visible_sthana_gate_summary(path)

    assert gate["status"] == (
        "visible_component_matrix_aligned_diagnostic_only"
    )
    assert gate["independentWitnessComplete"] is True
    assert gate["compatibilityAligned"] is True
    assert gate["sourceAlignedComponents"] == [
        "drekkana",
        "kendradi",
        "ojayugma",
        "uchcha",
    ]
    assert gate["sourceDivergentComponents"] == ["saptavargaja"]
    assert gate["sourceCertified"] is False
    assert gate["productionChangeAllowed"] is False
    assert gate["executionAllowed"] is False


def test_visible_sthana_witness_rejects_tampered_locked_input(
    tmp_path: Path,
) -> None:
    summary_path = tmp_path / "visible_sthana.json"
    source_path = (
        Path(__file__).parent
        / "status"
        / "evidence"
        / "jhora_sthana_subcomponents_20260729"
        / "jhora_sthana_subcomponent_profile_comparison_20260729.json"
    )
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    tampered = tmp_path / "tampered.csv"
    tampered.write_text("changed", encoding="utf-8")
    payload["inputs"]["witness"]["path"] = str(tampered)
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    gate = visible_sthana_gate_summary(summary_path)

    assert gate["status"] == "blocked_incomplete_visible_sthana_witness"
    assert gate["compatibilityAligned"] is False
    assert "witness locked input SHA-256 mismatch" in gate["input"]["issues"]


def test_kaala_capture_assistant_is_available_but_cannot_promote() -> None:
    summary = kaala_capture_assistant_summary(Path(__file__).parent)

    assert summary["available"] is True
    assert summary["script"]["sha256"]
    assert summary["launcher"]["sha256"]
    assert summary["readsJHoraAutomatically"] is False
    assert summary["infersAstrologicalValues"] is False
    assert summary["overwritesPendingTemplates"] is False
    assert summary["productionChangeAllowed"] is False
    assert summary["executionAllowed"] is False


def test_kaala_formula_profiles_are_diagnostic_and_fail_closed(
    tmp_path: Path,
) -> None:
    profiles = {}
    for name, measure, passed in (
        ("nathonnatha_lmt_source", "nathonnatha", 11),
        ("nathonnatha_apparent_solar", "nathonnatha", 11),
        ("hora_astronomical_sunrise", "hora", 33),
        ("hora_variable_day_night", "hora", 27),
        ("ayana_actual_declination", "ayana", 13),
        ("ayana_tropical_projection", "ayana", 30),
    ):
        profiles[name] = {
            "measure": measure,
            "rows": 35,
            "pass": passed,
            "fail": 35 - passed,
            "maeVirupa": 0.3,
            "maxErrorVirupa": 2.1,
            "recentRows": 28,
            "recentPass": min(passed, 28),
            "historicalRows": 7,
            "historicalPass": max(0, passed - 28),
        }
    path = tmp_path / "formula_profiles.json"
    path.write_text(
        json.dumps(
            {
                "contract": (
                    "GANN_JHORA_KAALA_FORMULA_PROFILE_RECONCILIATION_V1"
                ),
                "status": "diagnostic_profiles_only_no_production_change",
                "toleranceVirupa": 0.5,
                "tolerancePolicy": "frozen; no widening",
                "profiles": profiles,
                "horaBoundary": {
                    "case_8_event_start": {
                        "gapMinutes": 3.436256,
                        "currentLord": "MOON",
                        "jhoraLord": "SATURN",
                        "swissApparentTipSunriseLmtHour": 6.367290929,
                        "awardFlipSunriseLmtHour": 6.31002,
                    }
                },
                "workedExamples": {},
                "evidenceConclusions": ["No production formula changed."],
            }
        ),
        encoding="utf-8",
    )

    gate = kaala_formula_profile_gate_summary(path)

    assert gate["status"] == (
        "diagnostic_profiles_only_no_production_change"
    )
    assert gate["certified"] is False
    assert gate["productionChangeAllowed"] is False
    assert gate["profiles"]["ayana_tropical_projection"]["pass"] == 30
    assert gate["horaBoundary"]["case_8_event_start"]["gapMinutes"] == (
        3.436256
    )

    missing = kaala_formula_profile_gate_summary(
        tmp_path / "missing.json"
    )
    assert missing["status"] == "blocked_missing_kaala_formula_profiles"
    assert missing["productionChangeAllowed"] is False


def test_shadbala_component_witness_admits_only_row_complete_components(
    tmp_path: Path,
) -> None:
    top_level = {
        name: {
            "rows": 35,
            "localPass": 35 if name == "naisargika" else 34,
            "localFail": 0 if name == "naisargika" else 1,
            "localMeanAbsoluteDeltaVirupa": 0.01,
            "localMaxAbsoluteDeltaVirupa": (
                0.01 if name == "naisargika" else 1.0
            ),
        }
        for name in (
            "sthana",
            "kaala",
            "dig",
            "chesta",
            "naisargika",
            "drik",
            "total",
        )
    }
    path = tmp_path / "shadbala_components.json"
    path.write_text(
        json.dumps(
            {
                "contract": "GANN_JHORA_DOCTRINE_RECONCILIATION_V3",
                "topLevel": top_level,
                "componentCertification": {
                    "independentWitnessComplete": True,
                    "witnessAlignedTopLevel": ["naisargika"],
                    "provisionalTopLevel": [
                        "chesta",
                        "dig",
                        "drik",
                        "kaala",
                        "sthana",
                        "total",
                    ],
                    "witnessAlignedKaalaSubcomponents": [
                        "abda",
                        "masa",
                        "paksha",
                        "tribhaga",
                        "vara",
                        "yuddha",
                    ],
                    "provisionalKaalaSubcomponents": [
                        "ayana",
                        "hora",
                        "nathonnatha",
                        "total",
                    ],
                    "fullShadbalaCertified": False,
                    "drikCertified": False,
                },
            }
        ),
        encoding="utf-8",
    )

    gate = shadbala_component_witness_gate_summary(path)

    assert gate["status"] == "partial_independent_witness_alignment"
    assert gate["independentWitnessComplete"] is True
    assert gate["witnessAlignedTopLevel"] == ["naisargika"]
    assert gate["topLevel"]["naisargika"]["witnessAligned"] is True
    assert gate["topLevel"]["drik"]["witnessAligned"] is False
    assert gate["sourceCertified"] is False
    assert gate["financiallyValidated"] is False
    assert gate["executionAllowed"] is False
    assert gate["fullShadbalaCertified"] is False

    stale = json.loads(path.read_text(encoding="utf-8"))
    stale["contract"] = "GANN_JHORA_DOCTRINE_RECONCILIATION_V2"
    path.write_text(json.dumps(stale), encoding="utf-8")

    stale_gate = shadbala_component_witness_gate_summary(path)
    assert stale_gate["status"] == "blocked_stale_component_witness_contract"
    assert stale_gate["executionAllowed"] is False


def test_local_certification_matrix_contains_finite_planet_values() -> None:
    config = load_doctrine_config(Path(__file__).with_name("doctrine_config.yaml"))
    positions, panchanga, templates, drik_contributions = build_position_baseline(config)
    strength_rows = [
        item
        for item in templates
        if item.feature_key.startswith(STRENGTH_FEATURE_PREFIXES)
    ]
    assert len(positions) == len(SAMPLES) * 9
    assert len(panchanga) == len(SAMPLES)
    assert len(drik_contributions) == len(SAMPLES) * len(CLASSICAL_PLANETS) * 6
    assert all(item.nature_reason for item in drik_contributions)
    assert len(strength_rows) == len(SAMPLES) * len(CLASSICAL_PLANETS) * 2
    assert all(not item.local_value.startswith("needs ") for item in strength_rows)
    assert all(float(item.local_value) == float(item.local_value) for item in strength_rows)


def test_reconciled_drik_matches_saved_pyjhora_tier_b_matrix() -> None:
    root = Path(__file__).parent
    config = load_doctrine_config(root / "doctrine_config.yaml")
    _positions, _panchanga, templates, _contributions = build_position_baseline(config)
    local = {
        (item.sample_id, item.feature_key): float(item.local_value)
        for item in templates
        if item.feature_key.startswith("drik_bala_virupa.")
    }
    with (root / "pyjhora_external_strength_values_20260718.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        expected = {
            (row["sample_id"], row["feature_key"]): float(row["external_expected_value"])
            for row in csv.DictReader(handle)
            if row["feature_key"].startswith("drik_bala_virupa.")
        }
    assert len(local) == len(SAMPLES) * len(CLASSICAL_PLANETS)
    assert local.keys() == expected.keys()
    residuals = {
        key: abs(local_value - expected[key])
        for key, local_value in local.items()
    }
    assert max(residuals.values()) <= 0.5, sorted(
        residuals.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]


def test_reconciled_drik_contributions_match_saved_pyjhora_ledger() -> None:
    root = Path(__file__).parent
    config = load_doctrine_config(root / "doctrine_config.yaml")
    _positions, _panchanga, _templates, local_rows = build_position_baseline(config)
    local = {
        (row.sample_id, row.target, row.aspector): row
        for row in local_rows
    }
    with (root / "pyjhora_drik_contributions_20260718.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        external = {
            (row["sample_id"], row["target"], row["aspector"]): row
            for row in csv.DictReader(handle)
        }
    assert len(local) == len(SAMPLES) * len(CLASSICAL_PLANETS) * 6
    assert local.keys() == external.keys()
    for key, local_row in local.items():
        expected = external[key]
        assert local_row.nature == expected["nature"], key
        assert abs(float(local_row.angle_deg) - float(expected["angle_deg"])) <= 0.021, key
        assert abs(local_row.gross_virupa - float(expected["gross_virupa"])) <= 0.021, key
        assert abs(
            local_row.raw_signed_virupa - float(expected["raw_signed_virupa"])
        ) <= 0.021, key
        assert abs(
            local_row.normalized_signed_virupa
            - float(expected["normalized_signed_virupa"])
        ) <= 0.0051, key
