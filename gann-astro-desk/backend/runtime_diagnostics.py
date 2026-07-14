from __future__ import annotations

import json
import math
import threading
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNTIME_DIAGNOSTICS_CONTRACT = "GANN_RUNTIME_DIAGNOSTICS_V1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _percentile(samples: list[float], percentile: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    index = max(0, min(len(ordered) - 1, math.ceil(percentile * len(ordered)) - 1))
    return round(ordered[index], 2)


class _MetricSeries:
    def __init__(self, maximum_samples: int) -> None:
        self.samples: deque[float] = deque(maxlen=maximum_samples)
        self.count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_ms = 0.0
        self.last_at_utc = ""

    def record(self, duration_ms: float, ok: bool) -> None:
        value = round(max(0.0, float(duration_ms)), 2)
        self.samples.append(value)
        self.count += 1
        self.success_count += int(ok)
        self.failure_count += int(not ok)
        self.last_ms = value
        self.last_at_utc = _utc_now()

    def snapshot(self, name: str) -> dict[str, Any]:
        samples = list(self.samples)
        return {
            "name": name,
            "count": self.count,
            "successCount": self.success_count,
            "failureCount": self.failure_count,
            "sampleCount": len(samples),
            "lastMs": self.last_ms,
            "averageMs": round(sum(samples) / len(samples), 2) if samples else 0.0,
            "p50Ms": _percentile(samples, 0.50),
            "p95Ms": _percentile(samples, 0.95),
            "maxMs": round(max(samples), 2) if samples else 0.0,
            "lastAtUtc": self.last_at_utc,
        }


class RuntimeDiagnostics:
    """Bounded operational telemetry that cannot alter research or execution policy."""

    def __init__(
        self,
        log_path: Path | None = None,
        *,
        maximum_samples: int = 200,
        maximum_events: int = 50,
        slow_threshold_ms: float = 2_000.0,
        maximum_log_bytes: int = 5 * 1024 * 1024,
    ) -> None:
        self.session_id = uuid.uuid4().hex
        self.started_at_utc = _utc_now()
        self._started_monotonic = time.perf_counter()
        self._maximum_samples = max(10, min(int(maximum_samples), 2_000))
        self._slow_threshold_ms = max(100.0, float(slow_threshold_ms))
        self._maximum_log_bytes = max(64 * 1024, int(maximum_log_bytes))
        self._log_path = Path(log_path).resolve() if log_path else None
        self._lock = threading.RLock()
        self._metrics: dict[str, _MetricSeries] = {}
        self._recent_events: deque[dict[str, Any]] = deque(maxlen=max(10, maximum_events))
        self._startup_phases: dict[str, float] = {}
        self._startup_metadata: dict[str, Any] = {}
        self.record_lifecycle("sidecar_session_started")

    @staticmethod
    def _normalized_name(name: str) -> str:
        normalized = " ".join(str(name or "").strip().split())[:160]
        if not normalized:
            raise ValueError("diagnostic metric name is required")
        return normalized

    def _rotate_log_if_needed(self) -> None:
        if self._log_path is None or not self._log_path.exists():
            return
        if self._log_path.stat().st_size < self._maximum_log_bytes:
            return
        archived = self._log_path.with_suffix(self._log_path.suffix + ".1")
        if archived.exists():
            archived.unlink()
        self._log_path.replace(archived)

    def _append_event(self, event: dict[str, Any]) -> None:
        self._recent_events.append(event)
        if self._log_path is None:
            return
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_log_if_needed()
        with self._log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True, default=str) + "\n")

    def record_lifecycle(self, event_name: str, **details: Any) -> None:
        event = {
            "atUtc": _utc_now(),
            "sessionId": self.session_id,
            "kind": "lifecycle",
            "name": self._normalized_name(event_name),
            "details": details,
            "executionAllowed": False,
        }
        with self._lock:
            self._append_event(event)

    def set_startup_timings(
        self,
        phases: dict[str, float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        normalized = {
            self._normalized_name(name): round(max(0.0, float(value)), 2)
            for name, value in phases.items()
        }
        with self._lock:
            self._startup_phases = dict(sorted(normalized.items()))
            self._startup_metadata = dict(metadata or {})
            self._append_event(
                {
                    "atUtc": _utc_now(),
                    "sessionId": self.session_id,
                    "kind": "startup",
                    "name": "sidecar_ready",
                    "phasesMs": self._startup_phases,
                    "metadata": self._startup_metadata,
                    "executionAllowed": False,
                }
            )

    def record(
        self,
        name: str,
        duration_ms: float,
        *,
        ok: bool = True,
        details: dict[str, Any] | None = None,
    ) -> None:
        normalized = self._normalized_name(name)
        duration = round(max(0.0, float(duration_ms)), 2)
        with self._lock:
            metric = self._metrics.setdefault(normalized, _MetricSeries(self._maximum_samples))
            metric.record(duration, ok)
            if not ok or duration >= self._slow_threshold_ms:
                self._append_event(
                    {
                        "atUtc": _utc_now(),
                        "sessionId": self.session_id,
                        "kind": "failure" if not ok else "slow_operation",
                        "name": normalized,
                        "durationMs": duration,
                        "details": details or {},
                        "executionAllowed": False,
                    }
                )

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            operations = [
                metric.snapshot(name)
                for name, metric in sorted(self._metrics.items())
            ]
            startup_total = max(self._startup_phases.values(), default=0.0)
            return {
                "contract": RUNTIME_DIAGNOSTICS_CONTRACT,
                "sessionId": self.session_id,
                "startedAtUtc": self.started_at_utc,
                "uptimeSeconds": round(time.perf_counter() - self._started_monotonic, 1),
                "startup": {
                    "totalMs": startup_total,
                    "phasesMs": dict(self._startup_phases),
                    "metadata": dict(self._startup_metadata),
                },
                "operations": operations,
                "recentEvents": list(self._recent_events),
                "logPath": str(self._log_path) if self._log_path else "",
                "guardrails": {
                    "observabilityOnly": True,
                    "changesInferencePolicy": False,
                    "consumedByLiveInference": False,
                    "consumedByShadowLedger": False,
                    "executionAllowed": False,
                },
            }
