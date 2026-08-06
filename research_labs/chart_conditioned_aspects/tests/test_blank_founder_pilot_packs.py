from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "founder_review"
UTC = timezone.utc


def _parse(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _load(side: str) -> tuple[dict, dict, Path]:
    prefix = f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1"
    path = ROOT / f"{prefix}.json"
    return (
        json.loads(path.read_text(encoding="utf-8")),
        json.loads((ROOT / f"{prefix}.manifest.json").read_text(encoding="utf-8")),
        path,
    )


def test_blank_founder_packets_are_exactly_blank_and_non_outcome_selected() -> None:
    for side, instrument in (("USD", "FX_CURRENCY:USD"), ("JPY", "FX_CURRENCY:JPY")):
        packet, manifest, path = _load(side)
        assert packet["contract"] == "FOUNDER_BLANK_POLARITY_REVIEW_PACKET_V1"
        assert packet["packetStatus"] == "BLANK_FOUNDER_REVIEW_REQUIRED"
        assert packet["sideIdentity"] == side
        assert packet["instrumentIdentity"] == instrument
        assert packet["includedEventCount"] == 12
        assert len(packet["rows"]) == 12
        assert packet["selectionWindow"]["nonOutcomeSelected"] is True
        assert packet["selectionWindow"]["priceRead"] is False
        assert packet["selectionWindow"]["sbcRead"] is False
        assert packet["selectionWindow"]["llmUsed"] is False
        assert packet["guardrails"]["polarityAssigned"] is False
        assert packet["guardrails"]["executionAllowed"] is False
        exacts = [row["eventIdentity"]["exactUtc"] for row in packet["rows"]]
        assert exacts == sorted(exacts)
        for row in packet["rows"]:
            event = row["eventIdentity"]
            review = row["founderReview"]
            assert event["eventId"].startswith("TN_")
            assert event["applyingStartUtc"] < event["exactUtc"] < event["separatingEndUtc"]
            assert review == {
                "reviewedPolarity": None,
                "evidenceClassification": None,
                "sourceReferences": [],
                "reasoning": "",
                "reviewer": "",
                "reviewTimestampUtc": None,
                "reviewClassification": "",
                "reviewPacketHash": None,
            }
        assert manifest["includedEventCount"] == 12
        assert manifest["includedEventIds"] == [row["eventIdentity"]["eventId"] for row in packet["rows"]]
        assert manifest["outputSha256"] == hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_v1_packets_are_preserved_after_independent_identity_audit() -> None:
    for side in ("USD", "JPY"):
        packet, original_manifest, path = _load(side)
        audit_manifest = json.loads(
            (ROOT / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json").read_text(
                encoding="utf-8"
            )
        )
        rendering = (ROOT / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.md").read_text(
            encoding="utf-8"
        )

        assert audit_manifest["contract"] == "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1"
        assert audit_manifest["allRowsSinglePassVerified"] is True
        assert audit_manifest["packetSha256"] == hashlib.sha256(path.read_bytes()).hexdigest().upper()
        assert audit_manifest["originalGenerationManifestOutputSha256"] == original_manifest["outputSha256"]
        assert audit_manifest["verifiedEventIds"] == [row["eventIdentity"]["eventId"] for row in packet["rows"]]
        assert "Founder polarity" in rendering
        assert "bullish" not in rendering.lower()
        assert "bearish" not in rendering.lower()
