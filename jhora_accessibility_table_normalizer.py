from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Final


PLANETS: Final = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
)
TABLE_HEADERS: Final = {
    "shadbala-summary": (
        "Shadbala",
        "In rupas",
        "% Strength",
        "IshtaPhala",
        "KashtaPhala",
    ),
    "shadbala-breakup": (
        "Shadbala Rupas",
        "Sthana Bala",
        "Kala Bala",
        "DigBala",
        "Cheshta Bala",
        "DrigBala",
        "Naisargika Bala",
    ),
}
PLANET_ITEM = re.compile(
    r"^\s*\d+\s+list item \(selectable\) "
    r"(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn)\s*$",
    re.MULTILINE,
)
NUMERIC_TEXT = re.compile(
    r"^\s*\d+\s+text\s+(-?\d+(?:\.\d+)?)\s*$",
    re.MULTILINE,
)
NEXT_LIST = re.compile(r"^\s*\d+\s+list ID:", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize a visible JHora accessibility table into a compact "
            "seven-planet text witness."
        )
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--table", choices=tuple(TABLE_HEADERS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def _require_headers(text: str, headers: tuple[str, ...], path: Path) -> int:
    planet_header = text.find("header item Planet")
    if planet_header < 0:
        raise RuntimeError(f"{path}: missing JHora Planet header")
    cursor = planet_header
    for header in headers:
        marker = f"header item {header}"
        cursor = text.find(marker, cursor)
        if cursor < 0:
            raise RuntimeError(f"{path}: missing JHora header {header!r}")
        cursor += len(marker)
    return planet_header


def parse_accessibility_matrix(
    path: Path,
    table: str,
) -> dict[str, tuple[float, ...]]:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise RuntimeError(f"{path}: accessibility evidence is empty")
    headers = TABLE_HEADERS[table]
    table_start = _require_headers(text, headers, path)
    matches = list(PLANET_ITEM.finditer(text, table_start))
    first_by_planet: dict[str, re.Match[str]] = {}
    for match in matches:
        planet = match.group(1).upper()
        first_by_planet.setdefault(planet, match)
        if len(first_by_planet) == len(PLANETS):
            break
    if tuple(first_by_planet) != PLANETS:
        raise RuntimeError(
            f"{path}: JHora planet order/membership mismatch: "
            f"{tuple(first_by_planet)}"
        )

    ordered = [first_by_planet[planet] for planet in PLANETS]
    rows: dict[str, tuple[float, ...]] = {}
    for index, match in enumerate(ordered):
        if index + 1 < len(ordered):
            segment_end = ordered[index + 1].start()
        else:
            next_list = NEXT_LIST.search(text, match.end())
            segment_end = next_list.start() if next_list else len(text)
        segment = text[match.end() : segment_end]
        values = tuple(float(item.group(1)) for item in NUMERIC_TEXT.finditer(segment))
        if len(values) != len(headers):
            raise RuntimeError(
                f"{path}: {match.group(1)} expected {len(headers)} values "
                f"for {table}, got {len(values)}"
            )
        rows[match.group(1).upper()] = values
    return rows


def render_normalized_table(
    rows: dict[str, tuple[float, ...]],
    table: str,
) -> str:
    headers = TABLE_HEADERS[table]
    lines = ["Planet " + " ".join(headers), ""]
    for planet in PLANETS:
        values = " ".join(f"{value:.2f}" for value in rows[planet])
        lines.append(f"{planet.title()} {values}")
    return "\n".join(lines) + "\n"


def normalize_accessibility_table(
    source: Path,
    table: str,
    output: Path,
) -> None:
    rows = parse_accessibility_matrix(source, table)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_normalized_table(rows, table), encoding="utf-8")


def main() -> int:
    args = parse_args()
    normalize_accessibility_table(args.source, args.table, args.output)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
