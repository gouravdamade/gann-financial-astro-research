from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_ROOT = PROJECT_ROOT / "configs" / "sbc" / "arghya"
PROFILE_PATH = CONFIG_ROOT / "trailokya_arghya_reconciliation_v1.yaml"
PASS_1972_PATH = CONFIG_ROOT / "trailokya_1972_arghya_pass1.csv"
PASS_2016_PATH = CONFIG_ROOT / "trailokya_2016_arghya_pass2.csv"

EXPECTED_COLUMNS = {
    "table_id",
    "row_key",
    "column_key",
    "raw_token",
    "major",
    "kala",
    "normalized_value",
    "source_id",
    "transcription_pass",
    "pdf_page",
    "printed_page",
    "unit_kind",
    "notes",
}
EXPECTED_TABLE_COUNTS = {
    "relationship_vedha_viswa": 32,
    "planet_aspect_houses": 36,
    "five_class_vedha_viswa": 40,
}
ROW_FRACTIONS = {
    "full": Decimal("1"),
    "three_quarter": Decimal("0.75"),
    "half": Decimal("0.5"),
    "quarter": Decimal("0.25"),
}


class ArghyaExecutionLockedError(RuntimeError):
    """Raised when research-only Arghya data is asked to drive a market output."""


@dataclass(frozen=True)
class TranscribedCell:
    table_id: str
    row_key: str
    column_key: str
    raw_token: str
    major: int | None
    kala: int | None
    normalized_value: Decimal | None
    source_id: str
    transcription_pass: str
    pdf_page: int
    printed_page: int
    unit_kind: str
    notes: str

    @property
    def key(self) -> tuple[str, str, str]:
        return self.table_id, self.row_key, self.column_key

    @property
    def comparable(self) -> tuple[Any, ...]:
        return (
            self.raw_token,
            self.major,
            self.kala,
            self.normalized_value,
            self.unit_kind,
            self.notes,
        )


@dataclass(frozen=True)
class AvailabilityDirection:
    base_parts: Decimal
    benefic_viswa: Decimal
    malefic_viswa: Decimal
    net_viswa: Decimal
    availability_index: Decimal
    interpretation: str
    predicted_price: None
    market_label_allowed: bool
    execution_allowed: bool


@dataclass(frozen=True)
class ResearchPriceUnit:
    reference_value: Decimal
    divisor: Decimal
    fraction: Decimal
    percent: Decimal
    unit_value: Decimal
    forecast_allowed: bool
    execution_allowed: bool


def parse_viswa_kala(token: str) -> Decimal:
    parts = token.strip().split("|")
    if len(parts) != 2 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid Viswa|Kala token: {token!r}")
    major, kala = (int(part) for part in parts)
    if not 0 <= kala < 60:
        raise ValueError(f"Kala must be between 0 and 59: {token!r}")
    return Decimal(major) + Decimal(kala) / Decimal(60)


def parse_house_list(token: str) -> tuple[int, ...]:
    stripped = token.strip()
    if stripped == "0":
        return ()
    parts = stripped.split("|")
    if not parts or not all(part.isdigit() for part in parts):
        raise ValueError(f"Invalid house-list token: {token!r}")
    houses = tuple(int(part) for part in parts)
    if any(house < 1 or house > 12 for house in houses):
        raise ValueError(f"House must be between 1 and 12: {token!r}")
    if len(set(houses)) != len(houses):
        raise ValueError(f"Duplicate house in token: {token!r}")
    return houses


def _load_cells(path: Path) -> tuple[TranscribedCell, ...]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or ()) != EXPECTED_COLUMNS:
            raise ValueError(f"Unexpected transcription columns in {path}")
        cells: list[TranscribedCell] = []
        for row in reader:
            unit_kind = row["unit_kind"].strip()
            if unit_kind == "viswa_kala":
                major = int(row["major"])
                kala = int(row["kala"])
                normalized = Decimal(row["normalized_value"])
                parsed = parse_viswa_kala(row["raw_token"])
                if parsed != normalized:
                    raise ValueError(
                        f"Normalized value mismatch for {row['table_id']}/"
                        f"{row['row_key']}/{row['column_key']} in {path}"
                    )
                if parsed != Decimal(major) + Decimal(kala) / Decimal(60):
                    raise ValueError(f"Major/Kala mismatch in {path}")
            elif unit_kind == "house_list":
                parse_house_list(row["raw_token"])
                if row["major"] or row["kala"] or row["normalized_value"]:
                    raise ValueError(f"House-list row carries sexagesimal fields in {path}")
                major = kala = None
                normalized = None
            else:
                raise ValueError(f"Unknown unit kind {unit_kind!r} in {path}")
            cells.append(
                TranscribedCell(
                    table_id=row["table_id"].strip(),
                    row_key=row["row_key"].strip(),
                    column_key=row["column_key"].strip(),
                    raw_token=row["raw_token"].strip(),
                    major=major,
                    kala=kala,
                    normalized_value=normalized,
                    source_id=row["source_id"].strip(),
                    transcription_pass=row["transcription_pass"].strip(),
                    pdf_page=int(row["pdf_page"]),
                    printed_page=int(row["printed_page"]),
                    unit_kind=unit_kind,
                    notes=row["notes"].strip(),
                )
            )
    keys = [cell.key for cell in cells]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate transcription cell in {path}")
    if len(cells) != sum(EXPECTED_TABLE_COUNTS.values()):
        raise ValueError(f"Expected 108 cells in {path}; found {len(cells)}")
    table_counts = {
        table_id: sum(cell.table_id == table_id for cell in cells)
        for table_id in EXPECTED_TABLE_COUNTS
    }
    if table_counts != EXPECTED_TABLE_COUNTS:
        raise ValueError(f"Unexpected table counts in {path}: {table_counts}")
    return tuple(cells)


def load_reconciliation_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("Arghya reconciliation profile must be a mapping")
    if loaded.get("schema_version") != 1:
        raise ValueError("Unsupported Arghya reconciliation schema")
    for lock in ("execution_allowed", "promotion_allowed", "market_mapping_allowed"):
        if loaded.get(lock) is not False:
            raise ValueError(f"Arghya profile must keep {lock}=false")
    if loaded.get("source_lineage", {}).get("independent_worked_witness") is not None:
        raise ValueError("Independent worked witness is not yet certified")
    table_witness = loaded.get("source_lineage", {}).get("independent_table_witness")
    if not isinstance(table_witness, dict):
        raise ValueError("Independent table witness metadata is required")
    price_unit = loaded.get("price_unit_evidence")
    if not isinstance(price_unit, dict):
        raise ValueError("Guarded price-unit evidence is required")
    if Decimal(str(price_unit.get("divisor"))) != Decimal("20"):
        raise ValueError("Price-unit divisor must preserve the witnessed value 20")
    if Decimal(str(price_unit.get("fraction"))) != Decimal("0.05"):
        raise ValueError("Price-unit fraction must preserve the witnessed value 0.05")
    if Decimal(str(price_unit.get("percent"))) != Decimal("5"):
        raise ValueError("Price-unit percent must preserve the witnessed value 5")
    worked_examples = loaded.get("worked_example_evidence")
    if not isinstance(worked_examples, list) or not worked_examples:
        raise ValueError("Worked-example evidence must be recorded")
    for example in worked_examples:
        if not isinstance(example, dict):
            raise ValueError("Worked-example evidence entries must be mappings")
        if example.get("certifies_price_formula") is not False:
            raise ValueError("No current worked example may certify the price formula")
        if example.get("reusable_prediction_allowed") is not False:
            raise ValueError("Worked examples must remain unavailable to prediction")
    for finding in loaded.get("independent_witness_findings", {}).get(
        "table_anomalies", []
    ):
        if finding.get("correction_applied") is not False:
            raise ValueError("Independent anomaly readings cannot silently alter source data")
    return loaded


def _format_viswa_kala(value: Decimal) -> str:
    total_kala = value * Decimal(60)
    if total_kala != total_kala.to_integral_value():
        return str(value)
    total = int(total_kala)
    return f"{total // 60}|{total % 60}"


def _scaling_anomalies(cells: tuple[TranscribedCell, ...]) -> list[dict[str, str]]:
    indexed = {cell.key: cell for cell in cells}
    anomalies: list[dict[str, str]] = []
    for table_id in ("relationship_vedha_viswa", "five_class_vedha_viswa"):
        columns = sorted(
            cell.column_key
            for cell in cells
            if cell.table_id == table_id and cell.row_key == "full"
        )
        for column in columns:
            full = indexed[(table_id, "full", column)].normalized_value
            assert full is not None
            for row_key, fraction in ROW_FRACTIONS.items():
                observed = indexed[(table_id, row_key, column)].normalized_value
                assert observed is not None
                expected = full * fraction
                if observed != expected:
                    anomalies.append(
                        {
                            "cell": f"{table_id}/{row_key}/{column}",
                            "printed_value": indexed[(table_id, row_key, column)].raw_token,
                            "proportional_expectation": _format_viswa_kala(expected),
                        }
                    )
    return anomalies


def reconciliation_report() -> dict[str, Any]:
    profile = load_reconciliation_profile()
    primary = _load_cells(PASS_1972_PATH)
    witness = _load_cells(PASS_2016_PATH)
    primary_by_key = {cell.key: cell for cell in primary}
    witness_by_key = {cell.key: cell for cell in witness}
    mismatches: list[dict[str, Any]] = []
    for key in sorted(set(primary_by_key) | set(witness_by_key)):
        left = primary_by_key.get(key)
        right = witness_by_key.get(key)
        if left is None or right is None or left.comparable != right.comparable:
            mismatches.append(
                {
                    "cell": "/".join(key),
                    "primary": None if left is None else left.raw_token,
                    "witness": None if right is None else right.raw_token,
                }
            )
    anomalies = _scaling_anomalies(primary)
    declared = [
        {
            "cell": item["cell"],
            "printed_value": item["printed_value"],
            "proportional_expectation": item["proportional_expectation"],
        }
        for item in profile["source_preserved_anomalies"]
    ]
    if anomalies != declared:
        raise ValueError(
            f"Detected scaling anomalies differ from the guarded profile: {anomalies}"
        )
    return {
        "profile_id": profile["profile_id"],
        "status": profile["status"],
        "cells_per_pass": len(primary),
        "table_counts": EXPECTED_TABLE_COUNTS,
        "cross_edition_mismatches": mismatches,
        "source_preserved_anomalies": anomalies,
        "independent_table_witness": profile["source_lineage"][
            "independent_table_witness"
        ],
        "anomaly_witness_assessment": profile["independent_witness_findings"][
            "table_anomalies"
        ],
        "price_unit_evidence": profile["price_unit_evidence"],
        "worked_example_evidence": profile["worked_example_evidence"],
        "independent_worked_witness": None,
        "price_formula_certified": False,
        "execution_allowed": False,
    }


def evaluate_availability_direction(
    benefic_viswa: Decimal | int | str,
    malefic_viswa: Decimal | int | str,
) -> AvailabilityDirection:
    report = reconciliation_report()
    if report["cross_edition_mismatches"]:
        raise ValueError("Cross-edition transcription has unresolved mismatches")
    benefic = Decimal(str(benefic_viswa))
    malefic = Decimal(str(malefic_viswa))
    if benefic < 0 or malefic < 0:
        raise ValueError("Viswa totals cannot be negative")
    base = Decimal("20")
    net = benefic - malefic
    index = base + net
    if index > base:
        interpretation = "abundance_lower_price_pressure"
    elif index < base:
        interpretation = "scarcity_higher_price_pressure"
    else:
        interpretation = "balanced_by_narrow_arithmetic_only"
    return AvailabilityDirection(
        base_parts=base,
        benefic_viswa=benefic,
        malefic_viswa=malefic,
        net_viswa=net,
        availability_index=index,
        interpretation=interpretation,
        predicted_price=None,
        market_label_allowed=False,
        execution_allowed=False,
    )


def calculate_reference_price_unit(
    reference_value: Decimal | int | str,
) -> ResearchPriceUnit:
    """Return the witnessed 1/20 reference unit without producing a forecast."""

    profile = load_reconciliation_profile()
    reference = Decimal(str(reference_value))
    if reference <= 0:
        raise ValueError("Reference value must be positive")
    evidence = profile["price_unit_evidence"]
    divisor = Decimal(str(evidence["divisor"]))
    fraction = Decimal(str(evidence["fraction"]))
    percent = Decimal(str(evidence["percent"]))
    unit = reference / divisor
    if unit != reference * fraction:
        raise ValueError("Price-unit evidence is internally inconsistent")
    return ResearchPriceUnit(
        reference_value=reference,
        divisor=divisor,
        fraction=fraction,
        percent=percent,
        unit_value=unit,
        forecast_allowed=False,
        execution_allowed=False,
    )


def refuse_predicted_price(*_: Any, **__: Any) -> None:
    raise ArghyaExecutionLockedError(
        "Direct predicted price is blocked: table readings and the 1/20 reference unit "
        "have witnesses, but the score-to-unit equation and an independent reproducible "
        "worked forecast remain unresolved."
    )


def _json_default(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    payload = reconciliation_report()
    payload["synthetic_direction_only"] = asdict(
        evaluate_availability_direction(benefic_viswa=3, malefic_viswa=0)
    )
    print(json.dumps(payload, indent=2, default=_json_default))
