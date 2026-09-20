#!/usr/bin/env python3
"""Run the Candidate C EMP2-R1 market-only raw-stream reproduction gate."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path
import sys
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from research_labs.candidate_c_empirical_low_memory.market_stream import (
    validate_emp1_raw_market_stream,
    validate_streamed_admission_record,
)


EXPECTED_SNAPSHOT_HASH = "0F04578F8BB9FE08558889B3BBAC50F19DCE6702093856842B8A12ED32ACCEEC"


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong), ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t), ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t), ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def current_rss_bytes() -> int:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = ctypes.c_void_p
    get_memory_info = psapi.GetProcessMemoryInfo
    get_memory_info.argtypes = [ctypes.c_void_p, ctypes.POINTER(_ProcessMemoryCounters), ctypes.c_ulong]
    get_memory_info.restype = ctypes.c_bool
    if not get_memory_info(get_current_process(), ctypes.byref(counters), counters.cb):
        raise OSError(ctypes.get_last_error(), "GetProcessMemoryInfo failed")
    return int(counters.WorkingSetSize)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--private-raw-dir", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    inventory = json.loads((root / "status/research/mo_r4a_candidate_c_emp1_raw_market_artifact_inventory_v1.json").read_text(encoding="utf-8"))
    admission = json.loads((root / "status/research/mo_r4a_candidate_c_emp1_market_admission_record_v1.json").read_text(encoding="utf-8"))
    peak_rss = 0

    def observe_rss() -> int:
        nonlocal peak_rss
        peak_rss = max(peak_rss, current_rss_bytes())
        return peak_rss

    snapshot = validate_emp1_raw_market_stream(root, args.private_raw_dir, inventory, admission, expected_snapshot_hash=EXPECTED_SNAPSHOT_HASH, observe_rss=observe_rss)
    validated_admission = validate_streamed_admission_record(
        snapshot,
        admission,
        expected_snapshot_schema_hash="7D1C53F1E1B175A8BF7DD411994E60AA798ADDB21224A88AA503B1204DCBC269",
        expected_market_data_admission_contract_hash="BF8BD9B23633A07074BC4C40B1D11B480897FDF0D9C943C92B3DFDAAA80F59EC",
    )
    report: dict[str, Any] = {
        "schemaVersion": "MO_R4A_CANDIDATE_C_EMP2_R1_PRIVATE_MARKET_STREAM_VALIDATION_V1",
        "marketOnly": True,
        "providerCallCount": 0,
        "candidateCEventTimestampsAccessed": False,
        "realP0Computed": False,
        "realPHComputed": False,
        "realReturnsComputed": False,
        "realStatisticsComputed": False,
        "publicEMP2ExecutionPerformed": False,
        "rawArtifactCount": len(snapshot.raw_artifact_hashes),
        "rawQuoteCount": snapshot.raw_quote_count,
        "admittedQuoteCount": snapshot.admitted_quote_count,
        "marketSnapshotHash": snapshot.market_snapshot_hash,
        "marketAdmissionRecordHash": validated_admission.admission_record_hash,
        "exactDuplicateCount": snapshot.exact_duplicate_count,
        "peakRssBytes": peak_rss,
        "peakRssBelowFourGiB": peak_rss < 4 * 1024 ** 3,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
