"""Consistency gates for the bounded R4-T1 Trailokya page-certification packet."""

from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
PACKET_PATH = (
    ROOT
    / "configs"
    / "sbc"
    / "evidence_packets"
    / "trailokya_dipika_1972_vedha_page_certification_v1.yaml"
)

REQUIRED_PACKET_FIELDS = {
    "evidencePacketId",
    "category",
    "sourceCitation",
    "originalSanskritHindiText",
    "literalTranscription",
    "literalTranslation",
    "implementationInterpretation",
    "exactCategoricalRule",
    "numericalValue",
    "dependencies",
    "ambiguityNotes",
    "conflictingWitnessNotes",
    "proposedVariableId",
    "permittedOscillatorRole",
    "proposedMode1Limitations",
    "reviewer",
    "founderDecision",
    "founderReviewProposal",
}


def _packet() -> dict:
    return yaml.safe_load(PACKET_PATH.read_text(encoding="utf-8"))


def test_packet_is_tied_to_the_held_original_1972_scan() -> None:
    packet = _packet()
    source = packet["source"]
    assert source["sourceId"] == "TRAILOKYA_DIPIKA_VYAS_1972_ORIGINAL_SCAN"
    assert source["citationAuthority"] == "ORIGINAL_PAGE_IMAGE_ONLY"
    assert source["sha256"] == "1EF82899F8FEC6165E7F0514253EA0BE39D991226F9CD3773C9AF8D829892194"


def test_each_evidence_packet_is_complete_and_page_cited() -> None:
    packet = _packet()
    entries = packet["evidencePackets"]
    assert len(entries) == 6
    assert len({entry["evidencePacketId"] for entry in entries}) == len(entries)
    assert len({entry["proposedVariableId"] for entry in entries}) == len(entries)
    for entry in entries:
        assert REQUIRED_PACKET_FIELDS <= entry.keys()
        assert entry["sourceCitation"]["pdfImageIndex"]
        assert entry["originalSanskritHindiText"]
        assert entry["dependencies"]


def test_founder_approved_geometry_stays_narrow_and_non_scoring() -> None:
    packet = _packet()
    approved = [
        entry
        for entry in packet["evidencePackets"]
        if entry["founderDecision"] == "APPROVED_FOR_SOURCE_ONLY_WITH_LIMITS"
    ]
    assert {entry["proposedVariableId"] for entry in approved} == {
        "SBC_TD1972_VARIABLE_PLANET_DIRECTION",
        "SBC_TD1972_FIXED_THREE_DIRECTION_BODIES",
        "SBC_TD1972_RAY_EXTENT",
    }
    pending = {
        entry["proposedVariableId"]
        for entry in packet["evidencePackets"]
        if entry["founderDecision"] == "PENDING"
    }
    assert {
        "SBC_TD1972_BASE_NATURAL_PLANET_CLASS",
        "SBC_TD1972_ISOLATED_RESULT_FACTORS",
    } <= pending


def test_global_locks_and_unresolved_doctrine_remain_explicit() -> None:
    packet = _packet()
    locks = packet["globalLocks"]
    assert all(
        locks[key] is False
        for key in (
            "automaticPromotion",
            "priceDataUsed",
            "outcomeSelectionUsed",
            "llmGapFillingAllowed",
            "executionModified",
            "autoSuggestInfluenceAllowed",
            "packageCandidateAllowed",
        )
    )
    unresolved = set(packet["unresolvedOutsideMode1"])
    assert {
        "SBC_TD1972_NUMERIC_SWIFT_VS_MEAN_THRESHOLD",
        "SBC_TD1972_MODIFIER_STACKING_OR_PRECEDENCE",
        "SBC_TD1972_AUTOMATIC_MERCURY_ASSOCIATION",
        "SBC_TD1972_MOON_NATURE_BOUNDARY",
        "SBC_TD1972_ARGHYA_TABLE_UNRESOLVED_VALUES",
        "SBC_TD1972_MARKET_DIRECTION_INTERPRETATION",
    } <= unresolved
