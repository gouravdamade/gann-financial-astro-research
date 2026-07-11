from __future__ import annotations

import argparse
import hashlib
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent
DEFAULT_REGISTRY = ROOT / "classical_source_editions.yaml"


def digest(path: Path, algorithm: str) -> str:
    value = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest().upper()


def verify_configured_hash(path: Path, algorithm: str, expected: str | None, source_id: str) -> None:
    if expected and digest(path, algorithm) != expected.upper():
        raise ValueError(f"{source_id}: {algorithm} mismatch for {path}")


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.replace("\u00ad", "")
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", value)
    return re.sub(r"[ \t]+", " ", value).strip()


def page_text(obj: ET.Element) -> str:
    lines: list[str] = []
    for line in obj.findall(".//LINE"):
        words = [clean_text(str(word.text or "")) for word in line.findall(".//WORD")]
        value = " ".join(word for word in words if word)
        if value:
            lines.append(value)
    return "\n".join(lines)


def section_for(page: int, ranges: list[dict[str, Any]]) -> str:
    for item in ranges:
        if int(item["start"]) <= page <= int(item["end"]):
            return str(item["type"])
    return "unclassified"


def normalized_for_matching(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def topics_for(text: str, patterns: dict[str, list[str]]) -> list[str]:
    compact = normalized_for_matching(text)
    return [
        topic
        for topic, needles in patterns.items()
        if any(normalized_for_matching(str(needle)) in compact for needle in needles)
    ]


def render_source(source_id: str, config: dict[str, Any], minimum_chars: int = 20) -> dict[str, Any]:
    xml_path = Path(config["ocr_xml_path"])
    pdf_path = Path(config["pdf_path"]) if config.get("pdf_path") else None
    output_path = Path(config["output_path"])
    if pdf_path:
        verify_configured_hash(pdf_path, "sha256", config.get("pdf_sha256"), source_id)
    verify_configured_hash(xml_path, "md5", config.get("ocr_xml_md5"), source_id)
    objects = ET.parse(xml_path).getroot().findall(".//OBJECT")
    expected_pages = int(config["expected_pages"])
    if len(objects) != expected_pages:
        raise ValueError(f"{source_id}: expected {expected_pages} OCR pages, found {len(objects)}")

    blocks: list[str] = []
    skipped_pages: list[int] = []
    for page, obj in enumerate(objects, start=1):
        text = page_text(obj)
        if len(text) < minimum_chars:
            skipped_pages.append(page)
            continue
        topics = topics_for(text, config.get("topics", {}))
        markers = [
            f"[[SOURCE: {source_id}]]",
            f"[[TITLE: {config['title']}]]",
            f"[[AUTHOR: {config['author']}]]",
            f"[[TRANSLATOR: {config['translator']}]]",
            f"[[EDITION: {config['edition']}]]",
            f"[[AUTHORITY: {config['authority']}]]",
            f"[[PDF_PAGE: {page:04d}]]",
            f"[[CONTENT_LAYER: {section_for(page, config['section_ranges'])}]]",
            f"[[TOPICS: {','.join(topics) if topics else 'general'}]]",
            "[[OCR_SOURCE: internet_archive_djvu_xml]]",
        ]
        blocks.append("\n".join([*markers, text]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
    return {
        "source_id": source_id,
        "output_path": str(output_path),
        "pdf_pages": expected_pages,
        "retained_pages": len(blocks),
        "skipped_pages": skipped_pages,
        "bytes": output_path.stat().st_size,
    }


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(data["sources"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build page-cited local corpus text from public-domain DjVu OCR XML.")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--source-id", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    registry = load_registry(args.registry)
    selected = list(registry) if args.all else args.source_id
    if not selected:
        raise SystemExit("Select --all or at least one --source-id.")
    unknown = [source_id for source_id in selected if source_id not in registry]
    if unknown:
        raise SystemExit(f"Unknown source ids: {', '.join(unknown)}")

    for source_id in selected:
        print(render_source(source_id, registry[source_id]))


if __name__ == "__main__":
    main()
