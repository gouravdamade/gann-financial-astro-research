from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime_diagnostics import RUNTIME_DIAGNOSTICS_CONTRACT, RuntimeDiagnostics


class RuntimeDiagnosticsTests(unittest.TestCase):
    def test_metrics_are_bounded_and_guarded(self) -> None:
        diagnostics = RuntimeDiagnostics(maximum_samples=10, slow_threshold_ms=10_000)
        for value in range(15):
            diagnostics.record("http:GET /api/chart", value, ok=value != 14)

        snapshot = diagnostics.snapshot()
        metric = snapshot["operations"][0]

        self.assertEqual(snapshot["contract"], RUNTIME_DIAGNOSTICS_CONTRACT)
        self.assertEqual(metric["count"], 15)
        self.assertEqual(metric["sampleCount"], 10)
        self.assertEqual(metric["failureCount"], 1)
        self.assertEqual(metric["p50Ms"], 9.0)
        self.assertEqual(metric["p95Ms"], 14.0)
        self.assertFalse(snapshot["guardrails"]["executionAllowed"])
        self.assertFalse(snapshot["guardrails"]["consumedByShadowLedger"])

    def test_startup_and_slow_events_are_written_as_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            log_path = Path(temporary) / "runtime_diagnostics.jsonl"
            diagnostics = RuntimeDiagnostics(log_path, slow_threshold_ms=100)
            diagnostics.set_startup_timings(
                {"environment_ready": 12.5, "http_ready": 88.0},
                {"ollamaStarted": False},
            )
            diagnostics.record("local_jyotish_generate", 150, details={"model": "test"})

            rows = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]

            self.assertEqual(rows[-2]["kind"], "startup")
            self.assertEqual(rows[-1]["kind"], "slow_operation")
            self.assertFalse(rows[-1]["executionAllowed"])
            self.assertEqual(diagnostics.snapshot()["startup"]["totalMs"], 88.0)


if __name__ == "__main__":
    unittest.main()
