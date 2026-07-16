from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SNAPSHOT_CONTRACT = "MT5_TIMESTAMPED_CLOSED_BARS_V1"
NORMALIZED_SNAPSHOT_CONTRACT = "MT5_TIMESTAMP_NORMALIZED_CLOSED_BARS_V2"
SUPPORTED_SNAPSHOT_CONTRACTS = {SNAPSHOT_CONTRACT, NORMALIZED_SNAPSHOT_CONTRACT}
PROMOTED_PRICE_CONTRACT = "PROMOTED_MT5_PRICE_SOURCE_V1"
REQUIRED_PRICE_COLUMNS = ("open", "high", "low", "close")
TIMEFRAME_SECONDS = {
    "M30": 30 * 60,
    "H1": 60 * 60,
    "H4": 4 * 60 * 60,
    "D1": 24 * 60 * 60,
    "W1": 7 * 24 * 60 * 60,
}
SAFE_ID = re.compile(r"^[A-Za-z0-9_.-]{1,160}$")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_id(value: str, label: str) -> str:
    normalized = str(value or "").strip()
    if not SAFE_ID.fullmatch(normalized):
        raise ValueError(f"invalid {label}")
    return normalized


def _inside(path: Path, root: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_relative_to(root.expanduser().resolve()):
        raise ValueError(f"{label} leaves its approved storage root")
    return resolved


def validate_price_frame(frame: pd.DataFrame, timeframe: str, as_of: pd.Timestamp) -> pd.DataFrame:
    normalized_timeframe = str(timeframe or "").upper()
    if normalized_timeframe not in TIMEFRAME_SECONDS:
        raise ValueError(f"unsupported snapshot timeframe: {timeframe}")
    missing = sorted(set(REQUIRED_PRICE_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"price snapshot is missing OHLC columns: {missing}")
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is None:
        raise ValueError("price snapshot index must be timezone-aware")
    checked = frame.copy().sort_index()
    checked.index = checked.index.tz_convert("UTC")
    if checked.empty:
        raise ValueError("price snapshot is empty")
    if checked.index.has_duplicates or not checked.index.is_monotonic_increasing:
        raise ValueError("price snapshot timestamps must be unique and increasing")

    values = checked.loc[:, REQUIRED_PRICE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError("price snapshot contains missing or non-finite OHLC values")
    if (values["high"] < values[["open", "close", "low"]].max(axis=1)).any():
        raise ValueError("price snapshot contains an invalid high")
    if (values["low"] > values[["open", "close", "high"]].min(axis=1)).any():
        raise ValueError("price snapshot contains an invalid low")

    cutoff = pd.Timestamp(as_of)
    if cutoff.tzinfo is None:
        raise ValueError("snapshot as-of time must include a UTC offset")
    cutoff = cutoff.tz_convert("UTC")
    last_close = checked.index.max() + pd.Timedelta(seconds=TIMEFRAME_SECONDS[normalized_timeframe])
    if last_close > cutoff:
        raise ValueError("price snapshot includes a bar that was not closed by its as-of time")
    return checked


def validate_snapshot(snapshot_root: Path, snapshot_id: str) -> tuple[dict[str, Any], pd.DataFrame]:
    normalized_id = _safe_id(snapshot_id, "snapshot id")
    root = snapshot_root.expanduser().resolve()
    candidates = list(root.glob(f"*/*/{normalized_id}.manifest.json"))
    if len(candidates) != 1:
        raise KeyError(f"Unknown or ambiguous MT5 snapshot: {normalized_id}")
    manifest_path = _inside(candidates[0], root, "snapshot manifest")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("snapshot manifest is unreadable") from exc
    if not isinstance(manifest, dict):
        raise ValueError("snapshot manifest must be an object")
    if str(manifest.get("snapshotId") or "") != normalized_id:
        raise ValueError("snapshot manifest id does not match its filename")
    snapshot_contract = str(manifest.get("contract") or "")
    if snapshot_contract not in SUPPORTED_SNAPSHOT_CONTRACTS:
        raise ValueError("unsupported MT5 snapshot contract")
    if manifest.get("noLookahead") is not True or manifest.get("immutable") is not True:
        raise ValueError("snapshot is not marked immutable and no-lookahead")

    price_path = _inside(Path(str(manifest.get("parquetPath") or "")), root, "snapshot parquet")
    if not price_path.is_file():
        raise ValueError("snapshot parquet is missing")
    expected_sha = str(manifest.get("parquetSha256") or "").upper()
    actual_sha = file_sha256(price_path)
    if not expected_sha or actual_sha != expected_sha:
        raise ValueError("snapshot parquet SHA-256 does not match its manifest")

    as_of = pd.Timestamp(manifest.get("asOfUtc"))
    frame = validate_price_frame(pd.read_parquet(price_path), str(manifest.get("timeframe")), as_of)
    if snapshot_contract == NORMALIZED_SNAPSHOT_CONTRACT:
        normalization = manifest.get("timeNormalization") or {}
        if (
            normalization.get("contract") != "GANN_MT5_SERVER_TIME_NORMALIZATION_V1"
            or normalization.get("valid") is not True
        ):
            raise ValueError("normalized snapshot is missing valid MT5 clock evidence")
        if "raw_time" not in frame.columns:
            raise ValueError("normalized snapshot does not preserve raw MT5 timestamps")
        raw_time = pd.to_numeric(frame["raw_time"], errors="coerce")
        if raw_time.isna().any():
            raise ValueError("normalized snapshot contains invalid raw MT5 timestamps")
        offset = int(normalization.get("serverOffsetSeconds") or 0)
        normalized_epoch = frame.index.as_unit("ns").asi8 // 1_000_000_000
        if not np.array_equal(raw_time.to_numpy(dtype="int64") - offset, normalized_epoch):
            raise ValueError("normalized snapshot raw/UTC timestamps are inconsistent")
        if int(manifest.get("rawFirstBarOpenServerEpochSeconds") or 0) != int(raw_time.iloc[0]):
            raise ValueError("normalized snapshot raw first bar does not match its manifest")
        if int(manifest.get("rawLastBarOpenServerEpochSeconds") or 0) != int(raw_time.iloc[-1]):
            raise ValueError("normalized snapshot raw last bar does not match its manifest")
    if int(manifest.get("barCount") or -1) != len(frame):
        raise ValueError("snapshot bar count does not match its manifest")
    if pd.Timestamp(manifest.get("firstBarOpenUtc")) != frame.index.min():
        raise ValueError("snapshot first bar does not match its manifest")
    if pd.Timestamp(manifest.get("lastBarOpenUtc")) != frame.index.max():
        raise ValueError("snapshot last bar does not match its manifest")
    expected_close = frame.index.max() + pd.Timedelta(
        seconds=TIMEFRAME_SECONDS[str(manifest.get("timeframe")).upper()]
    )
    if pd.Timestamp(manifest.get("lastBarCloseUtc")) != expected_close:
        raise ValueError("snapshot last bar close does not match its manifest")
    manifest = {
        **manifest,
        "manifestPath": str(manifest_path),
        "parquetPath": str(price_path),
        "parquetSha256": actual_sha,
    }
    return manifest, frame


def promote_snapshot(
    snapshot_root: Path,
    price_sources_root: Path,
    snapshot_id: str,
    label: str | None = None,
) -> dict[str, Any]:
    snapshot, frame = validate_snapshot(snapshot_root, snapshot_id)
    source_id = _safe_id(f"mt5_{snapshot['snapshotId']}", "price source id")
    root = price_sources_root.expanduser().resolve()
    target_dir = _inside(root / source_id, root, "price source directory")
    target_dir.mkdir(parents=True, exist_ok=True)
    price_path = target_dir / "prices.parquet"
    manifest_path = target_dir / "price_source.manifest.json"

    if manifest_path.is_file():
        existing, _ = load_promoted_price_source(root, source_id)
        if existing.get("sourceSnapshotId") != snapshot["snapshotId"]:
            raise ValueError("existing price source has different snapshot lineage")
        return existing

    temporary_price = target_dir / f".prices.{uuid.uuid4().hex}.partial.parquet"
    shutil.copy2(snapshot["parquetPath"], temporary_price)
    copied_sha = file_sha256(temporary_price)
    if copied_sha != snapshot["parquetSha256"]:
        temporary_price.unlink(missing_ok=True)
        raise ValueError("promoted price copy failed SHA-256 verification")
    temporary_price.replace(price_path)

    promoted = {
        "priceSourceId": source_id,
        "label": str(label or f"{snapshot['symbol']} {snapshot['timeframe']} {snapshot['capturedAtUtc']}")[:120],
        "symbol": str(snapshot["symbol"]).upper(),
        "sourceTimeframe": str(snapshot["timeframe"]).upper(),
        "contract": PROMOTED_PRICE_CONTRACT,
        "sourceSnapshotContract": snapshot["contract"],
        "sourceSnapshotId": snapshot["snapshotId"],
        "sourceSnapshotManifestPath": snapshot["manifestPath"],
        "sourceSnapshotManifestSha256": file_sha256(Path(snapshot["manifestPath"])),
        "pricePath": str(price_path),
        "manifestPath": str(manifest_path),
        "priceSha256": copied_sha,
        "barCount": int(len(frame)),
        "dateStart": frame.index.min().isoformat(),
        "dateEnd": frame.index.max().isoformat(),
        "asOfUtc": str(snapshot["asOfUtc"]),
        "capturedAtUtc": str(snapshot["capturedAtUtc"]),
        "noLookahead": True,
        "immutable": True,
        "verified": True,
        "createdAtUtc": utc_now(),
        "builtIn": False,
    }
    temporary_manifest = target_dir / f".price_source.{uuid.uuid4().hex}.partial.json"
    temporary_manifest.write_text(
        json.dumps(promoted, indent=2, sort_keys=True, ensure_ascii=True), encoding="utf-8"
    )
    temporary_manifest.replace(manifest_path)
    return promoted


def load_promoted_price_source(
    price_sources_root: Path,
    price_source_id: str,
) -> tuple[dict[str, Any], pd.DataFrame]:
    normalized_id = _safe_id(price_source_id, "price source id")
    root = price_sources_root.expanduser().resolve()
    source_dir = _inside(root / normalized_id, root, "price source directory")
    manifest_path = _inside(source_dir / "price_source.manifest.json", root, "price source manifest")
    if not manifest_path.is_file():
        raise KeyError(f"Unknown promoted price source: {normalized_id}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("price source manifest is unreadable") from exc
    if not isinstance(manifest, dict) or manifest.get("priceSourceId") != normalized_id:
        raise ValueError("price source manifest id is invalid")
    if manifest.get("contract") != PROMOTED_PRICE_CONTRACT:
        raise ValueError("unsupported promoted price source contract")
    if manifest.get("noLookahead") is not True or manifest.get("immutable") is not True:
        raise ValueError("promoted price source lost its immutable/no-lookahead contract")
    price_path = _inside(Path(str(manifest.get("pricePath") or "")), root, "promoted price parquet")
    expected_sha = str(manifest.get("priceSha256") or "").upper()
    if not price_path.is_file() or file_sha256(price_path) != expected_sha:
        raise ValueError("promoted price source SHA-256 verification failed")
    frame = validate_price_frame(
        pd.read_parquet(price_path),
        str(manifest.get("sourceTimeframe")),
        pd.Timestamp(manifest.get("asOfUtc")),
    )
    if int(manifest.get("barCount") or -1) != len(frame):
        raise ValueError("promoted price source bar count is invalid")
    if pd.Timestamp(manifest.get("dateStart")) != frame.index.min():
        raise ValueError("promoted price source start time is invalid")
    if pd.Timestamp(manifest.get("dateEnd")) != frame.index.max():
        raise ValueError("promoted price source end time is invalid")
    return {**manifest, "pricePath": str(price_path), "manifestPath": str(manifest_path)}, frame
