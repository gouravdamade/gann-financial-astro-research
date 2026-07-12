from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from price_sources import (
    PROMOTED_PRICE_CONTRACT,
    SNAPSHOT_CONTRACT,
    file_sha256,
    load_promoted_price_source,
    promote_snapshot,
    validate_snapshot,
)


class PriceSourcePromotionTests(unittest.TestCase):
    def write_snapshot(self, root: Path, snapshot_id: str) -> tuple[Path, Path]:
        target = root / "USDJPY" / "H1"
        target.mkdir(parents=True)
        index = pd.date_range("2026-07-10T10:00:00Z", periods=3, freq="h")
        frame = pd.DataFrame(
            {
                "open": [150.0, 150.1, 150.2],
                "high": [150.2, 150.3, 150.4],
                "low": [149.8, 149.9, 150.0],
                "close": [150.1, 150.2, 150.3],
                "tick_volume": [100, 101, 102],
                "spread": [2, 2, 2],
                "real_volume": [0, 0, 0],
            },
            index=index,
        )
        frame.index.name = "time"
        parquet = target / f"{snapshot_id}.parquet"
        manifest = target / f"{snapshot_id}.manifest.json"
        frame.to_parquet(parquet)
        payload = {
            "snapshotId": snapshot_id,
            "contract": SNAPSHOT_CONTRACT,
            "symbol": "USDJPY",
            "timeframe": "H1",
            "capturedAtUtc": "2026-07-10T13:30:00+00:00",
            "requestedStartUtc": "2026-07-10T10:00:00+00:00",
            "requestedEndUtc": "2026-07-10T13:30:00+00:00",
            "asOfUtc": "2026-07-10T13:30:00+00:00",
            "barCount": 3,
            "firstBarOpenUtc": index.min().isoformat(),
            "lastBarOpenUtc": index.max().isoformat(),
            "lastBarCloseUtc": "2026-07-10T13:00:00+00:00",
            "incompleteBarsExcluded": 0,
            "noLookahead": True,
            "immutable": True,
            "parquetPath": str(parquet),
            "parquetSha256": file_sha256(parquet),
            "manifestPath": str(manifest),
        }
        manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return parquet, manifest

    def test_snapshot_promotes_idempotently_with_verified_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            snapshot_root = root / "snapshots"
            source_root = root / "price_sources"
            snapshot_id = "USDJPY_H1_20260710T133000Z_fixture"
            self.write_snapshot(snapshot_root, snapshot_id)

            promoted = promote_snapshot(snapshot_root, source_root, snapshot_id, "Fixture source")
            repeated = promote_snapshot(snapshot_root, source_root, snapshot_id, "Ignored relabel")
            loaded, frame = load_promoted_price_source(source_root, promoted["priceSourceId"])

            self.assertEqual(promoted["contract"], PROMOTED_PRICE_CONTRACT)
            self.assertEqual(repeated["priceSourceId"], promoted["priceSourceId"])
            self.assertEqual(loaded["sourceSnapshotId"], snapshot_id)
            self.assertEqual(len(frame), 3)
            self.assertTrue(loaded["verified"])
            self.assertTrue(loaded["noLookahead"])

    def test_tampered_snapshot_is_rejected_before_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            snapshot_root = Path(directory) / "snapshots"
            snapshot_id = "USDJPY_H1_20260710T133000Z_tampered"
            parquet, _ = self.write_snapshot(snapshot_root, snapshot_id)
            parquet.write_bytes(parquet.read_bytes() + b"tampered")

            with self.assertRaisesRegex(ValueError, "SHA-256"):
                validate_snapshot(snapshot_root, snapshot_id)


if __name__ == "__main__":
    unittest.main()
