from __future__ import annotations

import base64
import binascii
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(
    os.environ.get("GANN_ASTRO_PROJECT_ROOT") or Path(__file__).resolve().parents[2]
).resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sbc.chakra_lab import (  # noqa: E402
    ChakraLabActorSelection,
    ChakraLabEngine,
    ChakraLabRequest,
)
from sbc.atomic_intervals import (  # noqa: E402
    SbcAtomicIntervalCompiler,
    boundary_from_chakra_snapshot,
)
from sbc.audit_views import SbcLinkedAuditViewCompiler  # noqa: E402
from sbc.audit_packages import (  # noqa: E402
    SbcAuditBookmarkInput,
    SbcAuditComparisonPackageCompiler,
    SbcAuditPackageVerification,
    render_audit_package_html,
    validate_audit_package_payload,
    verify_audit_package_replay,
)
from sbc.audit_catalog import (  # noqa: E402
    SbcAuditPackageCatalogCompiler,
    load_or_create_signing_key,
    sign_audit_catalog,
    verify_signed_audit_catalog,
)
from sbc.fixed_phasor import SbcFixedPhasorCompiler  # noqa: E402
from sbc.models import GeoLocation  # noqa: E402
from sbc.multidimensional_ledger import (  # noqa: E402
    SbcMultidimensionalLedgerCompiler,
)
from sbc.timing_profile_admission import (  # noqa: E402
    SbcTimingProfileAdmissionGate,
)
from sbc.timing_profile_source_packet import (  # noqa: E402
    SbcTimingProfileSourcePacketGate,
)
from sbc.timing_profile_source_verification import (  # noqa: E402
    SbcTimingProfileSourceVerificationCompiler,
)
from sbc.vedha import (  # noqa: E402
    GUIDANCE_MODEL_ID,
    DignityState,
    MotionClass,
    PlanetNature,
    load_vedha_profile,
)


DEFAULT_BODIES = (
    "SUN",
    "MOON",
    "MARS",
    "MERCURY",
    "JUPITER",
    "VENUS",
    "SATURN",
    "RAHU",
    "KETU",
)
REQUEST_KEYS = {
    "at",
    "timezone",
    "latitude",
    "longitude",
    "altitudeM",
    "bodies",
    "actors",
    "foundationProfileId",
    "gridProfileId",
    "vedhaProfileId",
    "vowels",
    "nameInitials",
}
ACTOR_KEYS = {
    "body",
    "motionClass",
    "nature",
    "dignity",
    "mercuryAssociationNature",
}
AUDIT_REQUEST_KEYS = {
    "instrumentIdentity",
    "terminalEnd",
    "boundaries",
}
TIMING_PROFILE_ADMISSION_REQUEST_KEYS = {"profile"}
TIMING_SOURCE_PACKET_REQUEST_KEYS = {"profile", "packet"}
TIMING_SOURCE_VERIFICATION_REQUEST_KEYS = {
    "profile",
    "packet",
    "sourcePayloads",
    "excerptPayloads",
}
MAX_SOURCE_PAYLOAD_BYTES = 64 * 1024 * 1024
MAX_TOTAL_SOURCE_PAYLOAD_BYTES = 192 * 1024 * 1024
MAX_EXCERPT_PAYLOAD_BYTES = 256 * 1024
MAX_TOTAL_EXCERPT_PAYLOAD_BYTES = 8 * 1024 * 1024
AUDIT_BOUNDARY_KEYS = {
    "reason",
    "request",
}
AUDIT_PACKAGE_REQUEST_KEYS = {
    "auditRequest",
    "baselineIntervalId",
    "comparisonIntervalIds",
    "bookmarks",
    "sealedAt",
}
AUDIT_PACKAGE_BOOKMARK_KEYS = {
    "targetType",
    "targetId",
    "label",
    "note",
    "createdAt",
}
AUDIT_PACKAGE_VERIFY_KEYS = {
    "package",
}
AUDIT_PACKAGE_REPLAY_KEYS = {
    "audit_request",
    "baseline_interval_id",
    "comparison_interval_ids",
    "bookmarks",
    "sealed_at_utc",
}
AUDIT_CATALOG_REQUEST_KEYS = {
    "packages",
    "createdAt",
    "signedAt",
}
AUDIT_CATALOG_VERIFY_KEYS = {
    "bundle",
    "fullReplay",
}


def _reject_unknown(payload: dict[str, Any], allowed: set[str], label: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(unknown)}")


def _required_text(value: Any, label: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def _offset_datetime(value: Any, label: str = "at") -> datetime:
    text = _required_text(value, label).replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a UTC offset")
    return parsed


def _string_tuple(
    value: Any, label: str, default: tuple[str, ...] = ()
) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    normalized = tuple(str(item).strip().upper() for item in value)
    if any(not item for item in normalized):
        raise ValueError(f"{label} must contain non-empty values")
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{label} must not contain duplicates")
    return normalized


def _optional_enum(enum_type: type[Any], value: Any, label: str) -> Any:
    text = str(value or "").strip().upper()
    if not text:
        return None
    try:
        return enum_type(text)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ValueError(f"{label} must be one of: {allowed}") from exc


def _actor(value: Any) -> ChakraLabActorSelection:
    if not isinstance(value, dict):
        raise ValueError("each actor must be an object")
    _reject_unknown(value, ACTOR_KEYS, "actor")
    dignity = _optional_enum(
        DignityState, value.get("dignity") or "ORDINARY", "dignity"
    )
    return ChakraLabActorSelection(
        body=_required_text(value.get("body"), "actor.body").upper(),
        motion_class=_optional_enum(
            MotionClass, value.get("motionClass"), "motionClass"
        ),
        nature=_optional_enum(PlanetNature, value.get("nature"), "nature"),
        dignity=dignity,
        mercury_association_nature=_optional_enum(
            PlanetNature,
            value.get("mercuryAssociationNature"),
            "mercuryAssociationNature",
        ),
    )


def _chakra_lab_request(payload: Any) -> ChakraLabRequest:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab request must be an object")
    _reject_unknown(payload, REQUEST_KEYS, "Chakra Lab request")
    actors_raw = payload.get("actors") or []
    if not isinstance(actors_raw, list):
        raise ValueError("actors must be an array")
    return ChakraLabRequest(
        at=_offset_datetime(payload.get("at")),
        location=GeoLocation(
            latitude=float(payload.get("latitude", 28.6139)),
            longitude=float(payload.get("longitude", 77.2090)),
            timezone=str(payload.get("timezone") or "Asia/Kolkata"),
            altitude_m=float(payload.get("altitudeM", 0.0)),
        ),
        bodies=_string_tuple(payload.get("bodies"), "bodies", DEFAULT_BODIES),
        actors=tuple(_actor(item) for item in actors_raw),
        foundation_profile_id=str(
            payload.get("foundationProfileId") or "sbc_raman_foundation_v1"
        ),
        grid_profile_id=str(
            payload.get("gridProfileId") or "sbc_81_rotation_normalized_partial_v1"
        ),
        vedha_profile_id=str(
            payload.get("vedhaProfileId") or "phaladeepika_editor_vedha_guidance_v1"
        ),
        vowels=_string_tuple(payload.get("vowels"), "vowels"),
        name_initials=_string_tuple(payload.get("nameInitials"), "nameInitials"),
    )


def build_chakra_lab_snapshot(payload: Any) -> dict[str, Any]:
    request = _chakra_lab_request(payload)
    return ChakraLabEngine().snapshot(request).to_dict()


def _build_chakra_lab_ledger(payload: Any):
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit request must be an object")
    _reject_unknown(payload, AUDIT_REQUEST_KEYS, "Chakra Lab audit request")
    instrument_identity = _required_text(
        payload.get("instrumentIdentity"),
        "instrumentIdentity",
    )
    terminal_end = _offset_datetime(payload.get("terminalEnd"), "terminalEnd")
    boundaries_raw = payload.get("boundaries")
    if not isinstance(boundaries_raw, list) or not boundaries_raw:
        raise ValueError("boundaries must be a non-empty array")

    engine = ChakraLabEngine()
    boundaries = []
    for index, item in enumerate(boundaries_raw):
        if not isinstance(item, dict):
            raise ValueError(f"boundary {index + 1} must be an object")
        _reject_unknown(item, AUDIT_BOUNDARY_KEYS, f"boundary {index + 1}")
        reason = _required_text(item.get("reason"), f"boundary {index + 1}.reason")
        request = _chakra_lab_request(item.get("request"))
        snapshot = engine.snapshot(request)
        if snapshot.guidance is None:
            profile = load_vedha_profile(request.vedha_profile_id)
            boundary = boundary_from_chakra_snapshot(
                snapshot,
                boundary_reason=reason,
                unavailable_vedha_profile_id=profile.vedha_profile_id,
                unavailable_vedha_profile_hash=profile.profile_hash,
                unavailable_guidance_model_id=GUIDANCE_MODEL_ID,
            )
        else:
            boundary = boundary_from_chakra_snapshot(
                snapshot,
                boundary_reason=reason,
            )
        boundaries.append(boundary)

    atomic = SbcAtomicIntervalCompiler().compile(
        boundaries,
        terminal_end_utc=terminal_end,
    )
    ledger = SbcMultidimensionalLedgerCompiler().compile(
        atomic,
        instrument_identity=instrument_identity,
    )
    return ledger


def _build_chakra_lab_audit(payload: Any):
    return SbcLinkedAuditViewCompiler().compile(_build_chakra_lab_ledger(payload))


def build_chakra_lab_audit(payload: Any) -> dict[str, Any]:
    return _build_chakra_lab_audit(payload).to_dict()


def build_chakra_lab_fixed_phasor(payload: Any) -> dict[str, Any]:
    ledger = _build_chakra_lab_ledger(payload)
    return SbcFixedPhasorCompiler().compile(ledger).to_dict()


def build_chakra_lab_timing_profile_admission(
    payload: Any,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("timing profile admission request must be an object")
    _reject_unknown(
        payload,
        TIMING_PROFILE_ADMISSION_REQUEST_KEYS,
        "timing profile admission request",
    )
    registry_path = PROJECT_ROOT / "status" / "timing_phase_profile_registry.json"
    trials_path = PROJECT_ROOT / "status" / "research_trials.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    research_trials = json.loads(trials_path.read_text(encoding="utf-8"))
    return SbcTimingProfileAdmissionGate(
        registry,
        research_trials,
    ).evaluate(payload.get("profile")).to_dict()


def build_chakra_lab_timing_source_packet_readiness(
    payload: Any,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("timing source packet request must be an object")
    _reject_unknown(
        payload,
        TIMING_SOURCE_PACKET_REQUEST_KEYS,
        "timing source packet request",
    )
    return SbcTimingProfileSourcePacketGate().evaluate(
        payload.get("profile"),
        payload.get("packet"),
    ).to_dict()


def _decode_timing_source_payloads(value: Any) -> dict[str, bytes] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("sourcePayloads must be an object keyed by sourceId")
    decoded: dict[str, bytes] = {}
    total_bytes = 0
    for raw_source_id, encoded in value.items():
        source_id = _required_text(raw_source_id, "sourcePayloads sourceId")
        if not isinstance(encoded, str) or not encoded:
            raise ValueError(
                f"sourcePayloads.{source_id} must be non-empty base64 text"
            )
        try:
            payload = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(
                f"sourcePayloads.{source_id} is not valid base64"
            ) from exc
        if not payload:
            raise ValueError(f"sourcePayloads.{source_id} decodes to empty bytes")
        if len(payload) > MAX_SOURCE_PAYLOAD_BYTES:
            raise ValueError(
                f"sourcePayloads.{source_id} exceeds "
                f"{MAX_SOURCE_PAYLOAD_BYTES} bytes"
            )
        total_bytes += len(payload)
        if total_bytes > MAX_TOTAL_SOURCE_PAYLOAD_BYTES:
            raise ValueError(
                "combined sourcePayloads exceed "
                f"{MAX_TOTAL_SOURCE_PAYLOAD_BYTES} bytes"
            )
        decoded[source_id] = payload
    return decoded


def _decode_timing_excerpt_payloads(value: Any) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("excerptPayloads must be an object keyed by claimId")
    decoded: dict[str, str] = {}
    total_bytes = 0
    for raw_claim_id, excerpt in value.items():
        claim_id = _required_text(raw_claim_id, "excerptPayloads claimId")
        if not isinstance(excerpt, str) or not excerpt:
            raise ValueError(
                f"excerptPayloads.{claim_id} must be non-empty UTF-8 text"
            )
        byte_length = len(excerpt.encode("utf-8"))
        if byte_length > MAX_EXCERPT_PAYLOAD_BYTES:
            raise ValueError(
                f"excerptPayloads.{claim_id} exceeds "
                f"{MAX_EXCERPT_PAYLOAD_BYTES} UTF-8 bytes"
            )
        total_bytes += byte_length
        if total_bytes > MAX_TOTAL_EXCERPT_PAYLOAD_BYTES:
            raise ValueError(
                "combined excerptPayloads exceed "
                f"{MAX_TOTAL_EXCERPT_PAYLOAD_BYTES} UTF-8 bytes"
            )
        decoded[claim_id] = excerpt
    return decoded


def build_chakra_lab_timing_source_verification(
    payload: Any,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("timing source verification request must be an object")
    _reject_unknown(
        payload,
        TIMING_SOURCE_VERIFICATION_REQUEST_KEYS,
        "timing source verification request",
    )
    return SbcTimingProfileSourceVerificationCompiler().compile(
        payload.get("profile"),
        payload.get("packet"),
        _decode_timing_source_payloads(payload.get("sourcePayloads")),
        _decode_timing_excerpt_payloads(payload.get("excerptPayloads")),
    ).to_dict()


def _bookmark_input(payload: Any, label: str) -> SbcAuditBookmarkInput:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be an object")
    _reject_unknown(payload, AUDIT_PACKAGE_BOOKMARK_KEYS, label)
    return SbcAuditBookmarkInput(
        target_type=_required_text(payload.get("targetType"), f"{label}.targetType"),
        target_id=_required_text(payload.get("targetId"), f"{label}.targetId"),
        label=_required_text(payload.get("label"), f"{label}.label"),
        note=_required_text(payload.get("note"), f"{label}.note"),
        created_at_utc=_offset_datetime(
            payload.get("createdAt"),
            f"{label}.createdAt",
        ),
    )


def _bookmark_recipe(value: SbcAuditBookmarkInput) -> dict[str, Any]:
    return {
        "targetType": value.target_type,
        "targetId": value.target_id,
        "label": value.label,
        "note": value.note,
        "createdAt": value.created_at_utc.isoformat(),
    }


def _audit_package_inputs(
    payload: Any,
) -> tuple[
    Any,
    str,
    tuple[str, ...],
    tuple[SbcAuditBookmarkInput, ...],
    datetime,
    dict[str, Any],
]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit package request must be an object")
    _reject_unknown(
        payload,
        AUDIT_PACKAGE_REQUEST_KEYS,
        "Chakra Lab audit package request",
    )
    audit_request = payload.get("auditRequest")
    source_audit = _build_chakra_lab_audit(audit_request)
    baseline_interval_id = _required_text(
        payload.get("baselineIntervalId"),
        "baselineIntervalId",
    )
    comparison_interval_ids = _string_tuple(
        payload.get("comparisonIntervalIds"),
        "comparisonIntervalIds",
    )
    bookmark_payloads = payload.get("bookmarks") or []
    if not isinstance(bookmark_payloads, list):
        raise ValueError("bookmarks must be an array")
    bookmarks = tuple(
        _bookmark_input(item, f"bookmark {index + 1}")
        for index, item in enumerate(bookmark_payloads)
    )
    sealed_at_utc = _offset_datetime(payload.get("sealedAt"), "sealedAt")
    replay_recipe = {
        "audit_request": audit_request,
        "baseline_interval_id": baseline_interval_id,
        "comparison_interval_ids": list(comparison_interval_ids),
        "bookmarks": [_bookmark_recipe(item) for item in bookmarks],
        "sealed_at_utc": sealed_at_utc.isoformat(),
    }
    return (
        source_audit,
        baseline_interval_id,
        comparison_interval_ids,
        bookmarks,
        sealed_at_utc,
        replay_recipe,
    )


def build_chakra_lab_audit_package(payload: Any) -> dict[str, Any]:
    (
        source_audit,
        baseline_interval_id,
        comparison_interval_ids,
        bookmarks,
        sealed_at_utc,
        replay_recipe,
    ) = _audit_package_inputs(payload)
    package = SbcAuditComparisonPackageCompiler().compile(
        source_audit,
        baseline_interval_id=baseline_interval_id,
        comparison_interval_ids=comparison_interval_ids,
        bookmark_inputs=bookmarks,
        sealed_at_utc=sealed_at_utc,
        replay_recipe=replay_recipe,
    )
    return {
        "package": package.to_dict(),
        "htmlReport": render_audit_package_html(package),
    }


def _package_request_from_recipe(recipe: Any) -> dict[str, Any]:
    if not isinstance(recipe, dict):
        raise ValueError("replay_recipe must be an object")
    _reject_unknown(recipe, AUDIT_PACKAGE_REPLAY_KEYS, "replay recipe")
    return {
        "auditRequest": recipe.get("audit_request"),
        "baselineIntervalId": recipe.get("baseline_interval_id"),
        "comparisonIntervalIds": recipe.get("comparison_interval_ids"),
        "bookmarks": recipe.get("bookmarks"),
        "sealedAt": recipe.get("sealed_at_utc"),
    }


def verify_chakra_lab_audit_package(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit package verification must be an object")
    _reject_unknown(
        payload,
        AUDIT_PACKAGE_VERIFY_KEYS,
        "Chakra Lab audit package verification",
    )
    package_payload = payload.get("package")
    try:
        validate_audit_package_payload(package_payload)
        rebuilt = build_chakra_lab_audit_package(
            _package_request_from_recipe(package_payload["replay_recipe"])
        )["package"]
        return verify_audit_package_replay(package_payload, rebuilt).to_dict()
    except (KeyError, TypeError, ValueError) as exc:
        package_id = (
            package_payload.get("package_id")
            if isinstance(package_payload, dict)
            else None
        )
        source_audit_id = (
            package_payload.get("source_audit_id")
            if isinstance(package_payload, dict)
            else None
        )
        return SbcAuditPackageVerification(
            contract="SBC_AUDIT_PACKAGE_VERIFICATION_V1",
            state="FAIL",
            package_id=package_id,
            source_audit_id=source_audit_id,
            structural_hash_match=False,
            source_projection_match=False,
            replay_recipe_match=False,
            replay_audit_match=False,
            replay_package_match=False,
            errors=(str(exc),),
        ).to_dict()


def _audit_catalog_signing_key_path() -> Path:
    configured_key = str(
        os.environ.get("GANN_ASTRO_SBC_CATALOG_SIGNING_KEY") or ""
    ).strip()
    if configured_key:
        return Path(configured_key).resolve()
    configured_root = str(os.environ.get("GANN_ASTRO_DESKTOP_DATA") or "").strip()
    if configured_root:
        data_root = Path(configured_root).resolve()
    elif Path(r"D:\GannFinancialAstro").exists():
        data_root = Path(r"D:\GannFinancialAstro\app_data")
    else:
        data_root = PROJECT_ROOT / ".local_app_data"
    return data_root / "sbc_audit_catalog" / "ed25519_signing_key.dpapi"


def _audit_catalog_packages(value: Any) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list) or not value:
        raise ValueError("packages must be a non-empty array")
    packages: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"package {index + 1} must be an object")
        packages.append(item)
    return tuple(packages)


def build_chakra_lab_audit_catalog(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit catalog request must be an object")
    _reject_unknown(
        payload,
        AUDIT_CATALOG_REQUEST_KEYS,
        "Chakra Lab audit catalog request",
    )
    packages = _audit_catalog_packages(payload.get("packages"))
    created_at = _offset_datetime(payload.get("createdAt"), "createdAt")
    signed_at = _offset_datetime(payload.get("signedAt"), "signedAt")
    replay_verifications = {
        package.get("package_id"): verify_chakra_lab_audit_package({"package": package})
        for package in packages
    }
    catalog = SbcAuditPackageCatalogCompiler().compile(
        packages,
        replay_verifications=replay_verifications,
        created_at_utc=created_at,
    )
    private_key = load_or_create_signing_key(_audit_catalog_signing_key_path())
    bundle = sign_audit_catalog(
        catalog,
        private_key,
        signed_at_utc=signed_at,
    ).to_dict()
    verification = verify_signed_audit_catalog(
        bundle,
        replay_verifications=replay_verifications,
    ).to_dict()
    return {
        "bundle": bundle,
        "verification": verification,
        "signingIdentity": {
            "algorithm": bundle["signature"]["algorithm"],
            "keyId": bundle["signature"]["key_id"],
            "storage": "WINDOWS_DPAPI_APP_DATA"
            if os.name == "nt"
            else "LOCAL_USER_FILE",
            "claim": (
                "Local research provenance and integrity only; this is not an "
                "external identity, doctrine, or financial certification."
            ),
        },
    }


def verify_chakra_lab_audit_catalog(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Chakra Lab audit catalog verification must be an object")
    _reject_unknown(
        payload,
        AUDIT_CATALOG_VERIFY_KEYS,
        "Chakra Lab audit catalog verification",
    )
    bundle = payload.get("bundle")
    full_replay = payload.get("fullReplay", True)
    if not isinstance(full_replay, bool):
        raise ValueError("fullReplay must be a boolean")

    integrity = verify_signed_audit_catalog(bundle)
    if not full_replay or integrity.state != "PASS":
        return integrity.to_dict()

    replay_verifications: dict[str, dict[str, Any]] | None = None
    if isinstance(bundle, dict):
        catalog = bundle.get("catalog")
        entries = catalog.get("entries") if isinstance(catalog, dict) else None
        if isinstance(entries, list):
            replay_verifications = {}
            for item in entries:
                if not isinstance(item, dict):
                    continue
                package = item.get("package")
                package_id = item.get("package_id")
                if isinstance(package, dict) and isinstance(package_id, str):
                    replay_verifications[package_id] = verify_chakra_lab_audit_package(
                        {"package": package}
                    )
    return verify_signed_audit_catalog(
        bundle,
        replay_verifications=replay_verifications,
    ).to_dict()
