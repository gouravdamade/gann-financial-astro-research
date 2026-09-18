"""Canonical stdin/stdout IPC worker for the R3R3 B batch."""
from __future__ import annotations
import argparse, importlib.util, sys
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--runtime-root", required=True); parser.add_argument("--contract-input-root", required=True); parser.add_argument("--runtime-manifest", required=True); args = parser.parse_args()
    path = Path(__file__).resolve().parents[3] / "research_labs/candidate_c_reproduction/real_run/worker_runtime_r3r3.py"
    spec = importlib.util.spec_from_file_location("run1_r3r3_worker", path); assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    response = module.execute_worker(sys.stdin.buffer.read(), role="EVALUATOR_B", runtime_root=Path(args.runtime_root).resolve(), contract_input_root=Path(args.contract_input_root).resolve(), manifest_path=Path(args.runtime_manifest).resolve())
    sys.stdout.buffer.write(module._canonical(response) + b"\n"); return 0
if __name__ == "__main__": raise SystemExit(main())
