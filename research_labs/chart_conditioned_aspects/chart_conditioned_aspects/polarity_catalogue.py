from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping

from .models import stable_hash


POLARITY_CATALOGUE_CONTRACT = "CHART_CONDITIONED_POLARITY_CATALOGUE_V1"
POLARITY_CATALOGUE_SCHEMA_VERSION = 1
POLARITY_STATE = Literal["SUPPORTIVE", "ADVERSE", "MIXED", "NEUTRAL"]
LOOKUP_STATE = Literal[
    "READY",
    "POLARITY_CATALOGUE_MISSING",
    "TARGET_CONTEXT_INCOMPLETE",
]

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOGUE_PATH = (
    PACKAGE_ROOT / "profiles" / "target_aware_polarity_catalogue_v1.json"
)


def _required(value: str | None, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _upper(value: str | None, field_name: str) -> str:
    return _required(value, field_name).upper()


def _lower(value: str | None, field_name: str) -> str:
    return _required(value, field_name).lower()


@dataclass(frozen=True)
class TargetAwarePolarityEntry:
    entry_id: str
    instrument_id: str
    chart_id: str
    transit_body: str
    natal_target: str
    aspect_type: str
    precomputed_polarity: POLARITY_STATE
    evidence_status: str
    profile_hash: str
    evidence_packet_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_id", _required(self.entry_id, "entry_id"))
        object.__setattr__(self, "instrument_id", _upper(self.instrument_id, "instrument_id"))
        object.__setattr__(self, "chart_id", _required(self.chart_id, "chart_id"))
        object.__setattr__(self, "transit_body", _upper(self.transit_body, "transit_body"))
        object.__setattr__(self, "natal_target", _upper(self.natal_target, "natal_target"))
        object.__setattr__(self, "aspect_type", _lower(self.aspect_type, "aspect_type"))
        object.__setattr__(self, "evidence_status", _required(self.evidence_status, "evidence_status"))
        object.__setattr__(self, "profile_hash", _required(self.profile_hash, "profile_hash"))
        object.__setattr__(self, "evidence_packet_hash", _required(self.evidence_packet_hash, "evidence_packet_hash"))
        if self.precomputed_polarity not in {"SUPPORTIVE", "ADVERSE", "MIXED", "NEUTRAL"}:
            raise ValueError("precomputed_polarity must be a categorical polarity state")

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TargetAwarePolarityEntry":
        return cls(
            entry_id=str(raw.get("entry_id") or raw.get("entryId") or ""),
            instrument_id=str(raw.get("instrument_id") or raw.get("instrumentId") or ""),
            chart_id=str(raw.get("chart_id") or raw.get("chartId") or ""),
            transit_body=str(raw.get("transit_body") or raw.get("transitBody") or ""),
            natal_target=str(raw.get("natal_target") or raw.get("natalTarget") or ""),
            aspect_type=str(raw.get("aspect_type") or raw.get("aspectType") or ""),
            precomputed_polarity=str(raw.get("precomputed_polarity") or raw.get("precomputedPolarity") or ""),  # type: ignore[arg-type]
            evidence_status=str(raw.get("evidence_status") or raw.get("evidenceStatus") or ""),
            profile_hash=str(raw.get("profile_hash") or raw.get("profileHash") or ""),
            evidence_packet_hash=str(raw.get("evidence_packet_hash") or raw.get("evidencePacketHash") or ""),
        )

    def to_public(self) -> dict[str, str]:
        return {
            "entryId": self.entry_id,
            "instrumentId": self.instrument_id,
            "chartId": self.chart_id,
            "transitBody": self.transit_body,
            "natalTarget": self.natal_target,
            "aspectType": self.aspect_type,
            "precomputedPolarity": self.precomputed_polarity,
            "evidenceStatus": self.evidence_status,
            "profileHash": self.profile_hash,
            "evidencePacketHash": self.evidence_packet_hash,
        }


@dataclass(frozen=True)
class TargetAwarePolarityCatalogue:
    catalogue_id: str
    catalogue_status: str
    entries: tuple[TargetAwarePolarityEntry, ...]
    catalogue_hash: str

    @classmethod
    def load(cls, path: Path | None = None) -> "TargetAwarePolarityCatalogue":
        source = path or DEFAULT_CATALOGUE_PATH
        raw = json.loads(source.read_text(encoding="utf-8"))
        if raw.get("contract") != POLARITY_CATALOGUE_CONTRACT:
            raise ValueError("unsupported target-aware polarity catalogue contract")
        if raw.get("schema_version") != POLARITY_CATALOGUE_SCHEMA_VERSION:
            raise ValueError("unsupported target-aware polarity catalogue schema")
        guardrails = raw.get("guardrails")
        if not isinstance(guardrails, Mapping) or guardrails.get("execution_allowed") is not False:
            raise ValueError("polarity catalogue must keep execution_allowed=false")
        if guardrails.get("automatic_order_placement") is not False:
            raise ValueError("polarity catalogue must keep automatic_order_placement=false")
        if guardrails.get("magnitude_configured") is not False:
            raise ValueError("V2A catalogue must keep magnitude_configured=false")
        raw_entries = raw.get("entries")
        if not isinstance(raw_entries, list):
            raise ValueError("polarity catalogue entries must be a list")
        entries = tuple(TargetAwarePolarityEntry.from_mapping(item) for item in raw_entries)
        if len({entry.entry_id for entry in entries}) != len(entries):
            raise ValueError("polarity catalogue contains duplicate entry ids")
        return cls(
            catalogue_id=_required(str(raw.get("catalogue_id") or ""), "catalogue_id"),
            catalogue_status=_required(str(raw.get("catalogue_status") or ""), "catalogue_status"),
            entries=entries,
            catalogue_hash=stable_hash(raw),
        )


def normalize_instrument_id(value: str) -> str:
    token = _upper(value, "instrument_id")
    return token.split(":", 1)[-1]


def lookup_target_aware_polarity(
    catalogue: TargetAwarePolarityCatalogue,
    *,
    instrument_id: str,
    chart_id: str | None = None,
    transit_body: str | None = None,
    natal_target: str | None = None,
    aspect_type: str | None = None,
) -> dict[str, Any]:
    instrument = normalize_instrument_id(instrument_id)
    supplied_context = (chart_id, transit_body, natal_target, aspect_type)
    supplied_count = sum(bool(str(value or "").strip()) for value in supplied_context)
    if supplied_count not in {0, 4}:
        return _missing_result(
            catalogue,
            instrument=instrument,
            chart_id=chart_id,
            state="TARGET_CONTEXT_INCOMPLETE",
            reason="Chart id, transit body, natal target, and aspect type must be supplied together for an event-level lookup.",
        )
    if supplied_count == 0:
        return _missing_result(
            catalogue,
            instrument=instrument,
            chart_id=None,
            state="POLARITY_CATALOGUE_MISSING",
            reason="No accepted immutable target-aware polarity entry is available for this instrument.",
        )
    normalized_chart = _required(chart_id, "chart_id")
    normalized_transit = _upper(transit_body, "transit_body")
    normalized_target = _upper(natal_target, "natal_target")
    normalized_aspect = _lower(aspect_type, "aspect_type")
    matching = [
        entry
        for entry in catalogue.entries
        if entry.instrument_id == instrument
        and entry.chart_id == normalized_chart
        and entry.transit_body == normalized_transit
        and entry.natal_target == normalized_target
        and entry.aspect_type == normalized_aspect
    ]
    if not matching:
        return _missing_result(
            catalogue,
            instrument=instrument,
            chart_id=normalized_chart,
            state="POLARITY_CATALOGUE_MISSING",
            reason="No accepted immutable target-aware polarity entry matches this chart, transit, natal target, and aspect.",
        )
    if len(matching) != 1:
        raise ValueError("target-aware polarity lookup is ambiguous")
    entry = matching[0]
    return {
        "contract": POLARITY_CATALOGUE_CONTRACT,
        "schemaVersion": POLARITY_CATALOGUE_SCHEMA_VERSION,
        "lookupState": "READY",
        "catalogueId": catalogue.catalogue_id,
        "catalogueStatus": catalogue.catalogue_status,
        "catalogueHash": catalogue.catalogue_hash,
        "instrumentId": instrument,
        "chartId": entry.chart_id,
        "entry": entry.to_public(),
        "reason": "Accepted immutable categorical polarity entry found. Magnitude remains intentionally unconfigured.",
        "stateContract": "CATEGORICAL_POLARITY_STATE",
        "magnitudeState": "MAGNITUDE_NOT_CONFIGURED",
        "guardrails": _guardrails(),
    }


def _missing_result(
    catalogue: TargetAwarePolarityCatalogue,
    *,
    instrument: str,
    chart_id: str | None,
    state: LOOKUP_STATE,
    reason: str,
) -> dict[str, Any]:
    return {
        "contract": POLARITY_CATALOGUE_CONTRACT,
        "schemaVersion": POLARITY_CATALOGUE_SCHEMA_VERSION,
        "lookupState": state,
        "catalogueId": catalogue.catalogue_id,
        "catalogueStatus": catalogue.catalogue_status,
        "catalogueHash": catalogue.catalogue_hash,
        "instrumentId": instrument,
        "chartId": chart_id,
        "entry": None,
        "reason": reason,
        "stateContract": "CATEGORICAL_POLARITY_STATE",
        "magnitudeState": "MAGNITUDE_NOT_CONFIGURED",
        "guardrails": _guardrails(),
    }


def _guardrails() -> dict[str, bool]:
    return {
        "readOnly": True,
        "executionAllowed": False,
        "automaticOrderPlacement": False,
        "financiallyValidated": False,
        "actsAsSbcConfirmation": False,
    }
