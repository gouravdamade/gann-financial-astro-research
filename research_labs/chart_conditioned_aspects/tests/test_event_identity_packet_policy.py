from __future__ import annotations

import hashlib
import sys
from pathlib import Path


FOUNDER_REVIEW_ROOT = Path(__file__).resolve().parents[1] / "founder_review"
if str(FOUNDER_REVIEW_ROOT) not in sys.path:
    sys.path.insert(0, str(FOUNDER_REVIEW_ROOT))

from run_event_identity_integrity_audit import select_single_pass_replacements  # noqa: E402


def test_v2_replacements_are_exact_utc_then_event_id_and_exclude_unresolved_only() -> None:
    events = [
        {"eventId": "TN_B", "exactUtc": "2025-04-01T01:00:00Z"},
        {"eventId": "TN_A", "exactUtc": "2025-04-01T01:00:00Z"},
        {"eventId": "TN_C", "exactUtc": "2025-04-01T02:00:00Z"},
        {"eventId": "TN_OUTSIDE", "exactUtc": "2025-05-01T00:00:00Z"},
    ]
    verifications = {
        "TN_A": {"status": "SINGLE_PASS_VERIFIED"},
        "TN_B": {"status": "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED"},
        "TN_C": {"status": "SINGLE_PASS_VERIFIED"},
        "TN_OUTSIDE": {"status": "SINGLE_PASS_VERIFIED"},
    }

    first = select_single_pass_replacements(events, verifications)
    second = select_single_pass_replacements(events, verifications)

    assert [event["eventId"] for event in first] == ["TN_A", "TN_C"]
    assert first == second


def test_v1_packet_is_only_read_for_audit_history() -> None:
    packet = FOUNDER_REVIEW_ROOT / "USD_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"
    before = hashlib.sha256(packet.read_bytes()).hexdigest()
    _ = select_single_pass_replacements([], {})
    after = hashlib.sha256(packet.read_bytes()).hexdigest()

    assert after == before
