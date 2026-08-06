"""Explicit loader for founder-approved research chart hypotheses.

The loader is intentionally opt-in. Loading a record does not create polarity,
write an evidence packet, derive a pair field, or select a chart at runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .models import GeoLocation, OrganizationChartHypothesis, SourceRef


DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[1]
    / "profiles"
    / "founder_chart_hypotheses_v1.json"
)
_UTC = ZoneInfo("UTC")


@dataclass(frozen=True)
class FounderChartIdentityRecord:
    """Canonical accepted chart identity retained with its registry hypothesis id.

    The existing ``OrganizationChartHypothesis`` intentionally has no
    ``chart_hypothesis_id`` field because it is a reusable domain model.  This
    small registry projection retains the immutable identifier needed by the
    transit compiler without copying those identifiers into a client.
    """

    chart: OrganizationChartHypothesis
    chart_hypothesis_id: str
    registry_contract: str
    historical_time_policy_id: str
    astronomy_contract: dict[str, Any]
    chart_hash: str

    def __post_init__(self) -> None:
        if not self.chart_hypothesis_id.strip():
            raise ValueError("founder chart hypothesis id is required")
        if self.chart.status != "ACCEPTED_RESEARCH":
            raise ValueError("founder transit compiler requires an accepted research chart")
        if self.chart.chart_hash != self.chart_hash:
            raise ValueError(f"chart hash mismatch for {self.chart.chart_id}")


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
    return tuple(record.chart for record in load_founder_chart_identity_records(path))


def load_founder_chart_identity_records(
    path: Path = DEFAULT_REGISTRY_PATH,
) -> tuple[FounderChartIdentityRecord, ...]:
    """Load the only accepted source of founder chart identities.

    This remains a registry read.  It does not compile events, assign polarity,
    create evidence, derive a pair field, or authorize execution.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    registry_contract = str(raw.get("contract") or "")
    if registry_contract != "FOUNDER_APPROVED_CHART_HYPOTHESES_V1":
        raise ValueError("unexpected founder chart registry contract")
    contract = raw.get("astronomyContract")
    if not isinstance(contract, dict) or not contract.get("contractId"):
        raise ValueError("founder chart registry requires astronomy contract")
    if any(bool(contract.get(key)) for key in ("executionAllowed", "polarityAllowed", "pairDerivationAllowed")):
        raise ValueError("founder chart registry must remain inert")
    policy = raw.get("historicalCivilTimeConversionPolicy")
    if not isinstance(policy, dict) or not str(policy.get("policyId") or "").strip():
        raise ValueError("founder chart registry requires a historical civil-time policy")
    records = raw.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("founder chart registry requires records")
    parsed: list[FounderChartIdentityRecord] = []
    for raw_record in records:
        if not isinstance(raw_record, dict):
            raise ValueError("founder chart registry records must be objects")
        hypothesis_id = str(raw_record.get("chartHypothesisId") or "").strip()
        if not hypothesis_id:
            raise ValueError("founder chart registry record requires chartHypothesisId")
        parsed.append(
            FounderChartIdentityRecord(
                chart=_chart_from_record(raw_record, str(contract["contractId"])),
                chart_hypothesis_id=hypothesis_id,
                registry_contract=registry_contract,
                historical_time_policy_id=str(policy["policyId"]),
                astronomy_contract=dict(contract),
                chart_hash=str(raw_record["chartHash"]),
            )
        )
    if len({record.chart.chart_id for record in parsed}) != len(parsed):
        raise ValueError("founder chart registry contains duplicate chart ids")
    if len({record.chart_hypothesis_id for record in parsed}) != len(parsed):
        raise ValueError("founder chart registry contains duplicate chart hypothesis ids")
    return tuple(parsed)


def require_founder_chart_identity(
    instrument_id: str,
    *,
    path: Path = DEFAULT_REGISTRY_PATH,
) -> FounderChartIdentityRecord:
    """Return one accepted immutable chart identity for the required FX side."""
    matches = [
        record
        for record in load_founder_chart_identity_records(path)
        if record.chart.instrument_id == str(instrument_id).strip()
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one accepted founder chart for {instrument_id}")
    return matches[0]
