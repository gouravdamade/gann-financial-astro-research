from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "corpus_manifest.csv"
CORPUS_DIR = ROOT / "corpus_text"
INDEX_DIR = ROOT / "index"


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def allowed_for_ingestion(row: dict[str, str]) -> bool:
    policy = (row.get("ingestion_policy") or "").lower()
    return policy in {
        "public_domain_candidate",
        "local_user_reference",
        "local_structured_training_reference",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create local Jyotish corpus folders and a starter ingestion queue from the manifest."
    )
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--out", type=Path, default=ROOT / "ingestion_queue.json")
    args = parser.parse_args()

    rows = read_manifest(args.manifest)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    queue = []
    blocked = []
    for row in rows:
        item = {
            "source_id": row.get("source_id", ""),
            "title": row.get("title", ""),
            "source_url": row.get("source_url", ""),
            "ingestion_policy": row.get("ingestion_policy", ""),
            "priority": row.get("priority", ""),
            "text_path": str(CORPUS_DIR / f"{row.get('source_id', 'UNKNOWN')}.txt"),
        }
        if allowed_for_ingestion(row):
            queue.append(item)
        else:
            blocked.append(item)

    payload = {
        "policy_note": (
            "Queue includes only local/user-owned structured references and public-domain candidates. "
            "RAG-only modern translations must be manually approved before extraction."
        ),
        "queue": queue,
        "manual_review_required": blocked,
    }
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {args.out}")
    print(f"Queue items: {len(queue)} | manual review: {len(blocked)}")


if __name__ == "__main__":
    main()
