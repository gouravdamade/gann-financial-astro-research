"""Neutral-fixture adapters for the independently frozen evaluator schemas."""

from __future__ import annotations

from typing import Any

from .canonical import canonical_hash
from .models import NeutralFixture


SIGN_NAMES = {
    1: "ARIES", 2: "TAURUS", 3: "GEMINI", 4: "CANCER", 5: "LEO", 6: "VIRGO",
    7: "LIBRA", 8: "SCORPIO", 9: "SAGITTARIUS", 10: "CAPRICORN", 11: "AQUARIUS", 12: "PISCES",
}
BODIES = ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU")
A_ADAPTER_CONTRACT = {
    "adapterId": "MO_R4A_CANDIDATE_C_AB1_NEUTRAL_TO_A_V1",
    "eventIdPrefix": "SYNTHETIC_AB_",
    "inputKind": "SYNTHETIC_ONLY",
    "roles": {"sourceRole": "TRANSIT_BODY", "targetRole": "NATAL_TARGET"},
    "signEncoding": "CANONICAL_SIGN_NAME",
    "syntheticPositionAlgorithm": "SIGN_START_PLUS_ONE_DEGREE_V1",
}
B_ADAPTER_CONTRACT = {
    "adapterId": "MO_R4A_CANDIDATE_C_AB1_NEUTRAL_TO_B_V1",
    "eventIdPrefix": "SYNTHETIC_AB_",
    "roles": "SOURCE_BODY_TARGET_BODY_ONLY",
    "signEncoding": "CANONICAL_SIGN_NAME",
    "syntheticPositionAlgorithm": "SIGN_START_PLUS_ONE_DEGREE_V1",
}


def _position(body: str, sign_index: int, speed: float) -> dict[str, Any]:
    return {
        "body": body,
        "siderealLongitudeDeg": float((sign_index - 1) * 30 + 1),
        "siderealLongitudeSpeedDegPerDay": speed,
        "sign": SIGN_NAMES[sign_index],
        "signIndex": sign_index,
    }


def _synthetic_event_identity(fixture: NeutralFixture) -> tuple[str, str]:
    event_id = f"SYNTHETIC_AB_{fixture.fixture_id}"
    return event_id, canonical_hash({"eventId": event_id, "semanticFixtureIdentityHash": fixture.semantic_fixture_identity_hash})


def _shared_positions(fixture: NeutralFixture) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    signs = {
        "SUN": fixture.sun_sign_index,
        "MOON": 7,
        "MARS": 3,
        "MERCURY": 4,
        "JUPITER": 5,
        "VENUS": 8,
        "SATURN": 9,
        "RAHU": 10,
        "KETU": 11,
    }
    signs[fixture.source_body] = fixture.source_sign_index
    signs["SUN"] = fixture.sun_sign_index
    transit = _position(fixture.source_body, fixture.source_sign_index, 1.0)
    natal = _position(fixture.target_body, fixture.target_sign_index, 0.5)
    sun = _position("SUN", fixture.sun_sign_index, 0.9)
    moon = _position("MOON", signs["MOON"], 13.0)
    planetary = [_position(body, signs[body], 0.1) for body in BODIES]
    return transit, natal, sun, moon, planetary


def adapt_fixture_for_a(fixture: NeutralFixture) -> dict[str, Any]:
    """Build A's admitted synthetic-only event representation."""

    event_id, event_hash = _synthetic_event_identity(fixture)
    transit, natal, sun, moon, planetary = _shared_positions(fixture)
    event: dict[str, Any] = {
        "_evaluatorInputKind": "SYNTHETIC_ONLY",
        "eventId": event_id,
        "eventHash": event_hash,
        "sideIdentity": "SYNTHETIC_AB_NEUTRAL",
        "chartIdentity": {"chartId": "SYNTHETIC_AB_NEUTRAL_CHART"},
        "exactUtc": "2099-01-01T00:00:00Z",
        "eventRoles": {
            "sourceBody": fixture.source_body,
            "targetBody": fixture.target_body,
            "sourceRole": "TRANSIT_BODY",
            "targetRole": "NATAL_TARGET",
        },
        "transitPositionAtExactUtc": transit,
        "natalTargetPositionAtFrozenChartUtc": natal,
        "sunPositionAtExactUtc": sun,
        "moonPositionAtExactUtc": moon,
        "planetaryPositionsAtExactUtc": planetary,
    }
    if fixture.optional_aspect_type is not None:
        event["aspectType"] = fixture.optional_aspect_type
    return event


def adapt_fixture_for_b(fixture: NeutralFixture) -> dict[str, Any]:
    """Build B's independent synthetic input without A-only role fields."""

    event_id, event_hash = _synthetic_event_identity(fixture)
    transit, natal, sun, moon, planetary = _shared_positions(fixture)
    event: dict[str, Any] = {
        "eventId": event_id,
        "eventHash": event_hash,
        "sideIdentity": "SYNTHETIC_AB_NEUTRAL",
        "chartIdentity": "SYNTHETIC_AB_NEUTRAL_CHART",
        "exactUtc": "2099-01-01T00:00:00Z",
        "eventRoles": {"sourceBody": fixture.source_body, "targetBody": fixture.target_body},
        "transitPositionAtExactUtc": transit,
        "natalTargetPositionAtFrozenChartUtc": natal,
        "sunPositionAtExactUtc": sun,
        "moonPositionAtExactUtc": moon,
        "planetaryPositionsAtExactUtc": {position["body"]: position for position in planetary},
    }
    if fixture.optional_aspect_type is not None:
        event["aspectType"] = fixture.optional_aspect_type
    return event
