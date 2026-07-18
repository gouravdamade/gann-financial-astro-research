from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


PYJHORA_VERSION = "4.8.7"
PYJHORA_WHEEL_SHA256 = "D8D8014573A38DDEFEDCAE57D3B8D84687CAC2AD31BB5B1DD70D945906A4D54D"
PLANETS = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN")
SHADBALA_COMPONENTS = (
    "sthana",
    "kaala",
    "dig",
    "chesta",
    "naisargika",
    "drik",
)
KAALA_SUBCOMPONENTS = (
    "nathonnatha",
    "paksha",
    "tribhaga",
    "abda",
    "masa",
    "vara",
    "hora",
    "ayana",
    "yuddha",
    "total",
)
STRENGTH_PREFIXES = (
    "shadbala_implemented_total_virupa.",
    "drik_bala_virupa.",
)
BVRAMAN_DRIK_EXPECTED = (15.86, -21.73, 0.95, 15.64, -16.04, 18.47, 7.21)
BVRAMAN_DRIK_TOLERANCE = 0.05


@dataclass(frozen=True)
class Fixture:
    sample_id: str
    local_iso: str
    timezone: str
    latitude: float
    longitude: float
    location: str


FIXTURES = (
    Fixture(
        "case_8_event_start",
        "2025-03-07T19:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_43_event_start",
        "2025-04-04T02:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_103_event_start",
        "2025-05-15T22:30:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "case_127_sr_touch_start",
        "2025-05-28T22:00:00",
        "Asia/Kolkata",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
    Fixture(
        "gann_reference_tokyo",
        "1889-02-11T00:00:00",
        "Asia/Tokyo",
        35.6762,
        139.6503,
        "Tokyo reference location",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export hash-pinned PyJHora Shadbala/Drik values for Gate 3."
    )
    parser.add_argument(
        "--pyjhora-root",
        type=Path,
        default=Path(r"D:\GannFinancialAstro\external_validators\pyjhora_4_8_7"),
    )
    parser.add_argument(
        "--wheel",
        type=Path,
        default=Path(
            r"D:\GannFinancialAstro\external_validators\wheels"
            r"\pyjhora-4.8.7-py3-none-any.whl"
        ),
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(r"D:\PycharmProjects\astro_external_validation_template_20260718.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_external_strength_values_20260718.csv"),
    )
    parser.add_argument(
        "--contribution-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_drik_contributions_20260718.csv"),
    )
    parser.add_argument(
        "--component-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_shadbala_components_20260718.csv"),
    )
    parser.add_argument(
        "--kaala-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_kaala_subcomponents_20260718.csv"),
    )
    parser.add_argument(
        "--formula-input-output",
        type=Path,
        default=Path(r"D:\PycharmProjects\pyjhora_shadbala_formula_inputs_20260718.csv"),
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def metadata_version(pyjhora_root: Path) -> str:
    candidates = list(pyjhora_root.glob("PyJHora-*.dist-info/METADATA"))
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one PyJHora METADATA file.")
    for line in candidates[0].read_text(encoding="utf-8").splitlines():
        if line.startswith("Version:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("PyJHora METADATA has no Version field.")


def require_pinned_install(pyjhora_root: Path, wheel: Path) -> str:
    if not pyjhora_root.is_dir():
        raise FileNotFoundError(f"PyJHora root does not exist: {pyjhora_root}")
    if not wheel.is_file():
        raise FileNotFoundError(f"PyJHora wheel does not exist: {wheel}")
    version = metadata_version(pyjhora_root)
    if version != PYJHORA_VERSION:
        raise RuntimeError(f"Expected PyJHora {PYJHORA_VERSION}, found {version}.")
    digest = sha256(wheel)
    if digest != PYJHORA_WHEEL_SHA256:
        raise RuntimeError(f"PyJHora wheel hash mismatch: {digest}")
    return digest


def civil_time_parts(fixture: Fixture) -> tuple[tuple[int, int, int], tuple[int, int, int], float]:
    local = datetime.fromisoformat(fixture.local_iso).replace(tzinfo=ZoneInfo(fixture.timezone))
    offset = local.utcoffset()
    if offset is None:
        raise RuntimeError(f"Timezone has no UTC offset for {fixture.sample_id}.")
    return (
        (local.year, local.month, local.day),
        (local.hour, local.minute, local.second),
        offset.total_seconds() / 3600.0,
    )


def assert_bvraman_reference(utils: Any, strength: Any, drik: Any) -> list[float]:
    drik.set_ayanamsa_mode("RAMAN")
    jd = utils.julian_day_number((1918, 10, 16), (14, 22, 16))
    place = drik.Place("Bangalore B.V. Raman reference", 13.0, 77 + 35 / 60, 5.5)
    actual = [float(value) for value in strength._drik_bala(jd, place)]
    deltas = [abs(value - expected) for value, expected in zip(actual, BVRAMAN_DRIK_EXPECTED)]
    if len(actual) != len(BVRAMAN_DRIK_EXPECTED) or max(deltas) > BVRAMAN_DRIK_TOLERANCE:
        raise RuntimeError(
            "PyJHora B.V. Raman Drik reference failed: "
            f"actual={actual}, expected={list(BVRAMAN_DRIK_EXPECTED)}, deltas={deltas}"
        )
    return actual


def calculate_strengths(pyjhora_root: Path) -> dict[tuple[str, str], float]:
    sys.path.insert(0, str(pyjhora_root))
    from jhora import utils
    from jhora.horoscope.chart import strength
    from jhora.panchanga import drik

    assert_bvraman_reference(utils, strength, drik)
    values: dict[tuple[str, str], float] = {}
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        drik_values = [float(value) for value in strength._drik_bala(jd, place)]
        shadbala_values = [float(value) for value in strength.shad_bala(jd, place)[6]]
        if len(drik_values) != len(PLANETS) or len(shadbala_values) != len(PLANETS):
            raise RuntimeError(f"Unexpected PyJHora strength vector for {fixture.sample_id}.")
        for index, planet in enumerate(PLANETS):
            values[(fixture.sample_id, f"shadbala_implemented_total_virupa.{planet}")] = (
                shadbala_values[index]
            )
            values[(fixture.sample_id, f"drik_bala_virupa.{planet}")] = drik_values[index]
    return values


def component_rows_from_vectors(
    sample_id: str,
    vectors: list[Any],
    source: str,
) -> list[dict[str, str]]:
    if len(vectors) < len(SHADBALA_COMPONENTS):
        raise RuntimeError(
            f"Expected {len(SHADBALA_COMPONENTS)} Shadbala vectors, got {len(vectors)}."
        )
    rows: list[dict[str, str]] = []
    for component_index, component in enumerate(SHADBALA_COMPONENTS):
        vector = list(vectors[component_index])
        if len(vector) != len(PLANETS):
            raise RuntimeError(
                f"Unexpected {component} vector length for {sample_id}: {len(vector)}"
            )
        for planet_index, planet in enumerate(PLANETS):
            rows.append(
                {
                    "sample_id": sample_id,
                    "planet": planet,
                    "component": component,
                    "external_value_virupa": f"{float(vector[planet_index]):.9f}",
                    "source": source,
                }
            )
    return rows


def calculate_shadbala_components(
    pyjhora_root: Path,
    source: str,
) -> list[dict[str, str]]:
    if str(pyjhora_root) not in sys.path:
        sys.path.insert(0, str(pyjhora_root))
    from jhora import utils
    from jhora.horoscope.chart import strength
    from jhora.panchanga import drik

    rows: list[dict[str, str]] = []
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        vectors = list(strength.shad_bala(jd, place))
        vectors[SHADBALA_COMPONENTS.index("dig")] = strength._dig_bala(
            jd,
            place,
            method=2,
        )
        rows.extend(component_rows_from_vectors(fixture.sample_id, vectors, source))
    expected_rows = len(FIXTURES) * len(PLANETS) * len(SHADBALA_COMPONENTS)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} PyJHora component rows, got {len(rows)}."
        )
    return rows


def kaala_rows_from_vectors(
    sample_id: str,
    vectors: dict[str, Any],
    source: str,
) -> list[dict[str, str]]:
    if set(vectors) != set(KAALA_SUBCOMPONENTS):
        missing = sorted(set(KAALA_SUBCOMPONENTS) - set(vectors))
        extra = sorted(set(vectors) - set(KAALA_SUBCOMPONENTS))
        raise RuntimeError(
            f"Kaala vector mismatch for {sample_id}: missing={missing}, extra={extra}"
        )
    rows: list[dict[str, str]] = []
    for measure in KAALA_SUBCOMPONENTS:
        vector = list(vectors[measure])
        if len(vector) != len(PLANETS):
            raise RuntimeError(
                f"Unexpected {measure} vector length for {sample_id}: {len(vector)}"
            )
        for planet_index, planet in enumerate(PLANETS):
            rows.append(
                {
                    "sample_id": sample_id,
                    "planet": planet,
                    "measure": measure,
                    "external_value_virupa": f"{float(vector[planet_index]):.9f}",
                    "source": source,
                }
            )
    return rows


def calculate_kaala_subcomponents(
    pyjhora_root: Path,
    source: str,
) -> list[dict[str, str]]:
    if str(pyjhora_root) not in sys.path:
        sys.path.insert(0, str(pyjhora_root))
    from jhora import utils
    from jhora.horoscope.chart import strength
    from jhora.panchanga import drik

    functions = {
        "nathonnatha": strength._nathonnath_bala,
        "paksha": strength._paksha_bala,
        "tribhaga": strength._tribhaga_bala,
        "abda": strength._abdadhipathi,
        "masa": strength._masadhipathi,
        "vara": strength._vaaradhipathi,
        "hora": strength._hora_bala,
        "ayana": strength._ayana_bala,
        "yuddha": strength._yuddha_bala,
        "total": strength._kaala_bala,
    }
    rows: list[dict[str, str]] = []
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        vectors = {
            measure: function(jd, place)
            for measure, function in functions.items()
        }
        rows.extend(kaala_rows_from_vectors(fixture.sample_id, vectors, source))
    expected_rows = (
        len(FIXTURES) * len(PLANETS) * len(KAALA_SUBCOMPONENTS)
    )
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} PyJHora Kaala rows, got {len(rows)}."
        )
    return rows


def formula_input_row(
    *,
    sample_id: str,
    planet: str,
    planet_longitude_deg: float,
    chesta_true_longitude_deg: float,
    ascendant_longitude_deg: float,
    classical_longitudes: dict[str, float],
    mean_sun_longitude_deg: float | None,
    mean_planet_longitude_deg: float | None,
    external_chesta_virupa: float,
    source: str,
) -> dict[str, str]:
    if mean_sun_longitude_deg is None or mean_planet_longitude_deg is None:
        seegrocha = None
        midpoint = None
        reduced = None
    elif planet in {"MERCURY", "VENUS"}:
        seegrocha = mean_planet_longitude_deg
        midpoint = 0.5 * (
            chesta_true_longitude_deg + mean_sun_longitude_deg
        )
        reduced = abs(seegrocha - midpoint)
    else:
        seegrocha = mean_sun_longitude_deg
        midpoint = 0.5 * (
            chesta_true_longitude_deg + mean_planet_longitude_deg
        )
        reduced = abs(seegrocha - midpoint)
    return {
        "sample_id": sample_id,
        "planet": planet,
        "planet_longitude_deg": f"{float(planet_longitude_deg):.12f}",
        "chesta_true_longitude_deg": f"{float(chesta_true_longitude_deg):.12f}",
        "ascendant_longitude_deg": f"{float(ascendant_longitude_deg):.12f}",
        "classical_longitudes_json": json.dumps(
            classical_longitudes,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "mean_sun_longitude_deg": (
            "" if mean_sun_longitude_deg is None
            else f"{float(mean_sun_longitude_deg):.12f}"
        ),
        "mean_planet_longitude_deg": (
            "" if mean_planet_longitude_deg is None
            else f"{float(mean_planet_longitude_deg):.12f}"
        ),
        "seegrocha_longitude_deg": (
            "" if seegrocha is None else f"{float(seegrocha):.12f}"
        ),
        "mean_true_midpoint_linear_deg": (
            "" if midpoint is None else f"{float(midpoint):.12f}"
        ),
        "reduced_chesta_kendra_deg": (
            "" if reduced is None else f"{float(reduced):.12f}"
        ),
        "external_chesta_virupa": f"{float(external_chesta_virupa):.9f}",
        "source": source,
    }


def calculate_formula_inputs(
    pyjhora_root: Path,
    source: str,
) -> list[dict[str, str]]:
    if str(pyjhora_root) not in sys.path:
        sys.path.insert(0, str(pyjhora_root))
    from jhora import const, utils
    from jhora.horoscope.chart import charts, strength
    from jhora.panchanga import drik

    rows: list[dict[str, str]] = []
    chesta_planets = {
        "MARS": const._MARS,
        "MERCURY": const._MERCURY,
        "JUPITER": const._JUPITER,
        "VENUS": const._VENUS,
        "SATURN": const._SATURN,
    }
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        rasi_positions = charts.rasi_chart(jd, place)
        chesta_positions = drik.dhasavarga(
            jd,
            place,
            divisional_chart_factor=1,
        )
        ascendant_longitude = (
            float(rasi_positions[0][1][0]) * 30.0
            + float(rasi_positions[0][1][1])
        )
        classical_longitudes = {
            planet: (
                float(rasi_positions[index + 1][1][0]) * 30.0
                + float(rasi_positions[index + 1][1][1])
            )
            for index, planet in enumerate(PLANETS)
        }
        chesta_true_longitudes = {
            planet: (
                float(chesta_positions[index][1][0]) * 30.0
                + float(chesta_positions[index][1][1])
            )
            for index, planet in enumerate(PLANETS)
        }
        mean_sun = float(
            strength.get_planet_mean_longitude(
                jd,
                place,
                const._SUN,
            )
        )
        external_chesta = list(
            strength._cheshta_bala_new(
                jd,
                place,
                use_epoch_table=True,
            )
        )
        for index, planet in enumerate(PLANETS):
            mean_planet: float | None = None
            if planet in chesta_planets:
                p_id = drik.planet_list[chesta_planets[planet]]
                mean_planet = float(
                    strength.get_planet_mean_longitude_using_epoch_table(
                        jd,
                        place,
                        p_id,
                    )
                )
            rows.append(
                formula_input_row(
                    sample_id=fixture.sample_id,
                    planet=planet,
                    planet_longitude_deg=classical_longitudes[planet],
                    chesta_true_longitude_deg=chesta_true_longitudes[planet],
                    ascendant_longitude_deg=ascendant_longitude,
                    classical_longitudes=classical_longitudes,
                    mean_sun_longitude_deg=(
                        mean_sun if mean_planet is not None else None
                    ),
                    mean_planet_longitude_deg=mean_planet,
                    external_chesta_virupa=float(external_chesta[index]),
                    source=source,
                )
            )
    expected_rows = len(FIXTURES) * len(PLANETS)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} PyJHora formula-input rows, got {len(rows)}."
        )
    return rows


def calculate_drik_contributions(pyjhora_root: Path) -> list[dict[str, str]]:
    if str(pyjhora_root) not in sys.path:
        sys.path.insert(0, str(pyjhora_root))
    from jhora import const, utils
    from jhora.horoscope.chart import charts, strength
    from jhora.panchanga import drik

    aspect_strength = getattr(strength, "__drik_bala_calc_1")
    rows: list[dict[str, str]] = []
    for fixture in FIXTURES:
        date_parts, time_parts, utc_offset_hours = civil_time_parts(fixture)
        drik.set_ayanamsa_mode("RAMAN")
        jd = utils.julian_day_number(date_parts, time_parts)
        place = drik.Place(
            fixture.location,
            fixture.latitude,
            fixture.longitude,
            utc_offset_hours,
        )
        positions = charts.rasi_chart(jd, place)[: const._pp_count_upto_ketu]
        classical_positions = positions[1:-2]
        benefics, malefics = charts.benefics_and_malefics(
            jd,
            place,
            exclude_rahu_ketu=True,
        )
        for target_id, target in enumerate(PLANETS):
            target_sign, target_degree = classical_positions[target_id][1]
            target_lon = target_sign * 30.0 + target_degree
            for aspector_id, aspector in enumerate(PLANETS):
                if aspector_id == target_id:
                    continue
                aspector_sign, aspector_degree = classical_positions[aspector_id][1]
                aspector_lon = aspector_sign * 30.0 + aspector_degree
                angle = round((360.0 + target_lon - aspector_lon) % 360.0, 2)
                gross = round(
                    float(aspect_strength(angle, aspector_id, target_id)),
                    2,
                )
                if aspector_id in benefics:
                    nature = "benefic"
                    sign = 1.0
                elif aspector_id in malefics:
                    nature = "malefic"
                    sign = -1.0
                else:
                    raise RuntimeError(
                        f"PyJHora did not classify {aspector} for {fixture.sample_id}."
                    )
                raw_signed = round(gross * sign, 2)
                rows.append(
                    {
                        "sample_id": fixture.sample_id,
                        "target": target,
                        "aspector": aspector,
                        "angle_deg": f"{angle:.2f}",
                        "nature": nature,
                        "gross_virupa": f"{gross:.2f}",
                        "raw_signed_virupa": f"{raw_signed:.2f}",
                        "normalized_signed_virupa": f"{raw_signed / 4.0:.6f}",
                        "source": (
                            f"PyJHora {PYJHORA_VERSION}; Raman; wheel "
                            f"{PYJHORA_WHEEL_SHA256}"
                        ),
                    }
                )
    expected_rows = len(FIXTURES) * len(PLANETS) * (len(PLANETS) - 1)
    if len(rows) != expected_rows:
        raise RuntimeError(
            f"Expected {expected_rows} PyJHora Drik contributions, got {len(rows)}."
        )
    return rows


def merge_strength_rows(
    rows: list[dict[str, str]],
    values: dict[tuple[str, str], float],
    source: str,
) -> tuple[list[dict[str, str]], int]:
    provenance_note = (
        "Independent PyJHora Raman-mode export; shad_bala()[6] total or "
        "private _drik_bala() value."
    )
    expected_keys = {
        (fixture.sample_id, f"{prefix}{planet}")
        for fixture in FIXTURES
        for prefix in STRENGTH_PREFIXES
        for planet in PLANETS
    }
    if set(values) != expected_keys:
        missing = sorted(expected_keys - set(values))
        extra = sorted(set(values) - expected_keys)
        raise RuntimeError(f"Strength matrix mismatch: missing={missing}, extra={extra}")

    updated = 0
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for original in rows:
        row = dict(original)
        key = (row.get("sample_id", ""), row.get("feature_key", ""))
        if key in values:
            if key in seen:
                raise RuntimeError(f"Duplicate strength row in template: {key}")
            seen.add(key)
            row["external_expected_value"] = f"{values[key]:.9f}"
            row["external_source"] = source
            row["pass_fail"] = "pending_gate_comparison"
            note_parts = [
                part.strip()
                for part in str(row.get("notes") or "").split(" | ")
                if part.strip()
            ]
            base_parts = [
                part
                for part in note_parts
                if not part.startswith("numeric delta=")
                and part != "No external expected value entered."
                and part != provenance_note
            ]
            row["notes"] = " | ".join((*base_parts, provenance_note))
            updated += 1
        result.append(row)
    if seen != expected_keys:
        raise RuntimeError(f"Template is missing strength rows: {sorted(expected_keys - seen)}")
    return result, updated


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return list(reader.fieldnames), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    wheel_hash = require_pinned_install(args.pyjhora_root, args.wheel)
    fieldnames, rows = read_csv(args.template)
    values = calculate_strengths(args.pyjhora_root)
    contributions = calculate_drik_contributions(args.pyjhora_root)
    source = (
        f"PyJHora {PYJHORA_VERSION} Tier B isolated export; Raman ayanamsa; "
        f"wheel sha256 {wheel_hash}; event civil timezone; Tokyo reference coordinates; "
        "Dig uses _dig_bala(method=2) canonical bounded circular-distance variant because "
        "the package default method=1 can exceed 60 virupa"
    )
    components = calculate_shadbala_components(args.pyjhora_root, source)
    kaala_subcomponents = calculate_kaala_subcomponents(
        args.pyjhora_root,
        source,
    )
    formula_inputs = calculate_formula_inputs(args.pyjhora_root, source)
    merged, updated = merge_strength_rows(rows, values, source)
    if updated != len(FIXTURES) * len(PLANETS) * len(STRENGTH_PREFIXES):
        raise RuntimeError(f"Expected 70 strength updates, wrote {updated}.")
    write_csv(args.output, fieldnames, merged)
    write_csv(
        args.contribution_output,
        list(contributions[0]),
        contributions,
    )
    write_csv(
        args.component_output,
        list(components[0]),
        components,
    )
    write_csv(
        args.kaala_output,
        list(kaala_subcomponents[0]),
        kaala_subcomponents,
    )
    write_csv(
        args.formula_input_output,
        list(formula_inputs[0]),
        formula_inputs,
    )
    print(
        json.dumps(
            {
                "contract": "GANN_PYJHORA_EXTERNAL_STRENGTH_EXPORT_V3",
                "pyjhoraVersion": PYJHORA_VERSION,
                "wheelSha256": wheel_hash,
                "ayanamsa": "RAMAN",
                "fixtures": len(FIXTURES),
                "strengthRows": updated,
                "contributionRows": len(contributions),
                "componentRows": len(components),
                "kaalaSubcomponentRows": len(kaala_subcomponents),
                "formulaInputRows": len(formula_inputs),
                "output": str(args.output.resolve()),
                "outputSha256": sha256(args.output),
                "contributionOutput": str(args.contribution_output.resolve()),
                "contributionOutputSha256": sha256(args.contribution_output),
                "componentOutput": str(args.component_output.resolve()),
                "componentOutputSha256": sha256(args.component_output),
                "kaalaOutput": str(args.kaala_output.resolve()),
                "kaalaOutputSha256": sha256(args.kaala_output),
                "formulaInputOutput": str(args.formula_input_output.resolve()),
                "formulaInputOutputSha256": sha256(
                    args.formula_input_output
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
