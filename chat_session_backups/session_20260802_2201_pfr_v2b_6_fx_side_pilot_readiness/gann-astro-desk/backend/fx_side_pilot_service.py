from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
if str(INSTRUMENT_SBC_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUMENT_SBC_ROOT))

from chart_conditioned_aspects.polarity_catalogue import (  # noqa: E402
    TargetAwarePolarityCatalogue,
)
from chart_conditioned_aspects.polarity_evidence import (  # noqa: E402
    TargetAwarePolarityEvidencePacketRegistry,
)


FX_SIDE_PILOT_STATUS_CONTRACT = "FX_SIDE_POLARITY_PILOT_STATUS_V1"
FX_SIDE_PILOT_STATUS_SCHEMA_VERSION = 1
REQUEST_KEYS: set[str] = set()
SIDE_IDENTITIES = ("USD", "JPY")
REQUIRED_STATES = ("SUPPORTIVE", "ADVERSE")


def build_fx_side_pilot_status(
    payload: Mapping[str, Any],
    *,
    catalogue: TargetAwarePolarityCatalogue | None = None,
    registry: TargetAwarePolarityEvidencePacketRegistry | None = None,
) -> dict[str, Any]:
    """Report existing side-pilot evidence without admitting or deriving anything."""
    if not isinstance(payload, Mapping):
        raise ValueError("FX side pilot status request must be an object")
    unknown = sorted(set(payload) - REQUEST_KEYS)
    if unknown:
        raise ValueError("Unknown FX side pilot status field(s): " + ", ".join(unknown))

    loaded_registry = registry or TargetAwarePolarityEvidencePacketRegistry.load()
    loaded_catalogue = catalogue or TargetAwarePolarityCatalogue.load(
        evidence_registry=loaded_registry
    )
    side_statuses = {
        side: _side_status(side, catalogue=loaded_catalogue, registry=loaded_registry)
        for side in SIDE_IDENTITIES
    }
    ready_sides = [
        side for side, summary in side_statuses.items() if summary["pilotEvidenceComplete"]
    ]
    return {
        "contract": FX_SIDE_PILOT_STATUS_CONTRACT,
        "schemaVersion": FX_SIDE_PILOT_STATUS_SCHEMA_VERSION,
        "status": (
            "PILOT_EVIDENCE_PRESENT_RESEARCH_ONLY"
            if ready_sides
            else "PILOT_EVIDENCE_PENDING"
        ),
        "requiredStates": list(REQUIRED_STATES),
        "eligibleSides": ready_sides,
        "sides": side_statuses,
        "unknownGapPolicy": "UNREVIEWED_SIDE_EVENTS_REMAIN_UNKNOWN",
        "summary": (
            "At least one side has reviewed categorical examples in both required states. "
            "This remains research-only and does not create a pair direction."
            if ready_sides
            else "No side has the minimum reviewed categorical examples yet. Add real side-chart "
            "evidence through the existing immutable packet and catalogue review process."
        ),
        "guardrails": {
            "readOnly": True,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
            "financiallyValidated": False,
            "createsCatalogueEntry": False,
            "marketDirectionInferred": False,
            "fieldsFused": False,
            "actsAsSbcConfirmation": False,
        },
    }


def _side_status(
    side: str,
    *,
    catalogue: TargetAwarePolarityCatalogue,
    registry: TargetAwarePolarityEvidencePacketRegistry,
) -> dict[str, Any]:
    instrument_id = f"FX_CURRENCY:{side}"
    packets = [packet for packet in registry.packets if packet.instrument_id == instrument_id]
    entries = [entry for entry in catalogue.entries if entry.instrument_id == instrument_id]
    observed_states = sorted({entry.precomputed_polarity for entry in entries})
    missing_states = [state for state in REQUIRED_STATES if state not in observed_states]
    blockers: list[str] = []
    if not packets:
        blockers.append("NO_REVIEWED_IMMUTABLE_SIDE_PACKET")
    if not entries:
        blockers.append("NO_MATCHING_IMMUTABLE_CATALOGUE_ENTRY")
    if missing_states:
        blockers.append("MISSING_REQUIRED_CATEGORICAL_STATES")
    return {
        "sideIdentity": side,
        "instrumentId": instrument_id,
        "reviewedPacketCount": len(packets),
        "catalogueEntryCount": len(entries),
        "observedStates": observed_states,
        "missingRequiredStates": missing_states,
        "unknownGapsRetained": True,
        "pilotEvidenceComplete": not blockers,
        "blockers": blockers,
    }
