from __future__ import annotations

from fractions import Fraction

from panchanga_doctrine import NAKSHATRA_NAMES

from .enums import AbhijitPolicy
from .models import AbhijitInterval, NakshatraMembership


NAKSHATRA_SPAN_DEG = float(Fraction(360, 27))
PADA_SPAN_DEG = float(Fraction(360, 108))
CANONICAL_RULE_ID = "SBC_CANONICAL_27_NAKSHATRA_EQUAL_SPAN_V1"


def normalize_degrees(value: float) -> float:
    return float(value) % 360.0


def canonical_membership(longitude_deg: float) -> NakshatraMembership:
    longitude = normalize_degrees(longitude_deg)
    index0 = min(26, int(longitude // NAKSHATRA_SPAN_DEG))
    offset = longitude - index0 * NAKSHATRA_SPAN_DEG
    pada = min(4, int(offset // PADA_SPAN_DEG) + 1)
    fraction = offset / NAKSHATRA_SPAN_DEG
    return NakshatraMembership(
        name=NAKSHATRA_NAMES[index0],
        index_1=index0 + 1,
        pada=pada,
        fraction=fraction,
        membership_kind="CANONICAL_27",
        source_rule_ids=(CANONICAL_RULE_ID,),
    )


def _linear_contains(value: float, start: float, end: float, start_inclusive: bool, end_inclusive: bool) -> bool:
    left = value >= start if start_inclusive else value > start
    right = value <= end if end_inclusive else value < end
    return left and right


def interval_contains(longitude_deg: float, interval: AbhijitInterval) -> bool:
    value = normalize_degrees(longitude_deg)
    start = normalize_degrees(interval.start_deg)
    end = normalize_degrees(interval.end_deg)
    if start == end:
        return True
    if start < end:
        return _linear_contains(value, start, end, interval.start_inclusive, interval.end_inclusive)
    return _linear_contains(value, start, 360.0, interval.start_inclusive, False) or _linear_contains(
        value,
        0.0,
        end,
        True,
        interval.end_inclusive,
    )


def sbc_memberships(
    longitude_deg: float,
    policy: AbhijitPolicy,
    interval: AbhijitInterval | None = None,
) -> tuple[NakshatraMembership, ...]:
    canonical = canonical_membership(longitude_deg)
    if policy is AbhijitPolicy.IGNORE_FOR_PLANET_PLACEMENT:
        return (canonical,)
    if interval is None:
        raise ValueError("Abhijit overlap/replacement requires a source-cited interval")
    if not interval_contains(longitude_deg, interval):
        return (canonical,)
    abhijit = NakshatraMembership(
        name="Abhijit",
        index_1=None,
        pada=None,
        fraction=None,
        membership_kind="ABHIJIT_SOURCE_PROFILE",
        source_rule_ids=(interval.source_rule_id,),
    )
    if policy is AbhijitPolicy.REPLACE_SEGMENT:
        return (abhijit,)
    return (canonical, abhijit)
