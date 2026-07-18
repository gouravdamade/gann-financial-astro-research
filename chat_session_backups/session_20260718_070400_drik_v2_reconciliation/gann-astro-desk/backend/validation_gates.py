from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MATRIX_CONTRACT = "GANN_RESEARCH_VALIDATION_GATE_MATRIX_V1"
EXTERNAL_GATE_CONTRACT = "GANN_ASTRO_EXTERNAL_CERTIFICATION_GATE_V1"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _latest_external_gate(project_root: Path) -> Path | None:
    configured = str(os.environ.get("GANN_ASTRO_EXTERNAL_GATE") or "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    candidates = sorted(project_root.glob("astro_external_validation_gate_*.json"))
    return candidates[-1] if candidates else None


def load_external_gate(project_root: Path) -> dict[str, Any]:
    path = _latest_external_gate(project_root)
    if path is None:
        return {
            "status": "blocked_missing_external_gate",
            "certified": False,
            "executionAllowed": False,
            "sourcePath": None,
            "sourceSha256": None,
            "reason": "No versioned external Shadbala/Drik gate artifact is available.",
        }
    if not path.exists() or not path.is_file():
        return {
            "status": "blocked_missing_external_gate",
            "certified": False,
            "executionAllowed": False,
            "sourcePath": str(path),
            "sourceSha256": None,
            "reason": "Configured external certification gate does not exist.",
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "blocked_invalid_external_gate",
            "certified": False,
            "executionAllowed": False,
            "sourcePath": str(path),
            "sourceSha256": _sha256(path),
            "reason": f"External certification gate is unreadable: {exc}",
        }
    if payload.get("contract") != EXTERNAL_GATE_CONTRACT:
        return {
            "status": "blocked_invalid_external_gate",
            "certified": False,
            "executionAllowed": False,
            "sourcePath": str(path),
            "sourceSha256": _sha256(path),
            "reason": "External certification gate contract is not recognized.",
        }
    rows = dict(payload.get("rows") or {})
    strength = dict(payload.get("strengthMatrix") or {})
    independent_drik = dict(payload.get("independentDrikWitness") or {})
    independent_rows = dict(independent_drik.get("rows") or {})
    certified = (
        payload.get("status") == "passed_external_validation"
        and payload.get("certified") is True
        and payload.get("executionAllowed") is False
        and int(rows.get("fail") or 0) == 0
        and int(rows.get("pending") or 0) == 0
        and int(strength.get("expectedRows") or 0) > 0
        and int(strength.get("actualRows") or 0) == int(strength.get("expectedRows") or -1)
        and int(strength.get("pass") or 0) == int(strength.get("expectedRows") or -1)
        and int(strength.get("fail") or 0) == 0
        and int(strength.get("pending") or 0) == 0
        and independent_drik.get("status") == "passed_independent_validation"
        and independent_drik.get("certified") is True
        and int(independent_rows.get("expected") or 0) > 0
        and int(independent_rows.get("actual") or 0)
        == int(independent_rows.get("expected") or -1)
        and int(independent_rows.get("pass") or 0)
        == int(independent_rows.get("expected") or -1)
        and int(independent_rows.get("fail") or 0) == 0
        and int(independent_rows.get("pending") or 0) == 0
    )
    return {
        **payload,
        "certified": certified,
        "sourcePath": str(path),
        "sourceSha256": _sha256(path),
        "reason": (
            "All declared Shadbala/Drik rows and the separate independent Drik witness passed."
            if certified
            else "Shadbala/Drik evidence or the separate independent Drik witness is incomplete or failed."
        ),
    }


def _gate(
    gate_id: str,
    title: str,
    status: str,
    detail: str,
    *,
    blocking: bool,
    source: str | None = None,
    metrics: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "gateId": gate_id,
        "title": title,
        "status": status,
        "blocking": blocking,
        "detail": detail,
        "source": source,
        "metrics": dict(metrics or {}),
    }


def build_validation_gate_matrix(
    project_root: Path,
    shadow_snapshot: Mapping[str, Any],
    candlestick_snapshot: Mapping[str, Any] | None,
    *,
    historical_contract: str,
    historical_status: str,
    historical_report: str,
) -> dict[str, Any]:
    external = load_external_gate(project_root)
    shadow_summary = dict(shadow_snapshot.get("summary") or {})
    trial = dict(shadow_summary.get("trial") or {})
    chain = dict(shadow_summary.get("chain") or {})
    prospective_status = str(shadow_summary.get("gateStatus") or "not_available")
    retrospective_passed = historical_status.startswith("passed")
    prospective_passed = prospective_status.startswith("passed")
    prospective_integrity = (
        chain.get("valid") is True
        and trial.get("integrityValid") is True
        and int(trial.get("cohortCount") or 0) <= 1
    )
    external_status = (
        "passed"
        if external.get("certified") is True
        else "failed"
        if str(external.get("status") or "").startswith("failed")
        else "blocked"
    )
    retrospective_status = "passed" if retrospective_passed else "failed"
    if prospective_status.startswith("passed"):
        prospective_label = "passed"
    elif prospective_status.startswith("failed"):
        prospective_label = "failed"
    elif prospective_status.startswith("collecting"):
        prospective_label = "collecting"
    else:
        prospective_label = "blocked"

    candle_gate = dict(
        ((candlestick_snapshot or {}).get("model") or {}).get("retrospectiveGate")
        or {}
    )
    candle_status_raw = str(candle_gate.get("status") or "not_available")
    candle_passed = (
        candle_status_raw.startswith("passed")
        and candle_gate.get("promotionAuthorized") is True
    )
    candle_status = "passed" if candle_passed else "failed" if candle_status_raw.startswith("failed") else "blocked"

    gates = [
        _gate(
            "timestamp_safe_inference",
            "Timestamp-safe inference",
            "passed",
            "Live packets exclude future prices and outcome labels; Bar Replay reveals only closed evidence.",
            blocking=True,
            source="GANN_TIMESTAMP_SAFE_DECISION_PACKET_V1",
        ),
        _gate(
            "external_astrology",
            "External Shadbala / Drik",
            external_status,
            str(external.get("reason") or ""),
            blocking=True,
            source=external.get("sourcePath"),
            metrics=dict(external.get("strengthMatrix") or {}),
        ),
        _gate(
            "retrospective_policy",
            "Purged retrospective policy",
            retrospective_status,
            (
                "The frozen policy passed its predeclared retrospective statistical gate."
                if retrospective_passed
                else "The frozen evaluation did not clear its predeclared retrospective thresholds."
            ),
            blocking=True,
            source=historical_report,
            metrics={
                "contract": historical_contract,
                "status": historical_status,
            },
        ),
        _gate(
            "prospective_shadow",
            "Prospective shadow trial",
            prospective_label,
            (
                "Frozen prospective policy has passed every predeclared statistical criterion."
                if prospective_passed
                else "Evidence collection continues under one immutable policy cohort."
                if prospective_label == "collecting"
                else "Prospective evidence failed or its cohort integrity is blocked."
            ),
            blocking=True,
            source=str(trial.get("trialId") or "") or None,
            metrics={
                "integrityValid": prospective_integrity,
                "watchClusters": shadow_summary.get("watchClusterCount"),
                "targetWatchClusters": (trial.get("progress") or {}).get("watchClusters", {}).get("target"),
                "calendarMonths": shadow_summary.get("calendarMonthCount"),
                "targetCalendarMonths": (trial.get("progress") or {}).get("calendarMonths", {}).get("target"),
                "coverage": shadow_summary.get("coverage"),
                "wilson95Lower": shadow_summary.get("wilson95Lower"),
                "twoSidedBinomialP": shadow_summary.get("twoSidedBinomialP"),
                "meanSigned72hReturnPct": shadow_summary.get("meanSigned72hReturnPct"),
            },
        ),
        _gate(
            "candlestick_agent",
            "Candlestick agent",
            candle_status,
            (
                "Separate candlestick model cleared its own promotion gate."
                if candle_passed
                else "Separate candlestick model remains diagnostic and cannot influence astrology decisions."
            ),
            blocking=False,
            source=str(((candlestick_snapshot or {}).get("model") or {}).get("artifactId") or "") or None,
            metrics={
                "status": candle_status_raw,
                "primaryCandidate": candle_gate.get("primaryCandidate"),
                "promotionAuthorized": candle_gate.get("promotionAuthorized"),
            },
        ),
        _gate(
            "execution_authorization",
            "Order execution authorization",
            "locked",
            "The application is market-data and shadow-research only; no order-placement subsystem is authorized.",
            blocking=True,
            source="application_policy",
        ),
    ]
    prerequisites_passed = (
        external.get("certified") is True
        and retrospective_passed
        and prospective_passed
        and prospective_integrity
    )
    return {
        "contract": MATRIX_CONTRACT,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "overallStatus": (
            "prerequisites_passed_execution_still_locked"
            if prerequisites_passed
            else "research_only_blocked"
        ),
        "prerequisitesPassed": prerequisites_passed,
        "executionAllowed": False,
        "blockingGateIds": [
            item["gateId"]
            for item in gates
            if item["blocking"] and item["status"] != "passed"
        ],
        "gates": gates,
    }
