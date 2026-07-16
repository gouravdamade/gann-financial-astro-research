from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from sbc.models import GeoLocation, SbcSnapshotRequest
from sbc.snapshot import SbcFoundationEngine


LOCATION = GeoLocation(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata", altitude_m=216.0)
MOMENT = datetime(2026, 7, 17, 6, 30, tzinfo=timezone.utc)


def test_snapshot_is_reproducible_and_contains_no_trading_layer() -> None:
    request = SbcSnapshotRequest(
        at_utc=MOMENT,
        profile_id="sbc_raman_foundation_v1",
        bodies=("SATURN",),
        location=LOCATION,
    )
    engine = SbcFoundationEngine()
    first = engine.snapshot(request)
    second = engine.snapshot(request)
    assert first.snapshot_id == second.snapshot_id
    assert [item.body for item in first.positions] == ["SATURN", "SUN", "MOON"]
    assert first.astronomy_contract == "SBC_RAMAN_TRUE_NODE_SWISSEPH_FOUNDATION_V1"
    assert all(value is False for value in first.research_locks.values())
    encoded = json.dumps(first.to_dict(), sort_keys=True)
    assert "entry_price" not in encoded
    assert "profit" not in encoded
    assert "bullish" not in encoded
    assert "bearish" not in encoded


def test_snapshot_rejects_timezone_contract_mismatch() -> None:
    request = SbcSnapshotRequest(
        at_utc=MOMENT,
        profile_id="sbc_raman_foundation_v1",
        bodies=("SUN", "MOON"),
        location=GeoLocation(latitude=51.5, longitude=-0.1, timezone="Europe/London"),
    )
    with pytest.raises(ValueError, match="timezone must match"):
        SbcFoundationEngine().snapshot(request)


def test_sbc_package_is_isolated_from_market_and_execution_modules() -> None:
    package_root = Path(__file__).resolve().parent / "sbc"
    combined = "\n".join(path.read_text(encoding="utf-8") for path in package_root.glob("*.py"))
    forbidden_imports = (
        "decision_engine",
        "MetaTrader5",
        "reviewer_auto_suggest",
        "mt5_live",
        "plotly",
        "trade_candidate",
    )
    for name in forbidden_imports:
        assert name not in combined
