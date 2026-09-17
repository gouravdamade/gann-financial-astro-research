"""Neutral isolated entrypoint for the frozen Evaluator A runtime."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--contract-input-root", required=True)
    parser.add_argument("--runtime-manifest", required=True)
    args = parser.parse_args()
    runtime_module = Path(__file__).resolve().parents[3] / "research_labs" / "candidate_c_reproduction" / "real_run" / "worker_runtime.py"
    spec = importlib.util.spec_from_file_location("run1_r2_worker_runtime", runtime_module)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load neutral RUN1-R2 worker runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    response = module.execute_worker(sys.stdin.buffer.read(), role="EVALUATOR_A", runtime_root=Path(args.runtime_root).resolve(), contract_input_root=Path(args.contract_input_root).resolve(), manifest_path=Path(args.runtime_manifest).resolve())
    sys.stdout.buffer.write(module._canonical(response) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
