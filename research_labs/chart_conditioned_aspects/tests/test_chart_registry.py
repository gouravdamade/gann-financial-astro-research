from __future__ import annotations

from chart_conditioned_aspects import ChartRegistry

from conftest import NOW, make_chart


def test_registry_rejects_duplicate_chart_id() -> None:
    registry = ChartRegistry()
    chart = make_chart()
    registry.register(chart)
    try:
        registry.register(chart)
    except ValueError as exc:
        assert "already registered" in str(exc)
    else:
        raise AssertionError("duplicate chart registration was accepted")


def test_registry_refuses_silent_chart_shopping() -> None:
    registry = ChartRegistry()
    registry.register(make_chart(chart_id="HYPOTHESIS-A"))
    registry.register(make_chart(chart_id="HYPOTHESIS-B"))
    try:
        registry.require_single_active("TEST.EQUITY", at=NOW)
    except ValueError as exc:
        assert "evaluate separately" in str(exc)
    else:
        raise AssertionError("multiple active chart hypotheses were silently selected")
