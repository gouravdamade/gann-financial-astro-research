from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "source_registry.csv"
CORPUS_ROOT = ROOT / "corpus_text"
OUTPUT = ROOT / "corpus_chunks.jsonl"


def clean_text(value: str) -> str:
    value = value.replace("\x00", " ")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def chunk_text(source_id: str, title: str, text: str, max_chars: int = 2200) -> list[dict[str, str]]:
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", clean_text(text)) if item.strip()]
    chunks: list[dict[str, str]] = []
    current: list[str] = []
    size = 0

    def flush() -> None:
        nonlocal current, size
        if not current:
            return
        chunks.append(
            {
                "source_id": source_id,
                "title": title,
                "chunk_id": f"{source_id}-{len(chunks) + 1:04d}",
                "text": "\n\n".join(current),
            }
        )
        current = []
        size = 0

    for paragraph in paragraphs:
        if current and size + len(paragraph) + 2 > max_chars:
            flush()
        if len(paragraph) > max_chars:
            flush()
            for offset in range(0, len(paragraph), max_chars):
                chunks.append(
                    {
                        "source_id": source_id,
                        "title": title,
                        "chunk_id": f"{source_id}-{len(chunks) + 1:04d}",
                        "text": paragraph[offset : offset + max_chars],
                    }
                )
            continue
        current.append(paragraph)
        size += len(paragraph) + 2
    flush()
    return chunks


def build(manifest_path: Path = MANIFEST) -> list[dict[str, str]]:
    with manifest_path.open("r", encoding="utf-8", newline="") as handle:
        manifest = {row["source_id"]: row for row in csv.DictReader(handle)}
    chunks: list[dict[str, str]] = []
    for path in sorted(CORPUS_ROOT.glob("*.txt")):
        source_id = path.stem
        row = manifest.get(source_id)
        if row is None:
            raise ValueError(f"Corpus source is missing from registry: {source_id}")
        chunks.extend(
            chunk_text(
                source_id,
                str(row.get("title") or source_id),
                path.read_text(encoding="utf-8", errors="replace"),
            )
        )
    if not chunks:
        raise ValueError("No candlestick corpus text is available")
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the isolated candlestick RAG chunk file.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    chunks = build(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=True) + "\n")
    print(f"Wrote {len(chunks)} candlestick chunks to {args.output}")


if __name__ == "__main__":
    main()
