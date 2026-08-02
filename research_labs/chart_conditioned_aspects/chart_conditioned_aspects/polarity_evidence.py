from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Mapping

from .models import stable_hash


EVIDENCE_PACKET_REGISTRY_CONTRACT = (
    "CHART_CONDITIONED_POLARITY_EVIDENCE_PACKET_REGISTRY_V1"
)
EVIDENCE_PACKET_REGISTRY_SCHEMA_VERSION = 1
POLARITY_STATE = Literal["SUPPORTIVE", "ADVERSE", "MIXED", "NEUTRAL"]
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_PACKET_REGISTRY_PATH = (
    PACKAGE_ROOT / "profiles" / "target_aware_polarity_evidence_packets_v1.json"
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


def _aware_timestamp(value: str | None, field_name: str) -> str:
    token = _required(value, field_name).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(token)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a UTC offset")
    return parsed.isoformat()


@dataclass(frozen=True)
class TargetAwarePolarityEvidencePacket:
    packet_id: str
    instrument_id: str
    chart_id: str
    transit_body: str
    natal_target: str
    aspect_type: str
    reviewed_polarity: POLARITY_STATE
    evidence_status: str
    chart_acceptance_status: str
    astronomy_contract: str
    profile_hash: str
    reviewed_by: str
    reviewed_at_utc: str
    source_refs: tuple[str, ...]
    packet_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "packet_id", _required(self.packet_id, "packet_id"))
        object.__setattr__(self, "instrument_id", _upper(self.instrument_id, "instrument_id"))
        object.__setattr__(self, "chart_id", _required(self.chart_id, "chart_id"))
        object.__setattr__(self, "transit_body", _upper(self.transit_body, "transit_body"))
        object.__setattr__(self, "natal_target", _upper(self.natal_target, "natal_target"))
        object.__setattr__(self, "aspect_type", _lower(self.aspect_type, "aspect_type"))
        if self.reviewed_polarity not in {"SUPPORTIVE", "ADVERSE", "MIXED", "NEUTRAL"}:
            raise ValueError("reviewed_polarity must be categorical")
        if self.evidence_status != "REVIEWED_RESEARCH_ONLY":
            raise ValueError("evidence_status must be REVIEWED_RESEARCH_ONLY")
        if self.chart_acceptance_status != "ACCEPTED_RESEARCH":
            raise ValueError("chart_acceptance_status must be ACCEPTED_RESEARCH")
        object.__setattr__(self, "astronomy_contract", _required(self.astronomy_contract, "astronomy_contract"))
        object.__setattr__(self, "profile_hash", _required(self.profile_hash, "profile_hash"))
        object.__setattr__(self, "reviewed_by", _required(self.reviewed_by, "reviewed_by"))
        object.__setattr__(self, "reviewed_at_utc", _aware_timestamp(self.reviewed_at_utc, "reviewed_at_utc"))
        normalized_sources = tuple(sorted({_required(source, "source_ref") for source in self.source_refs}))
        if not normalized_sources:
            raise ValueError("at least one source_ref is required")
        object.__setattr__(self, "source_refs", normalized_sources)
        object.__setattr__(self, "packet_hash", _required(self.packet_hash, "packet_hash"))
        if self.packet_hash != self.computed_hash:
            raise ValueError("evidence packet hash does not match packet contents")

    @property
    def computed_hash(self) -> str:
        return stable_hash({
            "packetId": self.packet_id,
            "instrumentId": self.instrument_id,
            "chartId": self.chart_id,
            "transitBody": self.transit_body,
            "natalTarget": self.natal_target,
            "aspectType": self.aspect_type,
            "reviewedPolarity": self.reviewed_polarity,
            "evidenceStatus": self.evidence_status,
            "chartAcceptanceStatus": self.chart_acceptance_status,
            "astronomyContract": self.astronomy_contract,
            "profileHash": self.profile_hash,
            "reviewedBy": self.reviewed_by,
            "reviewedAtUtc": self.reviewed_at_utc,
            "sourceRefs": list(self.source_refs),
        })

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TargetAwarePolarityEvidencePacket":
        return cls(
            packet_id=str(raw.get("packet_id") or raw.get("packetId") or ""),
            instrument_id=str(raw.get("instrument_id") or raw.get("instrumentId") or ""),
            chart_id=str(raw.get("chart_id") or raw.get("chartId") or ""),
            transit_body=str(raw.get("transit_body") or raw.get("transitBody") or ""),
            natal_target=str(raw.get("natal_target") or raw.get("natalTarget") or ""),
            aspect_type=str(raw.get("aspect_type") or raw.get("aspectType") or ""),
            reviewed_polarity=str(raw.get("reviewed_polarity") or raw.get("reviewedPolarity") or ""),  # type: ignore[arg-type]
            evidence_status=str(raw.get("evidence_status") or raw.get("evidenceStatus") or ""),
            chart_acceptance_status=str(raw.get("chart_acceptance_status") or raw.get("chartAcceptanceStatus") or ""),
            astronomy_contract=str(raw.get("astronomy_contract") or raw.get("astronomyContract") or ""),
            profile_hash=str(raw.get("profile_hash") or raw.get("profileHash") or ""),
            reviewed_by=str(raw.get("reviewed_by") or raw.get("reviewedBy") or ""),
            reviewed_at_utc=str(raw.get("reviewed_at_utc") or raw.get("reviewedAtUtc") or ""),
            source_refs=tuple(str(value) for value in (raw.get("source_refs") or raw.get("sourceRefs") or ())),
            packet_hash=str(raw.get("packet_hash") or raw.get("packetHash") or ""),
        )


@dataclass(frozen=True)
class TargetAwarePolarityEvidencePacketRegistry:
    registry_id: str
    registry_status: str
    packets: tuple[TargetAwarePolarityEvidencePacket, ...]
    registry_hash: str

    @classmethod
    def load(cls, path: Path | None = None) -> "TargetAwarePolarityEvidencePacketRegistry":
        source = path or DEFAULT_EVIDENCE_PACKET_REGISTRY_PATH
        raw = json.loads(source.read_text(encoding="utf-8"))
        if raw.get("contract") != EVIDENCE_PACKET_REGISTRY_CONTRACT:
            raise ValueError("unsupported polarity evidence packet registry contract")
        if raw.get("schema_version") != EVIDENCE_PACKET_REGISTRY_SCHEMA_VERSION:
            raise ValueError("unsupported polarity evidence packet registry schema")
        guardrails = raw.get("guardrails")
        if not isinstance(guardrails, Mapping) or guardrails.get("execution_allowed") is not False:
            raise ValueError("evidence packet registry must keep execution_allowed=false")
        if guardrails.get("automatic_order_placement") is not False:
            raise ValueError("evidence packet registry must keep automatic_order_placement=false")
        raw_packets = raw.get("packets")
        if not isinstance(raw_packets, list):
            raise ValueError("evidence packet registry packets must be a list")
        packets = tuple(TargetAwarePolarityEvidencePacket.from_mapping(item) for item in raw_packets)
        if len({packet.packet_id for packet in packets}) != len(packets):
            raise ValueError("evidence packet registry contains duplicate packet ids")
        return cls(
            registry_id=_required(str(raw.get("registry_id") or ""), "registry_id"),
            registry_status=_required(str(raw.get("registry_status") or ""), "registry_status"),
            packets=packets,
            registry_hash=stable_hash(raw),
        )

    def require(self, packet_id: str) -> TargetAwarePolarityEvidencePacket:
        matches = [packet for packet in self.packets if packet.packet_id == str(packet_id)]
        if not matches:
            raise ValueError(f"missing reviewed evidence packet: {packet_id}")
        return matches[0]
