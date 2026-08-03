"""Explicit loader for founder-approved research chart hypotheses.

The loader is intentionally opt-in. Loading a record does not create polarity,
write an evidence packet, derive a pair field, or select a chart at runtime.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import GeoLocation, OrganizationChartHypothesis, SourceRef


DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "profiles"
    / "founder_chart_hypotheses_v1.json"
)
_UTC = ZoneInfo("UTC")


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(_UTC)


def _chart_from_record(record: dict[str, object], astronomy_contract: str) -> OrganizationChartHypothesis:
    location = record["location"]
    if not isinstance(location, dict):
        raise ValueError("chart record location must be an object")
    provenance = record["provenance"]
    if not isinstance(provenance, list) or not provenance:
        raise ValueError("chart record requires provenance")
    sources = tuple(
        SourceRef(
            source_id=str(item["sourceId"]),
            locator=str(item["locator"]),
            evidence_class=str(item["evidenceClass"]),  # type: ignore[arg-type]
            status=str(item["status"]),
            confidence=float(item["confidence"]),
            note=str(item.get("note") or ""),
        )
        for item in provenance
        if isinstance(item, dict)
    )
    chart = OrganizationChartHypothesis(
        chart_id=str(record["chartId"]),
        instrument_id=str(record["instrumentId"]),
        entity_id=str(record["entityId"]),
        chart_type=str(record["chartType"]),
        timestamp_utc=_parse_utc(str(record["timestampUtc"])),
        location=GeoLocation(
            name=str(location["name"]),
            latitude=float(location["latitude"]),
            longitude=float(location["longitude"]),
        ),
        sources=sources,
        time_accuracy=str(record["timeAccuracy"]),  # type: ignore[arg-type]
        ayanamsa="RAMAN",
        house_model=str(record["houseModel"]),
        astronomy_contract=astronomy_contract,
        effective_from=date.fromisoformat(str(record["effectiveFrom"])),
        effective_to=(date.fromisoformat(str(record["effectiveTo"])) if record.get("effectiveTo") else None),
        status=str(record["status"]),  # type: ignore[arg-type]
        accepted_by=str(record["acceptedBy"]),
        accepted_at=datetime.fromisoformat(str(record["acceptedAt"])),
    )
    if str(record["chartHash"]) != chart.chart_hash:
        raise ValueError(f"chart hash mismatch for {chart.chart_id}")
    return chart


def load_founder_chart_hypotheses(
    path: Path = DEFAULT_REGISTRY_PATH,
) -> tuple[OrganizationChartHypothesis, ...]:
    """Load exact founder-approved records without registering or selecting them."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("contract") != "FOUNDER_APPROVED_CHART_HYPOTHESES_V1":
        raise ValueError("unexpected founder chart registry contract")
    contract = raw.get("astronomyContract")
    if not isinstance(contract, dict) or not contract.get("contractId"):
        raise ValueError("founder chart registry requires astronomy contract")
    if any(bool(contract.get(key)) for key in ("executionAllowed", "polarityAllowed", "pairDerivationAllowed")):
        raise ValueError("founder chart registry must remain inert")
    records = raw.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("founder chart registry requires records")
    charts = tuple(_chart_from_record(record, str(contract["contractId"])) for record in records if isinstance(record, dict))
    if len(charts) != len(records) or len({chart.chart_id for chart in charts}) != len(charts):
        raise ValueError("founder chart registry contains invalid or duplicate charts")
    return charts
