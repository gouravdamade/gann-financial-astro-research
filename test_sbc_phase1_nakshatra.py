from __future__ import annotations

import pytest

from sbc.enums import AbhijitPolicy
from sbc.models import AbhijitInterval
from sbc.nakshatra import NAKSHATRA_SPAN_DEG, canonical_membership, interval_contains, sbc_memberships


def test_canonical_nakshatra_and_pada_boundaries() -> None:
    assert canonical_membership(0.0).name == "Ashwini"
    assert canonical_membership(0.0).pada == 1
    assert canonical_membership(NAKSHATRA_SPAN_DEG).name == "Bharani"
    assert canonical_membership(359.999999).name == "Revati"
    assert canonical_membership(359.999999).pada == 4


def test_longitudes_normalize_without_changing_membership() -> None:
    assert canonical_membership(-1.0) == canonical_membership(359.0)
    assert canonical_membership(361.0) == canonical_membership(1.0)


def test_abhijit_is_only_added_by_a_source_cited_profile_interval() -> None:
    interval = AbhijitInterval(276.0, 280.0, "SOURCE_RULE_PAGE_12")
    assert interval_contains(276.0, interval)
    assert not interval_contains(280.0, interval)
    ignored = sbc_memberships(277.0, AbhijitPolicy.IGNORE_FOR_PLANET_PLACEMENT)
    overlap = sbc_memberships(277.0, AbhijitPolicy.OVERLAP_FLAG, interval)
    replacement = sbc_memberships(277.0, AbhijitPolicy.REPLACE_SEGMENT, interval)
    assert len(ignored) == 1
    assert [item.name for item in overlap] == [ignored[0].name, "Abhijit"]
    assert [item.name for item in replacement] == ["Abhijit"]
    assert replacement[0].source_rule_ids == ("SOURCE_RULE_PAGE_12",)


def test_abhijit_policy_refuses_uncited_magic_interval() -> None:
    with pytest.raises(ValueError, match="source-cited interval"):
        sbc_memberships(277.0, AbhijitPolicy.OVERLAP_FLAG)
