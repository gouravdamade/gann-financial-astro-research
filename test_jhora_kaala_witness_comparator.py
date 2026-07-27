from __future__ import annotations

from pathlib import Path

import pytest

from jhora_kaala_witness_comparator import (
    DISPLAY_SUM_TOLERANCE_VIRUPA,
    MEASURES,
    PLANETS,
    compare_profiles,
    expected_kaala_keys,
    parse_accessibility_table,
    summarize,
)


def accessibility_fixture(
    *,
    component_override: dict[tuple[str, str], float] | None = None,
) -> str:
    component_override = component_override or {}
    lines = [
        'Window: "Jagannatha Hora - fixture.jhd", App: jhora.exe.',
        "  7 header item Planet",
        "  8 header item Kaala Bala",
        "  9 header item In rupas",
        "  10 header item Natonnata",
        "  11 header item Paksha",
        "  12 header item Tribhaga",
        "  13 header item Abda",
        "  14 header item Maasa",
        "  15 header item Vaara",
        "  16 header item Hora",
        "  17 header item Ayana",
        "  18 header item Yuddha",
    ]
    row_id = 20
    for planet in PLANETS:
        values = {
            "nathonnatha": 10.0,
            "paksha": 20.0,
            "tribhaga": 0.0,
            "abda": 0.0,
            "masa": 0.0,
            "vara": 0.0,
            "hora": 0.0,
            "ayana": 30.0,
            "yuddha": 0.0,
        }
        for measure in values:
            values[measure] = component_override.get(
                (planet, measure),
                values[measure],
            )
        total = sum(values.values())
        lines.append(f"  {row_id} list item (selectable) {planet.title()}")
        lines.append(f"    {row_id + 1} text {planet.title()}")
        lines.append(f"    {row_id + 2} text {total:.2f}")
        lines.append(f"    {row_id + 3} text {total / 60.0:.2f}")
        for offset, measure in enumerate(MEASURES[1:], start=4):
            lines.append(
                f"    {row_id + offset} text {values[measure]:.2f}"
            )
        row_id += 20
    return "\n".join(lines) + "\n"


def write_fixture(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "case_8_event_start_kaala_bala_accessibility.txt"
    path.write_text(text, encoding="utf-8")
    path.with_name("case_8_event_start_kaala_bala_locked.jpg").write_bytes(
        b"locked screenshot"
    )
    return path


def test_parser_extracts_complete_visible_table(tmp_path: Path) -> None:
    rows = parse_accessibility_table(
        write_fixture(tmp_path, accessibility_fixture())
    )

    assert len(rows) == 7 * 10
    assert {
        (row["planet"], row["measure"])
        for row in rows
    } == {(planet, measure) for planet in PLANETS for measure in MEASURES}
    total = next(
        row
        for row in rows
        if row["planet"] == "SUN" and row["measure"] == "total"
    )
    assert float(total["jhora_value_virupa"]) == 60.0
    assert abs(float(total["displayed_total_minus_sum_virupa"])) <= (
        DISPLAY_SUM_TOLERANCE_VIRUPA
    )


def test_parser_rejects_empty_or_incomplete_table(tmp_path: Path) -> None:
    path = write_fixture(tmp_path, accessibility_fixture())
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("Saturn", "Rahu"), encoding="utf-8")

    with pytest.raises(RuntimeError, match="planet order/membership mismatch"):
        parse_accessibility_table(path)


def test_profile_comparison_keeps_all_ten_measures_separate() -> None:
    witness = []
    local = {}
    pyjhora = {}
    for key in expected_kaala_keys():
        sample_id, planet, measure = key
        witness.append(
            {
                "sample_id": sample_id,
                "planet": planet,
                "measure": measure,
                "jhora_value_virupa": "10.0",
                "source": "locked witness",
            }
        )
        local[key] = 10.0
        pyjhora[key] = 10.0
    changed = sorted(local)[0]
    local[changed] = 10.51

    rows = compare_profiles(
        witness,
        local,
        pyjhora,
        "pinned PyJHora",
    )
    summary = summarize(rows)

    assert len(rows) == 5 * 7 * 10
    assert sum(row["local_pass_fail"] == "fail" for row in rows) == 1
    assert set(summary) == set(MEASURES)
    assert all(item["rows"] == 35 for item in summary.values())


def test_profile_comparison_rejects_incomplete_matrix() -> None:
    expected = expected_kaala_keys()
    witness = [
        {
            "sample_id": sample_id,
            "planet": planet,
            "measure": measure,
            "jhora_value_virupa": "10.0",
            "source": "locked witness",
        }
        for sample_id, planet, measure in expected
    ]
    local = {key: 10.0 for key in expected}
    pyjhora = dict(local)
    pyjhora.pop(next(iter(pyjhora)))

    with pytest.raises(RuntimeError, match="PyJHora profile matrix mismatch"):
        compare_profiles(witness, local, pyjhora, "pinned PyJHora")
