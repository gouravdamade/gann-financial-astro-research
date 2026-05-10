from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(r"C:\Users\ADMIN\PycharmProjects")
BUILDER = PROJECT_DIR / "build_aspect_sr_touch_log.py"
DEFAULT_EVENTS = PROJECT_DIR / "astro_training_data_ipo_tokyo_18890211_orb_1y_nodes.parquet"
DEFAULT_PRICE = PROJECT_DIR / "usd_jpy_h1_mt5_metaquotes_demo_full.parquet"
DEFAULT_CHECKPOINT_DIR = PROJECT_DIR / "touchlog_rebuild_checkpoints_transitsign_nodes_20260511"
DEFAULT_FINAL_OUTPUT = PROJECT_DIR / (
    "aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_"
    "usdjpy_basequote_all_durations_transitsign.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run build_aspect_sr_touch_log.py in resumable event-slice checkpoints."
    )
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--final-output", type=Path, default=DEFAULT_FINAL_OUTPUT)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--price", type=Path, default=DEFAULT_PRICE)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, default=0, help="Exclusive event index. Use 0 for all events.")
    parser.add_argument("--stop-after-batches", type=int, default=0, help="Testing guard. Use 0 for no limit.")
    parser.add_argument("--force", action="store_true", help="Rebuild existing checkpoint parts.")
    parser.add_argument("--no-merge", action="store_true", help="Do not merge parts after all batches complete.")
    parser.add_argument(
        "--allow-slice-merge",
        action="store_true",
        help=(
            "Allow merging event-sliced parts. This is diagnostic only: per-slice "
            "SR/longitude/regime context can differ from a single-pass build."
        ),
    )
    return parser.parse_args()


def run_command(cmd: list[str], log_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_DIR),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if log_path is not None:
        log_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
    return proc


def get_total_events(events_path: Path, price_path: Path) -> int:
    cmd = [
        sys.executable,
        str(BUILDER),
        "--events",
        str(events_path),
        "--price",
        str(price_path),
        "--include-natal",
        "--aspect-mode",
        "orb",
        "--max-event-days",
        "0",
        "--dry-run-count",
    ]
    proc = run_command(cmd)
    if proc.returncode != 0:
        raise RuntimeError(f"Count command failed:\n{proc.stdout}")
    match = re.search(r"Filtered events available:\s*(\d+)", proc.stdout)
    if not match:
        raise RuntimeError(f"Could not parse event count from:\n{proc.stdout}")
    return int(match.group(1))


def part_paths(checkpoint_dir: Path, start: int, end_exclusive: int) -> tuple[Path, Path]:
    name = f"part_{start:05d}_{end_exclusive - 1:05d}"
    return checkpoint_dir / f"{name}.csv", checkpoint_dir / f"{name}.log"


def part_has_required_json_keys(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    required = {"transit_lon", "transit_sign", "natal_lon"}
    checked_hits = 0
    row_count = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return False
        for row in reader:
            row_count += 1
            for col in ("tn_hits_json", "base_tn_hits_json"):
                raw = row.get(col) or ""
                if not raw.strip():
                    continue
                try:
                    hits = json.loads(raw)
                except json.JSONDecodeError:
                    return False
                for hit in hits:
                    if not isinstance(hit, dict):
                        continue
                    checked_hits += 1
                    if not required.issubset(hit):
                        return False
                    if checked_hits >= 20:
                        return True
    # Some event slices legitimately generate no touch rows after final gating.
    # Treat a header-only checkpoint as valid so a no-hit batch does not halt a
    # long rebuild. Non-empty batches with no TN hits are also valid; there are
    # simply no hit JSON records to validate in that slice.
    return row_count == 0 or checked_hits >= 0


def append_manifest(manifest_path: Path, record: dict[str, object]) -> None:
    with manifest_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def run_part(
    checkpoint_dir: Path,
    events_path: Path,
    price_path: Path,
    start: int,
    end_exclusive: int,
    force: bool,
) -> dict[str, object]:
    part_csv, part_log = part_paths(checkpoint_dir, start, end_exclusive)
    if not force and part_has_required_json_keys(part_csv):
        return {
            "status": "skipped_existing",
            "start": start,
            "end_exclusive": end_exclusive,
            "part": str(part_csv),
            "bytes": part_csv.stat().st_size,
        }

    tmp_csv = part_csv.with_suffix(".csv.tmp")
    if tmp_csv.exists():
        tmp_csv.unlink()

    cmd = [
        sys.executable,
        str(BUILDER),
        "--events",
        str(events_path),
        "--price",
        str(price_path),
        "--include-natal",
        "--aspect-mode",
        "orb",
        "--max-event-days",
        "0",
        "--event-slice-start",
        str(start),
        "--event-slice-size",
        str(end_exclusive - start),
        "--output",
        str(tmp_csv),
    ]
    started = time.time()
    proc = run_command(cmd, part_log)
    elapsed = round(time.time() - started, 2)
    if proc.returncode != 0:
        return {
            "status": "failed",
            "start": start,
            "end_exclusive": end_exclusive,
            "part": str(part_csv),
            "log": str(part_log),
            "elapsed_seconds": elapsed,
            "returncode": proc.returncode,
        }

    if not part_has_required_json_keys(tmp_csv):
        return {
            "status": "failed_validation",
            "start": start,
            "end_exclusive": end_exclusive,
            "part": str(part_csv),
            "log": str(part_log),
            "elapsed_seconds": elapsed,
        }

    if part_csv.exists():
        part_csv.unlink()
    tmp_csv.rename(part_csv)
    return {
        "status": "completed",
        "start": start,
        "end_exclusive": end_exclusive,
        "part": str(part_csv),
        "log": str(part_log),
        "elapsed_seconds": elapsed,
        "bytes": part_csv.stat().st_size,
    }


def merge_parts(checkpoint_dir: Path, final_output: Path) -> dict[str, object]:
    parts = sorted(checkpoint_dir.glob("part_*.csv"))
    if not parts:
        raise RuntimeError(f"No checkpoint parts found in {checkpoint_dir}")

    frames = []
    for path in parts:
        frames.append(pd.read_csv(path))
    out = pd.concat(frames, ignore_index=True, sort=False)
    if "touch_id" in out.columns:
        out = out.drop_duplicates(subset=["touch_id"], keep="first")
    if "event_id" in out.columns:
        work = out.copy()
        work["touch_time_local"] = pd.to_datetime(work.get("touch_time_local"), errors="coerce")
        work["touch_distance_abs"] = pd.to_numeric(work.get("touch_distance_abs"), errors="coerce").fillna(float("inf"))
        work["edge_score"] = pd.to_numeric(work.get("ret_after_72h_pct"), errors="coerce").abs().fillna(float("-inf"))
        work["_touch_priority"] = work.get("touch_kind", "").astype(str).str.lower().ne("confluence").astype(int)
        has_event = work["event_id"].notna() & work["event_id"].astype(str).str.strip().ne("")
        with_event = (
            work[has_event]
            .sort_values(
                ["event_id", "_touch_priority", "touch_time_local", "touch_distance_abs", "edge_score"],
                ascending=[True, True, True, True, False],
            )
            .drop_duplicates(subset=["event_id"], keep="first")
        )
        without_event = work[~has_event].copy()
        out = pd.concat([with_event, without_event], ignore_index=True, sort=False)
        out = out.drop(columns=["_touch_priority", "edge_score"], errors="ignore")
    if {"touch_time_local", "pair_key", "aspect", "touch_kind"}.issubset(out.columns):
        out = out.sort_values(["touch_time_local", "pair_key", "aspect", "touch_kind"]).reset_index(drop=True)
    final_output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(final_output, index=False)
    return {"final_output": str(final_output), "rows": int(len(out)), "parts": len(parts), "bytes": final_output.stat().st_size}


def main() -> None:
    args = parse_args()
    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be positive")

    checkpoint_dir = args.checkpoint_dir
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = checkpoint_dir / "manifest.jsonl"
    total = get_total_events(args.events, args.price)
    stop = int(args.stop) if int(args.stop) > 0 else total
    stop = min(stop, total)
    start = min(max(0, int(args.start)), stop)

    header = {
        "status": "run_started",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "total_events": total,
        "start": start,
        "stop": stop,
        "batch_size": int(args.batch_size),
        "checkpoint_dir": str(checkpoint_dir),
        "final_output": str(args.final_output),
        "events": str(args.events),
        "price": str(args.price),
    }
    append_manifest(manifest_path, header)
    print(json.dumps(header, indent=2))

    completed_this_run = 0
    for batch_start in range(start, stop, int(args.batch_size)):
        batch_end = min(batch_start + int(args.batch_size), stop)
        record = run_part(checkpoint_dir, args.events, args.price, batch_start, batch_end, bool(args.force))
        record["timestamp"] = datetime.now().isoformat(timespec="seconds")
        append_manifest(manifest_path, record)
        print(json.dumps(record, indent=2))
        if record["status"] in {"failed", "failed_validation"}:
            raise SystemExit(1)
        if record["status"] == "completed":
            completed_this_run += 1
        if args.stop_after_batches and completed_this_run >= int(args.stop_after_batches):
            print("Stopping after requested completed batch limit.")
            return

    if not args.no_merge:
        if not args.allow_slice_merge:
            raise SystemExit(
                "Refusing to merge event-sliced checkpoints by default. "
                "The slice-local SR/longitude/regime context is not guaranteed "
                "to match a single-pass build. Use --no-merge for checkpoints, "
                "run the builder single-pass for the final CSV, or pass "
                "--allow-slice-merge only for diagnostics."
            )
        merge_record = merge_parts(checkpoint_dir, args.final_output)
        merge_record["status"] = "merged"
        merge_record["timestamp"] = datetime.now().isoformat(timespec="seconds")
        append_manifest(manifest_path, merge_record)
        print(json.dumps(merge_record, indent=2))


if __name__ == "__main__":
    main()
