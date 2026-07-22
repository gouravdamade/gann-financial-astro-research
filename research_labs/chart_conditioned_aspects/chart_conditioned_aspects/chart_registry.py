from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .models import OrganizationChartHypothesis


class ChartRegistry:
    """In-memory Milestone 1 registry that refuses silent chart selection."""

    def __init__(self) -> None:
        self._charts: dict[str, OrganizationChartHypothesis] = {}

    def register(self, chart: OrganizationChartHypothesis) -> None:
        if chart.chart_id in self._charts:
            raise ValueError(f"chart already registered: {chart.chart_id}")
        self._charts[chart.chart_id] = chart

    def get(self, chart_id: str) -> OrganizationChartHypothesis:
        try:
            return self._charts[str(chart_id)]
        except KeyError as exc:
            raise KeyError(f"unknown chart: {chart_id}") from exc

    def accept(
        self, chart_id: str, *, reviewer: str, accepted_at: datetime
    ) -> OrganizationChartHypothesis:
        chart = self.get(chart_id)
        accepted = replace(
            chart,
            status="ACCEPTED_RESEARCH",
            accepted_by=str(reviewer).strip(),
            accepted_at=accepted_at,
        )
        self._charts[chart_id] = accepted
        return accepted

    def active_candidates(
        self,
        instrument_id: str,
        *,
        at: datetime,
        accepted_only: bool = True,
    ) -> tuple[OrganizationChartHypothesis, ...]:
        matches = [
            chart
            for chart in self._charts.values()
            if chart.instrument_id == instrument_id
            and chart.effective_at(at)
            and (not accepted_only or chart.status == "ACCEPTED_RESEARCH")
        ]
        return tuple(sorted(matches, key=lambda item: item.chart_id))

    def require_single_active(
        self, instrument_id: str, *, at: datetime
    ) -> OrganizationChartHypothesis:
        matches = self.active_candidates(instrument_id, at=at)
        if not matches:
            raise ValueError(f"no accepted active chart for {instrument_id}")
        if len(matches) > 1:
            ids = ", ".join(chart.chart_id for chart in matches)
            raise ValueError(
                f"multiple accepted chart hypotheses for {instrument_id}: {ids}; "
                "evaluate separately or use a predeclared ensemble"
            )
        return matches[0]

    def all(self) -> tuple[OrganizationChartHypothesis, ...]:
        return tuple(sorted(self._charts.values(), key=lambda item: item.chart_id))
