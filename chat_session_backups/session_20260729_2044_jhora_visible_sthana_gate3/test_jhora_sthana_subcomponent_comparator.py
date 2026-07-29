from __future__ import annotations

from jhora_sthana_subcomponent_comparator import (
    DEFAULT_DOCTRINE_CONFIG,
    DEFAULT_TOP_LEVEL_WITNESS,
    DEFAULT_WITNESS,
    PROFILE_IDS,
    build_comparison_rows,
    build_summary,
)


def test_visible_jhora_profile_reconciles_complete_sthana_matrix() -> None:
    rows = build_comparison_rows()
    summary = build_summary(
        rows,
        witness_path=DEFAULT_WITNESS,
        top_level_path=DEFAULT_TOP_LEVEL_WITNESS,
        doctrine_config=DEFAULT_DOCTRINE_CONFIG,
    )

    assert len(rows) == 175
    assert summary["comparisonRows"] == 175
    assert summary["profiles"]["jhora_visible"]["profileId"] == (
        PROFILE_IDS["jhora_visible"]
    )
    assert all(
        values["pass"] == 35
        for values in summary["profiles"]["jhora_visible"][
            "components"
        ].values()
    )
    assert summary["profiles"]["jhora_visible"]["total"]["pass"] == 35
    assert summary["productionChangeAllowed"] is False
    assert summary["executionAllowed"] is False


def test_visible_witness_localizes_saptavargaja_profile_difference() -> None:
    rows = build_comparison_rows()
    summary = build_summary(
        rows,
        witness_path=DEFAULT_WITNESS,
        top_level_path=DEFAULT_TOP_LEVEL_WITNESS,
        doctrine_config=DEFAULT_DOCTRINE_CONFIG,
    )

    source = summary["profiles"]["source"]["components"]
    pyjhora = summary["profiles"]["pyjhora"]["components"]
    assert source["saptavargaja"]["pass"] == 3
    assert pyjhora["saptavargaja"]["pass"] == 34
    assert source["uchcha"]["pass"] == 35
    assert source["ojayugma"]["pass"] == 35
    assert source["kendradi"]["pass"] == 35
    assert source["drekkana"]["pass"] == 35
