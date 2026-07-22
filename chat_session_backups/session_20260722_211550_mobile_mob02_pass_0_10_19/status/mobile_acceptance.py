from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PLAN = Path(__file__).resolve().parent / "mobile_acceptance_plan.json"
DEFAULT_RESULT = Path(
    r"D:\GannFinancialAstro\acceptance\mobile\mobile_acceptance_results.local.json"
)
RESULT_CONTRACT = "GANN_MOBILE_PHYSICAL_ACCEPTANCE_RESULT_V1"
RESULT_STATUSES = {"passed", "failed", "blocked"}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def load_plan(path: Path = DEFAULT_PLAN) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def plan_sha256(plan: dict[str, Any]) -> str:
    return _sha256_bytes(_canonical_json(plan).encode("utf-8"))


def _evidence_record(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise ValueError(f"evidence file does not exist: {resolved}")
    return {
        "path": str(resolved),
        "sha256": _sha256_bytes(resolved.read_bytes()),
        "bytes": resolved.stat().st_size,
    }


def new_result(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": RESULT_CONTRACT,
        "planId": plan["planId"],
        "planSha256": plan_sha256(plan),
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updatedAtUtc": None,
        "status": "collecting_evidence",
        "candidatePair": {
            "desktop": dict(plan["desktopCandidate"]),
            "mobile": dict(plan["mobileCandidate"]),
        },
        "tests": {},
        "promotionAllowed": False,
        "executionAllowed": False,
    }


def load_result(path: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return new_result(plan)
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("contract") != RESULT_CONTRACT:
        raise ValueError("mobile result contract is invalid")
    if result.get("planId") != plan.get("planId"):
        raise ValueError("mobile result belongs to a different acceptance plan")
    if result.get("planSha256") != plan_sha256(plan):
        raise ValueError("mobile acceptance plan changed after evidence collection began")
    if result.get("executionAllowed") is not False:
        raise ValueError("mobile acceptance results cannot authorize execution")
    return result


def record_test(
    result: dict[str, Any],
    plan: dict[str, Any],
    *,
    test_id: str,
    status: str,
    observer: str,
    evidence_paths: list[Path],
    notes: str,
) -> dict[str, Any]:
    known = {item["testId"] for item in plan["tests"]}
    if test_id not in known:
        raise ValueError(f"unknown mobile acceptance test: {test_id}")
    if status not in RESULT_STATUSES:
        raise ValueError(f"unknown result status: {status}")
    normalized_observer = str(observer).strip()
    if not normalized_observer:
        raise ValueError("observer is required")
    evidence = [_evidence_record(path) for path in evidence_paths]
    if status == "passed" and not evidence:
        raise ValueError("a passed physical test requires at least one evidence file")
    recorded_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result["tests"][test_id] = {
        "status": status,
        "observer": normalized_observer,
        "recordedAtUtc": recorded_at,
        "notes": str(notes).strip(),
        "evidence": evidence,
    }
    result["updatedAtUtc"] = recorded_at
    statuses = [
        (result["tests"].get(item["testId"]) or {}).get("status", "pending")
        for item in plan["tests"]
    ]
    result["status"] = (
        "passed_all_physical_tests"
        if all(item == "passed" for item in statuses)
        else "failed_physical_tests"
        if "failed" in statuses
        else "blocked_physical_tests"
        if "blocked" in statuses
        else "collecting_evidence"
    )
    result["promotionAllowed"] = False
    result["executionAllowed"] = False
    return result


def save_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


def result_summary(result: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for test in plan["tests"]:
        recorded = result["tests"].get(test["testId"]) or {}
        rows.append(
            {
                "testId": test["testId"],
                "title": test["title"],
                "status": recorded.get("status", "pending"),
                "evidenceCount": len(recorded.get("evidence") or []),
            }
        )
    return {
        "contract": "GANN_MOBILE_PHYSICAL_ACCEPTANCE_SUMMARY_V1",
        "planId": plan["planId"],
        "status": result["status"],
        "tests": rows,
        "promotionAllowed": False,
        "executionAllowed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect hash-addressed physical mobile evidence.")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--record", metavar="MOB-ID")
    parser.add_argument("--status", choices=sorted(RESULT_STATUSES))
    parser.add_argument("--observer", default="")
    parser.add_argument("--evidence", action="append", type=Path, default=[])
    parser.add_argument("--notes", default="")
    args = parser.parse_args()
    plan = load_plan(args.plan)
    result = load_result(args.result, plan)
    if args.record:
        if not args.status:
            parser.error("--status is required with --record")
        record_test(
            result,
            plan,
            test_id=args.record,
            status=args.status,
            observer=args.observer,
            evidence_paths=args.evidence,
            notes=args.notes,
        )
        save_result(args.result, result)
    print(json.dumps(result_summary(result, plan), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
