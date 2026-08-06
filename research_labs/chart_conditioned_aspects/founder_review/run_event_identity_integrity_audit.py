"""Audit F2A transit identities and preserve founder packets fail-closed.

This is an offline astronomy-integrity tool.  It does not render price, infer
polarity, admit catalogue evidence, or write any founder decision.  V1 packets
are read-only audit history.  A V2 packet is written only if a V1 row fails the
new explicit single-pass identity rule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LAB_ROOT = PROJECT_ROOT / "research_labs" / "chart_conditioned_aspects"
INSTRUMENT_SBC_ROOT = PROJECT_ROOT / "research_labs" / "instrument_relative_sbc"
for candidate in (PROJECT_ROOT, LAB_ROOT, INSTRUMENT_SBC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from financial_astro_ephemeris import configure_ephemeris  # noqa: E402

from chart_conditioned_aspects.founder_chart_registry import require_founder_chart_identity  # noqa: E402
from chart_conditioned_aspects.models import stable_hash  # noqa: E402
from chart_conditioned_aspects.transits.chart_conditioned_event_compiler import (  # noqa: E402
    APPROVED_ASPECT_PROFILE_ID,
    _calculate_sidereal_geocentric_longitude,
    compile_chart_conditioned_transit_event_range,
)
from chart_conditioned_aspects.transits.event_identity_audit import (  # noqa: E402
    EVENT_IDENTITY_AUDIT_CONTRACT,
    EVENT_IDENTITY_AUDIT_VERSION,
    verify_event_identity,
)
from generate_blank_polarity_review_packs import (  # noqa: E402
    ALLOWED_EVIDENCE_CLASSES,
    ALLOWED_POLARITIES,
    MANIFEST_CONTRACT,
    PACK_CONTRACT,
    PILOT_END_UTC,
    PILOT_START_UTC,
    _blank_review_row,
    _event_identity,
    _parse_utc,
)


UTC = timezone.utc
AUDIT_CONTRACT = "PFR_V2B_R5_F2A_R1_EVENT_IDENTITY_INTEGRITY_AUDIT_V1"
V1_VERIFICATION_CONTRACT = "FOUNDER_BLANK_POLARITY_REVIEW_V1_IDENTITY_VERIFICATION_MANIFEST_V1"
V2_PACK_CONTRACT = "FOUNDER_BLANK_POLARITY_REVIEW_PACKET_V2"
V2_MANIFEST_CONTRACT = "FOUNDER_BLANK_POLARITY_REVIEW_GENERATION_MANIFEST_V2"
SIDES = ("USD", "JPY")
SPECIAL_BODIES = ("MERCURY", "VENUS", "MARS", "JUPITER", "SATURN", "RAHU", "KETU")


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _v1_path(output_root: Path, side: str) -> Path:
    return output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json"


def _v1_manifest_path(output_root: Path, side: str) -> Path:
    return output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.manifest.json"


def _is_exact_inside_pilot(event: dict[str, Any]) -> bool:
    return _parse_utc(PILOT_START_UTC) <= _parse_utc(event["exactUtc"]) < _parse_utc(PILOT_END_UTC)


def _intersects_pilot(observed: dict[str, Any]) -> bool:
    start = _parse_utc(observed["observedSearchStartUtc"])
    end = _parse_utc(observed["observedSearchEndUtc"])
    return start < _parse_utc(PILOT_END_UTC) and end > _parse_utc(PILOT_START_UTC)


def _record_identity_verification(
    *,
    side: str,
    event: dict[str, Any],
    natal_longitudes: dict[str, float],
    identity: Any,
) -> dict[str, Any]:
    verification = verify_event_identity(
        event=event,
        natal_longitude=natal_longitudes[event["natalTarget"]],
        longitude=_calculate_sidereal_geocentric_longitude,
        expected_instrument_identity=identity.chart.instrument_id,
        expected_chart_id=identity.chart.chart_id,
        expected_chart_hypothesis_id=identity.chart_hypothesis_id,
    )
    return {
        "sideIdentity": side,
        "eventId": event["eventId"],
        "eventHash": event["eventHash"],
        "transitBody": event["transitBody"],
        "natalTarget": event["natalTarget"],
        "aspectType": event["aspectType"],
        "applyingStartUtc": event["applyingStartUtc"],
        "exactUtc": event["exactUtc"],
        "separatingEndUtc": event["separatingEndUtc"],
        **verification,
    }


def _node_identity_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    node_events = [event for event in events if event["transitBody"] in {"RAHU", "KETU"} or event["natalTarget"] in {"RAHU", "KETU"}]
    ids = [event["eventId"] for event in node_events]
    hashes = [event["eventHash"] for event in node_events]
    return {
        "nodeEventCount": len(node_events),
        "duplicateEventIds": sorted({item for item in ids if ids.count(item) > 1}),
        "duplicateEventHashes": sorted({item for item in hashes if hashes.count(item) > 1}),
        "status": "NO_ACCIDENTAL_NODE_OPPOSITION_IDENTITY_DUPLICATES"
        if len(ids) == len(set(ids)) and len(hashes) == len(set(hashes))
        else "NODE_OPPOSITION_IDENTITY_COLLISION_DETECTED",
        "note": "Rahu/Ketu geometry may be symmetric, but immutable event identity includes the named transit and natal bodies. Only duplicate IDs/hashes are treated as accidental duplicates.",
    }


def _summary(records: list[dict[str, Any]], compiled: dict[str, Any]) -> dict[str, Any]:
    exact_inside = [record for record in records if _is_exact_inside_pilot(record)]
    exact_outside = [record for record in records if not _is_exact_inside_pilot(record)]
    incomplete = [item for item in compiled["rejectedEvents"] if _intersects_pilot(item)]
    special: dict[str, dict[str, Any]] = {}
    for body in SPECIAL_BODIES:
        body_records = [record for record in records if record["transitBody"] == body]
        special[body] = {
            "overlappingWindowCount": len(body_records),
            "singlePassVerifiedCount": sum(record["status"] == "SINGLE_PASS_VERIFIED" for record in body_records),
            "multiPassUnresolvedCount": sum(record["status"] == "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED" for record in body_records),
            "boundaryVerificationFailedCount": sum(record["status"] == "BOUNDARY_VERIFICATION_FAILED" for record in body_records),
            "stationOrMotionReversalEventIds": [
                record["eventId"]
                for record in body_records
                if record["audit"]["stationOrMotionReversalTimestamps"]
                or (record["audit"]["motionPhaseAtExact"] or {}).get("phase") in {"RETROGRADE", "STATION"}
            ],
        }
    return {
        "totalOverlappingWindows": len(records),
        "singlePassVerifiedEvents": sum(record["status"] == "SINGLE_PASS_VERIFIED" for record in records),
        "multiPassUnresolvedWindows": sum(record["status"] == "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED" for record in records),
        "boundaryVerificationFailedWindows": sum(record["status"] == "BOUNDARY_VERIFICATION_FAILED" for record in records),
        "incompleteBoundaryWindowsOverlappingPilot": incomplete,
        "exactMomentsInsideApril": len(exact_inside),
        "exactMomentsOutsideAprilWhoseIntervalsOverlapApril": len(exact_outside),
        "eventsAffectedByRetrogradeOrStation": [
            record["eventId"]
            for record in records
            if record["audit"]["stationOrMotionReversalTimestamps"]
            or (record["audit"]["motionPhaseAtExact"] or {}).get("phase") in {"RETROGRADE", "STATION"}
        ],
        "specialTransitBodyFocus": special,
        "affectedEventIds": [record["eventId"] for record in records if record["status"] != "SINGLE_PASS_VERIFIED"],
    }


def _v1_packet_audit(
    *,
    side: str,
    v1_pack: dict[str, Any],
    verification_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for row in v1_pack["rows"]:
        event = row["eventIdentity"]
        verification = verification_by_id.get(event["eventId"])
        if verification is None:
            rows.append({"eventId": event["eventId"], "status": "BOUNDARY_VERIFICATION_FAILED", "reason": "V1_EVENT_NOT_FOUND_IN_RECOMPILED_AUDIT_RANGE"})
        else:
            rows.append({"eventId": event["eventId"], "status": verification["status"], "checks": verification["checks"]})
    return {
        "sideIdentity": side,
        "v1RowCount": len(rows),
        "rows": rows,
        "allRowsSinglePassVerified": all(row["status"] == "SINGLE_PASS_VERIFIED" for row in rows),
        "affectedV1EventIds": [row["eventId"] for row in rows if row["status"] != "SINGLE_PASS_VERIFIED"],
    }


def select_single_pass_replacements(events: list[dict[str, Any]], verification_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Deterministic V2 candidate order, with no outcome or polarity input."""

    valid = [
        event
        for event in events
        if _is_exact_inside_pilot(event)
        and verification_by_id.get(event["eventId"], {}).get("status") == "SINGLE_PASS_VERIFIED"
    ]
    return sorted(valid, key=lambda event: (event["exactUtc"], event["eventId"]))[:12]


def _build_v2_pack(
    *,
    side: str,
    v1_pack: dict[str, Any],
    events: list[dict[str, Any]],
    verification_by_id: dict[str, dict[str, Any]],
    v1_audit: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected = select_single_pass_replacements(events, verification_by_id)
    v1_ids = [row["eventIdentity"]["eventId"] for row in v1_pack["rows"]]
    selected_ids = [event["eventId"] for event in selected]
    replacement_reason = {
        "rule": "EXCLUDE_RECORDS_NOT_SINGLE_PASS_VERIFIED_BY_PFR_V2B_R5_F2A_R1",
        "excludedV1EventIds": v1_audit["affectedV1EventIds"],
        "selectionOrder": "EXACT_UTC_THEN_EVENT_ID",
        "prohibitedInputs": ["price", "polarity", "SBC", "LLM", "waveCoverage", "visualAttractiveness"],
    }
    pack = {
        "contract": V2_PACK_CONTRACT,
        "packetVersion": 2,
        "packetStatus": "BLANK_FOUNDER_REVIEW_REQUIRED",
        "supersedesForIdentityReviewOnly": f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
        "sideIdentity": side,
        "instrumentIdentity": v1_pack["instrumentIdentity"],
        "chartId": v1_pack["chartId"],
        "chartHypothesisId": v1_pack["chartHypothesisId"],
        "selectionWindow": {
            **v1_pack["selectionWindow"],
            "selectionRule": "FIRST_TWELVE_SINGLE_PASS_VERIFIED_EVENT_IDENTITIES_SORTED_BY_EXACT_UTC",
        },
        "eventCompiler": v1_pack["eventCompiler"],
        "identityAudit": {
            "contract": EVENT_IDENTITY_AUDIT_CONTRACT,
            "auditVersion": EVENT_IDENTITY_AUDIT_VERSION,
            "selectionChangeReason": replacement_reason,
        },
        "allowedFounderPolarityDecisions": list(ALLOWED_POLARITIES),
        "allowedEvidenceClassifications": list(ALLOWED_EVIDENCE_CLASSES),
        "sourceOnlyAdmission": v1_pack["sourceOnlyAdmission"],
        "founderResearchAdmission": v1_pack["founderResearchAdmission"],
        "totalSinglePassVerifiedEventsInWindow": len(
            [event for event in events if _is_exact_inside_pilot(event) and verification_by_id.get(event["eventId"], {}).get("status") == "SINGLE_PASS_VERIFIED"]
        ),
        "includedEventCount": len(selected),
        "rows": [_blank_review_row(event) for event in selected],
        "guardrails": v1_pack["guardrails"],
    }
    manifest = {
        "contract": V2_MANIFEST_CONTRACT,
        "manifestVersion": 2,
        "sideIdentity": side,
        "supersedesForIdentityReviewOnly": f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.json",
        "sourceV1EventIds": v1_ids,
        "includedEventIds": selected_ids,
        "selectionChangeReason": replacement_reason,
        "eventIdentityAuditContract": EVENT_IDENTITY_AUDIT_CONTRACT,
        "guardrails": pack["guardrails"],
    }
    return pack, manifest


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_json_bytes(value))


def _write_human_review_rendering(
    *,
    path: Path,
    side: str,
    pack: dict[str, Any],
    v1_audit: dict[str, Any],
) -> None:
    lines = [
        f"# {side} April 2025 Blank Founder Review",
        "",
        "Non-authoritative convenience rendering. The JSON packet is canonical.",
        "This rendering contains astronomy identity only; it contains no polarity, price, SBC, or LLM recommendation.",
        "",
        f"- Chart: `{pack['chartId']}`",
        f"- Hypothesis: `{pack['chartHypothesisId']}`",
        f"- UTC review window: `{pack['selectionWindow']['startUtc']}` to `{pack['selectionWindow']['endUtc']}`",
        "- IST review window: `2025-04-01 05:30 IST` to `2025-05-01 05:30 IST`",
        "",
        "| # | Identity audit | Transit | Natal target | Aspect | Applying UTC | Exact UTC | Exact IST | Separating UTC | Event ID | Event hash | Founder polarity | Evidence class | References | Reasoning | Reviewer | Timestamp |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    audit_by_id = {row["eventId"]: row for row in v1_audit["rows"]}
    for index, row in enumerate(pack["rows"], start=1):
        event = row["eventIdentity"]
        exact_ist = _parse_utc(event["exactUtc"]).astimezone(timezone(timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M:%S IST")
        status = audit_by_id.get(event["eventId"], {}).get("status", "NOT_AUDITED")
        lines.append(
            "| {index} | {status} | {transit} | {target} | {aspect} | {start} | {exact} | {exact_ist} | {end} | `{event_id}` | `{event_hash}` |  |  |  |  |  |  |".format(
                index=index,
                status=status,
                transit=event["transitBody"],
                target=event["natalTarget"],
                aspect=event["aspectType"],
                start=event["applyingStartUtc"],
                exact=event["exactUtc"],
                exact_ist=exact_ist,
                end=event["separatingEndUtc"],
                event_id=event["eventId"],
                event_hash=event["eventHash"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _audit_side(side: str, output_root: Path) -> tuple[dict[str, Any], list[Path]]:
    configure_ephemeris()
    identity = require_founder_chart_identity(f"FX_CURRENCY:{side}")
    compiled = compile_chart_conditioned_transit_event_range(
        side_identity=side,
        range_start_utc=PILOT_START_UTC,
        range_end_utc=PILOT_END_UTC,
        aspect_profile_id=APPROVED_ASPECT_PROFILE_ID,
    )
    natal_longitudes = {
        body: _calculate_sidereal_geocentric_longitude(body, identity.chart.timestamp_utc)
        for body in ("SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN", "RAHU", "KETU")
    }
    records = [
        _record_identity_verification(side=side, event=event, natal_longitudes=natal_longitudes, identity=identity)
        for event in compiled["events"]
    ]
    records.sort(key=lambda record: (record["applyingStartUtc"], record["eventId"]))
    verification_by_id = {record["eventId"]: record for record in records}
    v1_path = _v1_path(output_root, side)
    v1_pack = _read_json(v1_path)
    v1_audit = _v1_packet_audit(side=side, v1_pack=v1_pack, verification_by_id=verification_by_id)
    outputs: list[Path] = []
    side_report: dict[str, Any] = {
        "sideIdentity": side,
        "acceptedChart": {
            "instrumentIdentity": identity.chart.instrument_id,
            "chartId": identity.chart.chart_id,
            "chartHypothesisId": identity.chart_hypothesis_id,
            "astronomyContract": identity.chart.astronomy_contract,
        },
        "summary": _summary(records, compiled),
        "nodeOppositionIdentityCheck": _node_identity_summary(compiled["events"]),
        "v1PacketAudit": v1_audit,
        "eventRecords": records,
    }
    if v1_audit["allRowsSinglePassVerified"]:
        v1_bytes = v1_path.read_bytes()
        v1_manifest = _read_json(_v1_manifest_path(output_root, side))
        verification_manifest = {
            "contract": V1_VERIFICATION_CONTRACT,
            "sideIdentity": side,
            "packetFile": v1_path.name,
            "packetSha256": _sha256(v1_bytes),
            "originalGenerationManifestFile": _v1_manifest_path(output_root, side).name,
            "originalGenerationManifestOutputSha256": v1_manifest.get("outputSha256"),
            "identityAuditContract": EVENT_IDENTITY_AUDIT_CONTRACT,
            "identityAuditVersion": EVENT_IDENTITY_AUDIT_VERSION,
            "allRowsSinglePassVerified": True,
            "verifiedEventIds": [row["eventId"] for row in v1_audit["rows"]],
            "guardrails": {
                "polarityAssigned": False,
                "priceDataRead": False,
                "sbcRead": False,
                "llmRead": False,
                "catalogueAdmission": False,
                "executionAllowed": False,
            },
        }
        path = output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.manifest.json"
        _write_json(path, verification_manifest)
        outputs.append(path)
        render_path = output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V1.identity_integrity.md"
        _write_human_review_rendering(path=render_path, side=side, pack=v1_pack, v1_audit=v1_audit)
        outputs.append(render_path)
        side_report["packetOutcome"] = "V1_PRESERVED_AND_VERIFIED"
    else:
        v2_pack, v2_manifest = _build_v2_pack(
            side=side,
            v1_pack=v1_pack,
            events=compiled["events"],
            verification_by_id=verification_by_id,
            v1_audit=v1_audit,
        )
        v2_path = output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V2.json"
        v2_manifest.update({"outputFile": v2_path.name, "outputSha256": _sha256(_json_bytes(v2_pack))})
        v2_manifest_path = output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V2.manifest.json"
        _write_json(v2_path, v2_pack)
        _write_json(v2_manifest_path, v2_manifest)
        outputs.extend((v2_path, v2_manifest_path))
        render_path = output_root / f"{side}_APRIL_2025_BLANK_POLARITY_REVIEW_V2.identity_integrity.md"
        _write_human_review_rendering(path=render_path, side=side, pack=v2_pack, v1_audit=v1_audit)
        outputs.append(render_path)
        side_report["packetOutcome"] = "V2_CREATED_FROM_SINGLE_PASS_VERIFIED_REPLACEMENTS"
    return side_report, outputs


def run_audit(*, output_root: Path, status_path: Path) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    outputs: list[str] = []
    for side in SIDES:
        report, side_outputs = _audit_side(side, output_root)
        reports[side] = report
        outputs.extend(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/") for path in side_outputs)
    result = {
        "contract": AUDIT_CONTRACT,
        "auditVersion": EVENT_IDENTITY_AUDIT_VERSION,
        "auditWindow": {
            "startUtc": PILOT_START_UTC,
            "endUtc": PILOT_END_UTC,
            "ist": "2025-04-01 05:30 IST through 2025-05-01 05:30 IST",
        },
        "method": {
            "provider": "Swiss Ephemeris",
            "approach": "independent signed-residual branch scan, bracketed root refinement, golden-section local-minimum check, and numerical motion-reversal scan",
            "doesNotReuseProductionTernarySearchAsVerifier": True,
            "failClosedStatus": "MULTI_PASS_EVENT_IDENTITY_UNRESOLVED",
        },
        "sideReports": reports,
        "generatedReviewArtifacts": outputs,
        "guardrails": {
            "polarityAssigned": False,
            "priceDataRead": False,
            "sbcRead": False,
            "llmRead": False,
            "catalogueAdmission": False,
            "directionalWaveRendered": False,
            "executionAllowed": False,
            "packagingPerformed": False,
        },
    }
    _write_json(status_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--status-path",
        type=Path,
        default=PROJECT_ROOT / "status" / "audits" / "pfr_v2b_r5_f2a_r1_event_identity_integrity.json",
    )
    args = parser.parse_args()
    result = run_audit(output_root=args.output_root, status_path=args.status_path)
    for side, report in result["sideReports"].items():
        summary = report["summary"]
        print(
            f"{side}: single={summary['singlePassVerifiedEvents']} multi={summary['multiPassUnresolvedWindows']} "
            f"boundary={summary['boundaryVerificationFailedWindows']} packet={report['packetOutcome']}"
        )
    print(f"audit: {args.status_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
