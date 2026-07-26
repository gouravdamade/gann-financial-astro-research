from __future__ import annotations

from jhora_doctrine_reconciliation import build_summary


def test_locked_reconciliation_metrics_are_reproducible() -> None:
    summary, top_level, drik_rows = build_summary()

    assert len(top_level) == 140
    assert len(drik_rows) == 175
    assert summary["toleranceVirupa"] == 0.5

    kaala = summary["topLevel"]["kaala"]
    assert kaala["localCloser"] == 35
    assert kaala["pyjhoraCloser"] == 0
    assert kaala["localPass"] == 4
    assert kaala["localMeanAbsoluteDeltaVirupa"] == 7.982740686
    assert kaala["pyjhoraMeanAbsoluteDeltaVirupa"] == 57.030571429

    corrected_total = summary["topLevel"]["total"]
    assert corrected_total["localCloser"] == 33
    assert corrected_total["localMeanAbsoluteDeltaVirupa"] == 17.416464092
    assert corrected_total["pyjhoraMeanAbsoluteDeltaVirupa"] == 71.741714286

    assert summary["chesta"]["moonRows"] == 5
    assert summary["chesta"]["moonDisplayMatchesHalfLocalPaksha"] == 5
    assert summary["chesta"]["moonHalfLocalMaxAbsoluteDeltaVirupa"] < 0.005


def test_named_drik_profiles_remain_diagnostic() -> None:
    summary, _, _ = build_summary()
    profiles = {
        row["profileId"]: row for row in summary["drikCandidateProfiles"]
    }

    current = profiles["current_dynamic_nature_range_special"]
    assert current["pass"] == 9
    assert current["fail"] == 26
    assert current["meanAbsoluteDeltaVirupa"] == 7.319928571

    bright_half = profiles[
        "bright_half_moon_current_mercury_no_range_special"
    ]
    assert bright_half["pass"] == 19
    assert bright_half["fail"] == 16
    assert bright_half["meanAbsoluteDeltaVirupa"] == 3.290214286

    assert summary["status"] == "diagnostic_reconciliation_not_certified"
    assert summary["kaalaCategoricalResiduals"] == [
        {
            "sampleId": "case_127_sr_touch_start",
            "planet": "MOON",
            "jhoraMinusLocalVirupa": 90.677900892,
            "nearestCategoricalQuantumVirupa": 90.0,
            "absoluteRemainderVirupa": 0.677900892,
            "interpretation": (
                "Possible 15/30/45/60-virupa lord-award disagreement; "
                "requires a visible JHora Kaala subcomponent table."
            ),
        },
        {
            "sampleId": "case_127_sr_touch_start",
            "planet": "MERCURY",
            "jhoraMinusLocalVirupa": 44.91937128,
            "nearestCategoricalQuantumVirupa": 45.0,
            "absoluteRemainderVirupa": 0.08062872,
            "interpretation": (
                "Possible 15/30/45/60-virupa lord-award disagreement; "
                "requires a visible JHora Kaala subcomponent table."
            ),
        },
    ]
