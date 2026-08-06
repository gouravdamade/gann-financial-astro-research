"""Generate immutable blank founder review packets from real TN astronomy events.

This is an offline artifact generator, not a polarity admission path.  Every
review decision remains deliberately empty when this command completes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
for candidate in (PROJECT_ROOT, LAB_ROOT, INSTRUMENT_SBC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (  # noqa: E402
    APPROVED_ASPECT_PROFILE_ID,
    CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
    compile_chart_conditioned_transit_event_range,
)


PACK_CONTRACT = "FOUNDER_BLANK_POLARITY_REVIEW_PACKET_V1"
MANIFEST_CONTRACT = "FOUNDER_BLANK_POLARITY_REVIEW_GENERATION_MANIFEST_V1"
UTC = timezone.utc
PILOT_START_UTC = "2025-04-01T00:00:00Z"
PILOT_END_UTC = "2025-05-01T00:00:00Z"
ALLOWED_POLARITIES = (
    "SUPPORTIVE",
    "ADVERSE",
    "MIXED",
    "NEUTRAL",
    "UNKNOWN_MORE_EVIDENCE_REQUIRED",
    "REJECT_EVENT_IDENTITY",
)
ALLOWED_EVIDENCE_CLASSES = (
    "SOURCE_BACKED_CLASSICAL_CANDIDATE",
    "FOUNDER_RESEARCH_HYPOTHESIS",
)


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _event_identity(event: dict[str, Any]) -> dict[str, Any]:
    return {
        key: event[key]
        for key in (
            "eventId",
            "eventHash",
            "eventContract",
            "sideIdentity",
            "instrumentIdentity",
            "chartId",
            "chartHypothesisId",
            "transitBody",
            "natalTarget",
            "aspectType",
            "applyingStartUtc",
            "exactUtc",
            "separatingEndUtc",
            "orbContract",
            "astronomyContract",
            "ayanamsha",
            "nodePolicy",
            "generatorVersion",
        )
    }


def _blank_review_row(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "eventIdentity": _event_identity(event),
        "founderReview": {
            "reviewedPolarity": None,
            "evidenceClassification": None,
            "sourceReferences": [],
            "reasoning": "",
            "reviewer": "",
            "reviewTimestampUtc": None,
            "reviewClassification": "",
            "reviewPacketHash": None,
        },
    }


def _build_pack(side: str) -> tuple[dict[str, Any], dict[str, Any]]:
    compiled = compile_chart_conditioned_transit_event_range(
        side_identity=side,
        range_start_utc=PILOT_START_UTC,
        range_end_utc=PILOT_END_UTC,
        aspect_profile_id=APPROVED_ASPECT_PROFILE_ID,
    )
    start, end = _parse_utc(PILOT_START_UTC), _parse_utc(PILOT_END_UTC)
    valid = sorted(
        (
            event
            for event in compiled["events"]
            if start <= _parse_utc(event["exactUtc"]) < end
        ),
        key=lambda event: (event["exactUtc"], event["eventId"]),
    )
    rows = [_blank_review_row(event) for event in valid[:12]]
    pack = {
        "contract": PACK_CONTRACT,
        "packetVersion": 1,
        "packetStatus": "BLANK_FOUNDER_REVIEW_REQUIRED",
        "sideIdentity": side,
        "instrumentIdentity": compiled["instrumentIdentity"],
        "chartId": compiled["chartId"],
        "chartHypothesisId": compiled["chartHypothesisId"],
        "selectionWindow": {
            "startUtc": PILOT_START_UTC,
            "endUtc": PILOT_END_UTC,
            "selectionRule": "FIRST_TWELVE_COMPLETE_EVENT_IDENTITIES_SORTED_BY_EXACT_UTC",
            "nonOutcomeSelected": True,
            "priceRead": False,
            "sbcRead": False,
            "llmUsed": False,
        },
        "eventCompiler": {
            key: compiled[key]
            for key in (
                "contract",
                "schemaVersion",
                "aspectProfileId",
                "astronomyContract",
                "historicalCivilTimeConversionPolicy",
                "ephemerisProvider",
                "ephemerisVersion",
                "ayanamsha",
                "nodePolicy",
                "generatorVersion",
                "generatorHash",
            )
        },
        "allowedFounderPolarityDecisions": list(ALLOWED_POLARITIES),
        "allowedEvidenceClassifications": list(ALLOWED_EVIDENCE_CLASSES),
        "sourceOnlyAdmission": "REQUIRES_SEPARATE_R4_MODE2_TO_MODE1_PROMOTION_GATE",
        "founderResearchAdmission": "CALIBRATED_RESEARCH_ONLY_NON_CLASSICAL_FINANCIALLY_UNVALIDATED",
        "totalValidEventsInWindow": len(valid),
        "includedEventCount": len(rows),
        "rows": rows,
        "guardrails": {
            "polarityAssigned": False,
            "catalogueEntryCreated": False,
            "modeOneAdmission": False,
            "magnitudeConfigured": False,
            "marketDirectionInferred": False,
            "executionAllowed": False,
            "automaticOrderPlacement": False,
        },
    }
    manifest = {
        "contract": MANIFEST_CONTRACT,
        "manifestVersion": 1,
        "sideIdentity": side,
        "selectionWindow": pack["selectionWindow"],
        "eventCompilerContract": CHART_CONDITIONED_TRANSIT_EVENT_RANGE_CONTRACT,
        "generatorHash": compiled["generatorHash"],
        "totalCompiledOverlapEvents": len(compiled["events"]),
        "totalValidEventsInWindow": len(valid),
        "includedEventCount": len(rows),
        "includedEventIds": [row["eventIdentity"]["eventId"] for row in rows],
        "rejectedEventCount": len(compiled["rejectedEvents"]),
        "guardrails": pack["guardrails"],
    }
    return pack, manifest


def _write(side: str, output_root: Path) -> tuple[Path, Path, dict[str, Any]]:
    pack, manifest = _build_pack(side)
    prefix = f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1"
    pack_path = output_root / f"{prefix}.json"
    manifest_path = output_root / f"{prefix}.manifest.json"
    pack_bytes = _json_bytes(pack)
    manifest.update(
        {
            "outputFile": pack_path.name,
            "outputSha256": _sha256(pack_bytes),
        }
    )
    output_root.mkdir(parents=True, exist_ok=True)
    pack_path.write_bytes(pack_bytes)
    manifest_path.write_bytes(_json_bytes(manifest))
    return pack_path, manifest_path, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    for side in ("USD", "JPY"):
        pack_path, manifest_path, manifest = _write(side, args.output_root)
        print(f"{side}: {manifest['includedEventCount']}/{manifest['totalValidEventsInWindow']} -> {pack_path}")
        print(f"{side} manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
