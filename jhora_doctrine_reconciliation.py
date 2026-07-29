from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from shadbala_component_comparator import (
    calculate_local_source_component_values,
)


CONTRACT = "GANN_JHORA_DOCTRINE_RECONCILIATION_V3"
FROZEN_TOLERANCE_VIRUPA = 0.5
CLASSICAL_PLANETS = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
)
TOTAL_COMPONENTS = ("sthana", "kaala", "dig", "chesta", "naisargika", "drik")

REPO_ROOT = Path(__file__).resolve().parent
EVIDENCE_DIR = REPO_ROOT / "status" / "evidence" / "jhora_shadbala_20260723"
DEFAULT_COMPARISON = (
    EVIDENCE_DIR / "jhora_pyjhora_component_comparison_20260726.csv"
)
DEFAULT_LOCAL_COMPONENTS = REPO_ROOT / "shadbala_component_residuals_20260718.csv"
DEFAULT_DOCTRINE_CONFIG = REPO_ROOT / "doctrine_config.yaml"
DEFAULT_DOCTRINE_MODULE = REPO_ROOT / "strict_shadbala_doctrine.py"
DEFAULT_KAALA_COMPONENTS = (
    REPO_ROOT / "shadbala_kaala_subcomponent_residuals_20260718.csv"
)
DEFAULT_KAALA_WITNESS_COMPARISON = (
    REPO_ROOT
    / "status"
    / "evidence"
    / "jhora_kaala_witness_20260727"
    / "jhora_kaala_profile_comparison_20260727.json"
)
DEFAULT_DRIK_LEDGER = REPO_ROOT / "drik_contribution_ledger_20260726.csv"
DEFAULT_FORMULA_INPUTS = REPO_ROOT / "pyjhora_shadbala_formula_inputs_20260718.csv"
DEFAULT_TOP_LEVEL_OUTPUT = (
    EVIDENCE_DIR / "jhora_local_doctrine_reconciliation_20260726.csv"
)
DEFAULT_DRIK_OUTPUT = (
    EVIDENCE_DIR / "jhora_drik_candidate_residuals_20260726.csv"
)
DEFAULT_JSON_OUTPUT = (
    EVIDENCE_DIR / "jhora_doctrine_reconciliation_20260726.json"
)
DEFAULT_REPORT_OUTPUT = REPO_ROOT / "jhora_doctrine_reconciliation_20260726.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile the locked JHora witness against the local source profile "
            "and named Drik sensitivity profiles without changing production doctrine."
        )
    )
    parser.add_argument("--comparison", type=Path, default=DEFAULT_COMPARISON)
    parser.add_argument(
        "--local-components", type=Path, default=DEFAULT_LOCAL_COMPONENTS
    )
    parser.add_argument(
        "--doctrine-config", type=Path, default=DEFAULT_DOCTRINE_CONFIG
    )
    parser.add_argument(
        "--kaala-components", type=Path, default=DEFAULT_KAALA_COMPONENTS
    )
    parser.add_argument(
        "--kaala-witness-comparison",
        type=Path,
        default=DEFAULT_KAALA_WITNESS_COMPARISON,
    )
    parser.add_argument("--drik-ledger", type=Path, default=DEFAULT_DRIK_LEDGER)
    parser.add_argument(
        "--formula-inputs", type=Path, default=DEFAULT_FORMULA_INPUTS
    )
    parser.add_argument(
        "--top-level-output", type=Path, default=DEFAULT_TOP_LEVEL_OUTPUT
    )
    parser.add_argument("--drik-output", type=Path, default=DEFAULT_DRIK_OUTPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path.resolve())


def unique_index(
    rows: list[dict[str, str]],
    keys: tuple[str, ...],
    *,
    source: Path,
) -> dict[tuple[str, ...], dict[str, str]]:
    indexed: dict[tuple[str, ...], dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        key = tuple(row[name].strip() for name in keys)
        if key in indexed:
            raise ValueError(f"{source}: row {row_number}: duplicate key {key}")
        indexed[key] = row
    return indexed


def corrected_local_total(
    components: dict[tuple[str, str, str], float],
    sample_id: str,
    planet: str,
) -> float:
    values = {
        component: components[(sample_id, planet, component)]
        for component in TOTAL_COMPONENTS
    }
    if planet in {"SUN", "MOON"}:
        values["chesta"] = 0.0
    return sum(values.values())


def reconciliation_classification(measure: str, planet: str) -> str:
    if measure == "sthana":
        return "independent_sthana_profile_residual"
    if measure == "kaala":
        return "local_source_profile_closer_requires_subcomponent_witness"
    if measure == "dig":
        return "independent_dig_profile_residual"
    if measure == "chesta" and planet in {"SUN", "MOON"}:
        return "luminary_display_only_excluded_from_total"
    if measure == "chesta":
        return "mean_longitude_profile_mixed_requires_reconciliation"
    if measure == "naisargika":
        return "independent_naisargika_alignment"
    if measure == "drik":
        return "independent_drik_profile_mismatch"
    if measure == "total" and planet in {"SUN", "MOON"}:
        return "corrected_total_excludes_luminary_chesta"
    return "corrected_local_source_total"


def build_top_level_rows(
    comparison_path: Path = DEFAULT_COMPARISON,
    doctrine_config_path: Path = DEFAULT_DOCTRINE_CONFIG,
) -> list[dict[str, str]]:
    local = calculate_local_source_component_values(doctrine_config_path)
    rows: list[dict[str, str]] = []
    for row in read_csv(comparison_path):
        measure = row["measure"].strip().lower()
        if measure not in {*TOTAL_COMPONENTS, "total"}:
            continue
        sample_id = row["sample_id"].strip()
        planet = row["planet"].strip().upper()
        if measure == "total":
            local_value = corrected_local_total(local, sample_id, planet)
        else:
            local_value = local[(sample_id, planet, measure)]
        jhora_value = float(row["jhora_value_virupa"])
        pyjhora_value = float(row["pyjhora_value_virupa"])
        local_delta = jhora_value - local_value
        pyjhora_delta = jhora_value - pyjhora_value
        local_absolute = abs(local_delta)
        pyjhora_absolute = abs(pyjhora_delta)
        nearest = (
            "local_source_profile"
            if local_absolute < pyjhora_absolute
            else "pyjhora_secondary_profile"
            if pyjhora_absolute < local_absolute
            else "tie"
        )
        rows.append(
            {
                "contract": CONTRACT,
                "sample_id": sample_id,
                "planet": planet,
                "measure": measure,
                "jhora_value_virupa": f"{jhora_value:.9f}",
                "local_source_value_virupa": f"{local_value:.9f}",
                "pyjhora_value_virupa": f"{pyjhora_value:.9f}",
                "jhora_minus_local_virupa": f"{local_delta:.9f}",
                "jhora_minus_pyjhora_virupa": f"{pyjhora_delta:.9f}",
                "local_absolute_delta_virupa": f"{local_absolute:.9f}",
                "pyjhora_absolute_delta_virupa": f"{pyjhora_absolute:.9f}",
                "nearest_profile": nearest,
                "local_pass_fail": (
                    "pass"
                    if local_absolute <= FROZEN_TOLERANCE_VIRUPA
                    else "fail"
                ),
                "classification": reconciliation_classification(measure, planet),
                "notes": (
                    "Diagnostic only. Luminary totals exclude displayed Chesta; "
                    "no tolerance widening and no execution authorization."
                ),
            }
        )
    expected_rows = 5 * len(CLASSICAL_PLANETS) * (len(TOTAL_COMPONENTS) + 1)
    if len(rows) != expected_rows:
        raise ValueError(
            f"top-level reconciliation expected {expected_rows} rows, "
            f"got {len(rows)}"
        )
    return rows


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    by_measure: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_measure[row["measure"]].append(row)

    result: dict[str, Any] = {}
    for measure in (*TOTAL_COMPONENTS, "total"):
        group = by_measure[measure]
        local_deltas = [float(row["local_absolute_delta_virupa"]) for row in group]
        pyjhora_deltas = [
            float(row["pyjhora_absolute_delta_virupa"]) for row in group
        ]
        result[measure] = {
            "rows": len(group),
            "localPass": sum(row["local_pass_fail"] == "pass" for row in group),
            "localFail": sum(row["local_pass_fail"] == "fail" for row in group),
            "localCloser": sum(
                row["nearest_profile"] == "local_source_profile" for row in group
            ),
            "pyjhoraCloser": sum(
                row["nearest_profile"] == "pyjhora_secondary_profile"
                for row in group
            ),
            "ties": sum(row["nearest_profile"] == "tie" for row in group),
            "localMeanAbsoluteDeltaVirupa": round(mean(local_deltas), 9),
            "localMaxAbsoluteDeltaVirupa": round(max(local_deltas), 9),
            "pyjhoraMeanAbsoluteDeltaVirupa": round(mean(pyjhora_deltas), 9),
            "pyjhoraMaxAbsoluteDeltaVirupa": round(max(pyjhora_deltas), 9),
        }
    return result


def kaala_categorical_residuals(
    top_level_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    quanta = (15.0, 30.0, 45.0, 60.0, 75.0, 90.0, 105.0, 120.0)
    diagnostics: list[dict[str, Any]] = []
    for row in top_level_rows:
        if row["measure"] != "kaala":
            continue
        residual = float(row["jhora_minus_local_virupa"])
        quantum = min(quanta, key=lambda value: abs(abs(residual) - value))
        remainder = abs(residual) - quantum
        if abs(residual) < 14.0 or abs(remainder) > 1.0:
            continue
        diagnostics.append(
            {
                "sampleId": row["sample_id"],
                "planet": row["planet"],
                "jhoraMinusLocalVirupa": round(residual, 9),
                "nearestCategoricalQuantumVirupa": quantum,
                "absoluteRemainderVirupa": round(abs(remainder), 9),
                "interpretation": (
                    "Possible 15/30/45/60-virupa lord-award disagreement; "
                    "requires a visible JHora Kaala subcomponent table."
                ),
            }
        )
    return diagnostics


def formula_longitudes(path: Path) -> dict[str, dict[str, float]]:
    longitudes: dict[str, dict[str, float]] = {}
    for row in read_csv(path):
        sample_id = row["sample_id"].strip()
        parsed = {
            str(planet).upper(): float(value)
            for planet, value in json.loads(row["classical_longitudes_json"]).items()
        }
        previous = longitudes.setdefault(sample_id, parsed)
        if previous != parsed:
            raise ValueError(f"{path}: inconsistent longitudes for {sample_id}")
    return longitudes


def bright_half_moon_nature(longitudes: dict[str, float]) -> tuple[str, float]:
    elongation = (longitudes["MOON"] - longitudes["SUN"]) % 360.0
    nature = "benefic" if 90.0 <= elongation <= 270.0 else "malefic"
    return nature, elongation


DRIK_PROFILES: tuple[dict[str, Any], ...] = (
    {
        "profile_id": "current_dynamic_nature_range_special",
        "moon_policy": "current",
        "mercury_policy": "current",
        "special_scale": 1.0,
    },
    {
        "profile_id": "current_dynamic_nature_no_range_special",
        "moon_policy": "current",
        "mercury_policy": "current",
        "special_scale": 0.0,
    },
    {
        "profile_id": "bright_half_moon_current_mercury_no_range_special",
        "moon_policy": "bright_half",
        "mercury_policy": "current",
        "special_scale": 0.0,
    },
    {
        "profile_id": "bright_half_moon_benefic_mercury_no_range_special",
        "moon_policy": "bright_half",
        "mercury_policy": "benefic",
        "special_scale": 0.0,
    },
    {
        "profile_id": "bright_half_moon_malefic_mercury_no_range_special",
        "moon_policy": "bright_half",
        "mercury_policy": "malefic",
        "special_scale": 0.0,
    },
)


def build_drik_candidate_rows(
    comparison_path: Path = DEFAULT_COMPARISON,
    drik_ledger_path: Path = DEFAULT_DRIK_LEDGER,
    formula_inputs_path: Path = DEFAULT_FORMULA_INPUTS,
) -> list[dict[str, str]]:
    jhora = {
        (row["sample_id"].strip(), row["planet"].strip().upper()): float(
            row["jhora_value_virupa"]
        )
        for row in read_csv(comparison_path)
        if row["measure"].strip().lower() == "drik"
    }
    contributions: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(drik_ledger_path):
        key = (row["sample_id"].strip(), row["target"].strip().upper())
        contributions[key].append(row)
    longitudes = formula_longitudes(formula_inputs_path)
    if set(jhora) != set(contributions):
        raise ValueError(
            "Drik comparison/contribution key mismatch: "
            f"missing={sorted(set(jhora) - set(contributions))}, "
            f"extra={sorted(set(contributions) - set(jhora))}"
        )

    rows: list[dict[str, str]] = []
    for profile in DRIK_PROFILES:
        for key in sorted(jhora):
            sample_id, target = key
            moon_nature, elongation = bright_half_moon_nature(
                longitudes[sample_id]
            )
            raw_net = 0.0
            for contribution in contributions[key]:
                nature = contribution["nature"].strip().lower()
                aspector = contribution["aspector"].strip().upper()
                if aspector == "MOON" and profile["moon_policy"] == "bright_half":
                    nature = moon_nature
                if (
                    aspector == "MERCURY"
                    and profile["mercury_policy"] != "current"
                ):
                    nature = str(profile["mercury_policy"])
                gross = float(contribution["base_virupa"]) + (
                    float(profile["special_scale"])
                    * float(contribution["special_bonus_virupa"])
                )
                raw_net += gross if nature == "benefic" else -gross
            predicted = raw_net / 4.0
            expected = jhora[key]
            residual = expected - predicted
            rows.append(
                {
                    "contract": CONTRACT,
                    "profile_id": str(profile["profile_id"]),
                    "sample_id": sample_id,
                    "target": target,
                    "moon_policy": str(profile["moon_policy"]),
                    "moon_elongation_deg": f"{elongation:.9f}",
                    "moon_candidate_nature": moon_nature,
                    "mercury_policy": str(profile["mercury_policy"]),
                    "special_aspect_scale": f"{float(profile['special_scale']):.1f}",
                    "normalization_divisor": "4.0",
                    "jhora_value_virupa": f"{expected:.9f}",
                    "candidate_value_virupa": f"{predicted:.9f}",
                    "signed_residual_virupa": f"{residual:.9f}",
                    "absolute_residual_virupa": f"{abs(residual):.9f}",
                    "pass_fail": (
                        "pass"
                        if abs(residual) <= FROZEN_TOLERANCE_VIRUPA
                        else "fail"
                    ),
                    "notes": (
                        "Sensitivity profile only. It cannot replace production "
                        "Drik without an explicit doctrine decision."
                    ),
                }
            )
    expected_count = len(DRIK_PROFILES) * 35
    if len(rows) != expected_count:
        raise ValueError(
            f"Drik candidate matrix expected {expected_count} rows, got {len(rows)}"
        )
    return rows


def summarize_drik_candidates(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["profile_id"]].append(row)
    summaries: list[dict[str, Any]] = []
    for profile in DRIK_PROFILES:
        profile_id = str(profile["profile_id"])
        group = grouped[profile_id]
        deltas = [float(row["absolute_residual_virupa"]) for row in group]
        summaries.append(
            {
                "profileId": profile_id,
                "rows": len(group),
                "pass": sum(row["pass_fail"] == "pass" for row in group),
                "fail": sum(row["pass_fail"] == "fail" for row in group),
                "meanAbsoluteDeltaVirupa": round(mean(deltas), 9),
                "maxAbsoluteDeltaVirupa": round(max(deltas), 9),
                "moonPolicy": profile["moon_policy"],
                "mercuryPolicy": profile["mercury_policy"],
                "specialAspectScale": profile["special_scale"],
                "normalizationDivisor": 4.0,
            }
        )
    return summaries


def chesta_diagnostics(
    top_level_rows: list[dict[str, str]],
    comparison_path: Path = DEFAULT_COMPARISON,
) -> dict[str, Any]:
    non_luminary = [
        row
        for row in top_level_rows
        if row["measure"] == "chesta" and row["planet"] not in {"SUN", "MOON"}
    ]
    jhora_values: dict[tuple[str, str, str], float] = {}
    for row in read_csv(comparison_path):
        key = (
            row["sample_id"].strip(),
            row["planet"].strip().upper(),
            row["measure"].strip().lower(),
        )
        jhora_values[key] = float(row["jhora_value_virupa"])

    excluded_residuals: list[float] = []
    included_residuals: list[float] = []
    sample_ids = sorted({key[0] for key in jhora_values})
    for sample_id in sample_ids:
        for planet in ("SUN", "MOON"):
            required = {
                measure: jhora_values[(sample_id, planet, measure)]
                for measure in (
                    "sthana",
                    "kaala",
                    "dig",
                    "chesta",
                    "naisargika",
                    "drik",
                    "total",
                )
            }
            without_chesta = sum(
                required[measure]
                for measure in ("sthana", "kaala", "dig", "naisargika", "drik")
            )
            excluded_residuals.append(required["total"] - without_chesta)
            included_residuals.append(
                required["total"] - (without_chesta + required["chesta"])
            )

    display_sum_tolerance = 0.06
    return {
        "luminaryRows": len(excluded_residuals),
        "jhoraTotalExcludesDisplayedChesta": sum(
            abs(value) <= display_sum_tolerance for value in excluded_residuals
        ),
        "excludedChestaMaxDisplayResidualVirupa": round(
            max(abs(value) for value in excluded_residuals), 9
        ),
        "includedChestaMinAbsoluteResidualVirupa": round(
            min(abs(value) for value in included_residuals), 9
        ),
        "nonLuminaryRows": len(non_luminary),
        "nonLuminaryLocalCloser": sum(
            row["nearest_profile"] == "local_source_profile"
            for row in non_luminary
        ),
        "nonLuminaryPyjhoraCloser": sum(
            row["nearest_profile"] == "pyjhora_secondary_profile"
            for row in non_luminary
        ),
        "totalPolicy": (
            "Sun and Moon Chesta is preserved as display evidence but excluded "
            "from Shadbala totals to prevent Ayana/Paksha double counting."
        ),
    }

def build_summary(
    comparison_path: Path = DEFAULT_COMPARISON,
    local_components_path: Path = DEFAULT_LOCAL_COMPONENTS,
    doctrine_config_path: Path = DEFAULT_DOCTRINE_CONFIG,
    kaala_components_path: Path = DEFAULT_KAALA_COMPONENTS,
    kaala_witness_comparison_path: Path = DEFAULT_KAALA_WITNESS_COMPARISON,
    drik_ledger_path: Path = DEFAULT_DRIK_LEDGER,
    formula_inputs_path: Path = DEFAULT_FORMULA_INPUTS,
) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
    top_level = build_top_level_rows(comparison_path, doctrine_config_path)
    drik_rows = build_drik_candidate_rows(
        comparison_path,
        drik_ledger_path,
        formula_inputs_path,
    )
    kaala_witness = json.loads(
        kaala_witness_comparison_path.read_text(encoding="utf-8")
    )
    if kaala_witness.get("contract") != "GANN_JHORA_KAALA_WITNESS_COMPARATOR_V1":
        raise ValueError("unexpected JHora Kaala witness contract")
    if kaala_witness.get("comparisonRows") != 350:
        raise ValueError("JHora Kaala witness must contain 350 comparison rows")
    kaala_components = dict(kaala_witness.get("components") or {})
    required_measures = {
        "abda",
        "ayana",
        "hora",
        "masa",
        "nathonnatha",
        "paksha",
        "total",
        "tribhaga",
        "vara",
        "yuddha",
    }
    if set(kaala_components) != required_measures:
        raise ValueError("JHora Kaala witness component set is incomplete")

    inputs = {
        "comparison": comparison_path,
        "tierBLocalComponents": local_components_path,
        "localDoctrineConfig": doctrine_config_path,
        "localDoctrineModule": DEFAULT_DOCTRINE_MODULE,
        "kaalaComponents": kaala_components_path,
        "kaalaVisibleWitness": kaala_witness_comparison_path,
        "drikLedger": drik_ledger_path,
        "formulaInputs": formula_inputs_path,
    }
    top_level_summary = summarize_rows(top_level)
    top_level_aligned = sorted(
        measure
        for measure, values in top_level_summary.items()
        if values["rows"] == 35
        and values["localPass"] == 35
        and values["localMaxAbsoluteDeltaVirupa"] <= FROZEN_TOLERANCE_VIRUPA
    )
    kaala_aligned = sorted(
        measure
        for measure, values in kaala_components.items()
        if measure != "total"
        and int(values.get("rows") or 0) == 35
        and int(values.get("localPass") or 0) == 35
        and float(values.get("localMaxVirupa") or 0.0)
        <= FROZEN_TOLERANCE_VIRUPA
    )
    summary = {
        "contract": CONTRACT,
        "generatedAtUtc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "status": "diagnostic_reconciliation_not_certified",
        "toleranceVirupa": FROZEN_TOLERANCE_VIRUPA,
        "tolerancePolicy": "frozen; no widening",
        "inputs": {
            name: {
                "path": relative_path(path),
                "sha256": sha256(path),
            }
            for name, path in inputs.items()
        },
        "topLevel": top_level_summary,
        "componentCertification": {
            "status": "partial_independent_witness_alignment",
            "independentWitnessComplete": True,
            "sourceCertified": False,
            "financiallyValidated": False,
            "executionAllowed": False,
            "policy": (
                "Production source-profile values are compared directly with the "
                "locked JHora witness. A component is witness-aligned only when "
                "all 35 locked rows pass at the frozen 0.5-virupa tolerance. "
                "Alignment does not by itself establish source certification, "
                "financial validity, or execution permission."
            ),
            "witnessAlignedTopLevel": top_level_aligned,
            "provisionalTopLevel": sorted(
                set(top_level_summary).difference(top_level_aligned)
            ),
            "witnessAlignedKaalaSubcomponents": kaala_aligned,
            "provisionalKaalaSubcomponents": sorted(
                set(kaala_components).difference(kaala_aligned)
            ),
            "fullShadbalaCertified": False,
            "drikCertified": False,
        },
        "kaalaVisibleWitness": {
            "contract": kaala_witness["contract"],
            "comparisonRows": kaala_witness["comparisonRows"],
            "components": kaala_components,
            "evidenceConclusions": list(
                kaala_witness.get("evidenceConclusions") or []
            ),
        },
        "kaalaCategoricalResiduals": kaala_categorical_residuals(top_level),
        "chesta": chesta_diagnostics(top_level, comparison_path),
        "drikCandidateProfiles": summarize_drik_candidates(drik_rows),
        "decisions": [
            (
                "Recognize Naisargika as independently witness-aligned in 35/35 "
                "top-level rows. This is component evidence only, not full "
                "Shadbala source certification or financial validation."
            ),
            (
                "Keep production Sthana provisional. The BPHS-labeled source "
                "profile passes only 1/35 locked JHora rows; the separately named "
                "PyJHora-compatible profile must remain diagnostic and must not "
                "be substituted into the production total."
            ),
            (
                "Promote dynamic Paksha classification: classical phase/nature "
                "rules and the locked visible JHora table agree in 35/35 rows "
                "within the frozen 0.5-virupa tolerance."
            ),
            (
                "Retain Abda, Masa, Vara, Tribhaga, and Yuddha: each matches "
                "all 35 visible JHora rows."
            ),
            (
                "Keep Hora provisional. It matches 33/35 rows, but the case-8 "
                "Moon/Saturn award remains a sunrise-boundary disagreement; do "
                "not replace the current algorithm with a temporal-hour guess."
            ),
            (
                "Keep Sthana, Dig, Nathonnatha, Ayana, aggregate Kaala, "
                "non-luminary Chesta, Drik, and full Shadbala uncertified until "
                "their remaining formula and time-basis residuals are "
                "independently reconciled."
            ),
            (
                "Promote luminary Chesta total exclusion: classical text and "
                "locked JHora total arithmetic independently agree that displayed "
                "Sun/Moon Chesta must not be added again."
            ),
            (
                "Retain the current production Drik profile as provisional and "
                "execution-ineligible. Named candidate profiles are sensitivity "
                "tests, not silent replacements."
            ),
        ],
    }
    return summary, top_level, drik_rows

def markdown_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    output.extend(
        "| " + " | ".join(str(value) for value in row) + " |" for row in rows
    )
    return output


def render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# JHora Doctrine Reconciliation",
        "",
        f"Contract: `{CONTRACT}`",
        "",
        "Status: diagnostic reconciliation; no execution authorization.",
        "",
        "Tolerance remains frozen at 0.5 virupa.",
        "",
        "## Top-Level Profile Comparison",
        "",
    ]
    lines.extend(
        markdown_table(
            [
                "Measure",
                "Local pass",
                "Local closer",
                "PyJHora closer",
                "Local MAE",
                "PyJHora MAE",
            ],
            [
                [
                    measure.title(),
                    f"{values['localPass']}/{values['rows']}",
                    values["localCloser"],
                    values["pyjhoraCloser"],
                    f"{values['localMeanAbsoluteDeltaVirupa']:.3f}",
                    f"{values['pyjhoraMeanAbsoluteDeltaVirupa']:.3f}",
                ]
                for measure, values in summary["topLevel"].items()
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Component Admission Boundary",
            "",
            summary["componentCertification"]["policy"],
            "",
            (
                "Witness-aligned top-level components: "
                + ", ".join(
                    summary["componentCertification"]["witnessAlignedTopLevel"]
                )
                + "."
            ),
            (
                "Witness-aligned Kaala subcomponents: "
                + ", ".join(
                    summary["componentCertification"][
                        "witnessAlignedKaalaSubcomponents"
                    ]
                )
                + "."
            ),
            (
                "Full Shadbala, Drik, source certification, financial validation, "
                "and execution remain blocked."
            ),
            "",
            "## Visible Kaala Subcomponent Witness",
            "",
        ]
    )
    kaala = summary["kaalaVisibleWitness"]["components"]
    lines.extend(
        markdown_table(
            ["Measure", "Local pass", "Local MAE", "Local max", "Decision"],
            [
                [
                    measure,
                    f"{kaala[measure]['localPass']}/{kaala[measure]['rows']}",
                    f"{kaala[measure]['localMaeVirupa']:.3f}",
                    f"{kaala[measure]['localMaxVirupa']:.3f}",
                    (
                        "retain"
                        if measure in {"abda", "masa", "vara", "tribhaga", "yuddha"}
                        else "promote dynamic nature"
                        if measure == "paksha"
                        else "provisional"
                    ),
                ]
                for measure in (
                    "abda",
                    "masa",
                    "vara",
                    "hora",
                    "tribhaga",
                    "paksha",
                    "nathonnatha",
                    "ayana",
                    "yuddha",
                    "total",
                )
            ],
        )
    )
    lines.extend(
        [
            "",
            "Paksha now has direct visible support in 35/35 rows. Hora remains "
            "33/35 because only case 8 changes the categorical award; the current "
            "fixed-hour algorithm is retained until that sunrise boundary is "
            "independently resolved. Nathonnatha, Ayana, and aggregate Kaala remain "
            "provisional.",
            "",
            "## Chesta Decision",
            "",
            (
                f"JHora's displayed total equals the sum with Sun/Moon Chesta "
                f"excluded in {summary['chesta']['jhoraTotalExcludesDisplayedChesta']}/"
                f"{summary['chesta']['luminaryRows']} luminary rows; maximum residual "
                f"is {summary['chesta']['excludedChestaMaxDisplayResidualVirupa']:.3f} "
                "virupa from two-decimal display rounding."
            ),
            "",
            summary["chesta"]["totalPolicy"],
            "",
            "Non-luminary Chesta remains mixed across mean-longitude profiles and "
            "is not promoted.",
            "",
            "## Drik Sensitivity Profiles",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            ["Profile", "Pass", "MAE", "Max", "Moon", "Mercury", "Special scale"],
            [
                [
                    row["profileId"],
                    f"{row['pass']}/{row['rows']}",
                    f"{row['meanAbsoluteDeltaVirupa']:.3f}",
                    f"{row['maxAbsoluteDeltaVirupa']:.3f}",
                    row["moonPolicy"],
                    row["mercuryPolicy"],
                    row["specialAspectScale"],
                ]
                for row in summary["drikCandidateProfiles"]
            ],
        )
    )
    lines.extend(
        [
            "",
            "The bright-half Moon/no-range-special profile is a useful doctrine "
            "lead, but the remaining Mercury and special-aspect residuals prevent "
            "promotion. Production Drik remains provisional and execution-locked.",
            "",
            "## Locked Decisions",
            "",
        ]
    )
    lines.extend(f"- {decision}" for decision in summary["decisions"])
    lines.append("")
    return "\n".join(lines)

def main() -> int:
    args = parse_args()
    summary, top_level, drik_rows = build_summary(
        args.comparison,
        args.local_components,
        args.doctrine_config,
        args.kaala_components,
        args.kaala_witness_comparison,
        args.drik_ledger,
        args.formula_inputs,
    )
    write_csv(args.top_level_output, top_level)
    write_csv(args.drik_output, drik_rows)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.write_text(render_report(summary), encoding="utf-8")
    print(
        json.dumps(
            {
                "contract": CONTRACT,
                "topLevelRows": len(top_level),
                "drikCandidateRows": len(drik_rows),
                "topLevelOutput": str(args.top_level_output),
                "drikOutput": str(args.drik_output),
                "jsonOutput": str(args.json_output),
                "reportOutput": str(args.report_output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
