from __future__ import annotations

import argparse
import csv
import json
import subprocess
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import swisseph as swe

from doctrine_config import configure_swiss_ephemeris_sidereal, load_doctrine_config
from panchanga_doctrine import panchanga_context


REPORT_VERSION = "astro_certification_4_gate_v1_20260527"
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

PLANETS = {
    "SUN": swe.SUN,
    "MOON": swe.MOON,
    "MARS": swe.MARS,
    "MERCURY": swe.MERCURY,
    "JUPITER": swe.JUPITER,
    "VENUS": swe.VENUS,
    "SATURN": swe.SATURN,
    "RAHU_TRUE_NODE": swe.TRUE_NODE,
}

SAMPLES = [
    ("case_8_event_start", "2025-03-07T19:30:00", "Asia/Kolkata"),
    ("case_43_event_start", "2025-04-04T02:30:00", "Asia/Kolkata"),
    ("case_103_event_start", "2025-05-15T22:30:00", "Asia/Kolkata"),
    ("case_127_sr_touch_start", "2025-05-28T22:00:00", "Asia/Kolkata"),
    ("gann_reference_tokyo", "1889-02-11T00:00:00", "Asia/Tokyo"),
]


@dataclass
class InventoryRow:
    gate: str
    feature_key: str
    source_anchor: str
    implementation: str
    function_or_file: str
    status_label: str
    strict_or_proxy: str
    validation_status: str
    current_gap: str
    next_action: str
    train_policy: str


@dataclass
class PositionRow:
    sample_id: str
    local_time: str
    utc_time: str
    jd_ut: float
    ayanamsa: str
    ayanamsa_deg: float
    planet: str
    tropical_lon_deg: float
    sidereal_lon_deg: float
    speed_deg_day: float
    baseline_status: str


@dataclass
class PanchangaRow:
    sample_id: str
    local_time: str
    sun_sidereal_lon_deg: float
    moon_sidereal_lon_deg: float
    tithi: str
    paksha: str
    nakshatra: str
    pada: str
    yoga: str
    karana: str
    weekday: str
    weekday_lord: str
    validation_status: str


@dataclass
class ExternalTemplateRow:
    gate: str
    sample_id: str
    feature_key: str
    local_value: str
    external_expected_value: str
    external_source: str
    pass_fail: str
    notes: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the four-gate astro/trading certification report.")
    parser.add_argument("--out-dir", default=".", help="Output directory for report and CSV ledgers.")
    parser.add_argument("--date-tag", default="20260527", help="Date tag for output files.")
    parser.add_argument(
        "--external-values",
        default="",
        help=(
            "Optional CSV with external_expected_value/external_source filled. "
            "When omitted, an existing output template for the same date tag is reused if present."
        ),
    )
    parser.add_argument("--skip-replay", action="store_true", help="Skip reviewer_rule_replay.py execution.")
    return parser.parse_args()


def csv_write(path: Path, rows: list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def csv_dict_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def external_key(row: dict[str, Any] | ExternalTemplateRow) -> tuple[str, str, str]:
    if isinstance(row, ExternalTemplateRow):
        return row.gate, row.sample_id, row.feature_key
    return row.get("gate", ""), row.get("sample_id", ""), row.get("feature_key", "")


def as_float(value: str) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def tolerance_for(feature_key: str) -> float | None:
    key = feature_key.lower()
    if "lon_deg" in key:
        return 0.02
    if "shadbala" in key or "drik_bala" in key or "virupa" in key:
        return 0.5
    return None


def compare_external_value(feature_key: str, local_value: str, expected_value: str) -> tuple[str, str]:
    expected = str(expected_value).strip()
    local = str(local_value).strip()
    if not expected:
        return "pending", "No external expected value entered."
    if local.startswith("needs "):
        return "pending_manual_context", "Local value requires row-specific event context before comparison."

    local_num = as_float(local)
    expected_num = as_float(expected)
    tol = tolerance_for(feature_key)
    if local_num is not None and expected_num is not None and tol is not None:
        delta = abs(local_num - expected_num)
        status = "pass" if delta <= tol else "fail"
        return status, f"numeric delta={delta:.9f}; tolerance={tol}"

    status = "pass" if local.casefold() == expected.casefold() else "fail"
    return status, "categorical exact compare"


def merge_external_values(
    templates: list[ExternalTemplateRow],
    external_rows: list[dict[str, str]],
) -> list[ExternalTemplateRow]:
    external_by_key = {external_key(row): row for row in external_rows}
    merged: list[ExternalTemplateRow] = []
    for row in templates:
        source = external_by_key.get(external_key(row), {})
        expected = source.get("external_expected_value", row.external_expected_value)
        external_source = source.get("external_source", row.external_source)
        notes = source.get("notes", row.notes)
        pass_fail, compare_note = compare_external_value(row.feature_key, row.local_value, expected)
        if notes:
            notes = f"{notes} | {compare_note}"
        else:
            notes = compare_note
        merged.append(
            ExternalTemplateRow(
                gate=row.gate,
                sample_id=row.sample_id,
                feature_key=row.feature_key,
                local_value=row.local_value,
                external_expected_value=expected,
                external_source=external_source,
                pass_fail=pass_fail,
                notes=notes,
            )
        )
    return merged


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(value).replace("\n", "<br>") for value in row) + " |")
    return "\n".join(out)


def sample_datetime(value: str, tz_name: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=ZoneInfo(tz_name))


def jd_ut_for(local_dt: datetime) -> tuple[float, datetime]:
    utc = local_dt.astimezone(UTC)
    hour = utc.hour + utc.minute / 60.0 + utc.second / 3600.0 + utc.microsecond / 3_600_000_000.0
    return float(swe.julday(utc.year, utc.month, utc.day, hour)), utc


def calc_planet(jd_ut: float, planet_id: int, ayanamsa_deg: float) -> tuple[float, float, float]:
    values, _flags = swe.calc_ut(jd_ut, planet_id)
    tropical = float(values[0]) % 360.0
    sidereal = (tropical - ayanamsa_deg) % 360.0
    speed = float(values[3]) if len(values) > 3 else 0.0
    return tropical, sidereal, speed


def build_inventory(config: dict[str, Any]) -> list[InventoryRow]:
    shadbala = config.get("shadbala", {})
    panchanga = config.get("panchanga", {})
    astronomy = config.get("astronomy", {})
    drik = config.get("drik_bala", {})
    drishti = config.get("drishti", {})
    rule_layer = config.get("rule_layer", {})

    rows = [
        InventoryRow(
            "Gate 1",
            "astronomy.raman_ayanamsa",
            "Swiss Ephemeris SIDM_RAMAN",
            f"{astronomy.get('zodiac')} / {astronomy.get('ayanamsa_swiss_ephemeris_id')}",
            "doctrine_config.configure_swiss_ephemeris_sidereal",
            "implemented_unvalidated",
            "strict astronomy setting",
            "baseline_generated_pending_external_reference",
            "Need independent ephemeris sample cross-check.",
            "Compare Gate 2 rows against Astro.com/JPL/other trusted ephemeris exports.",
            "allow_as_feature_after_external_position_check",
        ),
        InventoryRow(
            "Gate 1",
            "astronomy.true_node_rahu_ketu",
            "Swiss Ephemeris TRUE_NODE; Ketu = Rahu + 180 deg",
            str(astronomy.get("node_type")),
            "build_aspect_sr_touch_log.fetch_planetary_longitude_fast",
            "implemented_unvalidated",
            "strict node position, proxy strength",
            "baseline_generated_pending_external_reference",
            "Rahu/Ketu position is deterministic; strength doctrine remains proxy/excluded from Shadbala.",
            "Validate true-node longitude samples; keep Rahu/Ketu out of classical Shadbala totals.",
            "position_feature_ok_strength_policy_guarded",
        ),
        InventoryRow(
            "Gate 1",
            "shadbala.full_component_v1",
            "Local doctrine lock + uploaded Shadbala notes",
            str(shadbala.get("method")),
            "strict_shadbala_doctrine.event_strict_shadbala_context",
            "implemented_unvalidated",
            "strict formula attempt",
            str(shadbala.get("status")),
            "|".join(shadbala.get("missing", [])),
            "Fill Gate 3 external expected values from a known Shadbala calculator/book example.",
            "train_as_provisional_numeric_feature_only",
        ),
        InventoryRow(
            "Gate 1",
            "shadbala.avg_all_policy",
            "Project doctrine decision",
            str(shadbala.get("doctrine_decisions", {}).get("avg_all_policy")),
            "strict_shadbala_doctrine.aggregate_components",
            "implemented_unvalidated",
            "research aggregation",
            "pending_walk_forward_and_external_component_validation",
            "AVG(ALL) is an artificial seven-classical-planet mean, not a classical graha.",
            "Always label as artificial context feature in ML exports.",
            "train_with_explicit_artificial_feature_label",
        ),
        InventoryRow(
            "Gate 1",
            "drik_bala.strict_formula",
            "Parashara/Sripati six-formula local implementation",
            str(drik.get("method")),
            "strict_shadbala_doctrine.strict_drik_bala_for_planet",
            "implemented_unvalidated",
            "strict formula attempt",
            str(drik.get("status")),
            "Need external example with benefic/malefic split and exact aspect geometry.",
            "Add Gate 3 expected values before treating magnitude as certified.",
            "train_as_provisional_numeric_feature_only",
        ),
        InventoryRow(
            "Gate 1",
            "drishti.event_orb_strength",
            "Earlier BPHS-like orb heuristic",
            str(drishti.get("method")),
            "build_aspect_sr_touch_log.compute_event_aspect_metrics",
            "proxy_research_feature",
            "proxy",
            str(drishti.get("status")),
            "|".join(drishti.get("missing", [])),
            "Prefer strict Drik/Shadbala fields in explanations; keep orb as timing/proximity only.",
            "do_not_train_as_doctrine_strength",
        ),
        InventoryRow(
            "Gate 1",
            "panchanga.sun_moon_core",
            "Classical Panchanga formulas from sidereal Sun/Moon phase",
            str(panchanga.get("method")),
            "panchanga_doctrine.panchanga_context",
            "implemented_unvalidated",
            "formula foundation",
            str(panchanga.get("status")),
            "|".join(panchanga.get("missing", [])),
            "Compare Gate 2 rows to a traditional Panchanga for timezone/date rollover.",
            "train_as_provisional_categorical_feature",
        ),
        InventoryRow(
            "Gate 1",
            "rule_layer.auto_suggest_sr_gann",
            "Manual review-derived deterministic rules",
            str(rule_layer.get("status")),
            "build_repeatation_review_pack.py + reviewer_rule_replay.py",
            "replay_guarded_partial",
            "trading heuristic",
            "case_127_data_replay_passed_cases_8_43_103_source_guarded",
            "Browser JS still owns much Auto Suggest logic; not all teaching cases have data-level replay.",
            "Factor browser Auto Suggest into reusable Python and add data replays for 8/43/103.",
            "train_as_rule_lesson_with_outcome_tracking",
        ),
        InventoryRow(
            "Gate 1",
            "local_llm_dreaming",
            "Local RAG + verifier corrections",
            "extractive/LLM draft explanation layer",
            "jyotish_agent/explain_case.py + dream_review ledgers",
            "do_not_train_raw_text",
            "explanation layer",
            "deterministic_verifier_required",
            "LLM prose can drift and contradict evidence.",
            "Train only from deterministic evidence, manual notes, verifier corrections, and rule lessons.",
            "do_not_train_raw_llm_output",
        ),
    ]
    return rows


def build_position_baseline(config: dict[str, Any]) -> tuple[list[PositionRow], list[PanchangaRow], list[ExternalTemplateRow]]:
    ayanamsa_name = configure_swiss_ephemeris_sidereal(swe, config)
    positions: list[PositionRow] = []
    panchanga_rows: list[PanchangaRow] = []
    templates: list[ExternalTemplateRow] = []

    for sample_id, iso_text, tz_name in SAMPLES:
        local_dt = sample_datetime(iso_text, tz_name)
        jd_ut, utc_dt = jd_ut_for(local_dt)
        ayanamsa_deg = float(swe.get_ayanamsa_ut(jd_ut))
        sidereal_values: dict[str, float] = {}
        for planet, planet_id in PLANETS.items():
            tropical, sidereal, speed = calc_planet(jd_ut, planet_id, ayanamsa_deg)
            sidereal_values[planet] = sidereal
            positions.append(
                PositionRow(
                    sample_id=sample_id,
                    local_time=local_dt.isoformat(),
                    utc_time=utc_dt.isoformat(),
                    jd_ut=round(jd_ut, 9),
                    ayanamsa=ayanamsa_name,
                    ayanamsa_deg=round(ayanamsa_deg, 9),
                    planet=planet,
                    tropical_lon_deg=round(tropical, 9),
                    sidereal_lon_deg=round(sidereal, 9),
                    speed_deg_day=round(speed, 9),
                    baseline_status="self_consistency_generated_pending_external_reference",
                )
            )
        rahu = sidereal_values.get("RAHU_TRUE_NODE")
        if rahu is not None:
            ketu = (rahu + 180.0) % 360.0
            positions.append(
                PositionRow(
                    sample_id=sample_id,
                    local_time=local_dt.isoformat(),
                    utc_time=utc_dt.isoformat(),
                    jd_ut=round(jd_ut, 9),
                    ayanamsa=ayanamsa_name,
                    ayanamsa_deg=round(ayanamsa_deg, 9),
                    planet="KETU_DERIVED",
                    tropical_lon_deg=float("nan"),
                    sidereal_lon_deg=round(ketu, 9),
                    speed_deg_day=float("nan"),
                    baseline_status="derived_from_true_node_plus_180_pending_external_reference",
                )
            )

        panchanga = panchanga_context("cert", local_dt, sidereal_values["SUN"], sidereal_values["MOON"])
        panchanga_rows.append(
            PanchangaRow(
                sample_id=sample_id,
                local_time=local_dt.isoformat(),
                sun_sidereal_lon_deg=round(sidereal_values["SUN"], 9),
                moon_sidereal_lon_deg=round(sidereal_values["MOON"], 9),
                tithi=str(panchanga.get("cert_tithi_name", "")),
                paksha=str(panchanga.get("cert_paksha", "")),
                nakshatra=str(panchanga.get("cert_moon_nakshatra", "")),
                pada=str(panchanga.get("cert_moon_pada", "")),
                yoga=str(panchanga.get("cert_yoga_name", "")),
                karana=str(panchanga.get("cert_karana_name", "")),
                weekday=str(panchanga.get("cert_weekday", "")),
                weekday_lord=str(panchanga.get("cert_weekday_lord", "")),
                validation_status="local_formula_baseline_pending_traditional_panchanga_check",
            )
        )

        for feature_key, local_value in [
            ("sun_sidereal_lon_deg", f"{sidereal_values['SUN']:.9f}"),
            ("moon_sidereal_lon_deg", f"{sidereal_values['MOON']:.9f}"),
            ("rahu_true_node_sidereal_lon_deg", f"{sidereal_values['RAHU_TRUE_NODE']:.9f}"),
            ("tithi_name", str(panchanga.get("cert_tithi_name", ""))),
            ("moon_nakshatra_pada", f"{panchanga.get('cert_moon_nakshatra', '')} {panchanga.get('cert_moon_pada', '')}"),
            ("shadbala_total_virupa_by_classical_planet", "needs local row-specific event context plus external expected value"),
            ("drik_bala_virupa_by_classical_planet", "needs local row-specific event context plus external expected value"),
        ]:
            templates.append(
                ExternalTemplateRow(
                    gate="Gate 3",
                    sample_id=sample_id,
                    feature_key=feature_key,
                    local_value=local_value,
                    external_expected_value="",
                    external_source="",
                    pass_fail="pending",
                    notes="Fill expected value from trusted ephemeris/Panchanga/Shadbala source, then rerun certification.",
                )
            )

    return positions, panchanga_rows, templates


def run_replay(skip: bool) -> tuple[str, str]:
    if skip:
        return "skipped", "reviewer replay skipped by CLI flag"
    cmd = ["python", "reviewer_rule_replay.py"]
    try:
        proc = subprocess.run(cmd, cwd=Path(__file__).parent, text=True, capture_output=True, check=False)
    except Exception as exc:
        return "error", f"Could not run {' '.join(cmd)}: {exc}"
    status = "passed" if proc.returncode == 0 else "failed"
    text = (proc.stdout + "\n" + proc.stderr).strip()
    return status, text


def render_report(
    path: Path,
    inventory: list[InventoryRow],
    positions: list[PositionRow],
    panchanga_rows: list[PanchangaRow],
    templates: list[ExternalTemplateRow],
    replay_status: str,
    replay_output: str,
    output_files: dict[str, Path],
) -> None:
    gate_counts: dict[str, int] = {}
    for row in inventory:
        gate_counts[row.status_label] = gate_counts.get(row.status_label, 0) + 1

    position_preview = [
        [
            row.sample_id,
            row.planet,
            row.local_time,
            row.ayanamsa,
            row.ayanamsa_deg,
            row.sidereal_lon_deg,
            row.baseline_status,
        ]
        for row in positions
        if row.planet in {"SUN", "MOON", "RAHU_TRUE_NODE", "KETU_DERIVED"}
    ][:20]

    panchanga_preview = [
        [row.sample_id, row.tithi, row.paksha, row.nakshatra, row.pada, row.yoga, row.karana, row.validation_status]
        for row in panchanga_rows
    ]

    inventory_preview = [
        [row.feature_key, row.status_label, row.strict_or_proxy, row.validation_status, row.train_policy]
        for row in inventory
    ]

    pending_external = sum(1 for row in templates if row.pass_fail.startswith("pending"))
    passed_external = sum(1 for row in templates if row.pass_fail == "pass")
    failed_external = sum(1 for row in templates if row.pass_fail == "fail")
    lines = [
        f"# Astro Function Certification 4-Gate Report",
        "",
        f"- Report version: `{REPORT_VERSION}`",
        f"- Generated: `{datetime.now(IST).isoformat(timespec='seconds')}`",
        f"- Important interpretation: this report certifies traceability and local reproducibility first. External Jyotish/ephemeris validation remains explicitly pending where marked.",
        "",
        "## Gate Summary",
        "",
        markdown_table(
            ["Gate", "Result"],
            [
                ["Gate 1 - Formula inventory", f"{len(inventory)} feature rows inventoried"],
                ["Gate 2 - Astronomical baseline", f"{len(positions)} planet/node rows generated with Raman ayanamsa"],
                [
                    "Gate 3 - External validation template",
                    f"{passed_external} pass / {failed_external} fail / {pending_external} pending",
                ],
                ["Gate 4 - Trading replay", replay_status],
            ],
        ),
        "",
        "## Certification Labels",
        "",
        markdown_table(["Label", "Count"], [[key, value] for key, value in sorted(gate_counts.items())]),
        "",
        "## Gate 1 - Inventory Preview",
        "",
        markdown_table(["Feature", "Status", "Strict/Proxy", "Validation", "Training Policy"], inventory_preview),
        "",
        "## Gate 2 - Position Baseline Preview",
        "",
        markdown_table(
            ["Sample", "Planet", "Local Time", "Ayanamsa", "Ayanamsa Deg", "Sidereal Lon Deg", "Status"],
            position_preview,
        ),
        "",
        "## Gate 2 - Panchanga Baseline Preview",
        "",
        markdown_table(
            ["Sample", "Tithi", "Paksha", "Moon Nakshatra", "Pada", "Yoga", "Karana", "Status"],
            panchanga_preview,
        ),
        "",
        "## Gate 3 - External Validation",
        "",
        "Fill the expected-value columns from trusted ephemeris, Panchanga, and Shadbala examples. On each run, the script preserves those entries and computes pass/fail where a direct comparison is possible.",
        "",
        markdown_table(
            ["Status", "Rows"],
            [["pass", passed_external], ["fail", failed_external], ["pending", pending_external]],
        ),
        "",
        "## Gate 4 - Trading Replay",
        "",
        f"Status: `{replay_status}`",
        "",
        "```text",
        replay_output[-4000:] if replay_output else "",
        "```",
        "",
        "## Output Files",
        "",
        markdown_table(["Artifact", "Path"], [[name, str(file_path)] for name, file_path in output_files.items()]),
        "",
        "## Current Verdict",
        "",
        "- Safe to continue manual review with these labels visible.",
        "- Do not treat Shadbala/Drik/Panchanga as externally certified yet.",
        "- Do not train on raw local LLM prose. Train on deterministic evidence, manual notes, verified rule lessons, and verifier corrections.",
        "- Next certification lift: add external expected values for the Gate 3 template and factor browser Auto Suggest into reusable Python replay for cases 8, 43, and 103.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(__file__).parent
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    config = load_doctrine_config(root / "doctrine_config.yaml")
    inventory = build_inventory(config)
    positions, panchanga_rows, templates = build_position_baseline(config)
    replay_status, replay_output = run_replay(args.skip_replay)

    inventory_path = out_dir / f"astro_function_certification_inventory_{args.date_tag}.csv"
    positions_path = out_dir / f"astro_position_baseline_{args.date_tag}.csv"
    panchanga_path = out_dir / f"panchanga_baseline_{args.date_tag}.csv"
    template_path = out_dir / f"astro_external_validation_template_{args.date_tag}.csv"
    replay_path = out_dir / f"trading_rule_replay_result_{args.date_tag}.json"
    report_path = out_dir / f"astro_function_certification_report_{args.date_tag}.md"

    external_values_path = Path(args.external_values) if args.external_values else template_path
    if external_values_path and not external_values_path.is_absolute():
        external_values_path = root / external_values_path
    templates = merge_external_values(templates, csv_dict_rows(external_values_path))

    csv_write(inventory_path, inventory)
    csv_write(positions_path, positions)
    csv_write(panchanga_path, panchanga_rows)
    csv_write(template_path, templates)
    replay_path.write_text(
        json.dumps(
            {
                "report_version": REPORT_VERSION,
                "generated_at": datetime.now(IST).isoformat(timespec="seconds"),
                "status": replay_status,
                "output": replay_output,
            },
            indent=2,
            ensure_ascii=True,
        ),
        encoding="utf-8",
    )
    render_report(
        report_path,
        inventory,
        positions,
        panchanga_rows,
        templates,
        replay_status,
        replay_output,
        {
            "inventory_csv": inventory_path,
            "position_baseline_csv": positions_path,
            "panchanga_baseline_csv": panchanga_path,
            "external_validation_template_csv": template_path,
            "trading_rule_replay_json": replay_path,
            "report_md": report_path,
        },
    )
    print(f"Wrote {report_path}")
    print(f"Gate 4 replay: {replay_status}")


if __name__ == "__main__":
    main()
