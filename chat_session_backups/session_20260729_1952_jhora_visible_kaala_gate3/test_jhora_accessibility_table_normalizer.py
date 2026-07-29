from __future__ import annotations

from pathlib import Path

import pytest

from jhora_accessibility_table_normalizer import (
    PLANETS,
    TABLE_HEADERS,
    normalize_accessibility_table,
    parse_accessibility_matrix,
)


def accessibility_fixture(table: str) -> str:
    headers = TABLE_HEADERS[table]
    lines = ['Window: "Jagannatha Hora - fixture.jhd", App: jhora.exe.']
    lines.append("  10 header item Planet")
    for index, header in enumerate(headers, start=11):
        lines.append(f"  {index} header item {header}")
    row_id = 100
    for planet_index, planet in enumerate(PLANETS):
        lines.append(f"  {row_id} list item (selectable) {planet.title()}")
        lines.append(f"    {row_id + 1} text {planet.title()}")
        for value_index in range(len(headers)):
            value = planet_index * 10 + value_index + 0.25
            lines.append(f"    {row_id + value_index + 2} text {value:.2f}")
        row_id += 20
    lines.extend(
        [
            "  900 list ID: 59664",
            "    901 list item (selectable) Sun",
            "      902 text Sun",
            "      903 text 999.00",
        ]
    )
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize("table", tuple(TABLE_HEADERS))
def test_parser_extracts_only_the_first_seven_planet_table(
    tmp_path: Path,
    table: str,
) -> None:
    source = tmp_path / "capture.txt"
    source.write_text(accessibility_fixture(table), encoding="utf-8")

    rows = parse_accessibility_matrix(source, table)

    assert tuple(rows) == PLANETS
    assert len(rows["SATURN"]) == len(TABLE_HEADERS[table])
    assert 999.0 not in rows["SATURN"]


def test_normalizer_writes_compact_two_decimal_matrix(tmp_path: Path) -> None:
    source = tmp_path / "capture.txt"
    output = tmp_path / "normalized.txt"
    source.write_text(
        accessibility_fixture("shadbala-summary"),
        encoding="utf-8",
    )

    normalize_accessibility_table(
        source,
        "shadbala-summary",
        output,
    )

    lines = output.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("Planet Shadbala In rupas")
    assert lines[2] == "Sun 0.25 1.25 2.25 3.25 4.25"
    assert lines[-1] == "Saturn 60.25 61.25 62.25 63.25 64.25"


def test_parser_rejects_wrong_table_or_missing_planet(tmp_path: Path) -> None:
    source = tmp_path / "capture.txt"
    source.write_text(
        accessibility_fixture("shadbala-summary").replace(
            "list item (selectable) Saturn",
            "list item (selectable) Rahu",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="planet order/membership mismatch"):
        parse_accessibility_matrix(source, "shadbala-summary")
    with pytest.raises(RuntimeError, match="missing JHora header"):
        parse_accessibility_matrix(source, "shadbala-breakup")
