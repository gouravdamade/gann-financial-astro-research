from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from chart_conditioned_aspects.founder_chart_registry import (
    DEFAULT_REGISTRY_PATH,
    load_founder_chart_hypotheses,
)


def test_founder_approved_chart_records_are_exact_time_and_inert() -> None:
    charts = load_founder_chart_hypotheses()
    assert [chart.instrument_id for chart in charts] == ["FX_CURRENCY:USD", "FX_CURRENCY:JPY"]
    assert all(chart.status == "ACCEPTED_RESEARCH" for chart in charts)
    assert all(chart.time_accuracy == "EXACT_TIME" for chart in charts)
    assert all(chart.allows_houses for chart in charts)
    assert all("NOT_ADMITTED_FOR_FUNCTIONAL_LORDSHIP" in chart.house_model for chart in charts)


def test_historical_civil_times_round_trip_to_persisted_utc() -> None:
    raw = json.loads(DEFAULT_REGISTRY_PATH.read_text(encoding="utf-8"))
    for record in raw["records"]:
        local = datetime.fromisoformat(record["localCivilTime"]).replace(tzinfo=ZoneInfo(record["timezone"]))
        expected = datetime.fromisoformat(record["timestampUtc"].replace("Z", "+00:00"))
        assert local.astimezone(ZoneInfo("UTC")) == expected


def test_founder_chart_records_do_not_contain_polarity_or_execution_fields() -> None:
    raw = json.loads(Path(DEFAULT_REGISTRY_PATH).read_text(encoding="utf-8"))
    contract = raw["astronomyContract"]
    assert contract["executionAllowed"] is False
    assert contract["polarityAllowed"] is False
    assert contract["pairDerivationAllowed"] is False
    for record in raw["records"]:
        assert "polarity" not in record
        assert "catalogue" not in record
