from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


TELEGRAM_DIR = Path(r"D:\Trading_Algo\New folder")
if str(TELEGRAM_DIR) not in sys.path:
    sys.path.insert(0, str(TELEGRAM_DIR))

from telegram_remote_control import TelegramClient, load_legacy_telegram_config, load_state, process_alive


PROJECT_DIR = Path(r"D:\PycharmProjects")
DEFAULT_CHECKPOINT_DIR = PROJECT_DIR / "touchlog_rebuild_checkpoints_transitsign_nodes_20260511"
DEFAULT_FINAL_OUTPUT = PROJECT_DIR / (
    "aspect_sr_touch_log_72h_orb_1y_nodes_outer_sr_eventfirst_"
    "usdjpy_basequote_all_durations_transitsign.csv"
)
DEFAULT_STATE_FILE = TELEGRAM_DIR / ".telegram_remote_control_state.json"
DEFAULT_LEGACY_BOT_FILE = Path(r"D:\Trading_Algo\WD GANN\telegram_bot.py")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send Telegram progress updates for touch-log rebuild checkpoints.")
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--final-output", type=Path, default=DEFAULT_FINAL_OUTPUT)
    parser.add_argument("--interval-seconds", type=int, default=900)
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_FILE)
    parser.add_argument("--legacy-bot-file", type=Path, default=DEFAULT_LEGACY_BOT_FILE)
    parser.add_argument("--log-file", type=Path, default=PROJECT_DIR / "touchlog_rebuild_telegram_monitor.log")
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def latest_run_started(rows: list[dict]) -> dict:
    starts = [r for r in rows if r.get("status") == "run_started"]
    return starts[-1] if starts else {}


def rows_after_latest_run_start(rows: list[dict]) -> list[dict]:
    latest_idx = -1
    for idx, row in enumerate(rows):
        if row.get("status") == "run_started":
            latest_idx = idx
    return rows[latest_idx + 1 :] if latest_idx >= 0 else rows


def process_snapshot() -> tuple[bool, list[int], list[str]]:
    # Keep this Windows-specific logic local and minimal to avoid a psutil dependency.
    import subprocess

    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        (
            "Get-CimInstance Win32_Process -Filter \"name = 'python.exe'\" | "
            "Where-Object { $_.CommandLine -like '*run_touchlog_rebuild_checkpoints.py*' -or "
            "$_.CommandLine -like '*build_aspect_sr_touch_log.py*' } | "
            "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
        ),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    raw = (proc.stdout or "").strip()
    if not raw:
        return False, [], []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return False, [], []
    if isinstance(data, dict):
        data = [data]
    pids: list[int] = []
    commands: list[str] = []
    runner_alive = False
    for item in data:
        try:
            pid = int(item.get("ProcessId"))
        except Exception:
            continue
        cmdline = str(item.get("CommandLine") or "")
        pids.append(pid)
        commands.append(cmdline)
        if "run_touchlog_rebuild_checkpoints.py" in cmdline:
            # Presence in the Win32_Process query is sufficient here. os.kill(0)
            # is not a reliable liveness probe on all Windows/Python setups.
            runner_alive = True
    return runner_alive, pids, commands


def build_status(checkpoint_dir: Path, final_output: Path) -> tuple[str, str]:
    manifest = checkpoint_dir / "manifest.jsonl"
    rows = load_jsonl(manifest)
    run = latest_run_started(rows)
    active_rows = rows_after_latest_run_start(rows)
    total_events = int(run.get("total_events") or 0)
    batch_size = int(run.get("batch_size") or 50)
    completed = [r for r in active_rows if r.get("status") == "completed"]
    skipped = [r for r in active_rows if r.get("status") == "skipped_existing"]
    failed = [r for r in active_rows if str(r.get("status", "")).startswith("failed")]
    merged = [r for r in active_rows if r.get("status") == "merged"]
    parts = sorted(checkpoint_dir.glob("part_*.csv"))
    latest_part = parts[-1].name if parts else "none"
    latest_completed = completed[-1] if completed else {}
    max_done = max([int(r.get("end_exclusive") or 0) for r in completed + skipped], default=0)
    percent = (100.0 * max_done / total_events) if total_events else 0.0
    runner_alive, pids, commands = process_snapshot()
    active_slice = ""
    for cmdline in commands:
        marker = "--event-slice-start "
        if marker in cmdline:
            after = cmdline.split(marker, 1)[1]
            start = after.split()[0]
            active_slice = f"{start}-{int(start) + batch_size - 1}"
            break
    final_exists = final_output.exists()
    final_size = final_output.stat().st_size if final_exists else 0

    if merged or final_exists:
        state = "complete"
    elif runner_alive:
        state = "running"
    elif failed:
        state = "failed"
    else:
        state = "stopped"

    text = (
        "Touch-log rebuild update\n"
        f"State: {state}\n"
        f"Completed event index: {max_done}/{total_events} ({percent:.1f}%)\n"
        f"Checkpoint parts: {len(parts)}\n"
        f"Latest part: {latest_part}\n"
        f"Active slice: {active_slice or 'n/a'}\n"
        f"Runner PIDs: {', '.join(map(str, pids)) if pids else 'none'}\n"
        f"Final output: {'yes' if final_exists else 'no'}"
    )
    if final_exists:
        text += f" ({final_size:,} bytes)"
    if latest_completed:
        text += f"\nLast completed elapsed: {latest_completed.get('elapsed_seconds')}s"
    if failed:
        text += f"\nFailure: {failed[-1]}"
    return state, text


def log_line(log_file: Path, text: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.open("a", encoding="utf-8").write(f"{datetime.now().isoformat(timespec='seconds')} | {text}\n")


def main() -> None:
    args = parse_args()
    token, legacy_chat = load_legacy_telegram_config(str(args.legacy_bot_file))
    state = load_state(args.state_file)
    chat_id = str(state.get("bound_chat_id") or legacy_chat or "").strip()
    if not token or not chat_id:
        raise SystemExit("Telegram token/chat id unavailable from legacy config/state.")

    tg = TelegramClient(token.strip())
    sent_terminal = False
    while True:
        status, text = build_status(args.checkpoint_dir, args.final_output)
        tg.send_message(chat_id, text)
        log_line(args.log_file, f"sent status={status}")
        if args.once:
            return
        if status in {"complete", "failed", "stopped"}:
            if sent_terminal:
                return
            sent_terminal = True
        time.sleep(max(60, int(args.interval_seconds)))


if __name__ == "__main__":
    main()
