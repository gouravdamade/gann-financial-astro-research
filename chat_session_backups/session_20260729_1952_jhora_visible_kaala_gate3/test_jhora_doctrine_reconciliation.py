from __future__ import annotations

from jhora_doctrine_reconciliation import build_summary


def test_locked_reconciliation_metrics_are_reproducible() -> None:
    summary, top_level, drik_rows = build_summary()

    assert len(top_level) == 245
    assert len(drik_rows) == 175
    assert summary["toleranceVirupa"] == 0.5

    kaala = summary["topLevel"]["kaala"]
    assert kaala["localCloser"] == 35
    assert kaala["pyjhoraCloser"] == 0
    assert kaala["localPass"] == 5
    assert kaala["localMeanAbsoluteDeltaVirupa"] == 2.762980006
    assert kaala["pyjhoraMeanAbsoluteDeltaVirupa"] == 57.030571429

    corrected_total = summary["topLevel"]["total"]
    assert corrected_total["localCloser"] == 33
    assert corrected_total["localPass"] == 3
    assert corrected_total["localMeanAbsoluteDeltaVirupa"] == 11.829084359
    assert corrected_total["pyjhoraMeanAbsoluteDeltaVirupa"] == 71.741714286

    sthana = summary["topLevel"]["sthana"]
    assert sthana["localPass"] == 1
    assert sthana["localMeanAbsoluteDeltaVirupa"] == 6.296255146
    assert sthana["pyjhoraMeanAbsoluteDeltaVirupa"] == 0.965714286

    naisargika = summary["topLevel"]["naisargika"]
    assert naisargika["localPass"] == 35
    assert naisargika["localMaxAbsoluteDeltaVirupa"] == 0.01

    component_gate = summary["componentCertification"]
    assert component_gate["status"] == "partial_independent_witness_alignment"
    assert component_gate["witnessAlignedTopLevel"] == ["naisargika"]
    assert component_gate["witnessAlignedKaalaSubcomponents"] == [
        "abda",
        "hora",
        "masa",
        "paksha",
        "tribhaga",
        "vara",
        "yuddha",
    ]
    assert component_gate["fullShadbalaCertified"] is False
    assert component_gate["drikCertified"] is False
    assert component_gate["executionAllowed"] is False

    chesta = summary["chesta"]
    assert chesta["luminaryRows"] == 10
    assert chesta["jhoraTotalExcludesDisplayedChesta"] == 10
    assert chesta["excludedChestaMaxDisplayResidualVirupa"] <= 0.01
    assert chesta["includedChestaMinAbsoluteResidualVirupa"] > 0.5


def test_visible_kaala_witness_locks_promoted_and_pending_components() -> None:
    summary, _, _ = build_summary()
    visible = summary["kaalaVisibleWitness"]

    assert visible["comparisonRows"] == 350
    for measure in ("abda", "masa", "vara", "tribhaga", "yuddha"):
        assert visible["components"][measure]["localPass"] == 35

    paksha = visible["components"]["paksha"]
    assert paksha["localPass"] == 35
    assert paksha["localMaxVirupa"] < 0.5

    assert visible["components"]["hora"]["localPass"] == 35
    assert visible["components"]["nathonnatha"]["localPass"] == 11
    assert visible["components"]["ayana"]["localPass"] == 13
    assert visible["components"]["total"]["localPass"] == 5
    assert summary["kaalaCategoricalResiduals"] == []


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
    assert any(
        "Paksha" in decision and "35/35" in decision
        for decision in summary["decisions"]
    )
