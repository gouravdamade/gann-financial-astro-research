"""Frozen Holm and Benjamini-Hochberg adjustment functions."""

from __future__ import annotations

from typing import Mapping


def holm_bonferroni(raw_p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(raw_p_values.items(), key=lambda item: (item[1], item[0]))
    total, running, adjusted = len(ordered), 0.0, {}
    for index, (key, value) in enumerate(ordered):
        running = max(running, min(1.0, (total - index) * value))
        adjusted[key] = running
    return adjusted


def benjamini_hochberg(raw_p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(raw_p_values.items(), key=lambda item: (item[1], item[0]))
    total, running, adjusted = len(ordered), 1.0, {}
    for index in range(total - 1, -1, -1):
        key, value = ordered[index]
        running = min(running, min(1.0, value * total / (index + 1)))
        adjusted[key] = running
    return adjusted
