from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from .constants import CONTRIBUTORS, EXPECTED_BAV_TOTALS, EXPECTED_SAV_TOTAL, PLANETS
from .core import compute_bav, compute_sav, validate_chart


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = LAB_ROOT / "fixtures" / "bv_raman_standard_horoscope.json"


def load_fixture(path: str | Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def certify(path: str | Path = DEFAULT_FIXTURE, random_trials: int = 250) -> dict[str, Any]:
    fixture = load_fixture(path)
    actual_bav = compute_bav(fixture["sign_positions"])
    actual_sav = compute_sav(actual_bav)
    expected_bav = {planet: tuple(values) for planet, values in fixture["expected_bav"].items()}
    expected_sav = tuple(fixture["expected_sav"])

    fixture_rows = {planet: actual_bav[planet] == expected_bav[planet] for planet in PLANETS}
    fixture_passed = all(fixture_rows.values()) and actual_sav == expected_sav
    random_failures = []
    rng = random.Random(20260710)
    for trial in range(int(random_trials)):
        positions = {body: rng.randint(1, 12) for body in CONTRIBUTORS}
        bav = compute_bav(positions)
        sav = compute_sav(bav)
        validation = validate_chart(bav, sav)
        if not validation["passed"]:
            random_failures.append({"trial": trial, "positions": positions, "validation": validation})
            break

    constants_passed = all(
        sum(actual_bav[planet]) == EXPECTED_BAV_TOTALS[planet] for planet in PLANETS
    ) and sum(actual_sav) == EXPECTED_SAV_TOTAL
    internal_passed = fixture_passed and constants_passed and not random_failures
    return {
        "lab_id": "ashtakavarga_validation_v1_20260710",
        "certification_status": "partial_external_calculators_pending" if internal_passed else "failed",
        "internal_engine_passed": internal_passed,
        "published_fixture": {
            "name": fixture["fixture_id"],
            "source": fixture["source"],
            "row_matches": fixture_rows,
            "sav_matches": actual_sav == expected_sav,
            "passed": fixture_passed,
        },
        "constant_total_checks": {
            "expected_bav_totals": EXPECTED_BAV_TOTALS,
            "actual_bav_totals": {planet: sum(actual_bav[planet]) for planet in PLANETS},
            "expected_sav_total": EXPECTED_SAV_TOTAL,
            "actual_sav_total": sum(actual_sav),
            "passed": constants_passed,
        },
        "random_property_trials": {
            "count": int(random_trials),
            "failures": random_failures,
            "passed": not random_failures,
        },
        "outside_calculator_gate": {
            "required_independent_calculators": 2,
            "completed_independent_calculators": 0,
            "passed": False,
        },
        "trading_permission": False,
    }
